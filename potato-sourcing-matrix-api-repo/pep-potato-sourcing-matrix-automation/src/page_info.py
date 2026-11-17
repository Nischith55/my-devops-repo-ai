"""Page Information API"""
import schemas
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (page_information,country_information,access_type_information)
from sqlalchemy.orm import Session


router = APIRouter()

@router.get('/get_page_information')
async def get_page_information(db: Session = Depends(get_db)):
    """
    Retrieve all records from the page_information table.
    
    Args:
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: Dictionary containing all page information records.
    """
    try:
        records = db.query(page_information).all()
        return {"data": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/get_country_information')
async def get_country_information(db: Session = Depends(get_db)):
    """
    Retrieve all records from the country_information table.
    
    Args:
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: Dictionary containing all country information records.
    """
    try:
        records = db.query(country_information).all()
        return {"data": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get('/get_access_information')
async def get_access_type_information(db: Session = Depends(get_db)):
    """
    Retrieve all records from the access_type_information table.
    
    Args:
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: Dictionary containing all access type information records.
    """
    try:
        records = db.query(access_type_information).all()
        return {"data": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post('/create_page_information', status_code=status.HTTP_201_CREATED)
async def create_page_information(payload: schemas.PageInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new record in the page_information table.
    
    Args:
        payload (schemas.PageInfoSchema): Data for the new page information record.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: Status of the creation operation.
    """
    try:
        page_info= page_information(**payload.dict())
        db.add(page_info)
        db.commit()
        db.refresh(page_info)
        return {"status": "success"}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.post('/create_country_information', status_code=status.HTTP_201_CREATED)
async def create_country_information(payload: schemas.CountryInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new record in the country_information table.
    
    Args:
        payload (schemas.CountryInfoSchema): Data for the new country information record.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: Status of the creation operation.
    """
    try:
        new_country= country_information(**payload.dict())
        db.add(new_country)
        db.commit()
        db.refresh(new_country)
        return {"status": "success"}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post('/create_access_type_information', status_code=status.HTTP_201_CREATED)
async def create_access_type_information(payload: schemas.AccessInfoSchema, db: Session = Depends(get_db)):
    """
    Create a new record in the access_type_information table.
    
    Args:
        payload (schemas.AccessInfoSchema): Data for the new access type information record.
        db (Session): SQLAlchemy database session dependency.
    
    Returns:
        dict: Status of the creation operation.
    """
    try:
        access_details= access_type_information(**payload.dict())
        db.add(access_details)
        db.commit()
        db.refresh(access_details)
        return {"status": "success"}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e