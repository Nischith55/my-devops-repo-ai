from models import productivity_plan_task_info,productivity_plan_task_mapping, country_division_name
from schemas import ProductivityPlanInfoSchema,ProductivityPlanTaskMappingPayload,ProductivityPlanTaskMappingSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_productivity_plan_task_info(db: Session = Depends(get_db)):
    """Retrieve all productivity plan task information records.

    Queries the `productivity_plan_task_info` table and returns all
    records. If no records are found, raises an HTTP 404 exception.

    Args:
        db (Session): SQLAlchemy database session injected by FastAPI.

    Returns:
        dict: A response dictionary with keys `status` and `data` where
            `data` is the list of `productivity_plan_task_info` records.

    Raises:
        HTTPException: 404 if no records are found.
    """
    query = db.query(productivity_plan_task_info).all()
    if not query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No productivity_plan_task_info found")
    return {"status": "success", "data": query}


@router.get('/get_productivity_plan_task_mapping_by_year_and_country/{year}/{country}')
def get_productivity_plan_task_mapping_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)):
    """Retrieve productivity plan task mappings filtered by year and country.

    Args:
        year (str): The year to filter mappings by.
        country (str): The company/country name to filter mappings by.
        db (Session): SQLAlchemy database session injected by FastAPI.

    Returns:
        dict: A response dictionary with keys `status` and `data` where
            `data` is the list of `productivity_plan_task_mapping` records
            that match the provided `year` and `country`.

    Raises:
        HTTPException: 404 if no matching records are found.
    """
    query = db.query(productivity_plan_task_mapping).filter(productivity_plan_task_mapping.year==year, productivity_plan_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No productivity_plan_task_mapping  found")
    return {"status": "success", "data": query}


@router.post("/create_productivity_plan_task_mapping_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_productivity_plan_task_mapping_for_next_year(year: int, db: Session = Depends(get_db)):
    """Create productivity plan task mapping rows for a specified year.

    This endpoint generates `productivity_plan_task_mapping` rows for the
    provided `year` by iterating all entries in
    `productivity_plan_task_info` and all active entries in
    `country_division_name`. For each combination of task, country and
    period (1..13) a new mapping row is created with `value=0` unless a
    mapping for the same task/company/period/year already exists.

    Note: If any mapping is detected to already exist for the target
    year, the function will return an error describing that records
    already exist for the year (current behavior stops on first
    duplicate and returns an error).

    Args:
        year (int): Target year for which mappings are to be created.
        db (Session): SQLAlchemy database session injected by FastAPI.

    Returns:
        dict: On success returns `{"status": "success", "Records added": <count>, "for Year": year}`.
        On duplicate detection returns an error response describing the
        duplicate. If no task info exists raises HTTPException(404).

    Raises:
        HTTPException: 404 when there are no `productivity_plan_task_info` records.
    """
    try:
        all_records = db.query(productivity_plan_task_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(productivity_plan_task_mapping)\
            .filter(productivity_plan_task_mapping.year == year).all()
        for ex in existing_record:
            key = str(ex.productivity_plan_task_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records: 
            for period in range(1,14): 
                for con in countries:
                    iskey = str(record.productivity_plan_task_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record: # pragma: no cover
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = productivity_plan_task_mapping(productivity_plan_task_id=record.productivity_plan_task_id,
                                                           period=period, year=year,
                                                           value=0, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_productivity_plan_task_info', status_code=status.HTTP_201_CREATED)
def create_productivity_plan_task_info(payload: ProductivityPlanInfoSchema, db: Session = Depends(get_db)):
    """Create a new `productivity_plan_task_info` record.

    Accepts a validated `ProductivityPlanInfoSchema` payload, inserts a
    new row into the `productivity_plan_task_info` table, commits the
    transaction and returns the generated primary key.

    Args:
        payload (ProductivityPlanInfoSchema): Validated request body.
        db (Session): SQLAlchemy database session injected by FastAPI.

    Returns:
        dict: A response containing `status` and `productivity_plan_task_id`.
    """
    try:
        new_record = productivity_plan_task_info(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "productivity_plan_task_id": new_record.productivity_plan_task_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_productivity_plan_task_mapping', status_code=status.HTTP_201_CREATED)
def create_productivity_plan_task_mapping(payload: ProductivityPlanTaskMappingSchema, db: Session = Depends(get_db)):
    """Insert a new `productivity_plan_task_mapping` row.

    Args:
        payload (ProductivityPlanTaskMappingSchema): Validated mapping payload.
        db (Session): SQLAlchemy database session injected by FastAPI.

    Returns:
        dict: A response containing `status` and the created `row_id`.
    """
    try:
        new_record = productivity_plan_task_mapping(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_productivity_plan_mapping_records/")
def update_productivity_plan_mapping_records(payload: ProductivityPlanTaskMappingPayload, db: Session = Depends(get_db)):
    """Batch update multiple productivity plan mapping records.

    The function expects `payload.data` to be an iterable of mapping
    items where each item contains `productivity_plan_task_id`,
    `period`, `year`, `company_name` and `value`. Each item is validated
    to ensure `productivity_plan_task_id`, `period` and `year` are
    positive integers. Matching rows are updated with the provided
    `value` and `period`.

    Args:
        payload (ProductivityPlanTaskMappingPayload): Payload wrapping
            the list of mapping update items.
        db (Session): SQLAlchemy database session injected by FastAPI.

    Returns:
        dict: A response containing `status` and `records_updated` count.

    Raises:
        HTTPException: 400 if an unexpected error occurs during update.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.productivity_plan_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(productivity_plan_task_mapping).filter(productivity_plan_task_mapping.productivity_plan_task_id == item.productivity_plan_task_id, productivity_plan_task_mapping.period==item.period, productivity_plan_task_mapping.year==item.year, productivity_plan_task_mapping.company_name==item.company_name).update(
                {productivity_plan_task_mapping.value: item.value, productivity_plan_task_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))