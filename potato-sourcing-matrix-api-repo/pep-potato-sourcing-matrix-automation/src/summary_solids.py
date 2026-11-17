"""Summary Solid API's"""
from models import solid_task_master, solids_task_mapping, summary_solids
from schemas import SolidTaskMasterSchema, SolidsTaskMappingSchema, SolidsTaskMappingSchemaPayload
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db

router = APIRouter()

@router.get('/')
def get_solid_task_master(db: Session = Depends(get_db)):
    """
    Retrieve all records from the solid_task_master table.
    
    Args:
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary containing a 'details' key with all solid_task_master records.
    
    Raises:
        HTTPException: Status code 400 if any exception occurs during query execution.
    """
    try:
        records = db.query(solid_task_master).all()
        return {"details": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_solid_task_mapping')
def get_solid_task_mapping(db: Session = Depends(get_db)):
    """
    Retrieve all solids task mapping records and aggregate values by period.
    
    Args:
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary containing 'task' key with a list of aggregated records.
              Each record includes period, Total, and period_with_P (formatted period).
    
    Raises:
        HTTPException: Status code 400 if any exception occurs during query execution.
    """
    try:
        records = db.query(solids_task_mapping).all()
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


@router.get('/get_solid_task_master/{solids_task_id}')
def get_solid_task_master_by_id(solids_task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific solid task master record by its ID.
    
    Args:
        solids_task_id (int): The unique identifier of the solid task record to retrieve.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status' and 'details' keys containing the found record.
    
    Raises:
        HTTPException: Status code 404 if no record with the given ID is found.
    """
    query = db.query(solid_task_master).filter(solid_task_master.solids_task_id == solids_task_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No solids_task_id: {solids_task_id} found")
    return {"status": "success", "details": query}


@router.get('/solids_task_mapping_by_year/{year}')
def solids_task_mapping_by_year(year: str, db: Session = Depends(get_db)):
    """
    Retrieve solids task mapping records for a specific year with aggregated values by period.
    
    Args:
        year (str): The year for which to retrieve solids task mapping records.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status' and 'data' keys containing aggregated records
              by period with prior, plan, and forecast values.
    
    Raises:
        HTTPException: Status code 404 if no records are found for the specified year.
    """
    query = (db.query(solids_task_mapping.period, func.sum(solids_task_mapping.value).label('prior'),func.sum(solids_task_mapping.value).label('plan'), func.sum(solids_task_mapping.value).label('forcast'))
             .join(solid_task_master, solid_task_master.solids_task_id==solids_task_mapping.solids_task_id)
             .filter(solids_task_mapping.year==year).group_by(solids_task_mapping.year, solids_task_mapping.period).all())
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No solids_task_mapping  found")
    return {"status": "success", "data": query}

@router.post("/update_solids_task_mappings/", status_code=status.HTTP_201_CREATED)
async def update_solids_task_mappings(year: int, db: Session = Depends(get_db)):
    """
    Create new solids task mapping records for a specified year for all task masters.
    
    This function iterates through all solid task master records and creates mapping
    records for periods 1-13 if they don't already exist for the given year.
    
    Args:
        year (int): The year for which to create solids task mapping records.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status', list of existing task names, and target year.
    
    Raises:
        HTTPException: Status code 404 if no records are found in the database.
    """
    try:
        # Fetch all records from the database
        all_records = db.query(solid_task_master).all()
        # Ensure there are records in the database
        if all_records.count==0:
            raise HTTPException(status_code=404, detail="No records found in the database")

        existing_task_names = []
        for record in all_records:
            existing_record = db.query(solids_task_mapping).filter(solids_task_mapping.year==year,solids_task_mapping.solids_task_id==record.solids_task_id ).first()
            if existing_record:
                existing_task_names.append(record.task_name)
                continue
            for period in range(1,14):
                new_record = solids_task_mapping(solids_task_id = record.solids_task_id, period=period, year=year, value=0.001)
                db.add(new_record)
                db.commit()

        return {"status": "success", "Records already exists for ":existing_task_names, "forYear": year}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_solid_task_master', status_code=status.HTTP_201_CREATED)
def create_solid_task_master(payload: SolidTaskMasterSchema, db: Session = Depends(get_db)):
    """
    Create a new solid task master record in the database.
    
    Args:
        payload (SolidTaskMasterSchema): The request payload containing solid task master details.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status' and the newly created 'solids_task_id'.
    """
    try:
        new_record = solid_task_master(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "solids_task_id": new_record.solids_task_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/create_solids_task_mappings', status_code=status.HTTP_201_CREATED)
def create_solid_rate_mappings(payload: SolidsTaskMappingSchema, db: Session = Depends(get_db)):
    """
    Create a new solids task mapping record in the database.
    
    Args:
        payload (SolidsTaskMappingSchema): The request payload containing solids task mapping details.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status' and the newly created 'row_id'.
    """
    try:
        new_record = solids_task_mapping(**payload.dict())
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "row_id": new_record.row_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_solids_task_mapping_records/")
def update_solid_rate_mapping_records(payload: SolidsTaskMappingSchemaPayload, db: Session = Depends(get_db)):
    """
    Update existing solids task mapping records in the database.
    
    This function validates input data and updates the value field for records matching
    the solids_task_id, year, period, and country_code criteria.
    
    Args:
        payload (SolidsTaskMappingSchemaPayload): The request payload containing a list of
                                                    records to update.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status' and the count of 'records_updated'.
              Returns error status if validation fails.
    
    Raises:
        HTTPException: Status code 400 if any exception occurs during update execution.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.solids_task_id<=0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(solids_task_mapping).filter(solids_task_mapping.solids_task_id == item.solids_task_id, solids_task_mapping.year==item.year, solids_task_mapping.period==item.period,solids_task_mapping.country_code == item.country_code).update(
                {solids_task_mapping.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get('/summary_solids_view/{year}/{country_code}')
def summary_solids_view_year_country_code(year:int,country_code:str,db: Session = Depends(get_db)):
    """
    Retrieve summary solids records filtered by year and country code.
    
    Args:
        year (int): The year for which to retrieve summary solids records.
        country_code (str): The country code to filter summary solids records.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'summary_solids_view' key containing records ordered by period.
    
    Raises:
        HTTPException: Status code 400 if any exception occurs during query execution.
    """
    try:
        records = db.query(summary_solids).filter(
            summary_solids.columns.year == year,
            summary_solids.columns.country_code == country_code
            ).order_by(summary_solids.columns.period).all()
        return {"summary_solids_view": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_summary_solids_for_next_year/", status_code=status.HTTP_201_CREATED)
async def create_summary_solids_for_next_year(year: int , db: Session = Depends(get_db)):
    """
    Create solids task mapping records for the specified year based on previous year's data.
    
    This function:
    - Retrieves all solid task master records
    - Fetches summary data from the previous year
    - Deletes any existing records for the target year
    - Creates new mapping records for PLAN, PRIOR, FORECAST, and other task types
      with appropriate values carried forward or reset
    
    Args:
        year (int): The target year for which to create solids task mapping records.
        db (Session): Database session dependency for executing queries.
    
    Returns:
        dict: A dictionary with 'status', count of 'Records added', and 'for Year'.
    """
    try:
        all_records = db.query(solid_task_master).all()
        query_view = db.query(summary_solids).filter(summary_solids.columns.year==(year-1)).all() #view which contains actual value by growing_area_id
        update_count = 0
        existing_record = db.query(solids_task_mapping)\
                        .filter(solids_task_mapping.year==year).all()
        for ex in existing_record:
            db.delete(ex)
        db.commit()

        solid_task_name_map = {}
        for record in all_records: # Iterate over all solids_rates
            solid_task_name_map[record.task_name] = record.solids_task_id

        for ele in query_view:  # Iterate through the view
            # PLAN - Plan current year = Plan for next year
            new_record = solids_task_mapping(solids_task_id = solid_task_name_map.get("PLAN") , period=ele.period, year=year, value=ele.Plan, country_code=ele.country_code)
            db.add(new_record)

            # PRIOR - Forecast of current year = Prior for next year
            forecastvalue = ele.forecast
            query= db.query(solids_task_mapping).filter(solids_task_mapping.solids_task_id==solid_task_name_map.get("PRIOR"), solids_task_mapping.period==ele.period, solids_task_mapping.country_code==ele.country_code, solids_task_mapping.year==year).first()
            if query and query.value >0: # pragma: no cover
                new_record = solids_task_mapping(solids_task_id = solid_task_name_map.get("PRIOR"), period=ele.period, year=year, value=query.value, country_code=ele.country_code)
            else:
                new_record = solids_task_mapping(solids_task_id = solid_task_name_map.get("PRIOR"), period=ele.period, year=year, value=forecastvalue, country_code=ele.country_code)
            db.add(new_record)

            # FORECAST - Forecast precalculated by formulae =  0 for next year
            new_record = solids_task_mapping(solids_task_id = solid_task_name_map.get("FORECAST"), period=ele.period, year=year, value=0, country_code=ele.country_code)
            db.add(new_record)

            # CF
            new_record = solids_task_mapping(solids_task_id = solid_task_name_map.get("Conversion Factor"), period=ele.period, year=year, value=ele.Conversion_Factor, country_code=ele.country_code)
            db.add(new_record)

            #M$ IMPACT_Plan_Value
            new_record = solids_task_mapping(solids_task_id = solid_task_name_map.get("M$ IMPACT_Plan_Value"), period=ele.period, year=year, value=0, country_code=ele.country_code)
            db.add(new_record)

            update_count += 5
        db.commit()

        return {"status": "success", "Records added": update_count, "for Year": year}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))