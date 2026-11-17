"""Plant_Site_Growing_Area_Mapping API"""
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
import models
from models import PlantSiteGrowingAreaMapping
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/get_plant_site_gowing_area_mapping')
def view_plant_site_growing_area(db: Session = Depends(get_db)):
    """
    Retrieve all plant-site-growing area mapping records.

    This endpoint fetches all records from the PlantSiteGrowingAreaMapping table.
    Returns a complete list of all plant, site, and growing area mappings in the system.

    Args:
        db (Session): Database session dependency for querying the database.

    Returns:
        dict: A dictionary containing:
            - data (list): List of all PlantSiteGrowingAreaMapping records.

    Raises:
        HTTPException: 400 status code if any exception occurs during query execution.
    """
    try:
        records = db.query(PlantSiteGrowingAreaMapping).all()
        return {"data": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/{growing_area_id}')
def get_plantid(growing_area_id: int, db: Session = Depends(get_db)):
    """
    Retrieve plant-site-growing area mappings for a specific growing area.

    This endpoint fetches plant mapping information filtered by the provided growing area ID.
    Returns a list of plants associated with the specified growing area.

    Args:
        growing_area_id (int): The growing area identifier to filter plant mappings.
        db (Session): Database session dependency for querying the database.

    Returns:
        dict: A dictionary containing:
            - status (str): "success" indicating successful retrieval
            - plant (list): List of plant mapping dictionaries with keys:
                - plant_name: Name of the plant
                - growing_area: Growing area name
                - plant_id: Identifier for the plant
                - growing_area_id: Growing area identifier

    Raises:
        HTTPException: 404 status code if no plants found for the given growing area ID.
        HTTPException: 400 status code if any exception occurs during query execution.
    """
    plants = db.query(models.PlantSiteGrowingAreaMapping).filter(models.PlantSiteGrowingAreaMapping.growing_area_id == growing_area_id).all()
    
    plants_data = [{"plant_name": plant.plant_name,"growing_area": plant.growing_area,"plant_id": plant.plant_id,"growing_area_id": plant.growing_area_id}for plant in plants]
    for i in plants:
        print(i.plant_name)
        print(i.growing_area_id)
    if not plants: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No plant with this id: {id} found")
    return {"status": "success", "plant": plants_data}