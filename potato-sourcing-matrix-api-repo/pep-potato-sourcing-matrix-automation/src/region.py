import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_region_all(db: Session = Depends(get_db)):
    """Retrieve all active regions.

    Queries the database for regions with a status of "ACTIVE" and returns
    a JSON-compatible dict with the results. If no active regions are found,
    raises an HTTP 404 error.

    Parameters:
    - db (Session): SQLAlchemy session injected by FastAPI's dependency.

    Returns:
    - dict: A dictionary containing a "status" key and a "regions" key
      holding the list of region model instances.

    Raises:
    - HTTPException: If no active regions are found (404 Not Found).
    """
    region = db.query(models.region).filter(models.region.status == "ACTIVE").all()
    if not region: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No region found")
    return {"status": "success", "regions": region}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_region(payload: schemas.Region, db: Session = Depends(get_db)): 
    """Create a new region record.

    Creates and persists a new `models.region` instance using data from the
    provided `schemas.Region` payload. Returns the created resource id on
    success.

    Parameters:
    - payload (schemas.Region): Pydantic model containing region data.
    - db (Session): SQLAlchemy session injected by FastAPI's dependency.

    Returns:
    - dict: A dictionary with "status" and the newly created "region_id".
    """
    try:
        new_region = models.region(**payload.dict())
        db.add(new_region)
        db.commit()
        db.refresh(new_region)
        return {"status": "success", "region_id": new_region.region_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{regionId}')
def get_regionid(regionId: str, db: Session = Depends(get_db)):
    """Fetch a single region by its identifier.

    Looks up a `models.region` record using `regionId` and returns it if
    present. Raises HTTP 404 if no record is found.

    Parameters:
    - regionId (str): The unique identifier of the region to fetch.
    - db (Session): SQLAlchemy session injected by FastAPI's dependency.

    Returns:
    - dict: A dictionary with "status" and the "region" model instance.

    Raises:
    - HTTPException: If no region is found for the provided id (404 Not Found).
    """
    region = db.query(models.region).filter(models.region.region_id == regionId).first()
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No region  with this id: {regionId} found')
    return {"status": "success", "region": region}


@router.delete('/{regionId}')
def delete_region(regionId: str, db: Session = Depends(get_db)):
    """Soft-delete a region by setting its status to 'IN-ACTIVE'.

    Updates the `status` field of the region matching `regionId` to
    `'IN-ACTIVE'`. If no matching region exists, raises HTTP 404. On
    success commits the transaction and returns an empty 204 response.

    Parameters:
    - regionId (str): The unique identifier of the region to delete.
    - db (Session): SQLAlchemy session injected by FastAPI's dependency.

    Returns:
    - Response: A FastAPI `Response` with status code 204 on success.

    Raises:
    - HTTPException: If no region exists with the provided id (404 Not Found).
    """
    region_query = db.query(models.region).filter(models.region.region_id == regionId).update({'status': 'IN-ACTIVE'})
    if not region_query: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No region  with this id: {id} found')
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)