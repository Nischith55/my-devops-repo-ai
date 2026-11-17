from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
import schemas
import models

router = APIRouter()


@router.get('/year/{year}')
def get_ownershipmapping(year: int, db: Session = Depends(get_db)):
    """Retrieve ownership-to-grower-growing mappings for a year.
    Fetches active `OwnershipGrowerGrowing` records for the requested
    `year` and the previous year. Joins with the `growers` table to
    include the grower name.
    Parameters:
    - year (int): The target year to filter mappings for.
    - db (Session): SQLAlchemy session provided by FastAPI via dependency.
    Returns:
    - dict: JSON containing status and a list of matching `grower_growing`
        records.
    Raises:
    - HTTPException(404): If no mapping records are found for the year.
    """
    grower_growing = db.query(models.OwnershipGrowerGrowing.row_id,
                              models.OwnershipGrowerGrowing.ownership_id,
                              models.OwnershipGrowerGrowing.growing_area_id,
                              models.OwnershipGrowerGrowing.grower_id,
                              models.growers.grower_name,
                              models.OwnershipGrowerGrowing.shrinkage,
                              models.OwnershipGrowerGrowing.shrinkage_volume,
                              models.OwnershipGrowerGrowing.contract_erp,
                              models.OwnershipGrowerGrowing.contract,
                              models.OwnershipGrowerGrowing.market,
                              models.OwnershipGrowerGrowing.flex,
                              models.OwnershipGrowerGrowing.year,
                              models.OwnershipGrowerGrowing.crop_type,
                              models.OwnershipGrowerGrowing.crop_year,
                              models.OwnershipGrowerGrowing.status)\
        .join(models.growers,
              models.OwnershipGrowerGrowing.grower_id == models.growers.grower_id)\
        .filter(models.OwnershipGrowerGrowing.status == "ACTIVE",
                or_(models.OwnershipGrowerGrowing.year == year,
                    models.OwnershipGrowerGrowing.year == year - 1)).all()
    if not grower_growing: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No mapping  found")
    return {"status": "success", "grower_growing": grower_growing}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_grower_growing_area_mapping(payload: schemas.OwnershipGrowerGrowingSchema, db: Session = Depends(get_db)):
    """Create a new ownership grower-growing area mapping.
    Validates whether a mapping already exists for the provided
    `grower_id`, `growing_area_id` and `year`. If a duplicate exists,
    returns a message indicating the record exists. Otherwise, inserts
    a new `OwnershipGrowerGrowing` record and returns its mapper id.
    Parameters:
    - payload (schemas.OwnershipGrowerGrowingSchema): Payload validated
        by Pydantic describing the mapping to create.
    - db (Session): SQLAlchemy session provided by FastAPI via dependency.
    Returns:
    - dict: JSON with creation status and the `grower_growing_mapping_id`.
    """
    try:
        ext_grower_id = payload.grower_id
        ext_growing_area_id = payload.growing_area_id
        ext_year = payload.year
        existing_record = (db.query(models.OwnershipGrowerGrowing).filter(
            models.OwnershipGrowerGrowing.growing_area_id == ext_growing_area_id,
            models.OwnershipGrowerGrowing.grower_id == ext_grower_id,
            models.OwnershipGrowerGrowing.year == ext_year).first())
        if existing_record:
            return {"message": "record exist"}
        else:
            new_Growermapping = models.OwnershipGrowerGrowing(**payload.dict())
            db.add(new_Growermapping)
        db.commit()
        db.refresh(existing_record if existing_record else new_Growermapping)

        return {
            "status": "success",
            "grower_growing_mapping_id": (
                existing_record if existing_record else new_Growermapping).growing_area_id_mapper_id
        }
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/{Growing_area_id}/{Grower_id}/{year}')
def delete_post(Growing_area_id: str, Grower_id, year, db: Session = Depends(get_db)):
    """Delete an active grower-growing mapping.

    Removes an `OwnershipGrowerGrowing` record that matches the provided
    `Growing_area_id`, `Grower_id` and `year` and has status `ACTIVE`.

    Parameters:
    - Growing_area_id (str): Identifier for the growing area.
    - Grower_id: Identifier for the grower (type preserved from route).
    - year: Year for which the mapping applies.
    - db (Session): SQLAlchemy session provided by FastAPI via dependency.

    Returns:
    - dict: JSON confirming successful deletion and echoing identifiers.

    Raises:
    - HTTPException(404): If no matching active record is found.
    """
    grower_growing = (db.query(models.OwnershipGrowerGrowing).filter(
        models.OwnershipGrowerGrowing.growing_area_id == Growing_area_id,
        models.OwnershipGrowerGrowing.grower_id == Grower_id,
        models.OwnershipGrowerGrowing.year == year, models.OwnershipGrowerGrowing.status == "ACTIVE").first())
    if not grower_growing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='No records found')
    db.delete(grower_growing)
    db.commit()
    return {"status": "success",
            "record has been deleted for": f"Grower Id: {Grower_id}, Growing Area Id: {Growing_area_id}"}


@router.post("/update_contract_erp/{crop_year}")
def update_contract_erp(crop_year: str, db: Session = Depends(get_db)):
    """Update contract ERP values from view data for a crop year.
    This endpoint finds the latest `crop_year` entries in the
    `View_growing_area_contract_erp` view for the requested `crop_year`
    STORAGE period and applies the `sum_contract` values to
    `OwnershipGrowerGrowing` records. If a matching record exists, it is
    updated; otherwise a new `OwnershipGrowerGrowing` record is created.
    Parameters:
    - crop_year (str): STORAGE_period identifier used to select view rows
        and determine the crop year to update.
    - db (Session): SQLAlchemy session provided by FastAPI via dependency.
    Returns:
    - dict: Message indicating whether the update succeeded or no view
        data was available.
    Raises:
    - HTTPException(500): If any unexpected error occurs during processing.
    """
    try:
        max_crop_year = db.query(func.max(models.View_growing_area_contract_erp.columns.crop_year))\
            .filter(models.View_growing_area_contract_erp.columns.STORAGE_period == crop_year).scalar()
        view_data = (db.query(models.View_growing_area_contract_erp)
                     .filter(models.View_growing_area_contract_erp.columns.STORAGE_period == crop_year,
                             models.View_growing_area_contract_erp.columns.crop_year == max_crop_year)
                     .all())
        if len(view_data) > 0:
            for data in view_data:
                row_id = f"{data.growignarea_id}#{data.grower_id}#{data.STORAGE_period}"
                ownershipid = f"{data.growignarea_id}#{data.STORAGE_period}"
                existing_record = (db.query(models.OwnershipGrowerGrowing)
                                   .filter(
                    models.OwnershipGrowerGrowing.growing_area_id == data.growignarea_id,
                    models.OwnershipGrowerGrowing.grower_id == data.grower_id,
                    models.OwnershipGrowerGrowing.crop_year == crop_year
                ).first())
                if existing_record is not None:
                    db.query(models.OwnershipGrowerGrowing).filter(
                        models.OwnershipGrowerGrowing.growing_area_id == data.growignarea_id,
                        models.OwnershipGrowerGrowing.grower_id == data.grower_id,
                        models.OwnershipGrowerGrowing.crop_year == crop_year
                    ).update({models.OwnershipGrowerGrowing.contract_erp: data.sum_contract,
                              models.OwnershipGrowerGrowing.status: "ACTIVE"})
                else:
                    payload = {"row_id": row_id,
                               "growing_area_id": data.growignarea_id,
                               "grower_id": data.grower_id,
                               "contract": 0,
                               "contract_erp": data.sum_contract,
                               "shrinkage": 0,
                               "market": 0,
                               "flex": 0,
                               "year": data.STORAGE_period[:4],
                               "crop_type": data.CROP_TYPE,
                               "crop_year": data.STORAGE_period,
                               "ownership_id": ownershipid,
                               "status": "ACTIVE"}
                    new_record = models.OwnershipGrowerGrowing(**payload)
                    db.add(new_record)
                db.commit()
            return {"message": f"Contract ERP updated for {crop_year}"}
        else: # pragma: no cover
            return {"message": f"Contract grower level ERP is not available for {crop_year}."}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")