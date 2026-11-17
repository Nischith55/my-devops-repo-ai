from datetime import date,datetime,timezone
from fastapi import Depends, HTTPException, status, APIRouter,File, UploadFile
import pandas as pd
from io import StringIO,BytesIO
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from potatorates import create_potato_rate_in_db, update_potato_rates_default
from solidrates import create_solid_rate_in_db, update_solids_rates_default
from freightcost import create_freight_rates_in_db,update_freight_cost_mapping_with_default_value,update_freight_rates_with_default_value
from plant_mtrx import func_getcrop_type

router = APIRouter()
var_not_appl = "Not Appl"
var_not_appl_ = "Not Appl."
var_format = "%Y-%m-%d %H:%M:%S.%f"

@router.get('/get_mapping')
def get_mapping(db: Session = Depends(get_db)): # pragma: no cover
    """
    Fetch master data required for plant/grower screens.

    Args:
        db (Session): Database session.

    Returns:
        dict: Region list, crop categories, company names, vendor sites, 
            growing areas, and growing area with description.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        region = db.query(models.region.region_name,models.region.region_id) \
                .filter(models.region.status == "ACTIVE").all()
        crop_category = db.query(models.category.category_name,models.category.crop_category) \
                .filter(models.category.status == "ACTIVE").all()
        company_name = db.query(models.Plant.company_name).distinct().all()
        vendor_site_code = db.query(models.vendor_site_code.VENDOR_SITE_CODE,models.vendor_site_code.VENDOR_SITE_ID) \
                .filter(models.vendor_site_code.status == "ACTIVE").distinct().all()
        growing_area = db.query(models.growing_area.growing_area_name,models.growing_area.growing_area_id) \
                .filter(models.growing_area.status=="ACTIVE").distinct().all()

        growing_area_desc = db.query(func.concat(models.growing_area.growing_area_name, ' | ', \
                                                models.growing_area.growing_area_desc).label('growing_area'), \
                                                models.growing_area.growing_area_id) \
                                                .filter(models.growing_area.status=="ACTIVE").distinct().all()

        return {"region": region, "crop_category":crop_category, "company_name":company_name, "vendor_site":vendor_site_code,"growing_area":growing_area,"gr_area_desc":growing_area_desc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_plant', status_code=status.HTTP_201_CREATED)
def add_new_plant(payload: schemas.PlantSchemaDummy, db: Session = Depends(get_db)): # pragma: no cover
    """
    Add a new plant and its basic master details.

    Args:
        payload (PlantSchemaDummy): Plant details from the request body.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success or if plant already exists.

    Raises:
        HTTPException: If insert fails.
    """
    try:
        plant_name = payload.plant_name
        plant_count = db.query(models.Plant).filter(models.Plant.plant_name == plant_name).count()
        if plant_count>0:
            return {"status":"plant already exists"}
        current_time = datetime.now(timezone.utc).strftime(var_format)[:-3]
        print(payload.dict())
        new_plant = models.Plant(
            **payload.dict(),
            created_time=current_time,
            updated_time=current_time,
            created_by="SYSTEM",
            updated_by="SYSTEM",
            status="ACTIVE"
        )
        db.add(new_plant)
        db.commit()
        db.refresh(new_plant)
        return {"status":"New Plant added successfully", "plant_id": new_plant.plant_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/add_grower', status_code=status.HTTP_201_CREATED)
def add_new_plant(payload: schemas.GrowersDummy, db: Session = Depends(get_db)): # pragma: no cover
    """
    Add a new grower and its master details.

    Args:
        payload (GrowersDummy): Grower details from the request body.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success or if grower already exists.

    Raises:
        HTTPException: If insert fails.
    """
    try:
        grower_name = payload.grower_name
        grower_count = db.query(models.growers).filter(models.growers.grower_name == grower_name).count()
        if grower_count>0:
            return {"status":"grower already exists"}
        current_time = datetime.now(timezone.utc).strftime(var_format)[:-3]
        print(payload.dict())
        new_grower = models.growers(
            **payload.dict(),
            created_time=current_time,
            updated_time=current_time,
            created_by="SYSTEM",
            updated_by="JP"
        )
        db.add(new_grower)
        db.commit()
        db.refresh(new_grower)
        return {"status":"New grower added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post('/add_vendor_site', status_code=status.HTTP_201_CREATED)
def add_vendor_site(payload: schemas.VendorSiteCodeSchemaMasters, db: Session = Depends(get_db)): # pragma: no cover
    """
    Add a new vendor site and its master details.

    Args:
        payload (VendorSiteCodeSchemaMasters): Vendor site details from the request body.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success or if vendor site already exists.

    Raises:
        HTTPException: If insert fails.
    """
    try:
        vendor_site_code = payload.VENDOR_SITE_CODE
        vsc_count = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_CODE == vendor_site_code).count()
        if vsc_count>0:
            return {"status":"Vendor Site already exists"}
        current_time = datetime.now(timezone.utc).strftime(var_format)[:-3]
        print(payload.dict())
        new_vsc = models.vendor_site_code(
            **payload.dict(),
            created_time=current_time,
            updated_time=current_time,
            created_by="SYSTEM",
            updated_by="JP",
            status = "ACTIVE"
        )
        db.add(new_vsc)
        db.commit()
        db.refresh(new_vsc)
        return {"status":"New vendor site added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_growing_area', status_code=status.HTTP_201_CREATED)
def add_growing_area(payload: schemas.GrowingAreaSchemaMasters, db: Session = Depends(get_db)): # pragma: no cover
    """
    Add a new growing area and initialize default potato and solids rates.

    Args:
        payload (GrowingAreaSchemaMasters): Growing area details.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If master or rate inserts fail.
    """
    try:
        growing_area_name = payload.growing_area_name
        ga_count = db.query(models.growing_area).filter(models.growing_area.growing_area_name == growing_area_name).count()
        if ga_count>0:
            return {"status":"growing area already exists"}
        current_time = datetime.now(timezone.utc).strftime(var_format)[:-3]
        new_ga = models.growing_area(
            **payload.dict(),
            created_time=current_time,
            updated_time=current_time,
            created_by="SYSTEM",
            updated_by="JP",
            status="ACTIVE"
        )
        db.add(new_ga)
        db.commit()
        db.refresh(new_ga)
        growing_area_id = new_ga.growing_area_id
        potato_rate_payload = { "year":datetime.now(timezone.utc).year,
                                "growing_area_id_old":999,
                                "created_time":current_time,
                                "created_by":"System",
                                "updated_time":current_time,
                                "updated_by":"SYSTEM",
                                "currency":"USD",
                                "growing_area_id":growing_area_id}
        potato_rates_record = create_potato_rate_in_db(potato_rate_payload, db)
        potato_rate_id = potato_rates_record.potato_rate_id
        ## Solids Rates
        solids_rate_payload = { "growing_area_id_old":999,
                                "created_time":current_time,
                                "created_by":"System",
                                "updated_time":current_time,
                                "updated_by":"SYSTEM",
                                "currency":"USD",
                                "growing_area_id":growing_area_id}
        solid_rate_record = create_solid_rate_in_db(solids_rate_payload, db)
        solids_rate_id = solid_rate_record.solids_rate_id
        ## Potato mappings
        update_potato_rates_default(db,potato_rate_id,datetime.now(timezone.utc).year)
        ## Solids mappings
        update_solids_rates_default(db, solids_rate_id, datetime.now(timezone.utc).year)
        db.commit()
        return {"status":"New growing area added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get_plants')
def get_plants(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all active plants.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of active plant records under 'plants'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_plants = (db.query(models.Plant.plant_id,
                               models.Plant.company_name,
                               func.trim(models.Plant.created_by).label("created_by"),
                               func.trim(models.Plant.status).label("status"),
                               func.trim(models.Plant.updated_by).label("updated_by"),
                               models.Plant.created_time,
                               models.Plant.pgt_plant_name,
                               models.Plant.plant_code,
                               models.Plant.plant_name,
                               models.Plant.region_id,
                               models.Plant.crop_category_id,
                               models.Plant.updated_time).filter(models.Plant.status=="ACTIVE").order_by(models.Plant.updated_time,models.Plant.plant_id).distinct().all())
        return {"plants":all_plants}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_plant/{plant_name}')
def get_plant(plant_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Fetch a plant's details along with its vendor-site-growing area mappings.

    Args:
        plant_name (str): Name of the plant.
        db (Session): Database session.

    Returns:
        dict: Plant detail and mapping list under 'details'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        plant_details = (db.query(models.Plant.plant_id,
                               models.Plant.company_name,
                               func.trim(models.Plant.created_by).label("created_by"),
                               func.trim(models.Plant.status).label("status"),
                               func.trim(models.Plant.updated_by).label("updated_by"),
                               models.Plant.created_time,
                               models.Plant.pgt_plant_name,
                               models.Plant.plant_code,
                               models.Plant.plant_name,
                               models.Plant.region_id,
                               models.Plant.crop_category_id,
                               models.Plant.updated_time).filter(models.Plant.plant_name == plant_name,models.Plant.status=="ACTIVE").first())
        vsc_ga = db.query(models.PlantSiteGrowingAreaMapping.growing_area,models.PlantSiteGrowingAreaMapping.Vendor_Site_Code,
                        models.PlantSiteGrowingAreaMapping.growing_area_id,
                        models.PlantSiteGrowingAreaMapping.vendor_site_id).filter(models.PlantSiteGrowingAreaMapping.plant_name==plant_name).all()
        empty_json =  [{
            "growing_area": var_not_appl,
            "Vendor_Site_Code": var_not_appl,
            "growing_area_id": 000,
            "vendor_site_id": 000
            }]
        combined_result = {
            "plant_detail": plant_details if plant_details else ["No plant detail found"],
            "vsc_ga": vsc_ga if vsc_ga else empty_json}
        return {"details":combined_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/modify_ex_plant')
def modify_ex_plant(payload: schemas.EditPSGAMastersSchema,db:Session = Depends(get_db)):  # pragma: no cover
    """
    Replace existing plant-site-growing area mappings and ensure freight cost defaults.

    Args:
        payload (EditPSGAMastersSchema): New PSGA mappings and plant information.
        db (Session): Database session.

    Returns:
        dict: Status message indicating update result.

    Raises:
        HTTPException: If mapping or freight cost operations fail.
    """
    try:
        plant_name = payload.plant_name
        plant_id = payload.plant_id
        flag=False
        existing_record = db.query(models.PlantSiteGrowingAreaMapping)\
                                .filter(models.PlantSiteGrowingAreaMapping.plant_name==plant_name).all()
        current_time = datetime.now(timezone.utc).strftime(var_format)[:-3]
        seen_combinations = set()
        for ex in existing_record:
            db.delete(ex)

        for ga, vsc, ga_id, vs_id in zip(payload.growing_area, payload.vsc, payload.ga_id, payload.vs_id):
            unique_combination = (payload.plant_name, vsc, ga)
            if unique_combination in seen_combinations:
                continue

            seen_combinations.add(unique_combination)
            new_mapping = models.PlantSiteGrowingAreaMapping(
                plant_name=payload.plant_name,
                growing_area=ga,
                Vendor_Site_Code=vsc,
                growing_area_id=ga_id,
                vendor_site_id=vs_id,
                plant_id=plant_id
            )
            db.add(new_mapping)
            flag=True

            freight_cost_exists = db.query(models.FreightCostRate).filter(
                models.FreightCostRate.plant_id == plant_id,
                models.FreightCostRate.growing_area_id == ga_id,
                models.FreightCostRate.vendor_site_id == vs_id
            ).first()
            
            if not freight_cost_exists:
                freight_cost_id = db.query(func.max(models.FreightCostRate.freight_cost_id)).scalar() or 0
                freight_cost_id += 1
                freight_cost_rate_payload = {"freight_cost_id":freight_cost_id,
                                            "plant_id":plant_id,
                                            "vendor_site_id":vs_id,
                                            "comment": "comment",
                                            "created_time":current_time,
                                            "created_by":"System",
                                            "updated_time":current_time,
                                            "updated_by":"SYSTEM",
                                            "currency":"USD",
                                            "growing_area_id":ga_id,
                                            "miles":0}
                create_freight_rates_in_db(freight_cost_rate_payload, db)

                ## Freight Cost mappings
                update_freight_rates_with_default_value(freight_cost_id,datetime.now(timezone.utc).year,db)
        db.commit()
        if flag:
            db.refresh(new_mapping)
        return {"status":"Updated the mapping successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_plant/{plant_id}', status_code=status.HTTP_200_OK)
def update_plant(plant_id: int, update_payload: schemas.UpdatePlantSchema, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update an existing plant with the provided fields.

    Args:
        plant_id (int): ID of the plant to update.
        update_payload (UpdatePlantSchema): Fields to update.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If plant not found or update fails.
    """
    try:
        # Fetch the existing region
        plant_to_update = db.query(models.Plant).filter(models.Plant.plant_id == plant_id).first()
        
        if not plant_to_update:
            raise HTTPException(status_code=404, detail="Plant not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plant_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            plant_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "plant updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/update_grower/{grower_id}', status_code=status.HTTP_200_OK)
def update_grower(grower_id: int, update_payload: schemas.GrowersDummy, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update an existing grower with the provided fields.

    Args:
        grower_id (int): ID of the grower to update.
        update_payload (GrowersDummy): Fields to update.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If grower not found or update fails.
    """
    try:
        # Fetch the existing region
        grower_to_update = db.query(models.growers).filter(models.growers.grower_id == grower_id).first()
        
        if not grower_to_update:
            raise HTTPException(status_code=404, detail="Grower not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(grower_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            grower_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "grower updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_plantmtrx_next_year_crop_type(growing_area_id,db):# pragma: no cover
    """
    Update next year's plant matrix crop_type for a given growing area.

    Args:
        growing_area_id (int): Growing area identifier.
        db (Session): Database session.

    Returns:
        dict | None: Status message if updates were applied, otherwise None.

    Raises:
        HTTPException: If query or update fails.
    """
    try:
        today_date = date.today()
        year = int(today_date.year)+1
        plant_mtrx = db.query(models.plantMtrx).filter(models.plantMtrx.year==year,
                                                             models.plantMtrx.growing_area_id == growing_area_id)
        if plant_mtrx:
            for record in plant_mtrx:
                crop_type, _ = func_getcrop_type(record.period, record.week, 
                                                        year,growing_area_id, db)
                setattr(record,"crop_type",crop_type)
            db.commit()
            return {"status": "Plant matrix updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_growing_area/{growing_area_id}', status_code=status.HTTP_200_OK)
def update_growing_area(growing_area_id: int, update_payload: schemas.UpdateGrowingAreaSchema, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update an existing growing area and refresh next year's plant matrix crop type.

    Args:
        growing_area_id (int): ID of the growing area.
        update_payload (UpdateGrowingAreaSchema): Fields to update.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If growing area not found or update fails.
    """
    try:
        # Fetch the existing region
        ga_to_update = db.query(models.growing_area).filter(models.growing_area.growing_area_id == growing_area_id).first()
        
        if not ga_to_update:
            raise HTTPException(status_code=404, detail="Growing Area not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ga_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            ga_to_update.updated_time = datetime.now()

        db.commit()
        
        #Updating the next year plant matrix table to fecth the crop type based on this change
        update_plantmtrx_next_year_crop_type(growing_area_id,db)

        return {"status": "Growing Area updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_vendor_site/{vendor_site_id}', status_code=status.HTTP_200_OK)
def update_vendor_site(vendor_site_id: int, update_payload: schemas.UpdateVendorSiteCodeSchema, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update an existing vendor site.

    Args:
        vendor_site_id (int): ID of the vendor site.
        update_payload (UpdateVendorSiteCodeSchema): Fields to update.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If vendor site not found or update fails.
    """
    try:
        # Fetch the existing region
        vsc_to_update = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_ID == vendor_site_id).first()
        
        if not vsc_to_update:
            raise HTTPException(status_code=404, detail="vendor site not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vsc_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            vsc_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "Vendor Site updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_growers')
def get_growers(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all active growers.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of active growers under 'growers'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_growers = (db.query(models.growers.grower_name, 
                               func.trim(models.growers.owner).label("owner"), 
                               func.trim(models.growers.country).label("country"), 
                               func.trim(models.growers.volume).label("volume"), 
                               func.trim(models.growers.status).label("status"),
                               models.growers.updated_by,
                               models.growers.updated_time,
                               models.growers.pgt_grower_name,
                               models.growers.region,
                               models.growers.grower_id,
                               models.growers.created_by,
                               models.growers.created_time,
                               models.growers.grower_abbreviation_code)
                               .filter(models.growers.status=="ACTIVE").order_by(models.growers.updated_time,models.growers.grower_id).distinct().all())
        return {"growers":all_growers}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_grower/{grower_name}')
def get_grower(grower_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Fetch a grower's master details and their growing area mappings.

    Args:
        grower_name (str): Name of the grower.
        db (Session): Database session.

    Returns:
        dict: Grower details and mapping list.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        grower_details = (db.query(models.growers.grower_name, 
                               func.trim(models.growers.owner).label("owner"), 
                               func.trim(models.growers.country).label("country"), 
                               func.trim(models.growers.volume).label("volume"), 
                               func.trim(models.growers.status).label("status"),
                               models.growers.updated_by,
                               models.growers.updated_time,
                               models.growers.pgt_grower_name,
                               models.growers.region,
                               models.growers.grower_id,
                               models.growers.created_by,
                               models.growers.created_time,
                               models.growers.grower_abbreviation_code)
                               .filter(models.growers.grower_name == grower_name,models.growers.status == "ACTIVE").all())
        grower_growing_area_details = (db.query(models.preferred_grower.grower_name,models.preferred_grower.growing_area_name,
                                                models.preferred_grower.grower_id,models.preferred_grower.growing_area_id).
                                        filter(models.preferred_grower.grower_name==grower_name).distinct().all())
        empty_json = {
        "grower_name": var_not_appl,
        "growing_area_name": var_not_appl,
        "grower_id": 000,
        "growing_area_id": 0
        }
        return {"grower_details":grower_details,"gr_grarea_details":grower_growing_area_details if grower_growing_area_details else [empty_json]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/modify_ex_grower')
def modify_ex_grower(payload: schemas.edit_gr_grarea_masters,db:Session = Depends(get_db)):  # pragma: no cover
    """
    Replace existing growing area mappings for a grower.

    Args:
        payload (edit_gr_grarea_masters): New growing area mappings for the grower.
        db (Session): Database session.

    Returns:
        dict: Status message indicating mapping update result.

    Raises:
        HTTPException: If delete or insert operations fail.
    """
    try:
        grower_name = payload.grower_name
        grower_id = payload.grower_id
        flag=False
        existing_record = db.query(models.preferred_grower)\
                                .filter(models.preferred_grower.grower_name==grower_name).all()
        seen_combinations = set()
        for ex in existing_record:
            db.delete(ex)

        for ga, ga_id in zip(payload.growing_area_name, payload.growing_area_id):
            unique_combination = (payload.grower_name, ga)
            if unique_combination in seen_combinations:
                continue

            seen_combinations.add(unique_combination)
            new_mapping = models.preferred_grower(
                grower_name=payload.grower_name,
                growing_area_name=ga,
                growing_area_id=ga_id,
                grower_id=grower_id
            )
            db.add(new_mapping)
            flag=True
        db.commit()
        if flag:
            db.refresh(new_mapping)
        return {"status":"Updated the grower growing area mapping successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_region')
def get_region(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all active regions.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of active regions under 'regions'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_regions = (db.query(models.region.region_name,
                                func.trim(models.region.country).label("country"),
                                func.trim(models.region.updated_by).label("updated_by"),
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.created_by).label("created_by"),
                                models.region.region_id,
                                models.region.created_time).filter(models.region.status=="ACTIVE").order_by(models.region.updated_time,models.region.region_id).distinct().all())
        return {"regions":all_regions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_region/{region_name}')
def get_region_by_name(region_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Fetch details of a specific active region by name.

    Args:
        region_name (str): Name of the region.
        db (Session): Database session.

    Returns:
        dict: Region details under 'region_details'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        region_details = (db.query(models.region.region_name,
                                func.trim(models.region.country).label("country"),
                                func.trim(models.region.updated_by).label("updated_by"),
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.created_by).label("created_by"),
                                models.region.region_id,
                                models.region.created_time).filter(models.region.region_name == region_name,
                                                        models.region.status == "ACTIVE").all())
        return {"region_details":region_details}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_region', status_code=status.HTTP_201_CREATED)
def add_new_region(payload: schemas.Region, db: Session = Depends(get_db)): # pragma: no cover
    """
    Add a new region to the region master.

    Args:
        payload (Region): Region details.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If insert fails.
    """
    try:
        new_region = models.region(**payload.dict())
        db.add(new_region)
        db.commit()
        return {"status":"New region added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_region/{region_id}', status_code=status.HTTP_200_OK)
def update_region(region_id: int, update_payload: schemas.UpdateRegion, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update an existing region.

    Args:
        region_id (int): ID of the region to update.
        update_payload (UpdateRegion): Fields to update.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If region not found or update fails.
    """
    try:
        # Fetch the existing region
        region_to_update = db.query(models.region).filter(models.region.region_id == region_id).first()
        
        if not region_to_update:
            raise HTTPException(status_code=404, detail="Region not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(region_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            region_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "Region updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get_crop_category')
def get_crop_category(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all active crop categories.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of active crop categories under 'crop_categories'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_crop_cat = (db.query(models.category.crop_category,
                                func.trim(models.category.created_by).label("created_by"),
                                func.trim(models.category.status).label("status"),
                                models.category.updated_time,
                                func.trim(models.category.updated_by).label("updated_by"),
                                models.category.category_name,
                                func.trim(models.category.country).label("country"),
                                models.category.created_time).filter(models.category.status=="ACTIVE").order_by(models.category.updated_time,models.category.crop_category).distinct().all())
        return {"crop_categories":all_crop_cat}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_crop_cat/{category_name}')
def get_crop_category_by_name(category_name: str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Fetch details of a specific crop category by name.

    Args:
        category_name (str): Crop category name.
        db (Session): Database session.

    Returns:
        dict: Crop category details under 'crop_details'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        crop_details = (db.query(models.category.crop_category,
                                func.trim(models.category.created_by).label("created_by"),
                                func.trim(models.category.status).label("status"),
                                models.category.updated_time,
                                func.trim(models.category.updated_by).label("updated_by"),
                                models.category.category_name,
                                func.trim(models.category.country).label("country"),
                                models.category.created_time).filter(models.category.category_name == category_name,
                                                        models.category.status == "ACTIVE").all())
        return {"crop_details":crop_details}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/add_crop', status_code=status.HTTP_201_CREATED)
def add_new_crop(payload: schemas.Category, db: Session = Depends(get_db)): # pragma: no cover
    """
    Add a new crop category.

    Args:
        payload (Category): Crop category details.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If insert fails.
    """
    try:
        new_crop_cat = models.category(**payload.dict())
        db.add(new_crop_cat)
        db.commit()
        return {"status":"New crop category added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/update_crop/{crop_category}', status_code=status.HTTP_200_OK)
def update_crop_category(crop_category: int, update_payload: schemas.Category, db: Session = Depends(get_db)): # pragma: no cover
    """
    Update an existing crop category.

    Args:
        crop_category (int): Crop category identifier.
        update_payload (Category): Fields to update.
        db (Session): Database session.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException: If crop category not found or update fails.
    """
    try:
        # Fetch the existing region
        crop_to_update = db.query(models.category).filter(models.category.crop_category == crop_category).first()
        
        if not crop_to_update:
            raise HTTPException(status_code=404, detail="Crop category not found")

        # Update fields if provided in the payload
        update_data = update_payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(crop_to_update, key, value)

        # Automatically set updated_time if not provided
        if 'updated_time' not in update_data:
            crop_to_update.updated_time = datetime.now()

        db.commit()
        return {"status": "crop category updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/plant/{plant_id}/{status}')
def delete_plant(plant_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Soft delete or reactivate a plant by updating status.

    Args:
        plant_id (int): Plant ID.
        status (str): New status value ("ACTIVE" or "INACTIVE").
        db (Session): Database session.

    Returns:
        dict: Status message based on operation.

    Raises:
        HTTPException: If plant not found.
    """
    try:
        plant_query = db.query(models.Plant).filter(models.Plant.plant_id == plant_id).update({'status': status})
        if not plant_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No growers  with this id: {id} found')

        db.commit()
        if status=="INACTIVE":
            return {"status":"Plant deleted successfully"}
        else:
            return {"status":"Plant made into Active state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post('/grower/{grower_id}/{status}')
def delete_grower(grower_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Soft delete or reactivate a grower by updating status.

    Args:
        grower_id (int): Grower ID.
        status (str): New status value ("ACTIVE" or "INACTIVE").
        db (Session): Database session.

    Returns:
        dict: Status message based on operation.

    Raises:
        HTTPException: If grower not found.
    """
    try:
        grower_query = db.query(models.growers).filter(models.growers.grower_id == grower_id).update({'status': status})
        if not grower_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No growers  with this id: {id} found')

        db.commit()
        if status=="INACTIVE":
            return {"status":"Grower deleted successfully"}
        else:
            return {"status":"Grower made into Active state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/growing_area/{growing_area_id}/{status}')
def delete_growing_area(growing_area_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Soft delete or reactivate a growing area by updating status.

    Args:
        growing_area_id (int): Growing area ID.
        status (str): New status value ("ACTIVE" or "INACTIVE").
        db (Session): Database session.

    Returns:
        dict: Status message based on operation.

    Raises:
        HTTPException: If growing area not found.
    """
    try:
        ga_query = db.query(models.growing_area).filter(models.growing_area.growing_area_id == growing_area_id).update({'status': status})
        if not ga_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No growers  with this id: {id} found')

        db.commit()
        if status=="INACTIVE":
            return {"status":"Growing area deleted successfully"}
        else:
            return {"status":"Growing area made into Active state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/vendor_site/{vendor_site_id}/{status}')
def delete_vendor_site(vendor_site_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Soft delete or reactivate a vendor site by updating status.

    Args:
        vendor_site_id (int): Vendor site ID.
        status (str): New status value ("ACTIVE" or "INACTIVE").
        db (Session): Database session.

    Returns:
        dict: Status message based on operation.

    Raises:
        HTTPException: If vendor site not found.
    """
    try:
        vendor_site_query = db.query(models.vendor_site_code).filter(models.vendor_site_code.VENDOR_SITE_ID == vendor_site_id).update({'status': status})
        if not vendor_site_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No growers  with this id: {id} found')

        db.commit()
        if status=="INACTIVE":
            return {"status":"Vendor Site deleted successfully"}
        else:
            return {"status":"Vendor Site made into Active state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/region/{region_id}/{status}')
def delete_region(region_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Soft delete or reactivate a region by updating status.

    Args:
        region_id (int): Region ID.
        status (str): New status value ("ACTIVE" or "INACTIVE").
        db (Session): Database session.

    Returns:
        dict: Status message based on operation.

    Raises:
        HTTPException: If region not found.
    """
    try:
        region_query = db.query(models.region).filter(models.region.region_id == region_id).update({'status': status})
        if not region_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No growers  with this id: {id} found')

        db.commit()
        if status=="INACTIVE":
            return {"status":"Region deleted successfully"}
        else:
            return {"status":"Region made into Active state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/crop_category/{crop_cat_id}/{status}')
def delete_category(crop_cat_id: int,status:str, db: Session = Depends(get_db)): # pragma: no cover
    """
    Soft delete or reactivate a crop category by updating status.

    Args:
        crop_cat_id (int): Crop category ID.
        status (str): New status value ("ACTIVE" or "INACTIVE").
        db (Session): Database session.

    Returns:
        dict: Status message based on operation.

    Raises:
        HTTPException: If crop category not found.
    """
    try:
        category_query = db.query(models.category).filter(models.category.crop_category == crop_cat_id).update({'status': status})
        if not category_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No growers  with this id: {id} found')

        db.commit()
        if status=="INACTIVE":
            return {"status":"Crop category deleted successfully"}
        else:
            return {"status":"Crop category made into Active state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_inactive_plants')
def get_inactive_plants(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all inactive plants.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of inactive plants (or default placeholder) under 'in_plants'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_plants = db.query(models.Plant.plant_id,
                               models.Plant.company_name,
                               func.trim(models.Plant.created_by).label("created_by"),
                               func.trim(models.Plant.status).label("status"),
                               func.trim(models.Plant.updated_by).label("updated_by"),
                               models.Plant.created_time,
                               models.Plant.pgt_plant_name,
                               models.Plant.plant_code,
                               models.Plant.plant_name,
                               models.Plant.region_id,
                               models.Plant.crop_category_id,
                               models.Plant.updated_time).filter(models.Plant.status=="INACTIVE").order_by(models.Plant.updated_time,models.Plant.plant_id).distinct().all()
        empty_json =  [{
            "plant_id": 000,
            "company_name": var_not_appl_,
            "created_by": var_not_appl_,
            "status": var_not_appl_,
            "updated_by": var_not_appl_,
            "created_time": "2023-10-18T13:17:55.120000",
            "pgt_plant_name": var_not_appl_,
            "plant_code": var_not_appl_,
            "plant_name": var_not_appl_,
            "region_id": 000,
            "crop_category_id": 000,
            "updated_time": "2024-03-18T16:29:09.660000"
            }]
        return {"in_plants":all_plants if all_plants else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
        
@router.get('/get_inactive_growers')
def get_inactive_growers(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all inactive growers.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of inactive growers (or default placeholder) under 'in_growers'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_growers = (db.query(models.growers.grower_name, 
                               func.trim(models.growers.owner).label("owner"), 
                               func.trim(models.growers.country).label("country"), 
                               func.trim(models.growers.volume).label("volume"), 
                               func.trim(models.growers.status).label("status"),
                               models.growers.updated_by,
                               models.growers.updated_time,
                               models.growers.pgt_grower_name,
                               models.growers.region,
                               models.growers.grower_id,
                               models.growers.created_by,
                               models.growers.created_time,
                               models.growers.grower_abbreviation_code).filter(models.growers.status=="INACTIVE").order_by(models.growers.updated_time,models.growers.grower_id).distinct().all())
        empty_json =  [{
                "grower_name": var_not_appl_,
                "owner": var_not_appl_,
                "country": var_not_appl_,
                "volume": "000",
                "status": var_not_appl_,
                "updated_by": var_not_appl_,
                "updated_time": "2024-03-28T07:49:16.353000",
                "pgt_grower_name": var_not_appl_,
                "region": 000,
                "grower_id": 000,
                "created_by": var_not_appl_,
                "created_time": "2023-10-12T08:10:20",
                "grower_abbreviation_code": var_not_appl_
                }]
        
        return {"in_growers":all_growers if all_growers else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
        
@router.get('/get_growing_area')
def get_active_growing_area(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all active growing areas.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of active growing areas under 'growing_area'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_ga = db.query(models.growing_area).filter(models.growing_area.status=="ACTIVE").distinct().all()
        return {"growing_area":all_ga}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_inactive_growing_area')
def get_inactive_growing_area(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all inactive growing areas.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of inactive growing areas (or default placeholder) under 'in_growing_area'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_ga = db.query(models.growing_area).filter(models.growing_area.status=="INACTIVE").distinct().all()
        empty_json = [{
                "created_by": var_not_appl_,
                "growing_area_name": var_not_appl_,
                "region": 000,
                "status": var_not_appl_,
                "fresh_period_start": 000,
                "fresh_period_end": 000,
                "storage_period_start": 000,
                "created_time": "2023-10-18T23:05:22.570000",
                "pgt_growing_area": var_not_appl_,
                "country": var_not_appl_,
                "growing_area_id": 000,
                "updated_by": var_not_appl_,
                "growing_area_desc": var_not_appl_,
                "fresh_week_start": 000,
                "fresh_week_end": 000,
                "storage_week_start": 000,
                "updated_time": "2023-10-18T23:05:22.570000"
                }]
        return {"in_growing_area":all_ga if all_ga else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_vsc')
def get_active_vsc(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all active vendor site codes.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of active vendor site codes under 'vsc'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_vsc = db.query(models.vendor_site_code).filter(models.vendor_site_code.status=="ACTIVE").order_by(models.vendor_site_code.updated_time,models.vendor_site_code.VENDOR_SITE_ID).distinct().all()
        return {"vsc":all_vsc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get('/get_inactive_vsc')
def get_inactive_vsc(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all inactive vendor site codes.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of inactive vendor site codes (or placeholder) under 'in_vsc'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_vsc = db.query(models.vendor_site_code).filter(models.vendor_site_code.status=="INACTIVE").order_by(models.vendor_site_code.updated_time,models.vendor_site_code.VENDOR_SITE_ID).distinct().all()
        empty_json = [{
                "created_by": var_not_appl_,
                "VENDOR_SITE_CODE": var_not_appl_,
                "status": var_not_appl_,
                "updated_time": "2024-03-15T11:06:13.363000",
                "pgt_vsc": var_not_appl_,
                "VENDOR_SITE_ID": 000,
                "created_time": "2024-03-15T11:06:13.363000",
                "updated_by": var_not_appl_,
                "region_id": 000
                }]
        return {"in_vsc":all_vsc if all_vsc else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
@router.get('/get_inactive_region')
def get_inactive_region(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all inactive regions.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of inactive regions (or placeholder) under 'in_regions'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_regions = db.query(models.region.region_name,
                                func.trim(models.region.country).label("country"),
                                func.trim(models.region.updated_by).label("updated_by"),
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.status).label("status"),
                                models.region.updated_time,
                                func.trim(models.region.created_by).label("created_by"),
                                models.region.region_id,
                                models.region.created_time).filter(models.region.status=="INACTIVE").order_by(models.region.updated_time,models.region.region_id).distinct().all()
        empty_json = [{
                "region_name": var_not_appl_,
                "country": var_not_appl_,
                "updated_by": var_not_appl_,
                "created_time": "2023-10-12T11:21:15.750000",
                "created_by": var_not_appl_,
                "region_id": 000,
                "status": var_not_appl_,
                "updated_time": "2023-10-12T11:21:15.750000"
                }]
        return {"in_regions":all_regions if all_regions else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
        
@router.get('/get_inactive_crop_category')
def get_inactive_crop_category(db: Session = Depends(get_db)):  # pragma: no cover
    """
    Fetch all inactive crop categories.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of inactive crop categories (or placeholder) under 'in_crop_categories'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        all_crop_cat = db.query(models.category.crop_category,
                                func.trim(models.category.created_by).label("created_by"),
                                func.trim(models.category.status).label("status"),
                                models.category.updated_time,
                                func.trim(models.category.updated_by).label("updated_by"),
                                models.category.category_name,
                                func.trim(models.category.country).label("country"),
                                models.category.created_time).filter(models.category.status=="INACTIVE").order_by(models.category.updated_time,models.category.crop_category).distinct().all()
        empty_json = [{
                    "crop_category": 0,
                    "created_by": var_not_appl_,
                    "status": var_not_appl_,
                    "updated_time": "2024-03-01T09:37:39.473000",
                    "updated_by": var_not_appl_,
                    "category_name": var_not_appl_,
                    "country": var_not_appl_,
                    "created_time": "2024-03-01T09:37:39.473000"
                    }]
        return {"in_crop_categories":all_crop_cat if all_crop_cat else empty_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_file")
def upload_file(file: UploadFile = File(...)):    # pragma: no cover
    """
    Upload a CSV or Excel file and return a preview of the first few rows.

    Args:
        file (UploadFile): Uploaded file object.

    Returns:
        dict: Filename and parsed content preview under 'file_content'.

    Raises:
        HTTPException:
            - 400: If file has no extension or format is unsupported.
    """
    try:
        contents = file.file.read()
        try:
            file_format = file.filename.rsplit(".", 1)[1].lower()
        except IndexError:
            raise HTTPException(
                status_code=400, detail="Uploaded file must have an extension"
            )

        if file_format == "csv":
            s = contents.decode("utf-8")
            data = StringIO(s)
            df = pd.read_csv(data)
        elif file_format in ["xls", "xlsx"]:
            data = BytesIO(contents)
            df = pd.read_excel(data)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only CSV, XLS, and XLSX are allowed.",
            )

        data.close()
        file.file.close()

        response_json = df.head().to_dict(orient="records")
        return {"filename": file.filename, "file_content": response_json}
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))