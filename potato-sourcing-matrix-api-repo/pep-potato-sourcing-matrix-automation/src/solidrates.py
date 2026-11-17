"""Solid Rates API for finance"""
from sqlalchemy.orm import Session
from database import get_db
from io import BytesIO
import pandas as pd
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, File
from models import (growing_area, solid_rate_mapping, solids_rate_table_period,solids_rate_plant_period,
                    solids_rates,region,FileUploadTemplate)
from schemas import solidRateMappingPayload,SolidRatesSchema
from pydantic import BaseModel
from sqlalchemy import func


router = APIRouter()

@router.get('/')
def get_solids_rates(db: Session = Depends(get_db)):
    """Retrieve all solids rates records.

    This endpoint returns all rows from the `solids_rates` table.

    Parameters:
    - db: SQLAlchemy `Session` provided by FastAPI dependency injection.

    Returns:
    - dict: A JSON-serializable dictionary containing a `status` key and
      a `data` key with the list of `solids_rates` records.

    Raises:
    - HTTPException(status_code=404): If no records are found.
    """
    query = db.query(solids_rates).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solids_rates  found")
    return {"status": "success", "data": query}

@router.get('/getBySolidsRateId/{solids_rate_id}')
def get_by_solids_rate_id(solids_rate_id: int, db: Session = Depends(get_db)):
    """Retrieve a single solids rate record by its identifier.

    Parameters:
    - solids_rate_id: int — primary key of the `solids_rates` record to fetch.
    - db: SQLAlchemy `Session` provided by FastAPI dependency injection.

    Returns:
    - dict: JSON object with `status` and `solid_rate` containing the record.

    Raises:
    - HTTPException(status_code=404): If a record with the given id does not exist.
    """
    solid_rate = db.query(solids_rates).filter(solids_rates.solids_rate_id ==
                                               solids_rate_id).first()
    if not solid_rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No solids_rate_id: {solids_rate_id} found")
    return {"status": "success", "solid_rate": solid_rate}

@router.get('/solid_rate_mapping/{year}')
def get_solid_rate_mapping(year: str, db: Session = Depends(get_db)):
    """Return all solid rate mapping records for a given year.

    Parameters:
    - year: str — period year to filter `solid_rate_mapping` records.
    - db: SQLAlchemy `Session` provided by FastAPI dependency injection.

    Returns:
    - dict: `status` and `data` containing the list of matching mappings.

    Raises:
    - HTTPException(status_code=404): If no mapping records are found for the year.
    """
    query = db.query(solid_rate_mapping).join(solids_rates,
                                        solids_rates.solids_rate_id ==
                                        solid_rate_mapping.solids_rate_id
                                        ).filter(solid_rate_mapping.period_year==year).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solid_rate_mapping  found")
    return {"status": "success", "data": query}

@router.post("/update_solid_rates_records/")
def update_solid_rates_records(payload: solidRateMappingPayload,db: Session = Depends(get_db)):
    """Update existing `solid_rate_mapping` records from a payload.

    The `payload` is expected to include a `data` attribute that is an iterable
    of objects with `solids_rate_id`, `period`, `period_year`, and `rate`.

    Parameters:
    - payload: `solidRateMappingPayload` containing mapping updates.
    - db: SQLAlchemy `Session` provided by FastAPI dependency injection.

    Returns:
    - dict: `status` and `records_updated` indicating the number of records updated.

    Raises:
    - HTTPException(status_code=400): On database errors or bad payloads.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            db.query(solid_rate_mapping).filter(solid_rate_mapping.solids_rate_id
                                                == item.solids_rate_id,
                                                solid_rate_mapping.period==item.period,
                                                solid_rate_mapping.period_year==item.period_year).update(
                {solid_rate_mapping.rate: item.rate}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

    
@router.get('/solid_rate_period_year_region/{year}/{region}')
def solid_rate_period_year_region(year:int,region_name:str, db: Session = Depends(get_db)):
    """Fetch solids rate period records filtered by year and region.
    Behavior:
    - If `region_name == 'All'` returns all records for the `year`.
    - If `region_name == 'US'` joins through `growing_area` and `region` and
        filters by `region.country == 'US'`.
    - Otherwise filters by the `region_name` column on the view/table.
    Parameters:
    - year: int — year to filter `solids_rate_table_period` records.
    - region_name: str — region name or special values 'All'/'US'.
    - db: SQLAlchemy `Session` provided by FastAPI dependency injection.
    Returns:
    - dict: key `solids_period_year_region` with a list of matching records.
    Raises:
    - HTTPException(status_code=400): On unexpected errors during the query.
    """
    try:
        if region_name == 'All':
            records = db.query(solids_rate_table_period
                           ).filter(solids_rate_table_period.columns.year == year
                                    ).order_by(solids_rate_table_period.columns.growing_area_id,
                                               solids_rate_table_period.columns.period).all()
        elif region_name == 'US':
            records =db.query(solids_rate_table_period).join(
                growing_area,growing_area.growing_area_id==solids_rate_table_period.columns.growing_area_id).join(
                    region,growing_area.region == region.region_id).filter(
                        region.country == region_name,solids_rate_table_period.columns.year == year).order_by(
                            solids_rate_table_period.columns.growing_area_id,solids_rate_table_period.columns.period).all()
            
        else:
            records = db.query(solids_rate_table_period
                           ).filter(solids_rate_table_period.columns.year == year,
                                    solids_rate_table_period.columns.region_name == region_name
                                    ).order_by(solids_rate_table_period.columns.growing_area_id,
                                               solids_rate_table_period.columns.period).all()
        
        return {"solids_period_year_region": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create_solid_rates_mappings_for_next_year/{year}", status_code=status.HTTP_201_CREATED)
async def create_solid_rates_mappings_for_next_year(year: int, db: Session = Depends(get_db)):
    """Create `solid_rate_mapping` records for the specified next year.

    This routine deletes any existing `solid_rate_mapping` rows for the
    requested `year` and recreates mappings for each distinct
    `(growing_area_id, solids_rate_id)` pair found in `solids_rates`.

    Behavior and details:
    - Determines whether each `solids_rate_id` is USD or CAD and assigns
      a country label of "US" or "Canada" accordingly.
    - For each period (1..13) it attempts to copy the `actual_rate` from
      `solids_rate_table_period` for the previous year; if no previous rate
      exists it uses `0`.

    Parameters:
    - year: int -- target year for which mappings will be created.
    - db: sqlalchemy.orm.Session -- database session provided by FastAPI.

    Returns:
    - dict: status and a summary containing records added and the year.

    Raises:
    - HTTPException(status_code=400): on any database or processing error.
    """

    try:
        # Deleting old records
        existing_record = db.query(solid_rate_mapping)\
                        .filter(solid_rate_mapping.period_year==year).all()
        for old in existing_record:
            db.delete(old)
        db.commit()

        # Retreiving the country data
        us = []
        canada = []
        country_data = db.query(solids_rates.solids_rate_id,solids_rates.currency).all()
        for items in country_data:
            if items.currency == "CAD":
                canada.append(items.solids_rate_id)
            elif items.currency == "USD":
                us.append(items.solids_rate_id)

        # Ids to create
        new_rec = (db.query(solids_rates.growing_area_id,
                            solids_rates.solids_rate_id).distinct().all())

        # Creating records
        period = 14
        update_count = 0

        for rec in new_rec:
            for p in range(1,period):
                rate = (db.query(solids_rate_table_period.columns.actual_rate)
                          .filter(solids_rate_table_period.columns.period == p,
                                  solids_rate_table_period.columns.growing_area_id== rec.growing_area_id,
                                  solids_rate_table_period.columns.year ==year-1)
                          .first())
                
                if rec.solids_rate_id in us:
                    country = "US"
                if rec.solids_rate_id in canada: # pragma: no cover
                    country = "Canada"

                if rate:
                    data = solid_rate_mapping(solids_rate_id = rec.solids_rate_id,
                                              period = p,
                                              period_year =  year,
                                              rate = rate.actual_rate, 
                                              country_code = country)
                else:
                    data = solid_rate_mapping(solids_rate_id = rec.solids_rate_id,
                                              period = p,
                                              period_year =  year,
                                              rate = 0, 
                                              country_code = country)
                db.add(data)
                update_count+=1
        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/solid_rate_data/{year}/{country}')
def solid_rate_data(year:int,country:str, db: Session = Depends(get_db)):
    """Return solids rate mapping rows for a given year and country.

    The response contains flattened mapping information joined to
    `growing_area` and `solids_rates` so callers can display human
    readable names and a labelled period (e.g. "P1").

    Parameters:
    - year: int -- the period year to filter mappings by.
    - country: str -- country code used in `solid_rate_mapping.country_code`.
    - db: sqlalchemy.orm.Session -- database session provided by FastAPI.

    Returns:
    - dict: with key `message` and a list of matching rows as the value.

    Raises:
    - HTTPException(status_code=400): when a query error occurs.
    """
    try:
        records = (db.query(solid_rate_mapping.solids_rate_id,
                            solid_rate_mapping.period,
                            solid_rate_mapping.rate,
                            solid_rate_mapping.period_year,
                            solid_rate_mapping.country_code,
                            growing_area.growing_area_name,
                            growing_area.growing_area_desc,
                            func.concat("P", solid_rate_mapping.period).label("period_with_P"),
                            func.concat(growing_area.growing_area_name, " | ",growing_area.growing_area_desc).label("growing_area"))
                    .select_from(solid_rate_mapping)
                    .join(solids_rates,
                          solids_rates.solids_rate_id == solid_rate_mapping.solids_rate_id)
                    .join(growing_area,
                          growing_area.growing_area_id == solids_rates.growing_area_id)
                    .filter(solid_rate_mapping.country_code==country,solid_rate_mapping.period_year==year).all())
        
        return {"message": records}
    
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


def create_solid_rate_in_db(payload: SolidRatesSchema, db: Session):
    """Insert a new `solids_rates` record from the provided payload.

    Accepts either a Pydantic model instance (and converts it to a dict)
    or a plain dictionary and creates a new `solids_rates` ORM object.

    Parameters:
    - payload: `SolidRatesSchema` or dict -- source data for the new row.
    - db: sqlalchemy.orm.Session -- active database session.

    Returns:
    - solids_rates: the newly created ORM instance (detached/refreshed).
    """
    try:
        if isinstance(payload, BaseModel):
            # Convert Pydantic model to dictionary
            payload_dict = payload.dict()
        else: # pragma: no cover
            # Assume payload is already a dictionary
            payload_dict = payload
        new_record = solids_rates(**payload_dict)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_solids_rates', status_code=status.HTTP_201_CREATED)
def create_solids_rates(payload: SolidRatesSchema, db: Session = Depends(get_db)):
    """API route helper to create a `solids_rates` record.

    Delegates the creation to `create_solid_rate_in_db` then returns a
    minimal JSON response containing the new `solids_rate_id`.

    Parameters:
    - payload: `SolidRatesSchema` -- validated request body.
    - db: sqlalchemy.orm.Session -- injected DB session.

    Returns:
    - dict: `status` and `solids_rate_id` of the created record.
    """
    try:
        new_record = create_solid_rate_in_db(payload, db)
        return {"status": "success", "solids_rate_id": new_record.solids_rate_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def update_solids_rates_default(db: Session, solids_rate_id: int, year: int):
    """Create default `solid_rate_mapping` rows for a given `solids_rate_id`.

    This helper queries the `solids_rates` table to ensure the provided
    `solids_rate_id` exists; if it does, it inserts 13 period rows
    (periods 1..13) with `rate=0` and `country_code='US'` for the given
    `year`.

    Parameters:
    - db: sqlalchemy.orm.Session -- database session.
    - solids_rate_id: int -- identifier of the solids rate to seed.
    - year: int -- the target period_year for the new rows.

    Returns:
    - True when rows were created, or None if the `solids_rate_id` does not exist.
    """
    try:
        all_records = db.query(solids_rates).filter(solids_rates.solids_rate_id == solids_rate_id).first()
        if not all_records:
            return None  # Indicate no records found

        for period in range(1, 14):
            new_record = solid_rate_mapping(solids_rate_id=all_records.solids_rate_id,
                                            period=period, period_year=year, rate=0,country_code="US")
            db.add(new_record)
        db.commit()  
        return True
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_solids_rates_with_default_value/{solids_rate_id}/{year}")
async def update_solids_rates_with_default_value(solids_rate_id:int, year:int, db: Session = Depends(get_db)):
    """API endpoint to seed default mapping rows for a solids rate.

    Calls `update_solids_rates_default` to insert default mapping rows
    (periods 1..13 with rate 0) for the specified `solids_rate_id` and
    `year`.

    Parameters:
    - solids_rate_id: int -- the solids rate to seed.
    - year: int -- target period_year for the seeded rows.
    - db: sqlalchemy.orm.Session -- injected DB session.

    Returns:
    - dict: success status if seeding succeeded.

    Raises:
    - HTTPException(status_code=404): if the `solids_rate_id` does not exist.
    """
    result = update_solids_rates_default(db, solids_rate_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="No records found in the database")
    return {"status": "success"}
    
@router.get('/solid_rate_period_year_plant/{year}/{country}')
def solid_rate_period_year_plant(year:int,country:str, db: Session = Depends(get_db)):
    """Return solids rate records from the plant-period view for a year.

    Queries the `solids_rate_plant_period` view/table to return all rows
    matching the provided `year` and `country`, ordered by `plant_id` and
    `period`.

    Parameters:
    - year: int -- year (`p_year` column) to filter by.
    - country: str -- country code to filter by.
    - db: sqlalchemy.orm.Session -- FastAPI-injected session.

    Returns:
    - dict: key `solids_plant_period_view` with a list of matching records.

    Raises:
    - HTTPException(status_code=400): on query or processing errors.
    """
    try:
        records = db.query(solids_rate_plant_period).filter(
            solids_rate_plant_period.columns.p_year == year,
            solids_rate_plant_period.columns.country == country
            ).order_by(solids_rate_plant_period.columns.plant_id,solids_rate_plant_period.columns.period).all()
        return {"solids_plant_period_view": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
    
     
def solids_upload_file(uploaded_year: int, user_email: str, file: UploadFile, db: Session):
    """Process an uploaded Excel file containing solids rate mappings.

    Expected Excel format:
    - Single sheet only; columns should include `solids_rate_id`, `country`,
        `year` (or equivalent), and period columns such as `P1`, `P2`, ...
    - Extra columns `growing_area_id` and `growing_area_name` are ignored.

    Processing steps:
    - Validate Excel extension (`.xls`/`.xlsx`) and single-sheet requirement.
    - Normalize the sheet to rows with `solids_rate_id`, `country`,
        `period_year`, `period`, and `rate`.
    - Validate that the year passed in `uploaded_year` matches the file's year.
    - Delete existing `solid_rate_mapping` rows for the `period_year` and insert
        the new rows in bulk.
    - Log the upload attempt to `FileUploadTemplate` with success/failure info.

    Parameters:
    - uploaded_year: int -- year the client requested to upload for (dropdown).
    - user_email: str -- email of the uploading user for audit logging.
    - file: UploadFile -- file object provided by FastAPI.
    - db: sqlalchemy.orm.Session -- active DB session.

    Returns:
    - dict: detail message on success.

    Raises:
    - HTTPException: for validation, parsing, or processing errors.
    """
    # Capture file upload start time
    file_uploaded_time = datetime.now()

    try:
        file_ext = os.path.splitext(file.filename)[-1].lower()
        if file_ext not in [".xls", ".xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats are xls, xlsx.")
        
        content = file.file.read()
        data = BytesIO(content)
        df_dict = pd.read_excel(data, sheet_name=None)
        if len(df_dict.keys()) != 1: # pragma: no cover
            raise HTTPException(status_code=400, detail="Multiple sheets detected. Please upload a file with only one sheet.")
        df = next(iter(df_dict.values()))
        df = df.drop(['growing_area_id', 'growing_area_name'], axis=1, errors='ignore')
        melted_df = df.melt(id_vars=['solids_rate_id', 'country', 'year'], var_name='period', value_name='rate')
        melted_df['period'] = melted_df['period'].str.extract(r'(\d+)').astype(int)
        
        melted_df['rate'] = melted_df['rate'].fillna(0)
        melted_df.rename(columns={'year': 'period_year', 'country': 'country_code'}, inplace=True)
        
        # Ensure 'period_year' column exists and is not empty
        if 'period_year' not in melted_df.columns or melted_df['period_year'].isnull().all(): # pragma: no cover
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year data is missing in the uploaded excel template.")
        
        # Check if the 'period_year' column has multiple distinct values
        if len(melted_df['period_year'].unique()) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year column in the uploaded file has multiple year values. Please check it once and then re-upload."
            )
        
        file_year = melted_df['period_year'].iloc[0]
        
        # Check if the uploaded_year matches the year value in the Excel file
        if uploaded_year != file_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dropdown year value {uploaded_year} does not match the year value {file_year} in the uploaded Excel file."
            )
        
        uploaded_year = int(uploaded_year)
        
        # Delete records for the specific year
        db.query(solid_rate_mapping).filter(
            solid_rate_mapping.period_year == uploaded_year
        ).delete()
        db.commit()
        
        # Insert new records
        records_to_insert = melted_df.to_dict(orient='records')
        db.execute(solid_rate_mapping.__table__.insert(), records_to_insert)
        db.commit()
        
        # Capture file process time
        file_process_time = datetime.now()
        
        # Get sheet name for logging
        sheet_name = next(iter(df_dict.keys()))
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_name = f"{file_name_without_ext}_{sheet_name}"
        file_type = file_ext
        file_process_status = True
        message = "Solids uploaded successfully"

        file_upload_details = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(file_upload_details)
        db.commit()
    except HTTPException as he:
        db.rollback()
        
        # File details
        file_name = file.filename
        file_type = file_ext
        file_process_time = None
        file_process_status = False
        message = str(he.detail)
        
        file_upload_details = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(file_upload_details)
        db.commit()

        raise he
    except Exception as e:
        db.rollback()
        
        # File details
        file_name = file.filename
        file_type = file_ext
        file_process_time = None
        file_process_status = False
        message = str(e)

        file_upload_details = FileUploadTemplate(
            file_name=file_name,
            file_uploaded_time=file_uploaded_time,
            file_type=file_type,
            file_process_status=file_process_status,
            file_process_time=file_process_time,
            file_uploaded_user=user_email,
            message=message
        )
        db.add(file_upload_details)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"detail": f"Solids successfully uploaded for the year: {uploaded_year}"}


# FastAPI route for file upload
@router.post("/upload_file_solids", status_code=status.HTTP_201_CREATED)
async def upload_file_solids(uploaded_year: int, user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """FastAPI route wrapper that delegates to `solids_upload_file`.

    Parameters:
    - uploaded_year: int -- target year coming from the request query/form.
    - user_email: str -- uploader's email.
    - file: UploadFile -- uploaded Excel file.
    - db: sqlalchemy.orm.Session -- injected DB session.

    Returns:
    - dict: forwarded return value from `solids_upload_file`.
    """
    return solids_upload_file(uploaded_year, user_email, file, db)