from models import off_contract_info, off_contract_task_mapping, country_division_name
from schemas import OffContractInfoSchema, OffContractTaskMappingSchema, OffContractTaskMappingPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()

@router.get('/')
def get_off_contract_info(db: Session = Depends(get_db)):
    """
    Retrieve all off-contract information records from the database.

    Fetches all records from the off_contract_info table, ordered by order_position,
    and returns them in a structured response.

    Args:
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records found.
            - data (list): List of all off_contract_info records ordered by position.

    Raises:
        HTTPException: 404 error if no off_contract_info records are found.
    """
    query = db.query(off_contract_info).order_by(off_contract_info.order_position).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_info found")
    return {"status": "success", "data": query}

@router.get('/get_off_contract_task_by_id/{off_contract_task_id}')
def get_off_contract_task_by_id(off_contract_task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific off-contract information record by task ID.

    Fetches a single off_contract_info record matching the provided off_contract_task_id.

    Args:
        off_contract_task_id (int): The unique identifier of the off-contract task.
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" if record found.
            - off_contract_task (object): The off_contract_info record with matching ID.

    Raises:
        HTTPException: 404 error if no record with the specified ID is found.
    """
    query = db.query(off_contract_info).filter(off_contract_info.off_contract_task_id == off_contract_task_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No off_contract_info_id: {off_contract_task_id} found")
    return {"status": "success", "off_contract_task": query}

@router.get('/off_contract_task_mapping/')
def get_off_contract_task_mapping(db: Session = Depends(get_db)):
    """
    Retrieve all off-contract task mapping records from the database.

    Fetches all records from the off_contract_task_mapping table without any filters.

    Args:
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records found.
            - data (list): List of all off_contract_task_mapping records.

    Raises:
        HTTPException: 404 error if no off_contract_task_mapping records are found.
    """
    query = db.query(off_contract_task_mapping).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No off_contract_task_mapping  found")
    return {"status": "success", "data": query}

@router.get('/off_contract_task_mapping_by_year_and_country/{year}/{country}')
def off_contract_task_mapping_by_year_and_country(year: str, country: str, db: Session = Depends(get_db)):
    """
    Retrieve off-contract task mapping records filtered by year and company name.

    Fetches records from the off_contract_task_mapping table that match both
    the specified year and company name (country).

    Args:
        year (str): The fiscal year to filter by.
        country (str): The company name or country code to filter by.
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records found.
            - data (list): List of off_contract_task_mapping records matching the criteria.

    Raises:
        HTTPException: 404 error if no matching records are found.
    """
    query = db.query(off_contract_task_mapping).filter(off_contract_task_mapping.year==year, off_contract_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No potato_rate_mapping  found")
    return {"status": "success", "data": query}


@router.post("/create_off_contract_task_mapping_for_year/", status_code=status.HTTP_201_CREATED)
async def create_off_contract_task_mapping_for_year(year: int, db: Session = Depends(get_db)):
    """
    Create off-contract task mapping records for a specified year across all countries.

    Generates new off_contract_task_mapping records for all combinations of existing
    off-contract tasks, active countries, and all 13 periods in the specified year.
    Prevents duplicate entries by checking existing records.

    Args:
        year (int): The fiscal year for which to create mappings.
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" if records created, "error" if duplicates exist.
            - Records added (int): Number of new mapping records created.
            - for Year (int): The year for which records were created.

    Raises:
        HTTPException: 404 error if no records exist in the off_contract_info table.
        dict: Error response if records already exist for the specified year.
    """
    try:
        # Fetch all records from the database
        all_records = db.query(off_contract_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        if all_records.count==0: # pragma: no cover
            raise HTTPException(status_code=404, detail="No records found in the database")

        update_count = 0
        if all_records.count==0: # pragma: no cover
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(off_contract_task_mapping)\
                        .filter(off_contract_task_mapping.year==year).all()
        for ex in existing_record:# pragma: no cover
            key = str(ex.off_contract_task_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records:
            for period in range(1,14):
                for con in countries:
                    iskey = str(record.off_contract_task_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record:# pragma: no cover
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = off_contract_task_mapping(off_contract_task_id = record.off_contract_task_id, period=period, year=year, value=0, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))



@router.post('/create_off_contract_info', status_code=status.HTTP_201_CREATED)
def create_off_contract_info(payload: OffContractInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new off-contract information record in the database.

    Accepts validated off-contract information data and creates a new record in
    the off_contract_info table.

    Args:
        payload (OffContractInfoSchema): Validated schema object containing off-contract information.
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" after successful record creation.
            - off_contract_task_id (int): The ID of the newly created off-contract task.
    """
    try:
        new_record = off_contract_info(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "off_contract_task_id": new_record.off_contract_task_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_off_contract_task_mapping', status_code=status.HTTP_201_CREATED)
def create_off_contract_task_mapping(payload: OffContractTaskMappingSchema, db: Session = Depends(get_db)):
    """
    Create a new off-contract task mapping record in the database.

    Accepts validated off-contract task mapping data and creates a single new record
    in the off_contract_task_mapping table.

    Args:
        payload (OffContractTaskMappingSchema): Validated schema object containing mapping data.
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" after successful record creation.
            - row_id (int): The unique row ID of the newly created mapping record.
    """
    try:
        new_record = off_contract_task_mapping(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_off_contract_records/{off_contract_task_id}")
def update_off_contract(off_contract_task_id: int, payload: OffContractTaskMappingSchema,
                        db: Session = Depends(get_db)):
    """
    Update a single off-contract task mapping record by task ID.

    Updates the value, period, and year fields of an existing off_contract_task_mapping
    record identified by off_contract_task_id.

    Args:
        off_contract_task_id (int): The unique identifier of the off-contract task to update.
        payload (OffContractTaskMappingSchema): Validated schema object with updated field values.
        db (Session): Database session dependency for executing queries.

    Returns:
        object: The updated off_contract_task_mapping record with refreshed database values.

    Raises:
        HTTPException: 404 error if no record is found with the specified task ID.
    """
    try:
        existing_records= db.query(off_contract_task_mapping).filter(
            off_contract_task_mapping.off_contract_task_id == off_contract_task_id
        ).first()

        if existing_records is None: # pragma: no cover
            raise HTTPException(status_code=404, detail="No record found with this f{off_contract_task_id}")

        existing_records.value = payload.value
        existing_records.period = payload.period
        existing_records.year = payload.year

        db.commit()
        db.refresh(existing_records)

        return existing_records
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_off_contract_records/")
def update_off_contract_records(payload: OffContractTaskMappingPayload, db: Session = Depends(get_db)):
    """
    Batch update multiple off-contract task mapping records.

    Accepts a payload containing a list of mapping records and updates their value
    field in the database. Validates that all IDs, periods, and years are positive
    before processing updates.

    Args:
        payload (OffContractTaskMappingPayload): Validated schema containing a list of
            off-contract task mapping records to update.
        db (Session): Database session dependency for executing queries.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" if updates completed, "error" if validation fails.
            - records_updated (int): Number of records successfully updated.
            - message (str): Error message if validation fails (optional).

    Raises:
        HTTPException: 400 error if a database error occurs during the update operation.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.off_contract_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(off_contract_task_mapping)\
                .filter(off_contract_task_mapping.off_contract_task_id == item.off_contract_task_id,
                        off_contract_task_mapping.period == item.period,
                        off_contract_task_mapping.year == item.year,
                        off_contract_task_mapping.company_name==item.company_name)\
                .update({off_contract_task_mapping.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))