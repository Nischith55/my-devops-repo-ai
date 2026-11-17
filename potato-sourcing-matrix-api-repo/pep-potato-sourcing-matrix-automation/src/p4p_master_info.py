from models import p4p_master_info, p4p_task_mappings, View_p4p_result_table, country_division_name
from schemas import p4pMasterInfoSchema, p4pTaskMappingsSchema, p4pTaskMappingsPayload, TaskItemPayload
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()

@router.get('/')
def get_p4p_master_info(db: Session = Depends(get_db)):
    """
    Retrieve all records from the p4p_master_info table.
    Args:
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and data containing all p4p_master_info records.
    Raises:
        HTTPException: If no records are found.
    """
    query = db.query(p4p_master_info).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No p4p_master_info found")
    return {"status": "success", "data": query}

@router.get('/get_p4p_master_info/{p4p_id}')
def get_p4p_master_info_byid(p4p_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific p4p_master_info record by its p4p_id.
    Args:
        p4p_id (int): The ID of the p4p_master_info record.
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and details of the found record.
    Raises:
        HTTPException: If the record is not found.
    """
    query = db.query(p4p_master_info).filter(p4p_master_info.p4p_id == p4p_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No p4p_id: {p4p_id} found")
    return {"status": "success", "details": query}

@router.get('/p4p_task_mappings/')
def get_p4p_task_mappings(db: Session = Depends(get_db)):
    """
    Retrieve all records from the p4p_task_mappings table.
    Args:
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and data containing all p4p_task_mappings records.
    Raises:
        HTTPException: If no records are found.
    """
    query = db.query(p4p_task_mappings).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No p4p_task_mappings  found")
    return {"status": "success", "data": query}

@router.get('/p4p_task_mappings_by_year/{year}/{country}')
def p4p_task_mappings_by_year(year: str, country:str, db: Session = Depends(get_db)):
    """
    Retrieve p4p_task_mappings records for a specific year and country.
    Args:
        year (str): The year to filter records.
        country (str): The country to filter records.
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and data containing filtered records.
    Raises:
        HTTPException: If no records are found.
    """
    query =(db.query(View_p4p_result_table).filter(View_p4p_result_table.columns.p_year==year, View_p4p_result_table.columns.company_name==country).all())
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No p4p_task_mappings  found")
    return {"status": "success", "data": query}


@router.post("/create_p4p_task_mappings_records_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_p4p_task_mappings_records_for_next_year(year: int, db: Session = Depends(get_db)):
    """
    Create p4p_task_mappings records for the next year for all active countries and periods.
    Args:
        year (int): The year for which to create records.
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and number of records added, or error if records already exist.
    Raises:
        HTTPException: If no master records are found.
    """
    try:
        all_records = db.query(p4p_master_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count==0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(p4p_task_mappings)\
                        .filter(p4p_task_mappings.year==year).all()
        for ex in existing_record:
            key = str(ex.p4p_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records: # Iterate over all frieight task info
            for period in range(1,14): # Iterating 1 to 13 periods
                for con in countries: # Iterate through the countries
                    iskey = str(record.p4p_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record:
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = p4p_task_mappings(p4p_id = record.p4p_id, period=period, year=year, value=0.0001, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_p4p_task_mappings_info', status_code=status.HTTP_201_CREATED)
def create_p4p_task_mappings_info(payload: p4pMasterInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new p4p_task_mappings record using the provided payload.
    Args:
        payload (p4pMasterInfoSchema): Data for the new record.
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and the p4p_id of the created record.
    """
    try:
        new_record = p4p_task_mappings(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "p4p_id": new_record.p4p_id}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_p4p_task_mappings', status_code=status.HTTP_201_CREATED)
def create_p4p_task_mappings(payload: p4pTaskMappingsSchema, db: Session = Depends(get_db)):
    """
    Create a new p4p_task_mappings record using the provided payload.
    Args:
        payload (p4pTaskMappingsSchema): Data for the new record.
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and the row_id of the created record.
    """
    try:
        new_record = p4p_task_mappings(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_p4p_task_mappings_records/")
def update_p4p_task_mappings_records(payload: p4pTaskMappingsPayload, db: Session = Depends(get_db)):
    """
    Update existing records in the p4p_task_mappings table based on the provided payload.
    Args:
        payload (p4pTaskMappingsPayload): Contains data for updating records.
        db (Session): SQLAlchemy database session dependency.
    Returns:
        dict: Status and number of records updated, or error message.
    Raises:
        HTTPException: If an exception occurs during update.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.p4p_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(p4p_task_mappings).filter(p4p_task_mappings.p4p_id == item.p4p_id, p4p_task_mappings.year==item.year, p4p_task_mappings.period==item.period, p4p_task_mappings.company_name==item.company_name,p4p_task_mappings.company_name==item.company_name).update(
                {p4p_task_mappings.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))