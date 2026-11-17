from datetime import date, datetime
import schemas
import models
import pytz
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
import period_week_calc

router = APIRouter()


@router.get('/')
def get_plant_all(db: Session = Depends(get_db)): # pragma: no cover
    """
    Retrieve all active plants and current period/week information.

    Args:
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status, list of plants, current period, week, year, and current CST time.
    """
    plant = db.query(models.Plant).filter(models.Plant.status == "ACTIVE").all()

    cst = pytz.timezone('US/Central')
    utc_now = datetime.now(pytz.utc)

    # Convert the current UTC time to CST
    cst_now = utc_now.astimezone(cst)

    cst_date = cst_now.date()
    today_date = cst_date
    res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
    current_period = res['Period']
    current_week = res['week']
    year_data = res['year']
    if not plant: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No plant  found")
    return {"status": "success", "plant": plant,
            "current_period": current_period, "current_week": current_week,
            "year": year_data, "current_time": cst_now}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_plant(payload: schemas.PlantSchema, db: Session = Depends(get_db)):
    """
    Create a new plant record in the database.

    Args:
        payload (schemas.PlantSchema): Plant data to create.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and the ID of the newly created plant.
    """
    try:
        new_plant = models.Plant(**payload.dict())
        db.add(new_plant)
        db.commit()
        db.refresh(new_plant)
        return {"status": "success", "plants_id": new_plant.plant_id}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{plantId}')
def get_plantid(plantId: str, db: Session = Depends(get_db)):
    """
    Retrieve a plant by its ID.

    Args:
        plantId (str): The ID of the plant to retrieve.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and the plant data if found.
    """
    plant = db.query(models.Plant).filter(models.Plant.plant_id == plantId).first()
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No plant with this id: {id} found")
    return {"status": "success", "plant": plant}


@router.get('/get_country_company_name/{filter_value}')
def get_plants_country_based(filter_value: str, db: Session = Depends(get_db)):
    """
    Retrieve plants filtered by country or company name.

    Args:
        filter_value (str): Country ('US', 'Canada') or company name to filter plants.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and list of filtered plants.
    """
    try:
        if filter_value == 'US' or filter_value == 'Canada':
            plants = db.query(models.Plant) \
                .join(models.region, models.Plant.region_id == models.region.region_id) \
                .filter(models.region.country == filter_value, models.Plant.status == 'ACTIVE') \
                .all()
        else:
            plants = db.query(models.Plant)\
                .filter(models.Plant.company_name == filter_value, models.Plant.status == 'ACTIVE').all()

        return {"status": "success", "plants": plants}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get('/get_region/{filter_value}')
def get_plants_region_based(filter_value: int, db: Session = Depends(get_db)):
    """
    Retrieve plants filtered by region ID.

    Args:
        filter_value (int): Region ID to filter plants.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        dict: Status and list of filtered plants.
    """
    try:
        plants = db.query(models.Plant)\
            .filter(models.Plant.region_id == filter_value, models.Plant.status == 'ACTIVE') \
            .all()
        return {"status": "success", "plants": plants}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=f"{str(e)}")