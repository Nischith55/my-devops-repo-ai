"""Potato Rates API for finance"""
from database import get_db
from io import BytesIO
import pandas as pd
import os
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, File,Query
from models import (growing_area, potato_rate_mapping,FileUploadTemplate,
                    potato_rate_table_period, potato_rate_table_weekly,
                    potato_rates,region,potato_rate_plant_weekly,potato_rate_plant_period,PotatoRateAreaCodeMapping)
from schemas import potatoRateMappingPayload,PotatoRatesSchema
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from period_week_calc import calculate_week_num, calculate_period_dates, calculate_period_and_week
from typing import List,Optional,Dict,Tuple,Set


router = APIRouter()

@router.get('/')
def get_potato_rates(db: Session = Depends(get_db)): 
    """
    Retrieve all potato rate records from the database.
    
    Args:
        db: Database session dependency.
    
    Returns:
        dict: A dictionary with status and list of all potato_rates records.
    
    Raises:
        HTTPException: 404 if no potato_rates records are found.
    """
    query = db.query(potato_rates).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rates  found")
    return {"status": "success", "data": query}

@router.get('/potato_rate_mapping_by_year/{year}')
def get_potato_rate_mapping_data(year: str, db: Session = Depends(get_db)):
    """
    Retrieve all potato rate mapping records for a specific year.
    
    Args:
        year: The year to filter records by.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary with status and list of potato_rate_mapping records for the specified year.
    
    Raises:
        HTTPException: 404 if no potato_rate_mapping records are found for the year.
    """
    query = db.query(potato_rate_mapping).join(potato_rates,
                                        potato_rates.potato_rate_id == potato_rate_mapping
                                        .potato_rate_id).filter(potato_rates.year==year).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}

@router.get("/get_potato_rate_mapping/{year}")
def get_potato_rate_mappings(year: str, db: Session = Depends(get_db)):
    """
    Retrieve distinct period records from potato_rate_mapping for a given year.
    
    Args:
        year: The year to filter records by.
        db: Database session dependency.
    
    Returns:
        list: A list of dictionaries containing potato_rate_id, period, rate, and week information.
    """
    try:
        records = (db.query(potato_rate_mapping.potato_rate_id,
                            potato_rate_mapping.period, potato_rate_mapping.rate, potato_rates)
                   .distinct(potato_rate_mapping.period)
                   .join(potato_rates,potato_rates
                         .potato_rate_id == potato_rate_mapping.potato_rate_id)
                   .order_by(potato_rate_mapping.potato_rate_id, potato_rate_mapping.period)
                                    .filter(potato_rates.year==year)
                                    .all())
        results = [{"potato_rate_id":row.potato_rate_id, "period":row.period,
                                                    "rate":row.rate, "week":0} for row in records]
        return results
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_potato_rates_records/")
def update_potato_rates_records(payload: potatoRateMappingPayload, db: Session = Depends(get_db)):
    """
    Update existing potato rate mapping records with new rate values.
    
    Args:
        payload: A potatoRateMappingPayload containing a list of rate updates.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary with status and count of records updated.
    
    Raises:
        HTTPException: 400 if potato_rate_id or period values are invalid (<=0).
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.potato_rate_id<=0 or item.period<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(potato_rate_mapping
                     ).filter(potato_rate_mapping.potato_rate_id == item.potato_rate_id,
                              potato_rate_mapping.period==item.period,
                              potato_rate_mapping.week==item.week,
                              potato_rate_mapping.p_year==item.p_year).update(
                                  {potato_rate_mapping.rate: item.rate},
                                  synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

    
@router.get('/potato_rate_period_year_region/{year}/{region}')
def potato_rate_period_year_region(year:int,region_name:str, db: Session = Depends(get_db)):
    """
    Fetch potato rate period records for a specific year and region.
    
    Supports filtering by region name, 'All' for all regions, or 'US' for United States records.
    
    Args:
        year: The year to filter records by.
        region_name: The region name ('All', 'US', or specific region name).
        db: Database session dependency.
    
    Returns:
        dict: A dictionary containing potato_rate_period_year_region records.
    
    Raises:
        HTTPException: 400 if database query fails.
    """
    try:
        if region_name == 'All':
            records = db.query(potato_rate_table_period
                           ).filter(potato_rate_table_period.columns.p_year == year
                                    ).order_by(potato_rate_table_period.columns.growing_area_id,
                                               potato_rate_table_period.columns.period).all()
        elif region_name == 'US':
            records =db.query(potato_rate_table_period).join(
                growing_area,growing_area.growing_area_id==potato_rate_table_period.columns.growing_area_id).join(
                    region,growing_area.region == region.region_id).filter(
                        region.country == region_name,potato_rate_table_period.columns.p_year == year).order_by(
                            potato_rate_table_period.columns.growing_area_id,potato_rate_table_period.columns.period).all()
            
        else:
            records = db.query(potato_rate_table_period
                           ).filter(potato_rate_table_period.columns.p_year == year,
                                    potato_rate_table_period.columns.region_name == region_name
                                    ).order_by(potato_rate_table_period.columns.growing_area_id,
                                               potato_rate_table_period.columns.period).all()
        
        return {"potato_rate_period_year_region": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

    
@router.get('/potato_rate_period_week_year_region/{year}/{region}')
def potato_rate_period_week_year_region(year:int,region_name:str, db: Session = Depends(get_db)):
    """
    Fetch weekly potato rate records for a specific year and region.
    
    Supports filtering by region name, 'All' for all regions, or 'US' for United States records.
    
    Args:
        year: The year to filter records by.
        region_name: The region name ('All', 'US', or specific region name).
        db: Database session dependency.
    
    Returns:
        dict: A dictionary containing potato_rate_period_week_year_region records.
    
    Raises:
        HTTPException: 400 if database query fails.
    """
    try:
        if region_name == 'All':
            records = db.query(potato_rate_table_weekly
                           ).filter(potato_rate_table_weekly.columns.p_year == year
                                    ).order_by(potato_rate_table_weekly.columns.growing_area_id,
                                               potato_rate_table_weekly.columns.period).all()
        elif region_name == 'US':
            records =db.query(potato_rate_table_weekly).join(
                growing_area,growing_area.growing_area_id==potato_rate_table_weekly.columns.growing_area_id).join(
                    region,growing_area.region == region.region_id).filter(
                        region.country == region_name,potato_rate_table_weekly.columns.p_year == year).order_by(
                            potato_rate_table_weekly.columns.growing_area_id,potato_rate_table_weekly.columns.period).all()
            
        else:
            records = db.query(potato_rate_table_weekly
                           ).filter(potato_rate_table_weekly.columns.p_year == year,
                                    potato_rate_table_weekly.columns.region_name == region_name
                                    ).order_by(potato_rate_table_weekly.columns.growing_area_id,
                                               potato_rate_table_weekly.columns.period).all()
        
        return {"potato_rate_period_week_year_region": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create_potato_rate_mapping_for_next_year/{year}", status_code=status.HTTP_201_CREATED)
async def create_potato_rate_mapping_for_next_year(year: int , db: Session = Depends(get_db)):  # pragma: no cover
    """
    Create potato rate mapping records for a new year based on previous year data.
    
    Deletes existing records for the year, then creates new records by copying rates from
    the previous year. Handles period and week calculations for each country (US/Canada).
    
    Args:
        year: The year to create mapping records for.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary with status, count of records added, and the year.
    
    Raises:
        HTTPException: 400 if an error occurs during creation.
    """
    try:
        #Deleting existing records
        existing_record = (db.query(potato_rate_mapping)
                        .filter(potato_rate_mapping.p_year==year).all())
        for old in existing_record:
            db.delete(old)
        db.commit()

        # Retreiving the country data
        us = []
        canada = []
        country_data = db.query(potato_rates.potato_rate_id,potato_rates.currency).all()
        for items in country_data:
            if items.currency == "CAD":
                canada.append(items.potato_rate_id)
            elif items.currency == "USD":
                us.append(items.potato_rate_id)

        # Ids to create
        new_rec = (db.query(potato_rates.potato_rate_id).distinct().all())

        # Creating records
        period = 14
        update_count = 0

        for rec in new_rec:
            for p in range(1,period):
                if calculate_week_num(year,p):
                    week = 6
                else:
                    week = 5
                for w in range(1,week):
                    rate = (db.query(potato_rate_table_weekly.columns.actual_rate)
                              .filter(potato_rate_table_weekly.columns.period == p,
                                      potato_rate_table_weekly.columns.week == w,
                                      potato_rate_table_weekly.columns.potato_rate_id== rec.potato_rate_id,
                                      potato_rate_table_weekly.columns.p_year ==year-1)
                              .first())
                    if rec.potato_rate_id in us:
                        country = "US"
                    if rec.potato_rate_id in canada:
                        country = "Canada"
                    
                    if rate:
                        data = potato_rate_mapping(potato_rate_id = rec.potato_rate_id,
                                                   period = p,
                                                   week = w,
                                                   p_year = year,
                                                   rate = rate.actual_rate, 
                                                   country_code = country)
                    else:
                        data = potato_rate_mapping(potato_rate_id = rec.potato_rate_id,
                                                   period = p,
                                                   week = w,
                                                   p_year = year,
                                                   rate = 0, 
                                                   country_code = country)

                    db.add(data)
                    update_count+=1
        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/potato_rate_data/{year}/{country}')
def potato_rate_data(year:int,country:str, db: Session = Depends(get_db)):
    """
    Fetch detailed potato rate data for a specific year and country.
    
    Retrieves rate information with growing area details and period/week labels.
    
    Args:
        year: The year to filter records by.
        country: The country code to filter records by.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary containing potato rate records with formatted labels.
    
    Raises:
        HTTPException: 400 if database query fails.
    """
    try:
        records = (db.query(potato_rate_mapping.potato_rate_id,
                            potato_rate_mapping.period,
                            potato_rate_mapping.week,
                            potato_rate_mapping.rate,
                            potato_rate_mapping.p_year,
                            potato_rate_mapping.country_code,
                            growing_area.growing_area_name,
                            growing_area.growing_area_desc,
                            func.concat("P", potato_rate_mapping.period).label("period_with_P"),
                            func.concat("W", potato_rate_mapping.week).label("week_with_w"),
                            func.concat("P", potato_rate_mapping.period,"W",potato_rate_mapping.week).label("period_week"),
                            func.concat(growing_area.growing_area_name, " | ",growing_area.growing_area_desc).label("growing_area"))
                    .select_from(potato_rate_mapping)
                    .join(potato_rates,
                          potato_rates.potato_rate_id == potato_rate_mapping.potato_rate_id)
                    .join(growing_area,
                          growing_area.growing_area_id == potato_rates.growing_area_id)
                    .filter(potato_rate_mapping.country_code==country,potato_rate_mapping.p_year==year).all())
        
        return {"message": records}
    
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


def create_potato_rate_in_db(payload: PotatoRatesSchema, db: Session):
    """
    Create a new potato rate record in the database.
    
    Args:
        payload: A PotatoRatesSchema object containing potato rate data.
        db: Database session for the operation.
    
    Returns:
        potato_rates: The newly created potato_rates record with assigned ID.
    """
    try:
        if isinstance(payload, BaseModel):
            # Convert Pydantic model to dictionary
            payload_dict = payload.dict()
        else:
            # Assume payload is already a dictionary
            payload_dict = payload
        new_record = potato_rates(**payload_dict)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_potato_rates', status_code=status.HTTP_201_CREATED)
def create_potato_rates(payload: PotatoRatesSchema, db: Session = Depends(get_db)):
    """
    API endpoint to create a new potato rate record.
    
    Args:
        payload: A PotatoRatesSchema object containing potato rate data.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary with status and the newly created potato_rate_id.
    """
    new_record = create_potato_rate_in_db(payload, db)
    return {"status": "success", "potato_rate_id": new_record.potato_rate_id}


def update_potato_rates_default(db: Session, potato_rate_id: int, year: int):
    """
    Create default potato rate mapping records for a specific rate and year.
    
    Creates mapping records with zero rates for all periods (1-13) and weeks (1-4).
    
    Args:
        db: Database session for the operation.
        potato_rate_id: The potato rate ID to create mappings for.
        year: The year to create mappings for.
    
    Returns:
        bool: True if records were successfully created, None if no matching rate found.
    """
    try:
        all_records = db.query(potato_rates).filter(potato_rates.potato_rate_id == potato_rate_id).first()
        if not all_records:
            return None  # Indicate no records found

        for period in range(1, 14):
            for week in range(1, 5):
                new_record = potato_rate_mapping(potato_rate_id=all_records.potato_rate_id,
                                                 period=period, week=week, p_year=year, rate=0,country_code="US")
                db.add(new_record)
        db.commit()
        return True
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_potato_rates_with_default_value/{potato_rate_id}/{year}")
async def update_potato_rates_with_default_value(potato_rate_id:int, year:int, db: Session = Depends(get_db)):
    """
    API endpoint to create default potato rate mapping records.
    
    Creates mapping records with zero rates for all periods and weeks for a given rate and year.
    
    Args:
        potato_rate_id: The potato rate ID to create mappings for.
        year: The year to create mappings for.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary with status.
    
    Raises:
        HTTPException: 404 if the potato_rate_id does not exist.
    """
    result = update_potato_rates_default(db, potato_rate_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}

@router.get('/potato_rate_plant_period_view/{year}/{country}')
def potato_rate_plant_period_view(year:int,country:str, db: Session = Depends(get_db)):
    """
    Fetch potato rate plant period view records for a specific year and country.
    
    Args:
        year: The year to filter records by.
        country: The country code to filter records by.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary containing potato_rates_plant_period_view records.
    
    Raises:
        HTTPException: 400 if database query fails.
    """
    try:
        records = db.query(potato_rate_plant_period).filter(
            potato_rate_plant_period.columns.p_year == year,
            potato_rate_plant_period.columns.country == country
            ).order_by(potato_rate_plant_period.columns.period).all()
        return {"potato_rates_plant_period_view": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/potato_rate_plant_week_view/{year}/{country}')
def potato_rate_plant_week_view(year: int,country:str,db: Session = Depends(get_db)):
    """
    Fetch potato rate plant week view records for a specific year and country.
    
    Args:
        year: The year to filter records by.
        country: The country code to filter records by.
        db: Database session dependency.
    
    Returns:
        dict: A dictionary containing potato_rates_plant_week_view records ordered by period and week.
    
    Raises:
        HTTPException: 400 if database query fails.
    """
    try:
        records = db.query(potato_rate_plant_weekly).filter(
            potato_rate_plant_weekly.columns.p_year == year,
            potato_rate_plant_weekly.columns.country == country
            ).order_by(potato_rate_plant_weekly.columns.period,
                      potato_rate_plant_weekly.columns.week_no).all()
        return {"potato_rates_plant_week_view": records}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    
def potato_rates_upload_file(uploaded_year: int, user_email: str, file: UploadFile, db: Session):  # pragma: no cover
    """
    Process and upload potato rates from an Excel file.
    
    Validates file format (xls/xlsx), parses data, validates year consistency,
    and inserts/updates records in the database. Logs upload status to FileUploadTemplate.
    
    Args:
        uploaded_year: The year provided by the user for validation against file data.
        user_email: Email of the user uploading the file.
        file: The uploaded Excel file containing potato rate data.
        db: Database session for the operation.
    
    Returns:
        dict: A dictionary with a detail message about the upload result.
    
    Raises:
        HTTPException: 400 for invalid file format, multiple sheets, missing year data, or year mismatch.
        HTTPException: 500 for unexpected errors during processing.
    """
    # Capture file upload start time
    file_uploaded_time = datetime.now()

    try:
        file_extension_details= os.path.splitext(file.filename)[-1].lower()
        
        if file_extension_details not in [".xls", ".xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats are xls, xlsx.")

        contents = file.file.read()
        data = BytesIO(contents)
        
        df_dict = pd.read_excel(data, sheet_name=None)
        
        if len(df_dict.keys()) != 1:
            raise HTTPException(status_code=400, detail="Multiple sheets detected. Please upload a file with only one sheet.")
        
        df = next(iter(df_dict.values()))
        rename_columns = {
            'country': 'country_code',  # Rename 'country' in Excel to 'country_code'
            'year': 'p_year'           # Rename 'year' in Excel to 'p_year'
        }
        df = df.rename(columns=rename_columns)

        df = df.drop(['growing_area_id', 'growing_area_name'], axis=1, errors='ignore')
        
        melted_df = df.melt(id_vars=['potato_rate_id', 'country_code', 'p_year'], 
                            var_name='period_week', value_name='rate')

        melted_df['period'] = melted_df['period_week'].str.extract(r'P(\d+)').astype(int)
        melted_df['week'] = melted_df['period_week'].str.extract(r'W(\d+)').astype(int)

        melted_df = melted_df.drop(columns=['period_week'])

        melted_df['rate'] = melted_df['rate'].fillna(0)
   
        if 'p_year' not in melted_df.columns or melted_df['p_year'].isnull().all():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year data is missing in the uploaded excel template.")
        
        # Check if the 'p_year' column has multiple distinct values
        if len(melted_df['p_year'].unique()) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year column in the uploaded file has multiple year values. Please check it once and then re-upload."
            )
        
        file_year = melted_df['p_year'].iloc[0]
        
        # Check if the uploaded_year matches the year value in the Excel file
        if uploaded_year != file_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dropdown year value {uploaded_year} does not match the year value {file_year} in the uploaded Excel file."
            )
        
        uploaded_year = int(uploaded_year)
        
        # Delete records for the specific year
        db.query(potato_rate_mapping).filter(
            potato_rate_mapping.p_year == uploaded_year
        ).delete()
        db.commit()
        
        # Insert new records
        records_to_insert = melted_df.to_dict(orient='records')
        db.execute(potato_rate_mapping.__table__.insert(), records_to_insert)
        db.commit()
        
        # Capture file process time
        file_process_time = datetime.now()
        
        # Get sheet name for logging
        sheet_name = next(iter(df_dict.keys()))
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_name = f"{file_name_without_ext}_{sheet_name}"
        file_type = file_extension_details
        file_process_status = True
        message = "Potato Rates uploaded successfully"

        upload_file_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(upload_file_data)
        db.commit()
    except HTTPException as he:
        db.rollback()
        
        # File details
        file_name = file.filename
        file_type = file_extension_details
        file_process_time = None
        file_process_status = False
        message = str(he.detail)
        
        upload_file_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(upload_file_data)
        db.commit()

        raise he
    except Exception as e:
        db.rollback()
        
        # File details
        file_name = file.filename
        file_type = file_extension_details
        file_process_time = None
        file_process_status = False
        message = str(e)

        upload_file_data = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(upload_file_data)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"detail": f"Rates successfully uploaded for the year: {uploaded_year}"}

@router.post("/upload_file_potato_rates", status_code=status.HTTP_201_CREATED)
async def upload_file_potato_rates(uploaded_year: int, user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):# pragma: no cover
    """
    API endpoint to upload and process potato rates from an Excel file.
    
    Args:
        uploaded_year: The year provided by the user for validation.
        user_email: Email of the user uploading the file.
        file: The Excel file to be processed.
        db: Database session dependency.
    
    Returns:
        dict: Result from potato_rates_upload_file processing.
    
    Raises:
        HTTPException: Various status codes depending on validation and processing errors.
    """
    return potato_rates_upload_file(uploaded_year, user_email, file, db)

@router.get('/potato_rate_period_week_year_region_v1/{year}/{region_name}')
def potato_rate_period_week_year_region_v1(year: int,region_name: str, db: Session = Depends(get_db), period: Optional[int] = Query(None, ge=1, le=13),): # pragma: no cover
    """
    Fetch comprehensive potato rates for a given year and region with optional period filter.
    
    Supports flexible region filtering:
    - 'All': Returns rates for all regions
    - 'US': Filters by country = 'US'
    - Other values: Filters by exact region name
    
    Args:
        year: The year to filter records by.
        region_name: The region name ('All', 'US', or specific region name).
        db: Database session dependency.
        period: Optional period number (1-13) to filter records.
    
    Returns:
        dict: A dictionary containing potato_rate_period_week_year_region records with formatted labels.
    
    Raises:
        HTTPException: 400 if database query fails.
    """
    try:
        q = (
            db.query(
                potato_rate_mapping.potato_rate_id.label("potato_rate_id"),
                potato_rate_mapping.p_year.label("p_year"),
                potato_rate_mapping.period.label("period"),
                potato_rate_mapping.week.label("week"),
                func.coalesce(potato_rate_mapping.rate, 0.0).label("rate"),
                growing_area.growing_area_id.label("growing_area_id"),
                growing_area.growing_area_desc.label("ga_desc"),
                growing_area.growing_area_name.label("ga_name"),
                growing_area.country.label("country"),
                region.region_id.label("region_id"),
                region.region_name.label("region_name"),
            )
            .join(potato_rates, potato_rates.potato_rate_id == potato_rate_mapping.potato_rate_id)
            .join(growing_area, growing_area.growing_area_id == potato_rates.growing_area_id)
            .join(region, region.region_id == growing_area.region)
            .filter(potato_rate_mapping.p_year == year)
        )

        if region_name != "All":
            if region_name == "US":
                q = q.filter(region.country == "US")
            else:
                q = q.filter(region.region_name == region_name)

        if period is not None:
            q = q.filter(potato_rate_mapping.period == period)

        rows = q.order_by(
            growing_area.growing_area_id,
            potato_rate_mapping.period,
            potato_rate_mapping.week
        ).all()
        result: List[dict] = []
        for r in rows:
            result.append({
                "growing_area_id": r.growing_area_id,
                "growing_area_name": f"{r.ga_name} | {r.ga_desc}",
                "country": "USA" if (r.country or "").upper() == "US" else r.country,
                "region_id": r.region_id,
                "region_name": r.region_name,
                "p_year": r.p_year,
                "period_with_P": f"P{r.period}",
                "period": r.period,
                "week": r.week,
                "period_with_week": f"P{r.period}W{r.week}",
                "potato_rate_id": r.potato_rate_id,
                "rate": float(r.rate or 0.0),
            })

        return {"potato_rate_period_week_year_region": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
def parse_mm_dates(x) -> Optional[date]:  # pragma: no cover
    """
    Safe date parsing for contract files.
    Accepts:
      - Excel date/datetime cells
      - MM/DD/YYYY or M/D/YYYY
      - MM-DD-YYYY or M-D-YYYY
    Rejects ambiguous/non-matching formats to prevent wrong period/week mapping.
    """
    if pd.isna(x):
        return None

    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    if isinstance(x, datetime):
        return x.date()

    s = str(x).strip()

    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    return None


def map_date_range_to_period_weeks(
    fy_year: int,
    item_start_date: date,
    item_end_date: date,
) -> List[Tuple[int, int]]:  # pragma: no cover
    """
    Map a contract date range to all (period, week) combinations in a given fiscal year
    using calculate_period_dates(fy_year).

    Returns:
        list[(period, week)]
    """
    if item_end_date < item_start_date:
        return []

    period_defs = calculate_period_dates(fy_year)  # existing helper
    result: List[Tuple[int, int]] = []

    for p in period_defs:
        period_num = int(p["Period"])
        for w in p["Weeks"]:
            week_num = int(w["Week"])
            week_start = datetime.strptime(w["Start_Date"], "%Y-%m-%d").date()
            week_end = datetime.strptime(w["End_Date"], "%Y-%m-%d").date()

            # overlap?
            if week_end < item_start_date or week_start > item_end_date:
                continue

            result.append((period_num, week_num))

    return result


def validate_target_year_is_current_or_next_fy(target_year: int) -> None:  # pragma: no cover
    """
    Safety guard:
    - Allow updates only for current Pepsi fiscal year or next Pepsi fiscal year.
    - Block updates to past years.
    """
    today = date.today()
    current_fy = int(calculate_period_and_week(today.year, today).get("year", today.year))
    allowed_years = {current_fy, current_fy + 1}

    if target_year not in allowed_years:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid target_year={target_year}. "
                f"Only current or next fiscal year is allowed: {sorted(list(allowed_years))}. "
                f"(Current Pepsi fiscal year is {current_fy})."
            ),
        )


def get_potato_rate_id_by_area_code(
    db: Session,
    area_code: str,
) -> Optional[int]:  # pragma: no cover
    """
    Resolve area_code from contracts file to potato_rate_id
    using PotatoRateAreaCodeMapping table.
    """
    mapping = (
        db.query(PotatoRateAreaCodeMapping)
        .filter(
            PotatoRateAreaCodeMapping.area_code == area_code,
            PotatoRateAreaCodeMapping.is_active == True,
        )
        .first()
    )
    if not mapping:
        return None
    return int(mapping.potato_rate_id)


def process_contracts_file_for_rates(
    target_year: int,
    user_email: str,
    file: UploadFile,
    db: Session,
):  # pragma: no cover
    """
    Process contracts Excel and update potato_rate_mapping for the target fiscal year.

    Behavior:
    - Filters to Status == APPROVED
    - Filters Item Start Date to:
        * target_year, OR
        * Dec of target_year-1
    - Maps each row's (start,end) to Pepsi (period,week) overlaps for target_year
    - Aggregates at (area_code, period, week) across vendors/rows
    - Weighted avg per (area_code, period, week):
        sum(qty*price)/sum(qty)
      then store as (rate * 100) rounded to 2 decimals (ex 0.1825 => 18.25)
    - Resolves area_code -> potato_rate_id via PotatoRateAreaCodeMapping
    - Uses prior-year ACTUAL rate from view View_potato_rates_period_week:
        final_rate = max(prior_actual_rate, new_weighted_rate)
    - Updates only the exact target_year (period,week) rows produced from Excel
    - Response shows only processed potato_rate_ids + periods from Excel-derived keys
    """
    validate_target_year_is_current_or_next_fy(target_year)

    file_uploaded_time = datetime.now()
    file_extension_details = os.path.splitext(file.filename)[-1].lower()

    if file_extension_details not in [".xls", ".xlsx"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Supported formats are xls, xlsx.",
        )

    try:
        # ----- 1) Read Excel -----
        contents = file.file.read()
        data = BytesIO(contents)
        df_dict = pd.read_excel(data, sheet_name=None)

        if len(df_dict.keys()) != 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple sheets detected. Please upload a file with only one sheet.",
            )

        sheet_name = next(iter(df_dict.keys()))
        df = df_dict[sheet_name]

        # ----- 2) Normalize column names -----
        column_map = {
            "Area Code": "area_code",
            "Item Start Date": "item_start_date",
            "Item End Date": "item_end_date",
            "Overall Quantity": "total_value",
            "Pricing": "price",
            "Status": "status",
        }
        df = df.rename(columns=column_map)

        required_cols = ["area_code", "item_start_date", "item_end_date", "total_value", "price", "status"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns in contracts file: {missing}",
            )

        # ----- 3) Clean + SAFE date cast (NO inference) -----
        df = df.dropna(subset=["area_code", "item_start_date", "item_end_date"])

        df["item_start_date"] = df["item_start_date"].apply(parse_mm_dates)
        df["item_end_date"] = df["item_end_date"].apply(parse_mm_dates)

        bad_date_rows = df[df["item_start_date"].isna() | df["item_end_date"].isna()]
        if not bad_date_rows.empty:
            # You can add row indices here if you want:
            bad_idx = bad_date_rows.index.tolist()[:20]
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid/unsupported date format detected in Item Start Date / Item End Date. "
                    "Supported formats: MM/DD/YYYY or MM-DD-YYYY. "
                    f"Bad row indices (first 20): {bad_idx}"
                ),
            )
        print(df[["area_code", "item_start_date", "item_end_date"]].sort_values("item_end_date").tail(15))
        print("MAX END DATE:", df["item_end_date"].max())
        # ----- 4) Numbers -----
        # numbers like "13,40,00,000.00" => remove commas
        df["total_value"] = df["total_value"].astype(str).str.replace(",", "", regex=False)
        df["total_value"] = pd.to_numeric(df["total_value"], errors="coerce").fillna(0)

        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

        # ----- 5) Status filter -----
        df["status"] = df["status"].astype(str).str.strip().str.upper()
        df = df[df["status"] == "APPROVED"]

        if df.empty:
            return {
                "status": "success",
                "target_year": target_year,
                "db_rows_updated": 0,
                "skipped_area_codes": [],
                "touched": [],
                "updated": [],
                "detail": "No APPROVED rows found.",
            }

        # ----- 6) Year filter: target_year OR Dec of previous year -----
        fy_prev = target_year - 1
        df = df[
            (df["item_start_date"].apply(lambda d: d.year == target_year))
            | (df["item_start_date"].apply(lambda d: (d.year == fy_prev and d.month == 12)))
        ]

        if df.empty:
            return {
                "status": "success",
                "target_year": target_year,
                "db_rows_updated": 0,
                "skipped_area_codes": [],
                "touched": [],
                "updated": [],
                "detail": "No rows for (target_year) or (Dec of previous year).",
            }

        # ----- 7) Guard: limit mapping strictly inside fiscal year window -----
        period_defs = calculate_period_dates(target_year)
        fy_start = datetime.strptime(period_defs[0]["Start_Date"], "%Y-%m-%d").date()
        fy_end = datetime.strptime(period_defs[-1]["End_Date"], "%Y-%m-%d").date()

        # ----- 8) Aggregate per (area_code, period, week) -----
        agg: Dict[Tuple[str, int, int], Dict[str, float]] = {}

        for _, row in df.iterrows():
            area_code = str(row["area_code"]).strip()
            start_date: date = row["item_start_date"]
            end_date: date = row["item_end_date"]
            total_value = float(row["total_value"] or 0.0)
            price = float(row["price"] or 0.0)

            if total_value <= 0:
                continue

            # strict FY clamp
            if end_date < fy_start or start_date > fy_end:
                continue

            # clamp to FY range (optional but safe)
            if start_date < fy_start:
                start_date = fy_start
            if end_date > fy_end:
                end_date = fy_end

            weeks_pw = map_date_range_to_period_weeks(target_year, start_date, end_date)
            if not weeks_pw:
                continue

            for p, w in weeks_pw:
                key = (area_code, int(p), int(w))
                if key not in agg:
                    agg[key] = {"sum_value": 0.0, "sum_value_price": 0.0}
                agg[key]["sum_value"] += total_value
                agg[key]["sum_value_price"] += total_value * price

        if not agg:
            return {
                "status": "success",
                "target_year": target_year,
                "db_rows_updated": 0,
                "skipped_area_codes": [],
                "touched": [],
                "updated": [],
                "detail": "No valid quantity rows to process after calendar mapping.",
            }

        # ----- 9) Resolve area_code -> potato_rate_id -----
        area_codes: Set[str] = {ac for (ac, _, _) in agg.keys()}

        mappings = (
            db.query(
                PotatoRateAreaCodeMapping.area_code,
                PotatoRateAreaCodeMapping.potato_rate_id,
            )
            .filter(
                PotatoRateAreaCodeMapping.area_code.in_(list(area_codes)),
                PotatoRateAreaCodeMapping.is_active == True,
            )
            .all()
        )
        area_to_rate_id: Dict[str, int] = {m.area_code: int(m.potato_rate_id) for m in mappings}
        skipped_area_codes: Set[str] = {ac for ac in area_codes if ac not in area_to_rate_id}

        potato_rate_ids: Set[int] = set(area_to_rate_id.values())
        if not potato_rate_ids:
            return {
                "status": "success",
                "target_year": target_year,
                "db_rows_updated": 0,
                "skipped_area_codes": sorted(area_codes),
                "touched": [],
                "updated": [],
                "detail": "No area codes from file are mapped to potato_rate_id.",
            }

        # ----- 10) Load prior-year ACTUAL rates from VIEW -----
        prior_rows = (
            db.query(
                potato_rate_table_weekly.columns.potato_rate_id,
                potato_rate_table_weekly.columns.period,
                potato_rate_table_weekly.columns.week,
                potato_rate_table_weekly.columns.actual_rate,
            )
            .filter(
                potato_rate_table_weekly.columns.p_year == fy_prev,
                potato_rate_table_weekly.columns.potato_rate_id.in_(list(potato_rate_ids)),
            )
            .all()
        )

        prior_rate_week: Dict[Tuple[int, int, int], float] = {}
        for r in prior_rows:
            prior_rate_week[(int(r.potato_rate_id), int(r.period), int(r.week))] = float(r.actual_rate or 0.0)

        # ----- 11) Apply updates + build response only from Excel-derived keys -----
        db_rows_updated = 0
        touched_periods_by_rate: Dict[int, Set[int]] = {}
        updated_periods_by_rate: Dict[int, Set[int]] = {}

        for (area_code, period, week), sums in agg.items():
            if area_code not in area_to_rate_id:
                skipped_area_codes.add(area_code)
                continue

            potato_rate_id = int(area_to_rate_id[area_code])

            # touched period comes only from agg (Excel -> calendar)
            touched_periods_by_rate.setdefault(potato_rate_id, set()).add(int(period))

            sum_value = float(sums["sum_value"] or 0.0)
            if sum_value <= 0:
                continue

            weighted_fraction = float(sums["sum_value_price"] or 0.0) / sum_value
            scaled_rate = round(weighted_fraction * 100, 2)

            prev_actual = float(prior_rate_week.get((potato_rate_id, int(period), int(week)), 0.0))
            final_rate = max(prev_actual, scaled_rate)

            row_obj = (
                db.query(potato_rate_mapping)
                .filter(
                    potato_rate_mapping.potato_rate_id == potato_rate_id,
                    potato_rate_mapping.p_year == target_year,
                    potato_rate_mapping.period == int(period),
                    potato_rate_mapping.week == int(week),
                )
                .first()
            )

            if not row_obj:
                continue

            current_rate = float(row_obj.rate or 0.0)
            if abs(current_rate - float(final_rate)) > 1e-9:
                row_obj.rate = float(final_rate)
                db_rows_updated += 1
                updated_periods_by_rate.setdefault(potato_rate_id, set()).add(int(period))

        db.commit()

        touched = [
            {"potato_rate_id": rid, "periods": sorted(p_set)}
            for rid, p_set in touched_periods_by_rate.items()
        ]
        updated = [
            {"potato_rate_id": rid, "periods": sorted(p_set)}
            for rid, p_set in updated_periods_by_rate.items()
        ]

        # ----- 12) Optional: log file upload -----
        try:
            file_name_without_ext = os.path.splitext(file.filename)[0]
            file_name = f"{file_name_without_ext}_{sheet_name}"
            upload_file_data = FileUploadTemplate(
                file_name=file_name,
                file_uploaded_time=file_uploaded_time,
                file_type=file_extension_details,
                file_process_status=True,
                file_process_time=datetime.now(),
                file_uploaded_user=user_email,
                message=f"Contracts processed. db_rows_updated={db_rows_updated}.",
            )
            db.add(upload_file_data)
            db.commit()
        except Exception:
            db.rollback()
            # don't fail main API for logging errors

        return {
            "status": "success",
            "target_year": target_year,
            "db_rows_updated": db_rows_updated,
            "skipped_area_codes": sorted(skipped_area_codes),
            "touched": touched,
            "updated": updated,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/upload_contracts_file_for_potato_rates/{target_year}", status_code=status.HTTP_201_CREATED)
async def upload_contracts_file_for_potato_rates(
    target_year: int,
    user_email: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):  # pragma: no cover
    """
    Upload contracts file and update potato_rate_mapping for a given fiscal year.
    """
    return process_contracts_file_for_rates(target_year, user_email, file, db)

