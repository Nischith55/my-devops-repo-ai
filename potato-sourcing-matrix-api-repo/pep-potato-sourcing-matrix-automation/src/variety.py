from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from typing import Optional
from datetime import date
from sqlalchemy import text
from period_week_calc import calculate_period_and_week

router = APIRouter()


@router.get('/')
def get_variety_all(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Retrieve all ACTIVE & inactive varieties.

    Args:
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and list of varieties.

    Raises:
        HTTPException: 404 if no active varieties found.
    """
    variety = db.query(models.Variety).all()

    if not variety:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No varieties found"
        )

    return {"status": "success", "variety": variety}


@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_variety(payload: schemas.VarietySchema, db: Session = Depends(get_db)):  # pragma: no cover
    """
    Create a new variety record in the database.

    Args:
        payload (schemas.VarietySchema): Variety data to create.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and the ID of the newly created variety.

    Raises:
        HTTPException: 400 for any insert errors.
    """
    try:
        new_variety = models.Variety(**payload.dict())
        if not new_variety.status:
            new_variety.status = "ACTIVE"

        db.add(new_variety)
        db.commit()
        db.refresh(new_variety)

        return {"status": "success", "variety_id": new_variety.variety_id}

    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/status_change/{variety_id}/{updated_by}', status_code=status.HTTP_201_CREATED)
def create_variety(variety_id: str, updated_by: str, db: Session = Depends(get_db)):  # pragma: no cover
    """
    Create a new variety record in the database.

    Args:
        payload (schemas.VarietySchema): Variety data to create.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and the ID of the newly created variety.

    Raises:
        HTTPException: 400 for any insert errors.
    """
    try:
        variety_obj = db.query(models.Variety).filter(models.Variety.variety_id == variety_id).first()
        status = variety_obj.status.upper()
        if status == "ACTIVE":
            variety_obj.status = "INACTIVE"
        else:
            variety_obj.status = "ACTIVE"
        
        variety_obj.updated_by = updated_by

        db.commit()
        db.refresh(variety_obj)
        return {"status": "success", "variety_id": variety_obj.variety_id}

    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/{variety_id}')
def update_variety(variety_id: int, payload: schemas.VarietyUpdateSchema, db: Session = Depends(get_db)):  # pragma: no cover
    """
    Update ONLY: variety_name, variety_mapping, description.
    Also updates updated_by. updated_time is auto-updated by model onupdate.
    """
    variety_obj = db.query(models.Variety).filter(models.Variety.variety_id == variety_id).first()

    if not variety_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No Variety with this id: {variety_id} found'
        )

    try:
        if payload.variety_name is not None:
            variety_obj.variety_name = payload.variety_name

        if payload.variety_mapping is not None:
            variety_obj.variety_mapping = payload.variety_mapping

        if payload.description is not None:
            variety_obj.description = payload.description

        if payload.updated_by is not None:
            variety_obj.updated_by = payload.updated_by

        db.commit()
        db.refresh(variety_obj)

        return {"status": "success", "variety_id": variety_obj.variety_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/variety_dashboard_refresh', status_code=status.HTTP_201_CREATED)
def create_erp_variety(year: Optional[int] = None,db: Session = Depends(get_db)):  # pragma: no cover
    """
    Refresh the variety dashboard materialized view.

    Args:
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status of the refresh operation.

    Raises:
        HTTPException: 400 for any refresh errors.
    """
    try:
        # Get calendar year from period_week_calc
        if year is not None:
            calendar_year = year
        else:
            today = date.today()
            period_week_info = calculate_period_and_week(today.year, today)
            calendar_year = period_week_info['year']    
        
        # Delete existing records for the calendar year
        delete_query = text("""
            DELETE FROM erp_variety 
            WHERE Receipt_Year = :year
        """)
        
        delete_result = db.execute(delete_query, {"year": calendar_year})
        deleted_count = delete_result.rowcount
        
        # Insert records from erp_raw_data
        insert_query = text("""
            INSERT INTO erp_variety (
                BPA_Number,
                Release_No,
                Line_No,
                Shipment,
                Crop_Type,
                Receipt_Date,
                Receipt_Year,
                Period,
                Week,
                Grower_id,
                Plant_id,
                Growing_area_id,
                Region_id,
                Variety,
                Variety_id,
                Quantity_Accepted_MCWT
            )
            SELECT 
                erp.BPA_Number,
                erp.Release_No,
                erp.Line_No,
                erp.Shipment,
                erp.Crop_Type,
                erp.Receipt_Date,
                erp.Receipt_Year,
                erp.Rec_Date_PD,
                erp.Rec_Date_WK,
                erp.Grower_id,
                erp.Plant_id,
                erp.Growing_area_id,
                erp.Region,
                erp.Variety,
                erp.variety_id,
                erp.Quantity_Accepted_MCWT
            FROM erp_raw_data erp
            WHERE erp.Receipt_Year = :year and erp.Source = 'SAP'
        """)
        
        insert_result = db.execute(insert_query, {"year": calendar_year})
        inserted_count = insert_result.rowcount
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully synced ERP variety data for year {calendar_year}",
            "calendar_year": calendar_year,
            "records_deleted": deleted_count,
            "records_inserted": inserted_count
        }
        
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))