from models import btl_plan_task_info,btl_plan_task_mapping, country_division_name
from schemas import BTLPlanInfoSchema,BTLPlanTaskMappingPayload,BTLPlanTaskMappingSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()


@router.get('/')
def get_btl_plan_task_info(db: Session = Depends(get_db)):
    """
    Fetch all BTL plan task info records.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of BTL plan task info under key `data`.

    Raises:
        HTTPException:
            - 404: When no records exist.
    """
    
    query = db.query(btl_plan_task_info).all()
    if not query:# pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No btl_plan_task_info found")
    return {"status": "success", "data": query}
    

@router.get('/get_btl_plan_task_mapping_by_year_and_country/{year}/{country}')
def get_btl_plan_task_mapping_by_year_and_country(year: str, country:str,db: Session = Depends(get_db)):

    """
    Fetch BTL plan task mappings filtered by year and country.

    Args:
        year (str): Plan year filter.
        country (str): Country/company identifier.
        db (Session): Database session.

    Returns:
        dict: Matching mapping records under key `data`.

    Raises:
        HTTPException:
            - 404: If no records found.
    """
    
    query = db.query(btl_plan_task_mapping).filter(btl_plan_task_mapping.year==year, btl_plan_task_mapping.company_name==country).all()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No btl_plan_task_mapping  found")
    return {"status": "success", "data": query}
    

@router.post("/create_btl_plan_task_mapping_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_btl_plan_task_mapping_for_next_year(year: int, db: Session = Depends(get_db)): # pragma: no cover
    """
    Create BTL plan task mapping records for the next year.

    Args:
        year (int): Target year to insert records for.
        db (Session): Database session.

    Returns:
        dict: Status, inserted record count, and year.

    Raises:
        HTTPException:
            - 404: If master task info is empty.
            - 400: On creation failure.
    """
    try:
        all_records = db.query(btl_plan_task_info).all()
        countries = db.query(country_division_name).filter(country_division_name.status == "Active").all()
        update_count = 0
        if all_records.count == 0:
            raise HTTPException(status_code=404, detail="No records found in the database")
        dict_existing_record = []
        existing_record = db.query(btl_plan_task_mapping)\
            .filter(btl_plan_task_mapping.year == year).all()
        for ex in existing_record:
            key = str(ex.btl_plan_task_id)+"-"+ex.company_name+"-"+str(ex.period)
            dict_existing_record.append(key)
        for record in all_records: # Iterate over all frieight task info
            for period in range(1,14): # Iterating 1 to 13 periods
                for con in countries: # Iterate through the countries
                    iskey = str(record.btl_plan_task_id)+"-"+con.task_desc+"-"+str(period)
                    if iskey in dict_existing_record:
                        return {"status": "error", "Records already exists for Year": year}
                    else:
                        new_record = btl_plan_task_mapping(btl_plan_task_id=record.btl_plan_task_id,
                                                        period=period, year=year,
                                                        value=0, company_name=con.task_desc)
                        db.add(new_record)
                        update_count += 1

        db.commit()
        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post('/create_btl_plan_task_info', status_code=status.HTTP_201_CREATED)
def create_btl_plan_task_info(payload: BTLPlanInfoSchema, db: Session = Depends(get_db)):
    """
    Insert a new BTL plan task info record.

    Args:
        payload (BTLPlanInfoSchema): Incoming request body.
        db (Session): Database session.

    Returns:
        dict: Status and created BTL plan task ID.
    """
    try:
        new_record = btl_plan_task_info(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "btl_plan_task_id": new_record.btl_plan_task_id}
    except Exception as e:# pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post('/create_btl_plan_task_mapping', status_code=status.HTTP_201_CREATED)
def create_btl_plan_task_mapping(payload: BTLPlanTaskMappingSchema, db: Session = Depends(get_db)):
    """
    Insert a new BTL plan task mapping record.

    Args:
        payload (BTLPlanTaskMappingSchema): Mapping details.
        db (Session): Database session.

    Returns:
        dict: Status and inserted row ID.
    """
    try:
        new_record = btl_plan_task_mapping(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e:# pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/update_btl_plan_mapping_records/")
def update_btl_plan_mapping_records(payload: BTLPlanTaskMappingPayload, db: Session = Depends(get_db)):
    """
    Update existing BTL plan task mapping records.

    Args:
        payload (BTLPlanTaskMappingPayload): List of mapping values to update.
        db (Session): Database session.

    Returns:
        dict: Count of updated records under `records_updated`.

    Raises:
        HTTPException:
            - 400: If update fails.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.btl_plan_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(btl_plan_task_mapping).filter(btl_plan_task_mapping.btl_plan_task_id == item.btl_plan_task_id, btl_plan_task_mapping.period==item.period, btl_plan_task_mapping.year==item.year, btl_plan_task_mapping.company_name==item.company_name).update(
                {btl_plan_task_mapping.value: item.value, btl_plan_task_mapping.period: item.period}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:# pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))