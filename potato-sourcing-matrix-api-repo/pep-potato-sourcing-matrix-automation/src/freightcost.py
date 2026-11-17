"""Freight Cost Management API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from models import (FreightCostMapping, FreightCostRate,growing_area,
                    PlantSiteGrowingAreaMapping, freight_cost_period_table,
                    freight_cost_period_week_table, rate_growing_area_table,
                    FileUploadTemplate,Plant,View_freight_fuel_cost,View_freight_fuel_cost_ga,View_freight_fuel_cost,freight_task_mappings)
from sqlalchemy import func, and_, text, or_, case, select, update
from sqlalchemy.orm import Session
from pydantic import BaseModel
from io import BytesIO
import pandas as pd
import os
from datetime import datetime,date, timezone
from typing import List, Optional,Tuple, Dict, Any
from period_week_calc import calculate_period_dates

details_exception = "No records found for the given filter"

# Response Models for fetch_freight_records endpoint
class FreightRecordDetail(BaseModel):
    """Individual freight record detail"""
    freight_cost_id: int
    year: int
    period: int
    period_with_P: str
    rate: float
    company_name: str
    business_unit: str
    fuel_cf: Optional[float]
    round_trip: Optional[int]
    miles: Optional[float]
    growing_area_id: int
    vendor_site_id: int
    plant_id: int
    plant_name: str
    growing_area: str
    vendor_site_code: str

    class Config:
        from_attributes = True


class FreightRecordsResponse(BaseModel):
    """Freight records API response"""
    status: str
    data: List[FreightRecordDetail]
    debug: Optional[dict] = None

    class Config:
        from_attributes = True

router = APIRouter()


@router.get('/get_freight_cost_rate')
def view_freight_cost(db: Session = Depends(get_db)):
    """
    Retrieve all freight cost rate records from the database.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "All_data" (list): List of all FreightCostRate records
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(FreightCostRate).all()
        return {"All_data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/freight_alert')
def view_freight_cost(db: Session = Depends(get_db)):
    """
    Check for incomplete freight cost mappings and alert user.
    
    Retrieves all active freight cost mappings from the current year that have missing
    rate or miles data, joining with plant, site, and growing area information.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "message" (str): Alert message or "0" if no issues found
            - "table" (list): List of tuples with (plant_name, vendor_site_code, growing_area_desc)
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        today_date = date.today()
        year = int(today_date.year)
        records = (db.query(PlantSiteGrowingAreaMapping.plant_name,
                            PlantSiteGrowingAreaMapping.Vendor_Site_Code,
                            growing_area.growing_area_desc)
                    .select_from(FreightCostMapping)
                    .join(FreightCostRate,
                          FreightCostRate.freight_cost_id == FreightCostMapping.freight_cost_id)
                    .join(growing_area,
                          growing_area.growing_area_id == FreightCostRate.growing_area_id)
                    .join(PlantSiteGrowingAreaMapping,
                     and_(PlantSiteGrowingAreaMapping.growing_area_id ==FreightCostRate.growing_area_id,
                          PlantSiteGrowingAreaMapping.plant_id == FreightCostRate.plant_id,
                          PlantSiteGrowingAreaMapping.vendor_site_id == FreightCostRate.vendor_site_id))
                    .filter(FreightCostMapping.year==year,
                            or_(FreightCostMapping.rate==0,FreightCostRate.miles==0))
                    .distinct(FreightCostMapping.freight_cost_id).all())
        
        alert = "New Mapping is created in Freight Rates tables"

        if len(records)>0:
            return {"message": alert, "table": records}
        else:
            return {"message":"0", "table": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_freight_cost_records")
def create_freight_cost(payload: schemas.FreightCostRateSchema, db: Session = Depends(get_db)):
    """
    Create freight cost rate records for all plant-site-growing area combinations.
    
    For each existing plant-site-growing area mapping, creates a new FreightCostRate record
    with the provided currency and comment values.
    
    Args:
        payload (FreightCostRateSchema): Contains currency, comment, created_by, created_time,
                                        updated_time, and updated_by fields.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        list: List containing the created FreightCostRate record.
    
    Raises:
        HTTPException: Status 404 if no records exist in plant_site_growing_area_mapping table.
    """
    try:
        mapping_values = db.query(PlantSiteGrowingAreaMapping.plant_id
                                  ,PlantSiteGrowingAreaMapping.vendor_site_id
                                  ,PlantSiteGrowingAreaMapping.growing_area_id).all()

        if not mapping_values:
            raise HTTPException(status_code=404 ,
                                detail="No records found in plant_site_growing_area_mapping table")
        freight_records = []
        for mapping in mapping_values:
            freight_record = FreightCostRate(
                currency=payload.currency,
                comment=payload.comment,
                plant_id=mapping.plant_id,
                vendor_site_id=mapping.vendor_site_id,
                growing_area_id=mapping.growing_area_id,
                created_by=payload.created_by,
                created_time=payload.created_time,
                updated_time=payload.updated_time,
                updated_by=payload.updated_by
            )
            db.add(freight_record)
        db.commit()
        db.refresh(freight_record)

        freight_records.append(freight_record)
        return freight_records
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_freight_cost_mapping/{year}')
def view_freight_mapping_by_year(year:int, db: Session = Depends(get_db)):
    """
    Retrieve freight cost mapping records for a specific year.
    
    Fetches all freight cost mapping records filtered by the provided year, returning
    freight cost ID, period, company name, rate, fuel conversion factor, and round trip value.
    
    Args:
        year (int): The year to filter freight cost mappings by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"
            - "freight_cost_mapping" (list): List of freight cost mapping records with
                                            freight_cost_id, period, company_name, 
                                            period_with_P, rate, fuel_cf, round_trip
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(FreightCostMapping.freight_cost_id,
                           FreightCostMapping.period,
                           FreightCostMapping.company_name,
                           func.concat("P", FreightCostMapping.period).label("period_with_P"),
                           FreightCostMapping.rate,FreightCostMapping.fuel_cf,FreightCostMapping.round_trip).filter(FreightCostMapping.year == year).all()
        return {"status": "success", "freight_cost_mapping": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_freight_cost_mapping_records")
def create_freight_mapping(payload: schemas.FreightCostMappingSchema,db: Session = Depends(get_db)):
    """
    Create freight cost mapping records for each freight cost ID for a given year.

    This function iterates over every distinct ``freight_cost_id`` present in the
    ``FreightCostRate`` table and creates mapping rows in the ``FreightCostMapping``
    table for periods 1 through 13 using the supplied ``payload`` values (typically
    ``year`` and ``rate``). Each created mapping is added to the session and committed,
    then refreshed and accumulated into a list that is returned to the caller.

    Args:
        payload (schemas.FreightCostMappingSchema): Pydantic model containing at minimum:
            - ``year`` (int): Target calendar year for the mapping records.
            - ``rate`` (float): Rate value to use for each created period record.
        db (Session): SQLAlchemy database session (injected via ``Depends(get_db)``).

    Returns:
        list[FreightCostMapping]: A list of newly created ``FreightCostMapping`` ORM objects.

    Raises:
        HTTPException: Status 400 if any error occurs while creating or committing records.

    Notes:
        - The function creates mapping rows for all distinct ``freight_cost_id`` values
          currently present in ``FreightCostRate``. If you need to restrict the set of
          freight IDs, filter ``FreightCostRate`` prior to calling this function.
        - This implementation commits inside the loop after creating each mapping to
          persist progress; this mirrors legacy behavior but can be optimized by
          batching inserts and committing once for better performance.
    """
    try:
        freight_cost_mapping_data = []
        distinct_freight_ids = db.query(FreightCostRate.freight_cost_id).distinct().all()

        for freight_cost_id_tuple in distinct_freight_ids:
            freight_cost_id = freight_cost_id_tuple[0]
            for period in range(1, 14):
                mapped_data = FreightCostMapping(
                    freight_cost_id=freight_cost_id,
                    year=payload.year,
                    period=period,
                    rate=payload.rate
                )
                db.add(mapped_data)
                db.commit()
                db.refresh(mapped_data)

                freight_cost_mapping_data.append(mapped_data)

        return freight_cost_mapping_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_freight_mapping/{freight_cost_id}/{year}/{period}/{country}")
def update_freight_mapping(freight_cost_id: int, year: int, period: int, country: str, new_rate: float, round_trip: int, db: Session = Depends(get_db)):
    """
    Update freight mapping rates for current and next year filtered by freight_cost_id and country.

    This endpoint updates all FreightCostMapping records for the provided
    `freight_cost_id` and `company_name` (country). It sets `rate` and `round_trip`
    for every mapping where the period is greater than or equal to `period` in the
    given `year`, and for all periods in `year + 1`.

    Args:
        freight_cost_id (int): Freight cost identifier to update.
        year (int): Year to start updates from.
        period (int): Period number; updates this period and later in the same year.
        country (str): Company name/country to filter mappings.
        new_rate (float): New rate value to set.
        round_trip (int): New round_trip flag to set.
        db (Session): SQLAlchemy session used for queries and commits.

    Returns:
        dict: A dictionary with keys:
            - "updated_records_count" (int): Number of records updated
            - "details" (list): Updated FreightCostMapping ORM objects

    Raises:
        HTTPException: 404 if no records found matching the filters, or 400 on other errors.
    """
    try:
        # Query to fetch records for the given year with period >= the provided period
        records_to_update_current_year = db.query(FreightCostMapping).filter(
            FreightCostMapping.freight_cost_id == freight_cost_id,
            FreightCostMapping.year == year,
            FreightCostMapping.company_name == country,
            FreightCostMapping.period >= period
        ).all()

        # Query to fetch all records for the next year (year + 1)
        records_to_update_next_year = db.query(FreightCostMapping).filter(
            FreightCostMapping.freight_cost_id == freight_cost_id,
            FreightCostMapping.year == year + 1,
            FreightCostMapping.company_name == country
        ).all()

        # Combine records from the current year and next year
        records_to_update = records_to_update_current_year + records_to_update_next_year

        if not records_to_update:
            raise HTTPException(status_code=404, detail=details_exception)

        # Update the rate and round_trip for each record
        for record in records_to_update:
            record.rate = new_rate
            record.round_trip = round_trip

        # Commit the changes to the database
        db.commit()

        return {"updated_records_count": len(records_to_update), "details": records_to_update}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/freight_cost_period_view/{year}/{country}')
def freight_cost_period_view_year(year:int,country:str, db: Session = Depends(get_db)):
    """
    Retrieve freight cost period summary for a specific year and country.
    
    Args:
        year (int): The year to filter by.
        country (str): The country/company name to filter by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "freight_cost_period_view" (list): List of period-level freight cost aggregates
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(freight_cost_period_table).filter(
            freight_cost_period_table.columns.p_year == year,
            freight_cost_period_table.columns.country == country
            ).order_by(freight_cost_period_table.columns.period).all()
        return {"freight_cost_period_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/freight_cost_period_week_view/{year}/{country}')
def freight_cost_period_week_view_year(year: int,country:str,db: Session = Depends(get_db)): # pragma: no cover
    """
    Retrieve freight cost by period and week for a specific year and country.
    
    Args:
        year (int): The year to filter by.
        country (str): The country/company name to filter by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "freight_cost_period_week_view" (list): List of period-week-level freight cost data,
                                                      ordered by period and week
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(freight_cost_period_week_table).filter(
            freight_cost_period_week_table.columns.p_year == year,
            freight_cost_period_week_table.columns.country == country
            ).order_by(freight_cost_period_week_table.columns.period,
                      freight_cost_period_week_table.columns.week_no).all()
        return {"freight_cost_period_week_view": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    

@router.get("/get_rate_gowing_area/{year}/{country}")
def get_rate_growing_area_year(year: int,country:str, db: Session = Depends(get_db)):
    """
    Retrieve freight rate data by growing area for a specific year and country.
    
    Queries the rate_growing_area_table view to fetch freight cost rates aggregated by
    growing area, period, and country. Results are ordered by growing area ID and period
    for easy analysis of rate patterns across different growing areas.
    
    Args:
        year (int): The calendar year to filter rate records by.
        country (str): The country/company name to filter rate records by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "freight_cost_rate_growing_area" (list): List of rate records by growing area,
                                                       ordered by growing area ID and period.
                                                       Each record includes year, country, 
                                                       growing area details, period, and rate information.
    
    Raises:
        HTTPException: Status 400 if any database query error occurs.
    """
    try:
        records = db.query(rate_growing_area_table).filter(
            rate_growing_area_table.columns.p_year == year,
            rate_growing_area_table.columns.country == country).order_by(rate_growing_area_table.columns.growing_area_id,
                                                                     rate_growing_area_table.columns.period).all()
        return {"freight_cost_rate_growing_area": records}
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    
def create_freight_rates_in_db(payload: schemas.FreightCostRatesSchema, db: Session): 
    """
    Create a new freight cost rate record in the database.

    Inserts a new FreightCostRate record with the provided payload data. Handles both
    Pydantic model and dictionary payloads by converting to the appropriate format.

    Args:
        payload: Either a FreightCostRatesSchema Pydantic model or a dictionary containing
                freight cost rate fields (plant_id, growing_area_id, vendor_site_id, etc.).
        db (Session): SQLAlchemy database session for add, commit, and refresh operations.

    Returns:
        FreightCostRate: The newly created and committed FreightCostRate record.
    """
    try:
        if isinstance(payload, BaseModel):
            # Convert Pydantic model to dictionary
            payload_dict = payload.dict()
        else:
            # Assume payload is already a dictionary
            payload_dict = payload
        new_record = FreightCostRate(**payload_dict)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_freight_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: schemas.FreightCostRatesSchema, db: Session = Depends(get_db)):
    """
    API endpoint to create a new freight cost rate record.

    Args:
        payload (FreightCostRatesSchema): The freight cost rate data to create.
        db (Session): SQLAlchemy database session dependency for querying the database.

    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"
            - "freight_cost_id" (int): The ID of the newly created record
    """
    try:
        new_record = create_freight_rates_in_db(payload, db)
        return {"status": "success", "freight_cost_id": new_record.freight_cost_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_freight_cost_mapping_records_for_next_year/{year}")
def create_freight_cost_mapping_records_for_next_year(year: int, db: Session = Depends(get_db)):  
    """
    Create freight cost mapping records for the next year based on previous year data.
    
    Deletes all existing FreightCostMapping records for the specified year, then creates
    new records for all freight cost IDs, copying rates, company names, fuel conversion factors,
    and round trip values from the previous year for each period.
    
    Args:
        year (int): The year to create records for (copies from year-1).
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"
            - "Records added" (int): Number of records created
            - "for Year" (int): The year the records were created for
    
    Raises:
        HTTPException: Status 404 if no freight cost records exist.
    """
    try:
        distinct_freight_ids = db.query(FreightCostRate.freight_cost_id).distinct().all()
        update_count = 0
        if distinct_freight_ids.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        existing_record = db.query(FreightCostMapping)\
            .filter(FreightCostMapping.year == year).all()
        for ex in existing_record:
            db.delete(ex)
        db.commit()
        for freight_cost_id_tuple in distinct_freight_ids:
            freight_cost_id = freight_cost_id_tuple[0]
            for period in range(1, 14):
                old_rates = db.query(FreightCostMapping)\
                    .filter(FreightCostMapping.year == (year-1),
                            FreightCostMapping.freight_cost_id == freight_cost_id,
                            FreightCostMapping.period == period).first()
                if old_rates is not None:  # Ensure old_rates is not None
                    new_record = FreightCostMapping(freight_cost_id=freight_cost_id,
                                                    period=period, year=year,
                                                    rate=old_rates.rate,
                                                    company_name=old_rates.company_name,
                                                    fuel_cf=old_rates.fuel_cf,
                                                    round_trip=old_rates.round_trip)
                    db.add(new_record)
                    update_count += 1
            db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_freight_rates_with_default_value(freight_cost_id: int, year: int, db: Session = Depends(get_db)):
    """
    Create default freight cost mapping records for a freight cost ID.

    Creates 13 period records with default values (rate=0, round_trip=1, fuel_cf=0.54)
    for the specified freight cost ID and year. Determines country from the plant's
    company name (mapping US-CORE and CO-MAN to 'US', CANADA-CORE to 'Canada').

    Args:
        freight_cost_id (int): The freight cost ID to create mappings for.
        year (int): The year to create records for.
        db (Session): SQLAlchemy database session dependency for querying the database.

    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"

    Raises:
        HTTPException: Status 404 if no plant found for the freight cost ID.
    """
    try:
        country_records = (db.query(Plant.plant_id, Plant.company_name).join(FreightCostRate,
                                                                            Plant.plant_id == FreightCostRate.plant_id)
                                                                       .filter(FreightCostRate.freight_cost_id == freight_cost_id)
                                                                       .first())
        if not country_records:
            raise HTTPException(status_code=404, detail=f"No growing area found for freight_cost_id: {freight_cost_id}")
        country = country_records.company_name

        if country == 'US-CORE' or country == 'CO-MAN':
            country = 'US'
        elif country == 'CANADA-CORE':
            country = 'Canada'
        for period in range(1, 14):
            new_record = FreightCostMapping(
                freight_cost_id=freight_cost_id,
                period=period,
                year=year,
                rate=0,
                company_name=country,
                round_trip=1,
                fuel_cf=0.54
            )
            db.add(new_record)

        db.commit()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_freight_rates_with_default_value/{freight_cost_id}/{year}")
async def update_freight_cost_mapping_with_default_value(freight_cost_id:int, year:int, db: Session = Depends(get_db)):  # pragma: no cover
    """
    API endpoint to create default freight cost mapping records for a freight cost ID.
    
    Args:
        freight_cost_id (int): The freight cost ID to create mappings for.
        year (int): The year to create records for.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"
    
    Raises:
        HTTPException: Status 404 if no records found in the database.
    """
    
    result = update_freight_rates_with_default_value(freight_cost_id, year,db)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}
    


@router.get("/fetch_freight_records/{year}/{country}/{business_unit}", response_model=FreightRecordsResponse)
async def fetch_records(year: int, country: str, business_unit: str, db: Session = Depends(get_db)):
    """
    Fetch consolidated freight records for a specific year, country, and business unit.

    Performs an optimized SQL query with indexed column filtering to retrieve distinct
    freight cost records enriched with plant, site, and growing area details, filtered by
    company name (country), freight mapping company (country parameter), and plant company (business_unit).

    Args:
        year (int): The year to filter freight cost mappings by (indexed column).
        country (str): The company name/country to filter by in FreightCostMapping (indexed column).
        business_unit (str): The plant company name/business unit to filter by (e.g., 'US-CORE', 'CANADA-CORE').
        db (Session): SQLAlchemy database session for executing the query.

    Returns:
        FreightRecordsResponse: A response model containing:
            - status: "success" on successful execution
            - data: List of FreightRecordDetail objects with all freight record details
            - debug: Optional debug information

    Raises:
        HTTPException: Status 400 if any database or processing error occurs.
    """
    try:
        
        fcm_count = db.query(FreightCostMapping).where(
            and_(
                FreightCostMapping.year == year,
                FreightCostMapping.company_name == country
            )
        ).count()
        print(f"DEBUG: FreightCostMapping records found: {fcm_count}")
        
        stmt = (
            select(
                FreightCostMapping.freight_cost_id,
                FreightCostMapping.year,
                FreightCostMapping.period,
                FreightCostMapping.rate,
                FreightCostMapping.company_name,
                Plant.company_name.label("business_unit"),
                FreightCostMapping.fuel_cf,
                FreightCostMapping.round_trip,
                FreightCostRate.miles,
                PlantSiteGrowingAreaMapping.growing_area_id,
                PlantSiteGrowingAreaMapping.vendor_site_id,
                PlantSiteGrowingAreaMapping.plant_id,
                PlantSiteGrowingAreaMapping.plant_name,
                PlantSiteGrowingAreaMapping.growing_area,
                PlantSiteGrowingAreaMapping.Vendor_Site_Code.label("vendor_site_code"),
            )
            .select_from(FreightCostMapping)
            .where(
                and_(
                    FreightCostMapping.year == year,
                    FreightCostMapping.company_name == country,
                    Plant.company_name == business_unit
                )
            )
            .join(
                FreightCostRate,
                FreightCostRate.freight_cost_id == FreightCostMapping.freight_cost_id,
                isouter=False
            )
            .join(
                PlantSiteGrowingAreaMapping,
                and_(
                    FreightCostRate.growing_area_id == PlantSiteGrowingAreaMapping.growing_area_id,
                    FreightCostRate.plant_id == PlantSiteGrowingAreaMapping.plant_id,
                    FreightCostRate.vendor_site_id == PlantSiteGrowingAreaMapping.vendor_site_id,
                ),
                isouter=False
            )
            .join(
                Plant,
                Plant.plant_id == PlantSiteGrowingAreaMapping.plant_id,
                isouter=False
            )
            .distinct()
        )
        records = db.execute(stmt).all()
        print(f"DEBUG: Final joined records: {len(records)}")

        if not records:
            print("DEBUG: No records found. Returning empty data.")
            return FreightRecordsResponse(
                status="success", 
                data=[],
                debug={
                    "year": year,
                    "country": country,
                    "business_unit": business_unit,
                    "fcm_count": fcm_count,
                    "message": "No records matched the filters"
                }
            )

        consolidated_data = [
            FreightRecordDetail(
                freight_cost_id=record[0],
                year=record[1],
                period=record[2],
                period_with_P=f"P{record[2]}",
                rate=record[3],
                company_name=record[4],
                business_unit=record[5],
                fuel_cf=record[6],
                round_trip=record[7],
                miles=record[8],
                growing_area_id=record[9],
                vendor_site_id=record[10],
                plant_id=record[11],
                plant_name=record[12],
                growing_area=record[13],
                vendor_site_code=record[14],
            )
            for record in records
        ]

        print(f"DEBUG: Successfully consolidated {len(consolidated_data)} records")
        return FreightRecordsResponse(status="success", data=consolidated_data)

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e


def handle_upload_file(uploaded_year: int, user_email: str, file: UploadFile, db: Session):
    """
    Process and load freight cost data from an uploaded Excel file.

    Validates the uploaded Excel file format and content, transforms the data into
    the required structure, and inserts it into the FreightCostMapping table. All errors
    are logged to the FileUploadTemplate table with status and message details.

    File requirements:
    - Single sheet only
    - Extensions: .xls or .xlsx
    - Must contain 'freight_cost_id', 'company_name', 'year' columns
    - Period columns named with format like 'P1', 'P2', etc.

    Args:
        uploaded_year (int): The year being uploaded for (must match year in Excel).
        user_email (str): Email of the user uploading the file.
        file (UploadFile): The Excel file to process.
        db (Session): SQLAlchemy database session for data operations.

    Returns:
        dict: A dictionary containing:
            - "detail" (str): Success message with the uploaded year

    Raises:
        HTTPException: Status 400 for validation errors (file format, multiple sheets, year mismatch)
        HTTPException: Status 500 for processing errors

    Note:
        All uploads are tracked in FileUploadTemplate table with timestamp, status, and message.
    """
    # Capture file upload start time
    file_uploaded_time = datetime.now()

    try:
        # Extract file extension
        file_extension = os.path.splitext(file.filename)[-1].lower()
        
        # Check if file extension is allowed
        if file_extension not in [".xls", ".xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats are xls, xlsx.")

        # Read file content based on file format
        contents = file.file.read()
        data = BytesIO(contents)
        # Read all sheets from the Excel file
        df_dict = pd.read_excel(data, sheet_name=None)
        # Check number of sheets
        if len(df_dict.keys()) != 1:
            raise HTTPException(status_code=400, detail="Multiple sheets detected. Please upload a file with only one sheet.")
        # Extract the DataFrame from the dictionary
        df = next(iter(df_dict.values()))
        # Drop unnecessary columns
        df = df.drop(['growing_area_id', 'plant_id', 'vendor_site_id', 'plant_name', 'growing_area', 'Vendor_Site_Code'], axis=1, errors='ignore')
        # Melt DataFrame
        melted_df = df.melt(id_vars=['freight_cost_id', 'company_name', 'year'], var_name='period', value_name='rate')
        melted_df['period'] = melted_df['period'].str.extract(r'(\d+)').astype(int)
        # Replace null values in the rate column with 0
        melted_df['rate'] = melted_df['rate'].fillna(0)
        # Ensure 'year' column exists and is not empty
        if 'year' not in melted_df.columns or melted_df['year'].isnull().all():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year data is missing in the uploaded excel template.")
        # Check if the 'year' column has multiple distinct values
        if len(melted_df['year'].unique()) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year column in the uploaded file has multiple year values.Please check it once and then re-upload.")
        file_year = melted_df['year'].iloc[0]

        # Check if the uploaded_year matches the year value in the Excel file
        if uploaded_year != file_year:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Dropdown year value {uploaded_year} does not match the year value {file_year} in the uploaded Excel file.")
        
        uploaded_year = int(uploaded_year)
        
        
        # Delete records for the specific freight_cost_id values for the given year
        db.query(FreightCostMapping).filter(
            FreightCostMapping.year == uploaded_year
        ).delete()
        db.commit()
        
        if 'round_trip' not in melted_df.columns:
            # Fill round_trip from previous year if available, else default to 1
            def get_previous_round_trip(row):
                prev_year = row['year'] - 1
                prev = (
                    db.query(FreightCostMapping.round_trip)
                    .filter(
                        FreightCostMapping.freight_cost_id == row['freight_cost_id'],
                        FreightCostMapping.company_name == row['company_name'],
                        FreightCostMapping.period == row['period'],
                        FreightCostMapping.year == prev_year
                    )
                    .order_by(FreightCostMapping.year.desc())
                    .first()
                )
                return prev[0] if prev else 1

            melted_df['round_trip'] = melted_df.apply(get_previous_round_trip, axis=1)
        if 'fuel_cf' not in melted_df.columns:
            # Fill fuel_cf from previous year if available, else default to 0.54
            def get_previous_fuel_cf(row):
                prev_year = row['year'] - 1
                prev = (
                    db.query(FreightCostMapping.fuel_cf)
                    .filter(
                        FreightCostMapping.freight_cost_id == row['freight_cost_id'],
                        FreightCostMapping.company_name == row['company_name'],
                        FreightCostMapping.period == row['period'],
                        FreightCostMapping.year == prev_year
                    )
                    .order_by(FreightCostMapping.year.desc())
                    .first()
                )
                return prev[0] if prev else 0.54

            melted_df['fuel_cf'] = melted_df.apply(get_previous_fuel_cf, axis=1)
        
        # Insert new records
        records_to_insert = melted_df.to_dict(orient='records')
        db.execute(FreightCostMapping.__table__.insert(), records_to_insert)
        db.commit()
        
        # Capture file process time
        file_process_time = datetime.now()
        
        sheet_name = next(iter(df_dict.keys()))
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_name = f"{file_name_without_ext}_{sheet_name}"
        file_type = file_extension
        file_process_status = True
        message = " rates uploaded successfully"

        file_upload_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,  
            message=message  
        )
        db.add(file_upload_data)
        db.commit()
    except HTTPException as he:
        db.rollback()
        # File details
        file_name = file.filename
        file_type = file_extension
        file_process_time = None
        file_process_status = False
        message = str(he.detail)
        
        file_upload_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email, 
            message=message  
        )
        db.add(file_upload_data)
        db.commit()

        raise he
    except Exception as e: # pragma: no cover
        db.rollback()
        # File details
        file_name = file.filename
        file_type = file_extension
        file_process_time = None
        file_process_status = False
        message = str(e)

        file_upload_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email, 
            message=message  
        )
        db.add(file_upload_data)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"detail": f" rates successfully uploaded for the year: {uploaded_year}"}

# FastAPI route for file upload
@router.post("/upload_file", status_code=status.HTTP_201_CREATED)
async def upload_file(uploaded_year: int, user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    API endpoint to upload and process freight cost data from an Excel file.

    Args:
        uploaded_year (int): The year being uploaded for.
        user_email (str): Email of the user uploading the file.
        file (UploadFile): The Excel file to upload (.xls or .xlsx).
        db (Session): SQLAlchemy database session dependency for querying the database.

    Returns:
        dict: Result from handle_upload_file containing success message and uploaded year.
    """
    try:
        return handle_upload_file(uploaded_year, user_email, file, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get_file_upload_details')
async def get_file_details(db: Session = Depends(get_db)):
    """
    Retrieve all file upload history records.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "data" (list): List of all FileUploadTemplate records with upload history
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(FileUploadTemplate).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.post("/miles")
async def update_miles(payload: schemas.FreightMiles, db: Session = Depends(get_db)): 
    """
    Update the miles value for a specific plant-vendor-growing area combination.
    
    Args:
        payload (FreightMiles): Contains plant_id, vendor_site_id, growing_area_id, and miles.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary confirming update with plant_id, vendor_site_id, growing_area_id.
    
    Raises:
        HTTPException: Status 404 if no records found for the given combination.
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(FreightCostRate).filter(FreightCostRate.plant_id == payload.plant_id,
                                                   FreightCostRate.growing_area_id == payload.growing_area_id,
                                                   FreightCostRate.vendor_site_id == payload.vendor_site_id).all()
        if not records:
            raise HTTPException(status_code=404, detail=details_exception)
        for record in records:
            record.miles = payload.miles
        db.commit()
        
        return {"Miles updated for": payload.plant_id and payload.vendor_site_id and payload.growing_area_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/fuel_conv_factor")
def update_fuel_cf(payload: schemas.FreightMilesSchema, db: Session = Depends(get_db)):
    """
    Update fuel conversion factor for freight cost mappings for a given year/country/period.

    This endpoint updates the `fuel_cf` field on all `FreightCostMapping` records that
    match the provided `year`, `country` (company_name) and `period` in the incoming
    `payload`. The function commits the change for each record and returns the list of
    updated ORM objects.

    Args:
        payload (schemas.FreightMilesSchema): Pydantic model containing the update values.
            Expected attributes:
                - year (int): Year of the freight mappings to update
                - country (str): Company name / country to filter mappings (company_name)
                - period (int): Period number to filter mappings
                - fuel_cf (float): New fuel conversion factor to apply
        db (Session): SQLAlchemy session (injected via FastAPI `Depends(get_db)`).

    Returns:
        list: List of updated `FreightCostMapping` ORM instances.

    Raises:
        HTTPException(404): If no records match the provided filters.
        HTTPException(400): For any other error during processing (database or validation).

    Notes:
        - The function updates and commits within the loop for each record to ensure
          partial progress is persisted; this matches legacy behavior but could be
          optimized to a single bulk update for performance if desired.
        - The `payload` type is expected to validate incoming fields; callers should
          ensure `fuel_cf` is numeric and within acceptable domain before calling.
    """
    try:
        update_records = db.query(FreightCostMapping).filter(
            FreightCostMapping.year == payload.year,
            FreightCostMapping.company_name == payload.country,
            FreightCostMapping.period == payload.period
        ).all()
        if not update_records:
            raise HTTPException(status_code=404, detail=details_exception)
        for record in update_records:
            record.fuel_cf = payload.fuel_cf
            db.commit()
        return update_records
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/freight_fuel_cost/{year}/{country}')
def fuel_cost(year: int,country:str,db: Session = Depends(get_db)):
    """
    Retrieve fuel and freight cost totals by period for a specific year and country.
    
    Args:
        year (int): The year to filter by.
        country (str): The country/company name to filter by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "freight_fuel_cost" (list): List of freight and fuel cost aggregates ordered by period
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(View_freight_fuel_cost).filter(
            View_freight_fuel_cost.columns.year == year,
            View_freight_fuel_cost.columns.country == country
            ).order_by(View_freight_fuel_cost.columns.period
                      ).all()
        return {"freight_fuel_cost": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/freight_fuel_cost_ga/{year}/{country}')
def fuel_cost_ga(year: int,country:str,db: Session = Depends(get_db)):
    """
    Retrieve fuel and freight cost totals by growing area for a specific year and country.
    
    Args:
        year (int): The year to filter by.
        country (str): The country/company name to filter by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "freight_fuel_cost_ga" (list): List of freight and fuel cost aggregates by growing area,
                                             ordered by period
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        records = db.query(View_freight_fuel_cost_ga).filter(
            View_freight_fuel_cost_ga.columns.year == year,
            View_freight_fuel_cost_ga.columns.country == country
            ).order_by(View_freight_fuel_cost_ga.columns.period
                      ).all()
        return {"freight_fuel_cost_ga": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    
@router.get("/freight_cost/{year}/{country_name}/{company_name}")
def get_freight_cost(year: int, country_name: str, company_name: str, db: Session = Depends(get_db)):  
    """
    Fetch detailed freight cost records by calling database table-valued functions.
    
    Calls either getplant_view_freight_cost_US or getplant_view_freight_cost TVF depending
    on the company_name parameter. The TVFs return comprehensive freight cost information
    including rates, miles, and plant details.
    
    Args:
        year (int): The year to query.
        country_name (str): The country name to filter by.
        company_name (str): The company name ('US' or other company).
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "freight_cost" (list): List of dictionaries with freight cost data from TVF results
    
    Raises:
        HTTPException: Status 400 with error details if TVF execution fails.
    """
    try:
        if company_name == 'US':
            # Define raw SQL query to call the TVF
            query = text("""
                        SELECT * FROM [dbo].[getplant_view_freight_cost_US] (:year, :country_name)
                        """)
            # Execute the query with parameters
            results = db.execute(query, {
                                        "year": year,
                                        "country_name": country_name
                                        }).fetchall()
            # Convert the results to a list of dictionaries
            data = [dict(row._mapping) for row in results]
            return {"freight_cost": data}
        
        else:
            # Define raw SQL query to call the TVF
            query = text("""
                        SELECT * FROM [dbo].[getplant_view_freight_cost] (:year, :country_name, :company_name)
                    """)
            # Execute the query with parameters
            results = db.execute(query, {
                                        "year": year,
                                        "country_name": country_name,
                                        "company_name": company_name
                                        }).fetchall()
            # Convert the results to a list of dictionaries
            data = [dict(row._mapping) for row in results]
            return {"freight_cost": data}

    except Exception as e:
        # Raise HTTPException for any errors
        raise HTTPException(status_code=400, detail=f"Error querying TVF: {str(e)}") from e
    
@router.get("/freight_cost_mapping_placeholder")
def get_freight_cost_mapping_placeholder(db: Session = Depends(get_db)): 
    """
    Create placeholder freight cost mapping records for newly added freight cost rates.
    
    Identifies freight cost IDs that don't have any mapping records yet, and creates
    placeholder records for all 13 periods with default values (rate=0, round_trip=1, fuel_cf=0.54)
    for the current year.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "message" (str): Status message
            - "Number of new mapping created" (int): Count of new freight cost IDs with placeholders
    
    Raises:
        HTTPException: Status 400 with error details if an error occurs.
    """
    try:
        
        freight_cost_records = (db.query(FreightCostRate.freight_cost_id,
                                         case(
                                             (Plant.company_name == "US-CORE","US"),
                                             (Plant.company_name == "CO-MAN", "US"),
                                             (Plant.company_name == "CANADA-CORE", "Canada"),
                                         ).label('company_name'))
                                  .join(Plant,
                                        FreightCostRate.plant_id==Plant.plant_id)
                                  .distinct().all()) 
                           
        freight_cost_mapping_records = (db.query(FreightCostMapping.freight_cost_id).distinct().all())
        freight_cost_mappings_ids = [ids[0] for ids in freight_cost_mapping_records]

        ids_to_create = []
        for items in freight_cost_records:
            if items.freight_cost_id not in freight_cost_mappings_ids:
                ids_to_create.append((items.freight_cost_id,items.company_name))

        today_date = date.today()
        year = int(today_date.year)

        for ids,cmp_name in ids_to_create:

            for period in range(1,14):
                payload = {'freight_cost_id' :ids,
                           'year' :year,
                           'period' :period,
                           'rate' : 0,
                           'company_name' : cmp_name,
                           'round_trip' : 1,
                           'fuel_cf' : 0.54}
                
                new_records = FreightCostMapping(**payload)
                db.add(new_records)
        
        db.commit()

        return {"message": "Placeholders for the new mappings has been created",
                "Number of new mapping created" : len(ids_to_create)}

    except Exception as e:
        # Raise HTTPException for any errors
        raise HTTPException(status_code=400, detail=f"Error creating placeholder in Freight Cost Mapping: {str(e)}") from e
    





FUEL_SURCHARGE_TASK_ID = 6

ALLOWED_COMPANIES = {"CO-MAN", "CANADA-CORE", "US-CORE"}
DEFAULT_COMPANIES = ["US-CORE", "CANADA-CORE", "CO-MAN"]


def _norm_company(name: str) -> str: # pragma: no cover
    return (name or "").strip().upper()


def _get_completed_periods(year: int) -> list[int]: # pragma: no cover
    """
    Uses calculate_period_dates(year) -> returns completed periods (End_Date < today).
    """
    today = date.today()
    periods = calculate_period_dates(year)

    completed = []
    for p in periods:
        end_dt = datetime.strptime(p["End_Date"], "%Y-%m-%d").date()
        if end_dt < today:
            completed.append(int(p["Period"]))
    return completed


def _compute_fuel_surcharge(
    db: Session,
    year: int,
    period: int,
    company_name: str,
) -> Tuple[Optional[float], Optional[int]]: # pragma: no cover
    stmt = (
        select(func.sum(View_freight_fuel_cost.c.total_fuel))
        .where(
            View_freight_fuel_cost.c.company_name == company_name,
            View_freight_fuel_cost.c.year == year,
            View_freight_fuel_cost.c.period == period,
        )
    )

    total_fuel_sum = db.execute(stmt).scalar()

    if total_fuel_sum is None:
        return None, None

    fuel_surcharge = int(round(float(total_fuel_sum) / 1000.0))
    return float(total_fuel_sum), fuel_surcharge


def _update_fuel_surcharge_only(
    db: Session,
    year: int,
    period: int,
    company_name: str,
    new_value: int,
) -> dict: # pragma: no cover
    """
    UPDATE-ONLY logic:
      - If mapping row exists -> update `value`
      - If not exists -> do NOT insert; return updated=False with reason
    """
    year_col = freight_task_mappings.year
    period_col = freight_task_mappings.period
    company_col = freight_task_mappings.company_name
    task_id_col = freight_task_mappings.freight_task_id
    value_col = freight_task_mappings.value
    updated_col = getattr(freight_task_mappings, "updated_time", None)

    # fetch existing value
    existing_stmt = select(value_col).where(
        year_col == year,
        period_col == period,
        company_col == company_name,
        task_id_col == FUEL_SURCHARGE_TASK_ID,
    )
    old_value = db.execute(existing_stmt).scalar()

    if old_value is None:
        return {
            "updated": False,
            "old_value": None,
            "reason": "Row not found in freight_task_mappings (insert not allowed)",
        }

    values = {value_col.key: new_value}
    if updated_col is not None:
        values[updated_col.key] = datetime.now(timezone.utc)
    upd_stmt = (
        update(freight_task_mappings)
        .where(
            year_col == year,
            period_col == period,
            company_col == company_name,
            task_id_col == FUEL_SURCHARGE_TASK_ID,
        )
        .values(**values)
    )
    result = db.execute(upd_stmt)
    return {
        "updated": result.rowcount == 1,
        "old_value": old_value,
        "reason": None,
    }


@router.post("/freight/fuel_surcharge/populate_test")
def populate_fuel_surcharge(
    year: int = Query(..., description="Production: 2026+. Use test_mode for 2025 validation."),
    dry_run: bool = Query(True, description="True = only calculate; False = update freight_task_mappings.value"),
    company_names: list[str] = Query(
        default=DEFAULT_COMPANIES,
        description="Allowed: CO-MAN, CANADA-CORE, US-CORE",
    ),
    test_mode: bool = Query(False, description="True = allow testing past year/forced period"),
    test_period: Optional[int] = Query(None, description="When test_mode=true, force a single period e.g. 1"),
    db: Session = Depends(get_db),
): # pragma: no cover
    # normalize + validate company names
    companies = [_norm_company(c) for c in company_names]
    invalid = sorted({c for c in companies if c not in ALLOWED_COMPANIES})
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid company_name(s): {invalid}. Allowed: {sorted(ALLOWED_COMPANIES)}",
        )

    # production guard (since requirement says don't apply to 2025)
    if not test_mode and year <= 2025:
        raise HTTPException(
            status_code=400,
            detail="Not allowed for 2025 or earlier unless test_mode=true",
        )

    # decide which periods to process
    if test_mode and test_period is not None:
        periods = [int(test_period)]
        period_source = "forced_test_period"
    else:
        periods = _get_completed_periods(year)
        period_source = "completed_periods"

    if not periods:
        return {
            "status": "success",
            "year": year,
            "period_source": period_source,
            "processed_periods": [],
            "dry_run": dry_run,
            "results": [],
            "message": "No eligible periods to process (none completed yet).",
        }

    results = []
    for period in periods:
        for company in companies:
            total_fuel_sum, fuel_surcharge = _compute_fuel_surcharge(
                db=db, year=year, period=period, company_name=company
            )

            if total_fuel_sum is None:
                results.append({
                    "company_name": company,
                    "year": year,
                    "period": period,
                    "total_fuel_sum": None,
                    "computed_fuel_surcharge": None,
                    "skipped": True,
                    "reason": "No rows in View_fuel_cost_calculation_growing_area_plant",
                })
                continue

            if dry_run:
                results.append({
                    "company_name": company,
                    "year": year,
                    "period": period,
                    "total_fuel_sum": total_fuel_sum,
                    "computed_fuel_surcharge": fuel_surcharge,
                    "updated": False,
                    "skipped": False,
                })
            else:
                upd = _update_fuel_surcharge_only(
                    db=db, year=year, period=period, company_name=company, new_value=fuel_surcharge
                )
                results.append({
                    "company_name": company,
                    "year": year,
                    "period": period,
                    "total_fuel_sum": total_fuel_sum,
                    "computed_fuel_surcharge": fuel_surcharge,
                    "old_value": upd["old_value"],
                    "updated": upd["updated"],
                    "skipped": not upd["updated"],
                    "reason": upd["reason"],
                })

    if not dry_run:
        db.commit()

    return {
        "status": "success",
        "year": year,
        "period_source": period_source,
        "processed_periods": periods,
        "dry_run": dry_run,
        "results": results,
    }


@router.post("/freight/fuel_surcharge/populate")
def populate_fuel_surcharge_prod(
    year: int = Query(2026, description="Production run year (2026+ only)"),
    db: Session = Depends(get_db),
):  # pragma: no cover

    if year <= 2025:
        raise HTTPException(
            status_code=400,
            detail="Production fuel surcharge update is allowed only for 2026 onward",
        )

    # only completed periods
    periods = _get_completed_periods(year)
    if not periods:
        return {
            "status": "success",
            "mode": "production",
            "year": year,
            "processed_periods": [],
            "results": [],
            "message": "No completed periods yet. Nothing updated.",
        }

    results: List[Dict[str, Any]] = []
    companies = [_norm_company(c) for c in DEFAULT_COMPANIES]  # or fixed list

    for period in periods:
        for company in companies:
            total_fuel_sum, fuel_surcharge = _compute_fuel_surcharge(
                db=db, year=year, period=period, company_name=company
            )

            if total_fuel_sum is None:
                results.append({
                    "company_name": company,
                    "year": year,
                    "period": period,
                    "skipped": True,
                    "reason": "No fuel data in view",
                })
                continue

            upd = _update_fuel_surcharge_only(
                db=db, year=year, period=period, company_name=company, new_value=fuel_surcharge
            )

            results.append({
                "company_name": company,
                "year": year,
                "period": period,
                "computed_fuel_surcharge": fuel_surcharge,
                "old_value": upd["old_value"],
                "updated": upd["updated"],
                "skipped": not upd["updated"],
                "reason": upd["reason"],
            })

    db.commit()

    return {
        "status": "success",
        "mode": "production",
        "year": year,
        "processed_periods": periods,
        "results": results,
    }
