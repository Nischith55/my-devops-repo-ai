import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_growers(db: Session = Depends(get_db)):
    """
    Retrieve all active growers.
    
    Fetches a list of all growers with ACTIVE status from the database,
    ordered alphabetically by grower name.
    
    Args:
        db (Session): Database session dependency injected by FastAPI.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" if growers are found
            - growers (list): List of grower objects with ACTIVE status
    
    Raises:
        HTTPException: 404 Not Found if no active growers exist in the database.
    """
    
    growers = db.query(models.growers).filter(models.growers.status == "ACTIVE")\
        .order_by(models.growers.grower_name.asc())\
        .all()
    if not growers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Growers  found")
    return {"status": "success", "growers": growers}



@router.post('/', status_code=status.HTTP_201_CREATED)
def create_growers(payload: schemas.GrowerSchema, db: Session = Depends(get_db)):
    """
    Create a new grower record.
    
    Adds a new grower to the database with the provided schema data.
    The new grower is committed to the database and refreshed to retrieve
    the auto-generated grower_id.
    
    Args:
        payload (GrowerSchema): Grower data to be created, validated against GrowerSchema.
        db (Session): Database session dependency injected by FastAPI.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" upon successful creation
            - growers_id (str): The auto-generated ID of the newly created grower
    """
    try:
        new_growers = models.growers(**payload.dict())
        db.add(new_growers)
        db.commit()
        db.refresh(new_growers)
        return {"status": "success", "growers_id": new_growers.grower_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{growerId}')
def get_post(growerId: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific grower by ID.
    
    Fetches a single grower record from the database using the provided grower ID.
    
    Args:
        growerId (str): The unique identifier of the grower to retrieve.
        db (Session): Database session dependency injected by FastAPI.
    
    Returns:
        dict: A dictionary containing:
            - status (str): "success" if grower is found
            - grower (object): The grower object with the matching grower_id
    
    Raises:
        HTTPException: 404 Not Found if no grower with the specified ID exists.
    """

    grower = db.query(models.growers).filter(models.growers.grower_id == growerId).first()
    if not grower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')
    return {"status": "success", "grower": grower}
    


@router.delete('/{growerId}')
def delete_grower(growerId: str, db: Session = Depends(get_db)):
    """
    Soft-delete a grower by marking it as inactive.
    
    Updates the status of a grower record to 'IN-ACTIVE' rather than permanently
    deleting it from the database. This allows for data retention and audit trails.
    
    Args:
        growerId (str): The unique identifier of the grower to delete.
        db (Session): Database session dependency injected by FastAPI.
    
    Returns:
        Response: HTTP 204 No Content response upon successful deletion.
    
    Raises:
        HTTPException: 404 Not Found if no grower with the specified ID exists.
    """

    grower_query = db.query(models.growers).filter(models.growers.grower_id == growerId).update({'status': 'IN-ACTIVE'})
    if not grower_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No growers  with this id: {id} found')
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    