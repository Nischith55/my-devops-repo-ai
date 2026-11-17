"""Summary Price Variance API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException,status
from models import (country_division_name, price_variance_task,
                    price_variance_task_mapping,summary_price_variance)
from schemas import (PriceVarianceMappingPayload)
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/price_variance_task_mapping')
def get_price_variance_task_mapping(db: Session = Depends(get_db)): # pragma: no cover
    """
    Retrieve all records from the price_variance_task_mapping table.
    
    Queries the entire price_variance_task_mapping table and returns all records with
    their associated period, year, value, and company name details. Each record is
    formatted to include a 'period_with_P' field for display purposes.
    
    Args:
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary containing 'price_variance_task_mapping' key with a list of
              mapping records, each containing price_variance_task_id, period, period_with_P,
              year, value, and company_name.
    
    Raises:
        HTTPException: 400 status code if an error occurs during database query.
    """
    try:
        records = db.query(price_variance_task_mapping).all()
        result = [
            {
                "price_variance_task_id": row.price_variance_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"price_variance_task_mapping": result}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get('/price_variance_task')
def get_price_variance_task(db: Session = Depends(get_db)): # pragma: no cover
    """
    Retrieve all price variance task definitions from the database.
    
    Queries the price_variance_task table and returns all available tasks with their
    unique identifiers and task names. Used to retrieve the list of all defined
    price variance tasks in the system.
    
    Args:
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary containing 'price_variance_task' key with a list of task records,
              each containing price_variance_task_id and task_name.
    
    Raises:
        HTTPException: 400 status code if an error occurs during database query.
    """
    try:
        records = db.query(price_variance_task).all()
        result = [
            {
                "price_variance_task_id": row.price_variance_task_id,
                "task_name": row.task_name,
            }
            for row in records
        ]
        return {"price_variance_task": result}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/price_variance_task_mapping_by_year/{year}/{company_name}')
def price_variance_task_mapping_by_year(year: int,company_name :str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Retrieve price variance task mappings filtered by year and company name.
    
    Queries the price_variance_task_mapping table and returns all records matching the
    specified year and company name. Each record includes period, year, value, and
    company name information formatted for client consumption.
    
    Args:
        year (int): The fiscal year to filter records by.
        company_name (str): The company name to filter records by.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary containing 'price_variance_task_mapping_year' key with a list of
              filtered mapping records, each containing price_variance_task_id, period,
              period_with_P, year, value, and company_name.
    
    Raises:
        HTTPException: 400 status code if an error occurs during database query.
    """
    try:
        records = db.query(price_variance_task_mapping
                           ).filter(price_variance_task_mapping.year==year,
                                    price_variance_task_mapping.company_name == company_name).all()
        result = [
            {
                "price_variance_task_id": row.price_variance_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"price_variance_task_mapping_year": result}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_total_price_variance/{year}/{company_name}')
def get_total_price_variance(year:int, company_name: str,db: Session = Depends(get_db)):
    """
    Calculate the aggregated total price variance per period for a given year and company.
    
    Retrieves all price variance task mapping records for the specified year and company,
    then aggregates the values by period to compute total variance for each period.
    Results are sorted by period and formatted with period display notation.
    
    Args:
        year (int): The fiscal year to calculate variance for.
        company_name (str): The company name to calculate variance for.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary containing 'task' key with a list of aggregated records, each
              containing period, period_with_P, and Total (sum of variance values).
    
    Raises:
        HTTPException: 400 status code if an error occurs during calculation.
    """
    try:
        records = db.query(price_variance_task_mapping).filter(price_variance_task_mapping.year==year,
                                                               price_variance_task_mapping.company_name == company_name).all()
        total = {}
        for record in records:
            period = record.period
            if period in total:
                total[period] += record.value
            else:
                total[period] = record.value
        result = [
            {"period": period, "Total": total[period]}
            for period in sorted(total.keys())
        ]
        for item in result:
            item["period_with_P"] = f'P{item["period"]}'
        return {"task": result}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_price_variance_task_mapping")
async def create_price_variance_task_mapping(year: int, db: Session = Depends(get_db)):
    """
    Create new price variance task mappings for all tasks and periods in a given year.
    
    Creates price_variance_task_mapping records for each combination of price variance task,
    period (1-13), and country division (company). Skips creation for tasks that already
    have mappings in the specified year. Initializes all new records with a value of 0.0.
    
    Args:
        year (int): The fiscal year to create mappings for.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary with status, list of task names that already exist for the year,
              and the year value.
    
    Raises:
        HTTPException: 404 if no price variance task records exist in the database.
        HTTPException: 400 if an error occurs during record creation or commit.
    """
    try:
        # Fetch all records from the database
        all_records = db.query(price_variance_task).all()
        countries = db.query(country_division_name).all()
        # Ensure there are records in the database
        if all_records.count==0: # pragma: no cover
            raise HTTPException(status_code=404, detail="No records found in the database")

        existing_task_names = []
        for record in all_records:
            existing_record = db.query(price_variance_task_mapping).filter(price_variance_task_mapping.year==year
                                                                                ,price_variance_task_mapping.price_variance_task_id==record.price_variance_task_id ).first()
            if existing_record:
                existing_task_names.append(record.task_name)
                continue
            for period in range(1,14):
                for con in countries:
                    new_record =price_variance_task_mapping(price_variance_task_id = record.price_variance_task_id, 
                                                                  period=period, year=year, value=0.0, company_name=con.task_desc)
                    db.add(new_record)
                    db.commit()

        return {"status": "success", "Records already exists for ":existing_task_names, "forYear": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete('delete_all')
def delete_all_post(db: Session = Depends(get_db)):
    """
    Delete all records from the price_variance_task_mapping table.
    
    Removes all records from the price_variance_task_mapping table. This is a destructive
    operation that affects the entire table regardless of year, period, or company.
    
    Args:
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A message dictionary confirming successful deletion of records.
    
    Raises:
        HTTPException: 404 if no records are found in the table to delete.
        HTTPException: 400 if an error occurs during deletion or commit.
    """
    records_to_delete = db.query(price_variance_task_mapping).all()
    if not records_to_delete:
        raise HTTPException(status_code=404,
                            detail='No records found')
    for record in records_to_delete:
            db.delete(record)
    db.commit()
    return {"message": "Records for the  deleted successfully."}

@router.post("/update_price_variance_mappings_records/")
def update_price_variance_mappings_records(payload: PriceVarianceMappingPayload, db: Session = Depends(get_db)):
    """
    Update price variance mapping records with new values from the provided payload.
    
    Updates existing price_variance_task_mapping records by matching on price_variance_task_id,
    year, period, and company_name. Validates that all IDs and period/year values are positive
    before processing updates. Each matching record's value is updated to the new value provided.
    
    Args:
        payload (PriceVarianceMappingPayload): Request payload containing a list of mapping
                                               records to update, each with price_variance_task_id,
                                               period, year, company_name, and value.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary with status (success/error), and records_updated count, or an
              error message if validation fails.
    
    Raises:
        HTTPException: 400 if an error occurs during database update or commit.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.price_variance_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(price_variance_task_mapping).filter(price_variance_task_mapping.price_variance_task_id == item.price_variance_task_id,
                                                         price_variance_task_mapping.year==item.year, 
                                                         price_variance_task_mapping.period==item.period,
                                                         price_variance_task_mapping.company_name == item.company_name).update(
                {price_variance_task_mapping.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/summary_price_variance_view/{year}/{company_name}')
def summary_price_variance_year_country_code(year:int,company_name:str,db: Session = Depends(get_db)):
    """
    Retrieve summary price variance view records filtered by year and company name.
    
    Queries the summary_price_variance database view and returns all records matching the
    specified year and company name. Results are ordered by period in ascending order for
    chronological consistency.
    
    Args:
        year (int): The fiscal year to filter records by.
        company_name (str): The company name to filter records by.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: A dictionary containing 'summary_price_variance' key with a list of view records
              filtered and ordered by period.
    
    Raises:
        HTTPException: 400 if an error occurs during database query.
    """
    try:
        records = db.query(summary_price_variance).filter(
            summary_price_variance.columns.year == year,
            summary_price_variance.columns.company_name == company_name
            ).order_by(summary_price_variance.columns.period).all()
        return {"summary_price_variance": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e