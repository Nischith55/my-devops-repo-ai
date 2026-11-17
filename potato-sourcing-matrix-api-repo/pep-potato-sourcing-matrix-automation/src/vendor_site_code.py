"""Vendor_Site_Code API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import vendor_site_code
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/get_vendor_site_code')
def view_vendor_site_code(db: Session = Depends(get_db)):
    """
    Fetch all active vendor site code records.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: List of active vendor site code records.

    Raises:
        HTTPException:
            - 404: If no records found.
            - 400: If query execution fails.
    """
    records = db.query(vendor_site_code).filter(vendor_site_code.status == "ACTIVE").all()
    if not records: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="No vendor site code found")
    return {"data": records}