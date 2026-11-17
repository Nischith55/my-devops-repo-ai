import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_growing_area(db: Session = Depends(get_db)):
    """
    Fetch all active growing areas.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: List of growing areas under key `growing_area`.

    Raises:
        HTTPException:
            - 404: If no active growing areas exist.
    """
    growing_area = db.query(models.growing_area).filter(models.growing_area.status == "ACTIVE").all()
    if not growing_area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No growing area  found")
    return {"status": "success", "growing_area": growing_area}
    


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_growing_area(payload: schemas.GrowingAreaSchema, db: Session = Depends(get_db)):
    """
    Create a new growing area entry.

    Args:
        payload (schemas.GrowingAreaSchema): Incoming growing area details.
        db (Session): Database session dependency.

    Returns:
        dict: Status and newly created growing_area_id.
    """
    try:
        new_area = models.growing_area(**payload.dict())
        db.add(new_area)
        db.commit()
        db.refresh(new_area)
        return {"status": "success", "growing_area_id": new_area.growing_area_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/preferred_grower')
def get_preferred_grower(db: Session = Depends(get_db)):
    """
    Fetch preferred grower mappings for all growing areas.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: Preferred grower records under key `preferred_grower`.

    Raises:
        HTTPException:
            - 404: If no grower mappings exist.
    """
   
    data = db.query(models.preferred_grower).all()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No grower  found")
    return {"status": "success", "preferred_grower": data}
 


@router.get('/{growing_areaId}')
def get_growingid(growing_areaId: str, db: Session = Depends(get_db)):
    """
    Fetch growing area details by ID.

    Args:
        growing_areaId (str): Growing area identifier.
        db (Session): Database session dependency.

    Returns:
        dict: Matching growing area record.

    Raises:
        HTTPException:
            - 404: If growing area does not exist.
    """
    
    growing_area = db.query(models.growing_area).filter(
        models.growing_area.growing_area_id == growing_areaId).first()
    if not growing_area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Growing area  with this id: {id} found")
    return {"status": "success", "growing-area": growing_area}
    


@router.delete('/{growing_areaId}')
def delete_growing_area(growing_areaId: str, db: Session = Depends(get_db)):
    """
    Soft delete a growing area by marking its status inactive.

    Args:
        growing_areaId (str): Growing area identifier.
        db (Session): Database session dependency.

    Returns:
        Response: HTTP 204 on successful deletion.

    Raises:
        HTTPException:
            - 404: If growing area does not exist.
    """
    growing_area_query = db.query(models.growing_area).filter(
        models.growing_area.growing_area_id == growing_areaId).update({'status': 'IN-ACTIVE'})
    if not growing_area_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growing area  with this id: {id} found')
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
