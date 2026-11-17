from models import general_administrative_task, general_administrative_mappings, country_division_name
from schemas import GeneralAdministrativeTaskSchema, GeneralAdministrativeMappingsPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_general_administrative_task_info(db: Session = Depends(get_db)):
    """Retrieve all general administrative task records.
    
    Fetches all records from the general_administrative_task table in the database.
    
    Args:
        db (Session): Database session dependency for querying the database.
        
    Returns:
        dict: A dictionary containing:
            - status (str): Success status of the operation.
            - data (list): List of all general administrative task records.
            
    Raises:
        HTTPException: 404 error if no general administrative task records are found.
    """
    
    query = db.query(general_administrative_task).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_info found")
    return {"status": "success", "data": query}
    
@router.get('/general_administrative_mappings_by_year/{year}/{country}')
def general_administrative_mappings_by_year(year: str, country: str, db: Session = Depends(get_db)):
    """Retrieve general administrative mappings for a specific year and country.
    
    Fetches general administrative mapping records filtered by the provided year and company name.
    
    Args:
        year (str): The year for which to retrieve mappings.
        country (str): The company name (country) to filter by.
        db (Session): Database session dependency for querying the database.
        
    Returns:
        dict: A dictionary containing:
            - status (str): Success status of the operation.
            - data (list): List of matching general administrative mapping records.
            
    Raises:
        HTTPException: 404 error if no matching records are found.
    """
    
    query = db.query(general_administrative_mappings).filter(general_administrative_mappings.year == year,
                                                              general_administrative_mappings.company_name == country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}
    

@router.post("/update_general_administrative_mappings/", status_code=status.HTTP_201_CREATED)
async def update_general_administrative_mappings(year: int, db: Session = Depends(get_db)):  
    """Update or create general administrative mappings for a specified year.
    
    Creates new general administrative mapping records for the given year, period, and countries.
    Skips creation if a record already exists for the specified general_administrative_id and year.
    
    Args:
        year (int): The year for which to create or update mappings.
        db (Session): Database session dependency for database operations.
        
    Returns:
        dict: A dictionary containing:
            - status (str): Success status of the operation.
            - Records already exists for (list): List of task names that already have records.
            - forYear (int): The year being processed.
            
    Raises:
        HTTPException: 404 error if no general administrative task records exist in the database.
    """
    try:
        # Fetch all records from the database
        all_records = db.query(general_administrative_task).all()
        countries = db.query(country_division_name).all()
        # Ensure there are records in the database
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")

        existing_task_names = []
        for record in all_records:
            existing_record = db.query(general_administrative_mappings).filter(general_administrative_mappings.year == year,
                                                                              general_administrative_mappings.general_administrative_id == record.general_administrative_id).first()
            if existing_record:
                existing_task_names.append(record.task_name)
                continue
            for period in range(1, 14):
                for con in countries:
                    new_record = general_administrative_mappings(general_administrative_id=record.general_administrative_id,
                                                                 period=period, year=year, value=0.001,
                                                                 company_name=con.task_desc)
                    db.add(new_record)
                    db.commit()

        return {"status": "success", "Records already exists for ": existing_task_names, "forYear": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_general_administrative_task', status_code=status.HTTP_201_CREATED)
def create_general_administrative_task(payload: GeneralAdministrativeTaskSchema, db: Session = Depends(get_db)):
    """Create a new general administrative task record.
    
    Creates and stores a new general administrative task in the database with the provided payload data.
    
    Args:
        payload (GeneralAdministrativeTaskSchema): The data for creating a new general administrative task.
        db (Session): Database session dependency for database operations.
        
    Returns:
        dict: A dictionary containing:
            - status (str): Success status of the operation.
            - general_administrative_id (int): The ID of the newly created record.
    """
    try:
        new_record = general_administrative_task(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "general_administrative_id": new_record.general_administrative_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_general_administrative_records/")
def update_general_administrative_records(payload: GeneralAdministrativeMappingsPayload, db: Session = Depends(get_db)):
    """Update existing general administrative mapping records.
    
    Updates values for multiple general administrative mapping records based on the provided data.
    Validates that all input IDs and periods are positive before processing updates.
    
    Args:
        payload (GeneralAdministrativeMappingsPayload): Contains a list of mapping records to update.
        db (Session): Database session dependency for database operations.
        
    Returns:
        dict: A dictionary containing:
            - status (str): Success or error status of the operation.
            - records_updated (int): Count of records successfully updated.
            - message (str): Error message if validation fails (only present on error).
            
    Raises:
        HTTPException: 400 error if an exception occurs during the update process.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.general_administrative_id <= 0 or item.period <= 0 or item.year <= 0:
                return {"status": "error", "message": "Please check details"}
            db.query(general_administrative_mappings).filter(
                general_administrative_mappings.general_administrative_id == item.general_administrative_id,
                general_administrative_mappings.period == item.period,
                general_administrative_mappings.year == item.year,
                general_administrative_mappings.company_name == item.company_name).update(
                {general_administrative_mappings.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_general_administrative_mappings_for_next_year/{year}")
async def create_g_and_a_mappings_for_next_year(year: int, db: Session = Depends(get_db)): 
    """Create general administrative mappings for all tasks and active countries for a given year.
    
    Generates new general administrative mapping records for the specified year. Creates entries for each
    general administrative task, period (1-13), and active country. Skips if records already exist for
    the combination of task, country, and period in the given year.
    
    Args:
        year (int): The year for which to create mappings.
        db (Session): Database session dependency for database operations.
        
    Returns:
        dict: A dictionary containing:
            - status (str): Success or error status of the operation.
            - Records added (int): Number of new records added (only on success).
            - for Year (int): The year for which records were created (only on success).
            - Records already exists for Year (int): Year with existing records (only on error).
            
    Raises:
        HTTPException: 404 error if no general administrative task records exist in the database.
    """
    try:
        all_records = db.query(general_administrative_task).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(general_administrative_mappings) \
            .filter(general_administrative_mappings.year == year).all()
        for ex in existing_record:
            key = str(ex.general_administrative_id) + "-" + ex.company_name + "-" + str(ex.period)
            dict_existing_record.append(key)
        for record in all_records:  # Iterate over all frieight task info
            for period in range(1, 14):  # Iterating 1 to 13 periods
                for con in countries:  # Iterate through the countries
                    iskey = str(record.general_administrative_id) + "-" + con.task_desc + "-" + str(period)
                    if iskey in dict_existing_record:
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = general_administrative_mappings(
                            general_administrative_id=record.general_administrative_id,
                            period=period, year=year, value=0,
                            company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1
    
        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
