from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
import schemas
import models
from datetime import datetime
import pandas as pd
import numpy as np

router = APIRouter()


@router.get('/')
def get_extension(db: Session = Depends(get_db)):
    """
    Retrieve all active extension ownership mappings.
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success" if records are found
            - "extensionMapping" (list): List of active ExtensionOwnershipMapping records
    
    Raises:
        HTTPException: Status 200 with detail message if no active extensions exist.
    """
    
    filtered_ext = db.query(models.ExtensionOwnershipMapping) \
        .filter(models.ExtensionOwnershipMapping.status == "ACTIVE").all()
    if not filtered_ext: # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No extension for this year.")
    return {"status": "success", "extensionMapping": filtered_ext}


@router.get('/year/{year}')
def filtered_extension(year: int, db: Session = Depends(get_db)):
    """
    Retrieve active extension ownership mappings for a specific crop year.
    
    Args:
        year (int): The crop year to filter by (last 2 digits are used for comparison).
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success" if records are found
            - "extensionMapping" (list): List of active ExtensionOwnershipMapping records for the year
    
    Raises:
        HTTPException: Status 200 with detail message if no extensions exist for the year.
    """
    
    compare_year = str(year)[-2:]
    filtered_ext = db.query(models.ExtensionOwnershipMapping) \
        .filter(models.ExtensionOwnershipMapping.status == "ACTIVE",
                models.ExtensionOwnershipMapping.crop_year.contains(compare_year)).all()
    if not filtered_ext: # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No extension is present for this year.")
    return {"status": "success", "extensionMapping": filtered_ext}
    


def update_ownership_extension_overlap(growing_area_id: int, crop_year, db):  # pragma: no cover
    """
    Update ownership table with final extension values when extension overlaps with fresh period.
    
    This function checks if the maximum period and week of the extension mapping overlaps with
    the fresh period start date for the growing area. If there is an overlap, it calculates the
    sum of total values for all extension records from the fresh start period onwards and updates
    the Ownership table's final_extension field. If no extensions exist, sets final_extension to 0.
    
    Args:
        growing_area_id (int): The ID of the growing area.
        crop_year (str): The crop year in format 'YYYY-YY' or numeric string.
        db (Session): SQLAlchemy database session for query and update operations.
    
    Returns:
        None. Updates the Ownership table directly.
    """
    try:
        print("Entering update_ownership_extension_overlap")
        if '-' in crop_year:
            get_max_period = db.query(func.max(models.ExtensionOwnershipMapping.period)) \
                .filter(models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                        models.ExtensionOwnershipMapping.status == 'ACTIVE',
                        models.ExtensionOwnershipMapping.crop_year == crop_year).scalar()
            if get_max_period:
                get_max_week = db.query(func.max(models.ExtensionOwnershipMapping.week)) \
                    .filter(models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                            models.ExtensionOwnershipMapping.status == 'ACTIVE',
                            models.ExtensionOwnershipMapping.crop_year == crop_year,
                            models.ExtensionOwnershipMapping.period == get_max_period).scalar()
                final_extension_limit = get_max_period * 100 + get_max_week
                print("final_extension_limit:", final_extension_limit)
                ga_fresh = db.query(models.growing_area.fresh_period_start,
                                    models.growing_area.fresh_week_start) \
                    .filter(models.growing_area.growing_area_id == growing_area_id).first()

                fresh_start = ga_fresh[0] * 100 + ga_fresh[1]
                print("fresh_start:", fresh_start)

                if final_extension_limit >= fresh_start:
                    """Update the ownership table with final_extension."""
                    new_final_extension = db.query(func.sum(models.ExtensionOwnershipMapping.total_value)
                                                   .label('total_value_sum')) \
                        .filter(models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                                models.ExtensionOwnershipMapping.crop_year == crop_year,
                                models.ExtensionOwnershipMapping.period * 100 +
                                models.ExtensionOwnershipMapping.week >= fresh_start) \
                        .group_by(models.ExtensionOwnershipMapping.growing_area_id,
                                  models.ExtensionOwnershipMapping.crop_year).first()
                    if new_final_extension:
                        db.query(models.Ownership).filter(models.Ownership.growing_area_id == growing_area_id,
                                                          models.Ownership.crop_year == crop_year) \
                            .update({models.Ownership.final_extension: new_final_extension[0]}, synchronize_session=False)
                    db.commit()
            else:
                db.query(models.Ownership).filter(models.Ownership.growing_area_id == growing_area_id,
                                                  models.Ownership.crop_year == crop_year) \
                    .update({models.Ownership.final_extension: 0}, synchronize_session=False)
                db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_final_extension_value(input_growing_area_id, input_crop_year,
                                 db: Session = Depends(get_db)): # pragma: no cover
    """
    Update the total extension value in the Ownership table for a growing area and crop year.
    
    This function calculates the sum of all total_value fields from ExtensionOwnershipMapping
    records for the specified growing area and crop year, then updates the Ownership table's
    extension field with this sum. It also calls update_ownership_extension_overlap to handle
    any final extension updates if there is an overlap with the fresh period.
    
    Args:
        input_growing_area_id: The ID of the growing area.
        input_crop_year: The crop year to filter by.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        None. Updates the Ownership table directly.
    """
    try:
        final_extension_value = db.query(func.sum(models.ExtensionOwnershipMapping.total_value)
                                         .label('total_value_sum')) \
            .filter(models.ExtensionOwnershipMapping.growing_area_id == input_growing_area_id,
                    models.ExtensionOwnershipMapping.crop_year == input_crop_year) \
            .group_by(models.ExtensionOwnershipMapping.growing_area_id,
                      models.ExtensionOwnershipMapping.crop_year).first()
        print("Final Extension Value:", final_extension_value[0])
        db.query(models.Ownership).filter(models.Ownership.growing_area_id == input_growing_area_id,
                                          models.Ownership.crop_year == input_crop_year) \
            .update({models.Ownership.extension: final_extension_value[0]}, synchronize_session=False)
        db.commit()
        update_ownership_extension_overlap(input_growing_area_id, input_crop_year, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/extension_mapping')
def update_extension_mapping(payload: schemas.ExtensionOwnershipPayload,
                             db: Session = Depends(get_db)): # pragma: no cover
    """
    Update extension mapping records and synchronize with plant matrix and ownership tables.
    
    This function processes a list of extension mapping updates:
    - For negative periods, marks records as INACTIVE and sets values to 0
    - For positive periods, creates new or updates existing extension records
    - Updates plant matrix based on the extension changes
    - Sets any records with period/week beyond the maximum to INACTIVE
    - Updates final extension values in the Ownership table
    
    Args:
        payload (ExtensionOwnershipPayload): Contains list of ExtensionData to update.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"
            - "message" (str): Confirmation message with the growing_area_id
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    update_extension = payload.ExtensionData
    input_growing_area_id = update_extension[0].growing_area_id
    input_crop_year = update_extension[0].crop_year
    try:
        max_period_week = max(item.period * 100 + item.week for item in update_extension)
        for item in update_extension:
            if item.period < 0:
                (db.query(models.ExtensionOwnershipMapping)
                 .filter(
                    models.ExtensionOwnershipMapping.growing_area_id == item.growing_area_id,
                    models.ExtensionOwnershipMapping.crop_year == item.crop_year)
                 .update({models.ExtensionOwnershipMapping.status: "INACTIVE",
                          models.ExtensionOwnershipMapping.total_value: 0,
                          models.ExtensionOwnershipMapping.split: "false"},
                         synchronize_session='fetch'))
                db.commit()
            else:
                print("--------positive input--------")
                record_to_check = db.query(models.ExtensionOwnershipMapping) \
                    .filter(models.ExtensionOwnershipMapping.extension_id == item.extension_id) \
                    .first()
                print(record_to_check)
                if record_to_check is not None:
                    db.query(models.ExtensionOwnershipMapping).filter(
                        models.ExtensionOwnershipMapping.extension_id == item.extension_id) \
                        .update({models.ExtensionOwnershipMapping.total_value: item.total_value,
                                 models.ExtensionOwnershipMapping.status: 'ACTIVE',
                                 models.ExtensionOwnershipMapping.split: item.split},
                                synchronize_session=False)
                else:  # pragma: no cover
                    payload = {
                        "extension_id": item.extension_id,
                        "growing_area_id": item.growing_area_id,
                        "crop_year": item.crop_year,
                        "crop_type": item.crop_type,
                        "period": item.period,
                        "week": item.week,
                        "total_value": item.total_value,
                        "split": item.split,
                        "year": item.year,
                        "status": "ACTIVE",
                        "updated_time": datetime.now()}
                    new_records = models.ExtensionOwnershipMapping(**payload)
                    db.add(new_records)
                db.commit()
            if (item.total_value!=0) or (item.total_value==0 and item.period>0):
                print('Front')
                update_plantmtrx(item.extension_id,item.growing_area_id,item.crop_type,item.crop_year, 
                         item.year, item.period, item.week,item.total_value,item.plant_distribution,db)
            elif item.period<0:
                print("Back")
                update_back_plantmtrx(item.growing_area_id,item.crop_year,db)
        # Setting status based on the maximum period and week combined value
        db.query(models.ExtensionOwnershipMapping) \
            .filter(models.ExtensionOwnershipMapping.growing_area_id == input_growing_area_id,
                    models.ExtensionOwnershipMapping.crop_year == input_crop_year,
                    models.ExtensionOwnershipMapping.period * 100 +
                    models.ExtensionOwnershipMapping.week > max_period_week) \
            .update({models.ExtensionOwnershipMapping.total_value: 0,
                     models.ExtensionOwnershipMapping.status: "INACTIVE",
                     models.ExtensionOwnershipMapping.split: "false"},
                    synchronize_session='fetch')
        db.commit()
        update_final_extension_value(input_growing_area_id, input_crop_year, db)
        return {"status": "success",
                "message": f"Extension updated Successfully for growing_area_id {input_growing_area_id}"}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def update_extension_plantmtrx(growing_area_id, year, period, week,
                               value, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update extension value when plant matrix value changes.
    
    This function finds an active extension record matching the provided parameters and updates
    its total_value. If the extension is not split, it sets the total_value directly. If it is
    split, it sets the total_value to the minimum of current and new values. Then it updates
    the final extension value in the Ownership table.
    
    Args:
        growing_area_id: The ID of the growing area.
        year (int): The year value.
        period (int): The period value.
        week (int): The week value.
        value: The new value to set for the extension.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        str: "No extension" if no matching extension record is found, "updated" if successful.
    """
    try:
        ext_record = db.query(models.ExtensionOwnershipMapping) \
            .filter(models.ExtensionOwnershipMapping.status == 'ACTIVE',
                    models.ExtensionOwnershipMapping.growing_area_id == growing_area_id,
                    models.ExtensionOwnershipMapping.year == year,
                    models.ExtensionOwnershipMapping.period == period,
                    models.ExtensionOwnershipMapping.week == week).first()
        if ext_record is None:
            print("No Extension Found")
            return "No extension"
        if ext_record.split == 'false':
            print("Split False")
            ext_record.total_value = value
        else:
            print("Test else")
            new_value = (db.query(func.sum(models.plantMtrx.value))
                           .filter(models.plantMtrx.growing_area_id == growing_area_id,
                                   models.plantMtrx.period == period,
                                   models.plantMtrx.week == week,
                                   models.plantMtrx.crop_year == ext_record.crop_year).scalar())
            print("New Value:", new_value)
            ext_record.total_value = new_value
        db.commit()
        update_final_extension_value(growing_area_id, ext_record.crop_year, db)
        return "updated"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def handling_inactive_plantmtrx_data(plantmtrx_id : str, db: Session = Depends(get_db)): # pragma: no cover
    try:
        inactive_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id).first()
        if inactive_rec:
            db.delete(inactive_rec)
            db.flush()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cleaning record {plantmtrx_id}: {str(e)}")
    
def update_plantmtrx(extension_id,growing_area_id,crop_type,crop_year, year, period,
                     week,value,plant_dist,db: Session = Depends(get_db)): # pragma: no cover
    """
    Update plant matrix records based on extension allocation.
    
    This function reverts existing extension records, then allocates the extension value across
    relevant plant matrix records. It handles two scenarios:
    - If crop_type is 'storage', queries fresh records with year+1
    - Otherwise, queries storage records with the provided year
    
    The allocation logic distributes the extension value across plant matrix rows sorted by
    highest value first, creating new records or splitting existing ones as needed.
    
    Args:
        extension_id: The extension ID being applied.
        growing_area_id: The ID of the growing area.
        crop_type (str): Type of crop ('storage' or 'fresh').
        crop_year: The crop year for the allocation.
        year (int): The year value.
        period (int): The period value.
        week (int): The week value.
        value: The total extension value to allocate.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        None. Updates plant matrix records directly.
    """

    #Reverting back the extensions
    try:
        extension_data = (db.query(models.ExtensionOwnershipMapping)
                            .filter(models.ExtensionOwnershipMapping.extension_id==extension_id,
                                    models.ExtensionOwnershipMapping.status=='active')
                            .all())

        print("Extension_Size",len(extension_data))

        for items in extension_data:
            print("calling revert")
            extension_update(items.extension_id,db)
            print("revert success")

        # Handling Manual entry
        if plant_dist is not None and len(plant_dist)>0:
            print("Manual Plant Distribution")
            print("plant_list",plant_dist)
            for plant in plant_dist:
                if plant['value'] ==0:
                    continue
                if value!=0:
                    if str(crop_type).lower() =="storage":
                        year_value = (int(year)+1)
                        plant_table = (db.query(models.plantMtrx)
                                    .filter(models.plantMtrx.growing_area_id==growing_area_id,
                                            models.plantMtrx.year==year_value,
                                            models.plantMtrx.period==period,
                                            models.plantMtrx.week==week,
                                            models.plantMtrx.crop_type=='fresh',
                                            models.plantMtrx.status=="active",
                                            models.plantMtrx.plant_id==plant['plant_id'])
                                    .order_by(models.plantMtrx.value.desc()).first())
                    else:
                        year_value = year
                        plant_table = (db.query(models.plantMtrx)
                                    .filter(models.plantMtrx.growing_area_id==growing_area_id,
                                            models.plantMtrx.year==year_value,
                                            models.plantMtrx.period==period,
                                            models.plantMtrx.week==week,
                                            models.plantMtrx.crop_type=='storage',
                                            models.plantMtrx.status=="active",
                                            models.plantMtrx.plant_id==plant['plant_id'])
                                    .order_by(models.plantMtrx.value.desc()).first())
                ext_value = plant['value']
                print("Input value", plant['value'])
                print("plant value", round(plant_table.value,0))
                if round(plant_table.value,0)>ext_value:
                    payload_1 = {"plant_matrix_id": plant_table.plant_matrix_id,
                                "region_id": plant_table.region_id, 
                                "plant_id": plant_table.plant_id,
                                "growing_area_id": plant_table.growing_area_id,
                                "period": plant_table.period, 
                                "week": plant_table.week,
                                "year": year_value,
                                "crop_type": plant_table.crop_type,
                                "crop_year": plant_table.crop_year,
                                "value": plant_table.value - ext_value,
                                "status": plant_table.status}
                    plantmtrx_id = str(plant_table.plant_id) + "#" + str(plant_table.region_id) + "#" + str(crop_year) + "#" + \
                                str(plant_table.period) + "#" + str(plant_table.week) + "#" + str(plant_table.growing_area_id)
                    payload_2 = {"plant_matrix_id": plantmtrx_id,
                                "region_id": plant_table.region_id, 
                                "plant_id": plant_table.plant_id,
                                "growing_area_id": plant_table.growing_area_id,
                                "period": plant_table.period, 
                                "week": plant_table.week,
                                "year": year_value, 
                                "crop_type": crop_type,
                                "crop_year": crop_year,
                                "value": ext_value,
                                "status": plant_table.status,
                                "type": "forecast"}    
                    newplantmtrx_record_1 = models.plantMtrx(**payload_1)
                    db.add(newplantmtrx_record_1)
                    existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id, models.plantMtrx.status=="active").first()
                    if not existing_rec:
                        handling_inactive_plantmtrx_data(plantmtrx_id, db)
                        newplantmtrx_record_2 = models.plantMtrx(**payload_2)
                        db.add(newplantmtrx_record_2) 
                    else:
                        new_value = ext_value+existing_rec.value
                        setattr(existing_rec,"value",new_value)
                    db.delete(plant_table)
                    db.commit()
                elif round(plant_table.value,0)==ext_value:
                    plantmtrx_id = str(plant_table.plant_id) + "#" + str(plant_table.region_id) + "#" + str(crop_year) + "#" + \
                                str(plant_table.period) + "#" + str(plant_table.week) + "#" + str(plant_table.growing_area_id)
                    existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id,
                                                                     models.plantMtrx.status=="active").first()
                    if not existing_rec:
                        handling_inactive_plantmtrx_data(plantmtrx_id, db)
                        setattr(plant_table,"plant_matrix_id",plantmtrx_id)
                        setattr(plant_table,"crop_type",crop_type)
                        setattr(plant_table,"crop_year",crop_year)
                        setattr(plant_table,"year",year_value)
                    else:
                        new_value = ext_value+existing_rec.value
                        setattr(existing_rec,"value",new_value)
                    db.commit()
                    
        # Handling Automatically    
        else:
            print("Automatic Plant Distribution")
            if value!=0:
                if str(crop_type).lower() =="storage":
                    year_value = (int(year)+1)
                    print("Storage extension")
                    plant_table = (db.query(models.plantMtrx)
                                .filter(models.plantMtrx.growing_area_id==growing_area_id,
                                        models.plantMtrx.year==year_value,
                                        models.plantMtrx.period==period,
                                        models.plantMtrx.week==week,
                                        models.plantMtrx.crop_type=='fresh',
                                        models.plantMtrx.status=="active")
                                .order_by(models.plantMtrx.value.desc()).all())
                else:
                    year_value = year
                    plant_table = (db.query(models.plantMtrx)
                                .filter(models.plantMtrx.growing_area_id==growing_area_id,
                                        models.plantMtrx.year==year_value,
                                        models.plantMtrx.period==period,
                                        models.plantMtrx.week==week,
                                        models.plantMtrx.crop_type=='storage',
                                        models.plantMtrx.status=="active")
                                .order_by(models.plantMtrx.value.desc()).all())

                ext_value = value
                print(len(plant_table))
                print("year",year_value)

                if len(plant_table)>0:
                    for items in plant_table:
                        if (items.value)>ext_value:
                            print("Plant Mtrx value",items.value)
                            print("Extension value",ext_value)
                            print("Entering if condition value greater than ext_value")
                            payload_1 = {"plant_matrix_id": items.plant_matrix_id,
                                        "region_id": items.region_id, 
                                        "plant_id": items.plant_id,
                                        "growing_area_id": items.growing_area_id,
                                        "period": items.period, 
                                        "week": items.week,
                                        "year": year_value,
                                        "crop_type": items.crop_type,
                                        "crop_year": items.crop_year,
                                        "value": items.value - ext_value,
                                        "status": items.status}
                            plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + str(crop_year) + "#" + \
                                        str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                            payload_2 = {"plant_matrix_id": plantmtrx_id,
                                        "region_id": items.region_id, 
                                        "plant_id": items.plant_id,
                                        "growing_area_id": items.growing_area_id,
                                        "period": items.period, 
                                        "week": items.week,
                                        "year": year_value, 
                                        "crop_type": crop_type,
                                        "crop_year": crop_year,
                                        "value": ext_value,
                                        "status": items.status,
                                        "type": "forecast"}    
                            newplantmtrx_record_1 = models.plantMtrx(**payload_1)
                            db.add(newplantmtrx_record_1)
                            existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id, models.plantMtrx.status=="active").first()
                            if not existing_rec:
                                handling_inactive_plantmtrx_data(plantmtrx_id, db)
                                newplantmtrx_record_2 = models.plantMtrx(**payload_2)
                                db.add(newplantmtrx_record_2) 
                            else:
                                new_value = ext_value+existing_rec.value
                                setattr(existing_rec,"value",new_value)
                            db.delete(items)
                            db.commit()
                            break
                        elif (items.value)==ext_value:
                            print("Entering elif condition values are same")
                            plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + str(crop_year) + "#" + \
                                        str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                            print("PlantMtrx_ID",plantmtrx_id)
                            existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id,
                                                                             models.plantMtrx.status=="active").first()
                            if not existing_rec:
                                handling_inactive_plantmtrx_data(plantmtrx_id, db)
                                print("PlantMtrx_ID",plantmtrx_id, "Crop_Year",crop_year, "Year",year_value, "Crop_Type",crop_type)
                                setattr(items,"plant_matrix_id",plantmtrx_id)
                                setattr(items,"crop_type",crop_type)
                                setattr(items,"crop_year",crop_year)
                                setattr(items,"year",year_value)
                            else:
                                new_value = ext_value+existing_rec.value
                                setattr(existing_rec,"value",new_value)
                            db.commit()
                            break
                        else:
                            plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + str(crop_year) + "#" + \
                                        str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                            existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id, models.plantMtrx.status=="active").first()
                            if not existing_rec:
                                handling_inactive_plantmtrx_data(plantmtrx_id, db)
                                setattr(items,"plant_matrix_id",plantmtrx_id)
                                setattr(items,"crop_type",crop_type)
                                setattr(items,"crop_year",crop_year)
                                setattr(items,"year",year_value)
                            else:
                                new_value = items.value+existing_rec.value
                                setattr(existing_rec,"value",new_value)
                            ext_value = ext_value - items.value
                            db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_back_plantmtrx(growing_area_id,crop_year,db: Session = Depends(get_db)): # pragma: no cover
    """
    Revert plant matrix records when extensions are deleted or deactivated.
    
    This function processes all extension records for a growing area and crop year and reverts
    the associated plant matrix changes. It determines whether each extension was for 'Fresh'
    or 'Storage' crop type based on the crop_year format and period/week values against the
    growing area's fresh and storage period boundaries. Records are consolidated with existing
    plant matrix entries where applicable.
    
    Args:
        growing_area_id: The ID of the growing area.
        crop_year: The crop year in format 'YYYY-YY' or numeric string.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        None. Updates plant matrix records directly.
    """

    try:
        extension_data = (db.query(models.ExtensionOwnershipMapping)
                            .filter(models.ExtensionOwnershipMapping.growing_area_id==growing_area_id,
                                    models.ExtensionOwnershipMapping.crop_year==crop_year)
                            .all())

        print("Extension_data_Length",len(extension_data))

        for items in extension_data:
            if str(items.crop_type).lower() =="storage":
                year_value = (int(items.year)+1)
            else:
                year_value = items.year

            plant_mtrx_table = (db.query(models.plantMtrx)
                            .filter(models.plantMtrx.growing_area_id==growing_area_id,
                                    models.plantMtrx.year==year_value,
                                    models.plantMtrx.period==items.period,
                                    models.plantMtrx.week==items.week,
                                    models.plantMtrx.crop_year==crop_year,
                                    models.plantMtrx.status=="active").all())

            ga = db.query(models.growing_area).filter(models.growing_area.growing_area_id==growing_area_id).first()
            upper_limit_fresh = ((int(ga.fresh_period_end)*5) + (ga.fresh_week_end))
            upper_limit_storage = ((int(ga.storage_period_end)*5) + (ga.storage_week_end))
            lower_limit_storage = ((int(ga.storage_period_start)*5) + (ga.storage_week_start))
            period_week_value = ((int(items.period)*5) + (items.week))
            condition = True
            c_type = ""
            if len(crop_year)>4:
                c_type = "Fresh"
                print(c_type)
                if (period_week_value> upper_limit_storage) and (period_week_value<=upper_limit_fresh):
                    condition = True
                else:
                    condition = False
            else:
                c_type = "Storage"
                print(c_type)
                if (period_week_value>=lower_limit_storage) or (period_week_value<=upper_limit_storage):
                    condition = True
                else:
                    condition = False

            if condition:
                if c_type=="Fresh":
                    print('fresh')
                    for items in plant_mtrx_table:
                        plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + str("20"+str(crop_year)[-2:]) + "#" + \
                                        str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                        print("Plantmtrx_id", plantmtrx_id)
                        print("crop_year",str("20"+str(crop_year)[-2:]))
                        existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id, models.plantMtrx.status=="active").first()
                        if not existing_rec:
                            handling_inactive_plantmtrx_data(plantmtrx_id, db)
                            setattr(items,"crop_type","Fresh")
                            setattr(items,"plant_matrix_id",plantmtrx_id)
                            setattr(items,"crop_year",str("20"+str(crop_year)[-2:]))
                        else:
                            print("Existing record found for PlantMtrx_ID", plantmtrx_id, "Adding values")
                            new_value = items.value+existing_rec.value
                            setattr(existing_rec,"value",new_value)
                            db.delete(items)
                        db.commit()
                elif c_type=="Storage":
                    print('storage')
                    try:
                        cy = str(int(crop_year))+"-"+str(int(crop_year[-2:])+1)
                    except Exception:
                        cy = str("20"+str(crop_year)[-2:])      
                    print(cy)
                    for items in plant_mtrx_table:
                        plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + cy + "#" + \
                                    str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                        existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id, models.plantMtrx.status=="active").first()
                        if not existing_rec:
                            handling_inactive_plantmtrx_data(plantmtrx_id, db)
                            setattr(items,"crop_type","Storage")
                            setattr(items,"crop_year",cy)
                            setattr(items,"plant_matrix_id",plantmtrx_id)
                        else:
                            print("Existing record found for PlantMtrx_ID", plantmtrx_id, "Adding values")
                            new_value = items.value+existing_rec.value
                            setattr(existing_rec,"value",new_value)
                            db.delete(items)
                        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
                
def extension_update(id,db: Session = Depends(get_db)): # pragma: no cover
    """
    Revert plant matrix records for a specific extension when it is updated.
    
    This function finds all extension records with the given extension_id and reverts their
    impact on the plant matrix. It determines crop type (Fresh or Storage) based on the
    crop_year format and period/week values against the growing area boundaries. Plant matrix
    records are consolidated with existing entries or deleted as appropriate.
    
    Args:
        id: The extension ID to revert.
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        None. Updates plant matrix records directly.
    """
    try:
        extension_records = (db.query(models.ExtensionOwnershipMapping)
                            .filter(models.ExtensionOwnershipMapping.extension_id==id)
                            .all())

        for items in extension_records:
            if str(items.crop_type).lower() =="storage":
                year_val = (int(items.year)+1)
            else:
                year_val = items.year

            plant_mtrx_table = (db.query(models.plantMtrx)
                            .filter(models.plantMtrx.growing_area_id==items.growing_area_id,
                                    models.plantMtrx.year==year_val,
                                    models.plantMtrx.period==items.period,
                                    models.plantMtrx.week==items.week,
                                    models.plantMtrx.crop_year==items.crop_year,
                                    models.plantMtrx.status=="active").all())

            ga = db.query(models.growing_area).filter(models.growing_area.growing_area_id==items.growing_area_id).first()
            ul_fresh = ((int(ga.fresh_period_end)*5) + (ga.fresh_week_end))
            ul_storage = ((int(ga.storage_period_end)*5) + (ga.storage_week_end))
            ll_storage = ((int(ga.storage_period_start)*5) + (ga.storage_week_start))
            pw_value = ((int(items.period)*5) + (items.week))
            cond = True
            c_type = ""
            if len(items.crop_year)>4:
                c_type = "Fresh"
                if (pw_value>ul_storage) and (pw_value<=ul_fresh):
                    cond = True
                else:
                    cond = False
            else:
                c_type = "Storage"
                if (pw_value>=ll_storage) or (pw_value<=ul_storage):
                    cond = True
                else:
                    cond = False

            if cond:
                if c_type=="Fresh":
                    for items in plant_mtrx_table:
                        plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + str("20"+str(items.crop_year)[-2:]) + "#" + \
                                        str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                        print(plantmtrx_id)
                        print("crop_year",str("20"+str(items.crop_year)[-2:]))
                        existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id,models.plantMtrx.status=="active").first()
                        if not existing_rec:
                            handling_inactive_plantmtrx_data(plantmtrx_id, db)
                            setattr(items,"crop_type","Fresh")
                            setattr(items,"plant_matrix_id",plantmtrx_id)
                            setattr(items,"crop_year",str("20"+str(items.crop_year)[-2:]))
                            print("if condition: no old records")
                        else:
                            new_value = items.value+existing_rec.value
                            setattr(existing_rec,"value",new_value)
                            db.delete(items)
                            print("else condition: yes old records")
                        db.commit()
                elif c_type=="Storage":
                    try:
                        crop_year = str(int(items.crop_year))+"-"+str(int(items.crop_year[-2:])+1)
                    except Exception:
                        crop_year = str("20"+str(items.crop_year)[-2:])      
                    for items in plant_mtrx_table:
                        plantmtrx_id = str(items.plant_id) + "#" + str(items.region_id) + "#" + crop_year + "#" + \
                                    str(items.period) + "#" + str(items.week) + "#" + str(items.growing_area_id)
                        existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id,models.plantMtrx.status=="active").first()
                        if not existing_rec:
                            handling_inactive_plantmtrx_data(plantmtrx_id, db)
                            setattr(items,"crop_type","Storage")
                            setattr(items,"crop_year",crop_year)
                            setattr(items,"plant_matrix_id",plantmtrx_id)
                            print("if condition: no old records")
                        else:
                            new_value = items.value+existing_rec.value
                            setattr(existing_rec,"value",new_value)
                            print("else condition: yes old records")
                            db.delete(items)
                        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/delete_all_extension_mapping')
def delete_extension_mapping(payload: schemas.ExtensionMappingDeleteSchema,
                             db: Session = Depends(get_db)): # pragma: no cover
    """
    Delete all active extension mappings for specified regions, year, and crop year.
    
    This function retrieves growing area IDs for the specified region(s), then identifies
    all active extension records matching the year, crop_year, and growing areas. Each
    matching extension is converted to a deletion payload (period = -1) and processed through
    update_extension_mapping to properly revert associated plant matrix changes.
    
    Args:
        payload (ExtensionMappingDeleteSchema): Contains:
            - year (int): The year to filter by
            - crop_year (str): The crop year to filter by
            - region (str): Region name ('US', 'All data', or specific region) to delete extensions for
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "status" (str): "success"
            - "message" (str): Confirmation message with year, crop_year, and region details
    
    Raises:
        HTTPException: Status 400 with exception details if an error occurs.
    """
    try:
        data_to_delete = []
        year = payload.year
        crop_year = payload.crop_year
        region = payload.region

        #Retreiving the region ids based on the region name
        region_ids_list = []
        if region=='All data' or region=='US':
            region_map ={'US':['East - US','Central - US','West - US'],
                     'All data' : ['East - US','Central - US','West - US','Canada']}
            region_ids = db.query(models.region.region_id).filter(models.region.region_name.in_(region_map[region])).all()
            region_ids_list.extend([r.region_id for r in region_ids])
        else:
            region_ids = db.query(models.region.region_id).filter(models.region.region_name==region).all()
            region_ids_list.extend([r.region_id for r in region_ids])

        print("Region IDs List:", region_ids_list)

        #Fetching growing area ids based on region ids
        growing_area_ids = db.query(models.growing_area.growing_area_id).filter(models.growing_area.region.in_(region_ids_list)).all()
        growing_area_ids_list = [g.growing_area_id for g in growing_area_ids]

        print(f"Growing area IDs:  {growing_area_ids_list}")

        #Deleting the extension mappings based on the filters
        records_to_delete = db.query(models.ExtensionOwnershipMapping) \
            .filter(
                    models.ExtensionOwnershipMapping.crop_year == crop_year,
                    models.ExtensionOwnershipMapping.growing_area_id.in_(growing_area_ids_list),
                    models.ExtensionOwnershipMapping.status == 'ACTIVE').all()
        
        print(f"Records size: {len(records_to_delete)}")
        if len(records_to_delete)> 0:
            for record in records_to_delete:
                payload = {
                    "extension_id": record.extension_id,
                    "growing_area_id": record.growing_area_id,
                    "crop_year": record.crop_year,
                    "crop_type": record.crop_type,
                    "period": -1,
                    "week": 0,
                    "total_value": 0,
                    "split": record.split,
                    "year": record.year
                    }
                print(payload)
                data_to_delete.append(payload)
                payload_object = schemas.ExtensionOwnershipPayload(ExtensionData=data_to_delete)
                update_extension_mapping(payload_object, db)
                data_to_delete = []
            return {'status': 'success',
                    'message': f'Extension mappings deleted successfully for year {year}, crop_year {crop_year}, region {region}'}
        else:
            return {'status': 'success',
                    'message': f'No active extension mappings found for year {year}, crop_year {crop_year}, region {region}'}    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/multi_plant_extension_selection')
def multi_plant_extension_selection(payload: schemas.ExtensionMappingMultiPlantSchema, db: Session = Depends(get_db)): # pragma: no cover
    try:
        print("Fetching extension records")
        extension_records = (db.query(models.ExtensionOwnershipMapping)
                             .filter(models.ExtensionOwnershipMapping.extension_id == payload.extension_id)
                             .first())
        print("Processing plant matrix records")
        db_data = []
        df_db = pd.DataFrame(db_data)
        final_in_memory_results = []
        if extension_records:
            print("Assigning year value based on crop type")
            if str(extension_records.crop_type).lower() == "storage":
                year_val = (int(extension_records.year) + 1)
            else:
                year_val = extension_records.year
            print("Fetching raw plant matrix data")
            print("Calculated Crop Year:", extension_records.crop_year, "Year Value:", year_val, "Growing Area ID:", extension_records.growing_area_id, "Period:", extension_records.period, "Week:", extension_records.week)
            old_extension_value = (db.query(models.plantMtrx).filter(models.plantMtrx.growing_area_id == payload.growing_area_id,
                                                                     models.plantMtrx.period == payload.period,
                                                                     models.plantMtrx.week == payload.week,
                                                                     models.plantMtrx.crop_type == payload.crop_type,
                                                                     models.plantMtrx.year == year_val,
                                                                     models.plantMtrx.status == "active").all())
            
            db_data = []
            if old_extension_value:
                for item in old_extension_value:
                    db_data.append({
                        'plant_id': item.plant_id,
                        'year': item.year,
                        'period': item.period,
                        'week': item.week,
                        'old_ext_value': item.value
                    })

            df_db = pd.DataFrame(db_data)
            print("Old Extension Value:", old_extension_value)

            raw_plant_mtrx = (db.query(models.plantMtrx)
                              .filter(models.plantMtrx.growing_area_id == extension_records.growing_area_id,
                                      models.plantMtrx.year == year_val,
                                      models.plantMtrx.period == extension_records.period,
                                      models.plantMtrx.week == extension_records.week,
                                      models.plantMtrx.crop_year == extension_records.crop_year,
                                      models.plantMtrx.status == "active").all())
            plant_mtrx_variable = []
            print(len(raw_plant_mtrx))
            for row in raw_plant_mtrx:
                row_dict = row.__dict__.copy()
                row_dict.pop('_sa_instance_state', None)
                plant_mtrx_variable.append(row_dict)
            print("Plant Matrix", plant_mtrx_variable)
            print("Determining crop type and filtering plant matrix records")
            ga = db.query(models.growing_area).filter(
                models.growing_area.growing_area_id == extension_records.growing_area_id).first()
            ul_fresh = ((int(ga.fresh_period_end) * 5) + (ga.fresh_week_end))
            ul_storage = ((int(ga.storage_period_end) * 5) + (ga.storage_week_end))
            ll_storage = ((int(ga.storage_period_start) * 5) + (ga.storage_week_start))
            pw_value = ((int(extension_records.period) * 5) + (extension_records.week))
            cond = True
            c_type = ""
            print("Evaluating crop year format")
            if len(extension_records.crop_year) > 4:
                c_type = "Fresh"
                if (pw_value > ul_storage) and (pw_value <= ul_fresh):
                    cond = True
                else:
                    cond = False
            else:
                c_type = "Storage"
                if (pw_value >= ll_storage) or (pw_value <= ul_storage):
                    cond = True
                else:
                    cond = False
            print("Processing plant matrix records based on crop type condition")
            if cond:
                print("Entering condition to process plant matrix records\n\n\n")
                for plant_row in plant_mtrx_variable[:]:
                    calculated_crop_year = ""
                    if c_type == "Fresh":
                        calculated_crop_year = str("20" + str(plant_row['crop_year'])[-2:])
                    elif c_type == "Storage":
                        try:
                            calculated_crop_year = str(int(plant_row['crop_year'])) + "-" + str(int(plant_row['crop_year'][-2:]) + 1)
                        except Exception:
                            calculated_crop_year = str("20" + str(plant_row['crop_year'])[-2:])
                    plantmtrx_id = str(plant_row['plant_id']) + "#" + str(plant_row['region_id']) + "#" + \
                                   calculated_crop_year + "#" + str(plant_row['period']) + "#" + \
                                   str(plant_row['week']) + "#" + str(plant_row['growing_area_id'])
                    print("Generated Plant Matrix ID:", plantmtrx_id)
                    existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id == plantmtrx_id).first()
                    if existing_rec:
                        plant_row['crop_type'] = c_type
                        plant_row['plant_matrix_id'] = plantmtrx_id
                        plant_row['crop_year'] = calculated_crop_year
                        final_in_memory_results.append(plant_row)
                    else:
                        plant_row['crop_type'] = c_type
                        plant_row['crop_year'] = calculated_crop_year
                        final_in_memory_results.append(plant_row)
            print("Filtering final results based on payload criteria")

        print("Step 1:", final_in_memory_results)
        # Fetching the actual records
        if str(payload.crop_type).lower() == "storage":
            year_val = (int(payload.year) + 1)
            calculated_crop_year = str("20" + str(payload.crop_year)[-2:])
        elif str(payload.crop_type).lower() == "fresh":
            try:
                calculated_crop_year = str(int(payload.crop_year)) + "-" + str(int(payload.crop_year[-2:]) + 1)
                year_val = (int(payload.year))
            except Exception:
                calculated_crop_year = str("20" + str(payload.crop_year)[-2:])
                year_val = (int(payload.year))
        print("Calculated Crop Year:", calculated_crop_year, "Year Value:", year_val, "Growing Area ID:", payload.growing_area_id, "Period:", payload.period, "Week:", payload.week)
        plant_mtrx_data  = (db.query(models.plantMtrx)
                          .filter(models.plantMtrx.growing_area_id == payload.growing_area_id,
                                  models.plantMtrx.year == year_val,
                                  models.plantMtrx.period == payload.period,
                                  models.plantMtrx.week == payload.week,
                                  models.plantMtrx.crop_year == calculated_crop_year,
                                  models.plantMtrx.status == "active").all())
        plant_mtrx_variable = []
        for row in plant_mtrx_data:
            row_dict = row.__dict__.copy()
            row_dict.pop('_sa_instance_state', None)
            plant_mtrx_variable.append(row_dict)

        print("Plant Matrix Data length", len(plant_mtrx_variable))
        print("plant_mtrx_variable", plant_mtrx_variable)
        for plant_row in plant_mtrx_variable:
            final_in_memory_results.append(plant_row)

        print("Step 2:", final_in_memory_results)
        

        # Fetch the records
        all_plants = db.query(models.Plant.plant_id, models.Plant.plant_name).all()
        plant_name_map = {p.plant_id: p.plant_name for p in all_plants}
        if not final_in_memory_results:
            return {'status': 'success', 'data': []}
        df = pd.DataFrame(final_in_memory_results)
        df['value'] = df.groupby('plant_matrix_id')['value'].transform('sum')
        df = df.drop_duplicates(subset=['plant_matrix_id'], keep='first').reset_index(drop=True)
        if str(payload.crop_type).lower() =="storage":
            year_value = (int(payload.year)+1)
            condition = ((df['growing_area_id'] == payload.growing_area_id) &
                         (df['period'] == payload.period) &
                         (df['week'] == payload.week) &
                         (df['crop_type'].str.lower() == "fresh") &
                         (df['year'].astype(str) == str(year_value)) &
                         (df['status'].str.lower() == "active"))
        else:
            year_value = payload.year
            condition = ((df['growing_area_id'] == payload.growing_area_id) &
                         (df['period'] == payload.period) &
                         (df['week'] == payload.week) &
                         (df['crop_type'].str.lower() == "storage") &
                         (df['year'].astype(str) == str(year_value)) &
                         (df['status'].str.lower() == "active"))         

        filtered_df = df[condition].copy()
        print("Filtered DF" , filtered_df)
        filtered_df['plant_name'] = filtered_df['plant_id'].map(plant_name_map).fillna("Unknown Plant")
        print("len(filtered_df)", len(filtered_df))
        filtered_df = filtered_df.sort_values(by='value', ascending=False)
        print(filtered_df)
        if not df_db.empty:
            filtered_df = pd.merge(filtered_df, df_db, on=['plant_id', 'year', 'period', 'week'], how='left')
        else:
            filtered_df['old_ext_value'] = np.nan
        filtered_df['old_ext_value'] = filtered_df['old_ext_value'].replace({np.nan: 0})
        result_columns = ["plant_name", "plant_id", "period", "week", "crop_type", "crop_year", "value", "old_ext_value"]
        final_data = filtered_df[result_columns].to_dict(orient='records') if not filtered_df.empty else []
        print(final_data)
        return {'status': 'success', 'data': final_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))