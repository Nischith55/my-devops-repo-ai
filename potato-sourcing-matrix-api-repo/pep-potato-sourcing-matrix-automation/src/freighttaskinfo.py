from models import freight_task_info, freight_task_mappings, country_division_name
from schemas import FreightTaskInfoSchema, FreightTaskMappingsSchema, FreightTaskMappingsPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_freight_task_info(db: Session = Depends(get_db)):
    """
    Retrieve all freight task info records.

    Queries the database for all rows in the `freight_task_info` table and
    returns them in a standardized response. If there are no records a
    404 HTTPException is raised.

    Parameters:
    - db (Session): SQLAlchemy database session provided by dependency.

    Returns:
    - dict: A response dictionary with keys `status` and `data`.

    Raises:
    - HTTPException: 404 if no freight task info records are found.
    """
    
    query = db.query(freight_task_info).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_info found")
    return {"status": "success", "data": query}
    

@router.get('/get_freight_task_info_byId/{freight_task_id}')
def get_frt_task_info_byid(freight_task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single freight task info record by its ID.
    Looks up the `freight_task_info` row matching `freight_task_id`.
    Parameters:
    - freight_task_id (int): Identifier of the freight task to retrieve.
    - db (Session): SQLAlchemy database session provided by dependency.
    Returns:
    - dict: A response with keys `status` and `freight_task` containing the
        found record.
    Raises:
    - HTTPException: 404 if the requested freight task ID does not exist.
    """
    
    freight_task = db.query(freight_task_info).filter(freight_task_info.freight_task_id == freight_task_id).first()
    if not freight_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No freight_task_info_id: {freight_task_id} found")
    return {"status": "success", "freight_task": freight_task}
    

@router.get('/get_freight_task_mappings_by_year_and_country/{year}/{country}')
def get_freight_task_mappings_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)):
    """
    Retrieve freight task mapping records for a given year and country.

    Filters the `freight_task_mappings` table by `year` and `company_name`
    (interpreted here as country) and returns matching records. If no
    records are found a 404 HTTPException is raised.

    Parameters:
    - year (str): Year to filter mappings (string to match stored values).
    - country (str): Name of the company/country to filter by.
    - db (Session): SQLAlchemy database session provided by dependency.

    Returns:
    - dict: A response dictionary with keys `status` and `data`.

    Raises:
    - HTTPException: 404 if no freight task mappings match the filters.
    """
    
    query = db.query(freight_task_mappings).filter(freight_task_mappings.year==year, freight_task_mappings.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No freight_task_mappings  found")
    return {"status": "success", "data": query}
    

@router.post("/create_freight_task_mappings_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_freight_task_mappings_for_next_year(year: int, db: Session = Depends(get_db)):  
    """
    Create freight task mapping entries for the specified year.
    For every active country (from `country_division_name`) and for every
    freight task (from `freight_task_info`), this function inserts a new
    `freight_task_mappings` row for each period (1..13) for the requested
    `year`. If mappings already exist for the year the function returns an
    error response indicating the records exist.
    Parameters:
    - year (int): The year for which to create mappings.
    - db (Session): SQLAlchemy database session provided by dependency.
    Returns:
    - dict: On success returns `status: success` and the number of records
        added. If mappings already exist for the year returns an error dict.
    Raises:
    - HTTPException: 404 if there are no source `freight_task_info` records.
    """
    try:
        all_records = db.query(freight_task_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(freight_task_mappings)\
            .filter(freight_task_mappings.year == year).all()
        for ex in existing_record:
            key = str(ex.freight_task_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records: # Iterate over all frieight task info
            for period in range(1,14): # Iterating 1 to 13 periods
                for con in countries: # Iterate through the countries
                    iskey = str(record.freight_task_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record:
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = freight_task_mappings(freight_task_id=record.freight_task_id,
                                                           period=period, year=year,
                                                           value=0, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_freight_task_info', status_code=status.HTTP_201_CREATED)
def create_freight_task_info(payload: FreightTaskInfoSchema, db: Session = Depends(get_db)):  
    """
    Create a new freight task info record.
    Persists a new row in the `freight_task_info` table using the values
    supplied in the validated `payload`.
    Parameters:
    - payload (FreightTaskInfoSchema): Pydantic schema containing the fields
        required to create the freight task info record.
    - db (Session): SQLAlchemy database session provided by dependency.
    Returns:
    - dict: A response with `status: success` and the generated
        `freight_task_id` for the new record.
    """
    try:
        new_record = freight_task_info(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "freight_task_id": new_record.freight_task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_freight_task_mappings', status_code=status.HTTP_201_CREATED)
def create_freight_task_mappings(payload: FreightTaskMappingsSchema, db: Session = Depends(get_db)): 
    """
    Create a single freight task mapping row.
    Inserts a new `freight_task_mappings` record using the validated
    `payload` and returns the created row id.
    Parameters:
    - payload (FreightTaskMappingsSchema): Pydantic schema for the mapping
        record to create.
    - db (Session): SQLAlchemy database session provided by dependency.
    Returns:
    - dict: A response with `status: success` and the created `row_id`.
    """
    try:
        new_record = freight_task_mappings(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_freight_task_mapping_records/")
def update_freight_task_mapping_records(payload: FreightTaskMappingsPayload, db: Session = Depends(get_db)):
    """
    Batch update freight task mapping records.
    Accepts a payload containing a list of mapping updates and applies each
    update to the corresponding row identified by `(freight_task_id, period,
    year, company_name)`. Records with non-positive identifiers are rejected
    and the function will return an error dictionary in that case. On
    unexpected failures the function raises an HTTPException with status 400.
    Parameters:
    - payload (FreightTaskMappingsPayload): Pydantic payload containing a
        `.data` attribute which is an iterable of update objects with fields
        `freight_task_id`, `period`, `year`, `company_name`, and `value`.
    - db (Session): SQLAlchemy database session provided by dependency.
    Returns:
    - dict: A response with `status: success` and `records_updated` count on
        success, or an error dict if validation fails.
    Raises:
    - HTTPException: 400 for unexpected exceptions during update.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.freight_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(freight_task_mappings).filter(freight_task_mappings.freight_task_id == item.freight_task_id, freight_task_mappings.period==item.period, freight_task_mappings.year==item.year, freight_task_mappings.company_name==item.company_name).update(
                {freight_task_mappings.value: item.value, freight_task_mappings.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))