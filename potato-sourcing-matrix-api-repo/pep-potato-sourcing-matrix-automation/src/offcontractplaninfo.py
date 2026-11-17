from models import off_contract_plan_info,off_contract_plan_task_mapping, country_division_name
from schemas import OffContractPlanInfoSchema,OffContractPlanTaskMappingPayload,OffContractPlanTaskMappingSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_off_contract_plan_info(db: Session = Depends(get_db)):
    """
    Retrieve all off-contract plan information records from the database.
    
    This endpoint fetches all records from the off_contract_plan_info table.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records are found, otherwise raises an exception.
            - data (list): List of all off_contract_plan_info records.
    
    Raises:
        HTTPException: 404 Not Found if no records exist in the table.
    """
    query = db.query(off_contract_plan_info).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_plan_info found")
    return {"status": "success", "data": query}


@router.get('/get_off_contract_plan_task_mapping_by_year_and_country/{year}/{country}')
def get_off_contract_plan_task_mapping_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)):
    """
    Retrieve off-contract plan task mappings filtered by year and country.
    
    This endpoint fetches task mapping records for a specific year and company/country.
    
    Args:
        year (str): The fiscal year for which to retrieve task mappings.
        country (str): The company/country name to filter the records.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records are found, otherwise raises an exception.
            - data (list): List of matching off_contract_plan_task_mapping records.
    
    Raises:
        HTTPException: 404 Not Found if no matching records are found for the given year and country.
    """
    query = db.query(off_contract_plan_task_mapping).filter(off_contract_plan_task_mapping.year==year, off_contract_plan_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_plan_task_mapping  found")
    return {"status": "success", "data": query}

@router.post("/create_off_contract_plan_task_mapping_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_off_contract_plan_task_mapping_for_next_year(year: int, db: Session = Depends(get_db)):
    """
    Create off-contract plan task mapping records for a specified year.
    
    This function generates new task mapping records for all active countries/companies
    and all off-contract plan tasks across 13 periods. It prevents duplicate entries
    by checking if mappings already exist for the specified year.
    
    Args:
        year (int): The fiscal year for which to create task mappings.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records are created, "error" if records already exist.
            - Records added (int): Number of new records added to the database.
            - for Year (int): The year for which records were created.
    
    Raises:
        HTTPException: 404 if no records are found in the off_contract_plan_info table.
    
    Note:
        - Creates mappings for 13 periods (1-13).
        - Only includes countries/divisions with status "Active".
        - Initial value for all mappings is set to 0.
        - Returns error if mappings already exist for the specified year.
    """
    try:
        all_records = db.query(off_contract_plan_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(off_contract_plan_task_mapping)\
            .filter(off_contract_plan_task_mapping.year == year).all()
        for ex in existing_record:
            key = str(ex.off_contract_plan_task_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records: # Iterate over all frieight task info
            for period in range(1,14): # Iterating 1 to 13 periods
                for con in countries: # Iterate through the countries
                    iskey = str(record.off_contract_plan_task_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record:
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = off_contract_plan_task_mapping(off_contract_plan_task_id=record.off_contract_plan_task_id,
                                                           period=period, year=year,
                                                           value=0, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_off_contract_plan_info', status_code=status.HTTP_201_CREATED)
def create_off_contract_plan_info(payload: OffContractPlanInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new off-contract plan info record in the database.
    
    This endpoint inserts a new off-contract plan task record based on the provided payload.
    
    Args:
        payload (OffContractPlanInfoSchema): Validated schema containing the off-contract plan info data.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" upon successful creation.
            - off_contract_plan_task_id (int): The ID of the newly created off-contract plan task.
    
    Note:
        Returns HTTP 201 Created status on successful record creation.
    """
    try:
        new_record = off_contract_plan_info(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "off_contract_plan_task_id": new_record.off_contract_plan_task_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_off_contract_plan_task_mapping', status_code=status.HTTP_201_CREATED)
def create_off_contract_plan_task_mapping(payload: OffContractPlanTaskMappingSchema, db: Session = Depends(get_db)):
    """
    Create a new off-contract plan task mapping record in the database.
    
    This endpoint inserts a new task mapping record based on the provided payload.
    
    Args:
        payload (OffContractPlanTaskMappingSchema): Validated schema containing the task mapping data.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" upon successful creation.
            - row_id (int): The primary key/row ID of the newly created task mapping record.
    
    Note:
        Returns HTTP 201 Created status on successful record creation.
    """
    try:
        new_record = off_contract_plan_task_mapping(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_off_contract_plan_mapping_records/")
def update_off_contract_plan_mapping_records(payload: OffContractPlanTaskMappingPayload, db: Session = Depends(get_db)):
    """
    Update existing off-contract plan task mapping records in the database.
    
    This endpoint updates multiple task mapping records based on the provided payload data.
    Validation is performed to ensure required fields have positive values.
    
    Args:
        payload (OffContractPlanTaskMappingPayload): Validated schema containing a list of task mapping updates.
        db (Session): SQLAlchemy database session dependency for database operations.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" if updates are applied, "error" if validation fails.
            - records_updated (int): Number of records successfully updated.
            - message (str): Error message if validation fails (only present on error).
    
    Raises:
        HTTPException: 400 Bad Request if any exception occurs during the update operation.
    
    Note:
        - Validates that off_contract_plan_task_id, period, and year are all positive integers.
        - Updates are matched based on off_contract_plan_task_id, period, year, and company_name.
        - Updates both the value and period fields for each matching record.
    
    Validation Error:
        - Returns error status if any record has off_contract_plan_task_id, period, or year <= 0.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.off_contract_plan_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(off_contract_plan_task_mapping).filter(off_contract_plan_task_mapping.off_contract_plan_task_id == item.off_contract_plan_task_id, off_contract_plan_task_mapping.period==item.period, off_contract_plan_task_mapping.year==item.year, off_contract_plan_task_mapping.company_name==item.company_name).update(
                {off_contract_plan_task_mapping.value: item.value, off_contract_plan_task_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))