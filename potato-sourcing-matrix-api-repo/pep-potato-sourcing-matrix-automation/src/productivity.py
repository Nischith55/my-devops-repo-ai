from models import productivity_task_info,productivity_task_mapping, country_division_name
from schemas import ProductivityInfoSchema,ProductivityTaskMappingPayload,ProductivityTaskMappingSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_productivity_task_info(db: Session = Depends(get_db)):
    """
    Retrieve all productivity task information records from the database.
    
    Fetches all records from the productivity_task_info table. Raises an HTTP 404 error
    if no records are found.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - status (str): Success status indicator.
            - data (list): List of all productivity_task_info records.
    
    Raises:
        HTTPException: 404 Not Found if no productivity_task_info records exist.
    """
    query = db.query(productivity_task_info).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No productivity_task_info found")
    return {"status": "success", "data": query}


@router.get('/get_productivity_task_mapping_by_year_and_country/{year}/{country}')
def get_productivity_task_mapping_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)):
    """
    Retrieve productivity task mapping records filtered by year and country.
    
    Queries the productivity_task_mapping table for records matching the specified year
    and company/country name. Returns an HTTP 404 error if no matching records are found.
    
    Args:
        year (str): The year to filter records by.
        country (str): The company/country name to filter records by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - status (str): Success status indicator.
            - data (list): List of matching productivity_task_mapping records.
    
    Raises:
        HTTPException: 404 Not Found if no matching records exist.
    """
    query = db.query(productivity_task_mapping).filter(productivity_task_mapping.year==year, productivity_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No productivity_task_mapping  found")
    return {"status": "success", "data": query}


@router.post("/create_productivity_task_mapping_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_productivity_task_mapping_for_next_year(year: int, db: Session = Depends(get_db)):
    """
    Create productivity task mapping records for the specified year.
    
    Generates new productivity_task_mapping records for all active countries/companies
    across all productivity tasks and 13 periods. Prevents duplicate records by checking
    existing entries for the given year. Each new record is initialized with a value of 0.
    
    Args:
        year (int): The year for which to create productivity task mapping records.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): 'success' if records were created, 'error' if duplicates exist.
            - Records added (int): Number of records created (on success).
            - for Year (int): The year for which records were created.
            - message (str): Error message if records already exist.
    
    Raises:
        HTTPException: 404 Not Found if no records exist in the productivity_task_info table.
    """
    try:
        all_records = db.query(productivity_task_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(productivity_task_mapping)\
            .filter(productivity_task_mapping.year == year).all()
        for ex in existing_record:
            key = str(ex.productivity_task_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records: 
            for period in range(1,14): 
                for con in countries: 
                    iskey = str(record.productivity_task_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record:
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = productivity_task_mapping(productivity_task_id=record.productivity_task_id,
                                                           period=period, year=year,
                                                           value=0, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_productivity_task_info', status_code=status.HTTP_201_CREATED)
def create_productivity_task_info(payload: ProductivityInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new productivity task information record.
    
    Adds a new record to the productivity_task_info table with the provided payload data.
    Automatically commits the transaction and refreshes the record to get the generated ID.
    
    Args:
        payload (ProductivityInfoSchema): The productivity task information data to create.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): Success status indicator.
            - productivity_task_id (int): The ID of the newly created productivity task.
    """
    try:
        new_record = productivity_task_info(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "productivity_task_id": new_record.productivity_task_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_productivity_task_mapping', status_code=status.HTTP_201_CREATED)
def create_productivity_task_mapping(payload: ProductivityTaskMappingSchema, db: Session = Depends(get_db)):
    """
    Create a new productivity task mapping record.
    
    Adds a new record to the productivity_task_mapping table with the provided payload data.
    Automatically commits the transaction and refreshes the record to get the generated row ID.
    
    Args:
        payload (ProductivityTaskMappingSchema): The productivity task mapping data to create.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): Success status indicator.
            - row_id (int): The ID of the newly created mapping record.
    """
    try:
        new_record = productivity_task_mapping(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_productivity_mapping_records/")
def update_productivity_mapping_records(payload: ProductivityTaskMappingPayload, db: Session = Depends(get_db)):
    """
    Update existing productivity task mapping records in batch.
    
    Updates multiple records in the productivity_task_mapping table based on matching
    productivity_task_id, period, year, and company_name. Validates that all required
    fields have positive values before processing updates.
    
    Args:
        payload (ProductivityTaskMappingPayload): Contains a list of mapping records to update.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): 'success' if updates completed, 'error' if validation fails.
            - records_updated (int): Number of records successfully updated.
            - message (str): Error message if validation failed.
    
    Raises:
        HTTPException: 400 Bad Request if an exception occurs during the update operation.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.productivity_task_id<=0 or item.period<=0 or item.year<=0: # pragma: no cover
                return {"status": "error", "message":"Please check details"}
            db.query(productivity_task_mapping).filter(productivity_task_mapping.productivity_task_id == item.productivity_task_id, productivity_task_mapping.period==item.period, productivity_task_mapping.year==item.year, productivity_task_mapping.company_name==item.company_name).update(
                {productivity_task_mapping.value: item.value, productivity_task_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))