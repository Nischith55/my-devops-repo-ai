import schemas
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from database import get_db

router = APIRouter()


@router.get('/')
def get_category(db: Session = Depends(get_db)):
    """
    Fetch all active categories.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: List of active categories under key `category`.

    Raises:
        HTTPException:
            - 404: If no active categories are found.
    """
    
    category = db.query(models.category).filter(models.category.status == "ACTIVE").all()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Category  found")
    return {"status": "success", "category": category}
    


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_category(payload: schemas.Category, db: Session = Depends(get_db)):
    """
    Create a new category record.

    Args:
        payload (schemas.Category): Incoming category request body.
        db (Session): Database session dependency.

    Returns:
        dict: Status and newly created category identifier.
    """
    try:
        new_category = models.category(**payload.dict())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return {"status": "success", "category": new_category.crop_category}
    except Exception as e:# pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/{categoryId}')
def get_post(categoryId: str, db: Session = Depends(get_db)):
    """
    Fetch category details by category ID.

    Args:
        categoryId (str): Crop category identifier.
        db (Session): Database session dependency.

    Returns:
        dict: Matching category record under key `category`.

    Raises:
        HTTPException:
            - 404: If category does not exist.
    """
  
    category_id = db.query(models.category).filter(models.category.crop_category == categoryId).first()
    if not category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No category  with this id: {id} found')
    return {"status": "success", "category": category_id}
    


@router.delete('/{categoryId}')
def delete_category(categoryId: str, db: Session = Depends(get_db)):
    """
    Soft-delete a category by marking its status as IN-ACTIVE.

    Args:
        categoryId (str): Crop category identifier.
        db (Session): Database session dependency.

    Returns:
        Response: HTTP 204 when deletion is successful.

    Raises:
        HTTPException:
            - 404: If category does not exist.
    """
   
    category_query = db.query(models.category).filter(models.category.crop_category == categoryId).update({'status': 'IN-ACTIVE'})
    if not category_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Category  with this id: {id} found')
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
