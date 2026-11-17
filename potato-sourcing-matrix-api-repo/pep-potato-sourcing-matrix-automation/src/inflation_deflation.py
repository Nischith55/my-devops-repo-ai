"""Inflation-Deflation API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import (inflation_deflation_task_mappings,country_division_name,inflation_deflation_task
                    ,inflation_deflation)
from schemas import InflationDeflationMappingPayload
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/inflation_deflation_task_mapping')
def get_inflation_deflation_task_mappings(db: Session = Depends(get_db)):
    """
    Fetch all inflation/deflation task mappings.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: List of mappings under key `inflation_deflation_task_mapping`.

    Raises:
        HTTPException:
            - 400: On query execution failure.
    """
    try:
        records = db.query(inflation_deflation_task_mappings).all()
        result = [
            {
                "inflation_deflation_task_id": row.inflation_deflation_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"inflation_deflation_task_mapping": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get('/inflation_deflation_task')
def get_inflation_deflation_task(db: Session = Depends(get_db)):
    """
    Fetch all inflation/deflation tasks.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: List of tasks under key `inflation_deflation_task`.

    Raises:
        HTTPException:
            - 400: On query execution failure.
    """
    try:
        records = db.query(inflation_deflation_task).all()
        result = [
            {
                "inflation_deflation_task_id": row.inflation_deflation_task_id,
                "task_name": row.task_name,
            }
            for row in records
        ]
        return {"inflation_deflation_task": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/inflation_deflation_task_mappings_by_year/{year}/{company_name}')
def inflation_deflation_task_mappings_by_year(year: int,company_name :str, db: Session = Depends(get_db)):
    """
    Fetch inflation/deflation task mappings filtered by year and company.

    Args:
        year (int): Year filter.
        company_name (str): Company name filter.
        db (Session): Database session dependency.

    Returns:
        dict: Filtered mappings under key `inflation_deflation_task_mappings_year`.

    Raises:
        HTTPException:
            - 400: On query execution failure.
    """
    try:
        records = db.query(inflation_deflation_task_mappings
                           ).filter(inflation_deflation_task_mappings.year==year,
                                    inflation_deflation_task_mappings.company_name == company_name).all()
        result = [
            {
                "inflation_deflation_task_id": row.inflation_deflation_task_id,
                "period": row.period,
                "period_with_P": f'P{row.period}',
                "year": row.year,
                "value":row.value,
                "company-name" :row.company_name
            }
            for row in records
        ]
        return {"inflation_deflation_task_mappings_year": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/update_inflation_deflation_task_mappings_records/")
def update_inflation_deflation_task_mappings_records(payload: InflationDeflationMappingPayload, db: Session = Depends(get_db)):
    """
    Update existing inflation/deflation task mapping records.

    Args:
        payload (InflationDeflationMappingPayload): List of mapping updates.
        db (Session): Database session dependency.

    Returns:
        dict: Status message and count of updated records.

    Raises:
        HTTPException:
            - 400: On update failure.
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if item.inflation_deflation_task_id <= 0 or item.period<=0 or item.year<=0:
                return {"status": "error", "message":"Please check details"}
            db.query(inflation_deflation_task_mappings).filter(
                inflation_deflation_task_mappings.inflation_deflation_task_id== item.inflation_deflation_task_id,
                inflation_deflation_task_mappings.year==item.year, 
                inflation_deflation_task_mappings.period==item.period,
                inflation_deflation_task_mappings.company_name == item.company_name).update(
                    {inflation_deflation_task_mappings.value: item.value}, synchronize_session='fetch')
            update_count += 1
        db.commit()

        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('inflation_deflation/year/{year}/company_name/{company_name}')
def inflation_deflation_year_country_code(year: int, company_name: str, db: Session = Depends(get_db)): 
    """
    Fetch inflation/deflation view records filtered by year and company.

    Args:
        year (int): Year filter.
        company_name (str): Company name filter.
        db (Session): Database session dependency.

    Returns:
        dict: View records under key `inflation_deflation`.

    Raises:
        HTTPException:
            - 400: On query execution failure.
    """
    try:
        records = db.query(inflation_deflation).filter(
            inflation_deflation.columns.year == year,
            inflation_deflation.columns.company_name == company_name
            ).order_by(inflation_deflation.columns.period).all()
        return {"inflation_deflation": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
