from sqlalchemy import or_, delete, extract
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from models import Ownership, OwnershipGrowerGrowing, OwnershipGrowerVariety
from database import get_db
from decimal import Decimal

router = APIRouter()


@router.get('/region/{region}/year/{year}')
def get_ownership_region(region: str, year: int, db: Session = Depends(get_db)):
    if region == 'US' or region == 'Canada':
        data = db.query(models.View_Ownership) \
            .join(models.growing_area,
                  models.View_Ownership.columns.growing_area_id == models.growing_area.growing_area_id) \
            .join(models.region, models.growing_area.region == models.region.region_id) \
            .filter(models.region.country == region, or_(models.View_Ownership.columns.year == year - 1,
                                                         models.View_Ownership.columns.year == year)).all()

        ownership_metric = db.query(models.View_OwnershipMetrics_country) \
            .filter(models.View_OwnershipMetrics_country.columns.country == region,
                    or_(models.View_OwnershipMetrics_region.columns.year == year - 1,
                        models.View_OwnershipMetrics_region.columns.year == year)) \
            .distinct().all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ownership data not found for : {region}")
    else:
        data = db.query(models.View_Ownership) \
            .join(models.growing_area,
                  models.View_Ownership.columns.growing_area_id ==
                  models.growing_area.growing_area_id) \
            .join(models.region, models.growing_area.region == models.region.region_id) \
            .filter(models.region.region_name == region,
                    or_(models.View_Ownership.columns.year == year - 1,
                        models.View_Ownership.columns.year == year)).all()

        ownership_metric = db.query(models.View_OwnershipMetrics_region) \
            .filter(models.View_OwnershipMetrics_region.columns.region_name == region,
                    or_(models.View_OwnershipMetrics_region.columns.year == year - 1,
                        models.View_OwnershipMetrics_region.columns.year == year)) \
            .distinct().all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ownership data not found for : {region}")

    return {"status": "success", "ownership": data, "ownership_metric_region": ownership_metric}


@router.get('/year/{year}')
def get_ownership(year: int, db: Session = Depends(get_db)):
    ownership = db.query(models.View_Ownership) \
        .filter(or_(models.View_Ownership.columns.year == year - 1,
                    models.View_Ownership.columns.year == year)).all()
    ownership_metric_all = db.query(models.View_OwnershipMetrics_all) \
        .filter(or_(models.View_OwnershipMetrics_all.columns.year == year - 1,
                    models.View_OwnershipMetrics_all.columns.year == year)) \
        .distinct().all()
    if not ownership: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No ownership_id found")
    return {"status": "success", "ownership": ownership,
            "ownership_metric_region": ownership_metric_all}


@router.post('/create_new_ownership/{year}')
def create_new_ownership(year: int, db: Session = Depends(get_db)):
    try:
        growing_area_list = db.query(models.growing_area).filter(models.growing_area.status == 'ACTIVE').all()
        for growing_area in growing_area_list:
            fresh_crop_year = str(year)
            fresh_crop_type = 'Fresh'
            storage_crop_type = 'Storage'
            storage_crop_year = str(year) + "-" + str(year + 1)[2:]
            fresh_ownership_id = str(growing_area.growing_area_id) + "#" + fresh_crop_year
            storage_ownership_id = str(growing_area.growing_area_id) + "#" + storage_crop_year

            payload = {"ownership_id": fresh_ownership_id, "growing_area_id": growing_area.growing_area_id,
                       "contract": 0, "contract_erp_value": 0, "shrinkage": 0, "to_ship": 0,
                       "extension": 0, "market": 0, "flex": 0, "total_ship": 0, "year": year,
                       "crop_type": fresh_crop_type,
                       "crop_year": fresh_crop_year, "final_extension": 0}
            new_ownership = models.Ownership(**payload)
            db.add(new_ownership)
            db.commit()
            payload = {"ownership_id": storage_ownership_id, "growing_area_id": growing_area.growing_area_id,
                       "contract": 0, "contract_erp_value": 0, "shrinkage": 0, "to_ship": 0,
                       "extension": 0, "market": 0, "flex": 0, "total_ship": 0, "year": year,
                       "crop_type": storage_crop_type,
                       "crop_year": storage_crop_year, "final_extension": 0}
            new_ownership = models.Ownership(**payload)
            db.add(new_ownership)
            db.commit()

        return {"Status": "success", "records_inserted": "Next year data are added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update_contract_erp/{crop_year}")
def update_ownership_contract_erp(crop_year: str, db: Session = Depends(get_db)):
    try:
        max_crop_year = db.query(func.max(models.View_total_sum_growing_area.columns.crop_year)) \
            .filter(models.View_total_sum_growing_area.columns.STORAGE_period == crop_year).scalar()
        view_data = db.query(models.View_total_sum_growing_area) \
            .filter(models.View_total_sum_growing_area.columns.STORAGE_period == crop_year,
                    models.View_total_sum_growing_area.columns.crop_year == max_crop_year) \
            .all()
        if len(view_data) > 0:
            for data in view_data:
                existing_record = db.query(models.Ownership) \
                    .filter(models.Ownership.growing_area_id == data.growing_area_id,
                            models.Ownership.crop_year == crop_year) \
                    .first()
                if existing_record is not None:
                    db.query(models.Ownership).filter(
                        models.Ownership.growing_area_id == data.growing_area_id,
                        models.Ownership.crop_year == crop_year
                    ).update({models.Ownership.contract_erp_value: data.totalsum})

                db.commit()
            return {"message": f"Total Contract ERP updated for {crop_year} in Ownership table"}
        else: # pragma: no cover
            return {"message": f"Total Contract ERP is not available for {crop_year} in erp table."}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


def generate_ownership_payload(growing_area_id, crop_year, crop_type, year):
    ownership_id = str(growing_area_id) + "#" + str(crop_year)
    payload = {
        "ownership_id": ownership_id,
        "growing_area_id": growing_area_id,
        "contract": 0,
        "contract_erp_value": 0,
        "shrinkage": 0,
        "to_ship": 0,
        "extension": 0,
        "market": 0,
        "flex": 0,
        "total_ship": 0,
        "year": year,
        "crop_type": crop_type,
        "crop_year": str(crop_year),
        "final_extension": 0
    }
    return payload


@router.post('/new_growing_area/{growing_area_name}')
def new_growing_area(growing_area_name: str, db: Session = Depends(get_db)):
    try:
        growing_area_id = db.query(models.growing_area.growing_area_id) \
            .filter(models.growing_area.growing_area_name == growing_area_name).scalar()
        current_year = date.today().year
        fresh_crop_year = str(current_year)
        previous_crop_year = str(current_year - 1) + "-" + str(current_year)[2:]
        storage_crop_year = str(current_year) + "-" + str(current_year + 1)[2:]

        prev_storage_ownership_payload = generate_ownership_payload(growing_area_id, previous_crop_year,
                                                                    'Storage', current_year - 1)
        fresh_ownership_payload = generate_ownership_payload(growing_area_id, fresh_crop_year,
                                                             'Fresh', current_year)
        storage_ownership_payload = generate_ownership_payload(growing_area_id, storage_crop_year,
                                                               'Storage', current_year)

        prev_ownership = models.Ownership(**prev_storage_ownership_payload)
        fresh_ownership = models.Ownership(**fresh_ownership_payload)
        storage_ownership = models.Ownership(**storage_ownership_payload)
        db.add(prev_ownership)
        db.add(fresh_ownership)
        db.add(storage_ownership)
        db.commit()
        return {"Status": "success",
                "message": f" Ownership record is added for {previous_crop_year}, "
                           f"{fresh_crop_year}, {storage_crop_year} seasons."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


def calculate_to_ship(growing_area_id: int, crop_period: str, db):
    total_contract = 0.0
    total_to_ship = 0.0
    total_shrinkage_per = 0.0
    total_shrinkage_volume = 0.0


    get_contract_volume = (
        db.query(OwnershipGrowerGrowing.contract, OwnershipGrowerGrowing.shrinkage_volume)
        .filter(
            OwnershipGrowerGrowing.growing_area_id == growing_area_id,
            OwnershipGrowerGrowing.crop_year == crop_period,
            OwnershipGrowerGrowing.status == 'ACTIVE'
        )
        .all()
    )

    print("Rows fetched:", len(get_contract_volume))
    if len(get_contract_volume) != 0:
        for idx, item in enumerate(get_contract_volume, start=1):
            # IMPORTANT: convert to float to avoid float += Decimal issue
            contract = float(item[0] or 0)
            shrinkage_volume = float(item[1] or 0)

            print(f"Row {idx} -> contract: {contract}, shrinkage_volume: {shrinkage_volume}")

            total_contract += contract
            total_shrinkage_volume += shrinkage_volume
            total_to_ship += contract - shrinkage_volume

        print("TOTAL contract:", total_contract)
        print("TOTAL shrinkage_volume:", total_shrinkage_volume)
        print("TOTAL to_ship:", total_to_ship)

        if total_contract == 0:
            total_shrinkage_per = 0
        else:
            total_shrinkage_per = (total_shrinkage_volume / total_contract) * 100

    print("TOTAL shrinkage % (summary):", total_shrinkage_per)

    updated_rows = db.query(Ownership) \
        .filter(Ownership.crop_year == crop_period,
                Ownership.growing_area_id == growing_area_id) \
        .update({Ownership.contract: total_contract,
                 Ownership.shrinkage: total_shrinkage_per,
                 Ownership.to_ship: total_to_ship}, synchronize_session=False)

    print("Ownership rows updated:", updated_rows)
    db.commit()
    print("=== calculate_to_ship END ===\n")


def calculate_market_and_flex(growing_area_id: int, crop_period: str, db):
    total_market = 0.0
    total_flex = 0.0

    get_market_flex = db.query(OwnershipGrowerGrowing.market, OwnershipGrowerGrowing.flex) \
        .filter(OwnershipGrowerGrowing.status == 'ACTIVE',
                OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                OwnershipGrowerGrowing.crop_year == crop_period).all()

    print("Rows fetched:", len(get_market_flex))
    if len(get_market_flex) != 0:
        for idx, item in enumerate(get_market_flex, start=1):
            market = float(item[0] or 0)
            flex = float(item[1] or 0)

            print(f"Row {idx} -> market: {market}, flex: {flex}")

            total_market += market
            total_flex += flex

    print("TOTAL market:", total_market)
    print("TOTAL flex:", total_flex)

    updated_rows = db.query(Ownership) \
        .filter(Ownership.crop_year == crop_period,
                Ownership.growing_area_id == growing_area_id) \
        .update({Ownership.market: total_market,
                 Ownership.flex: total_flex}, synchronize_session=False)

    print("Ownership rows updated:", updated_rows)
    db.commit()
    print("=== calculate_market_and_flex END ===\n")


def total_ship_calculation(growing_area_id: int, crop_period: str, db):

    ownership_record = db.query(Ownership) \
        .filter(Ownership.growing_area_id == growing_area_id,
                Ownership.crop_year == crop_period).first()

    if ownership_record:
        print("Ownership record found.")
        print("to_ship:", ownership_record.to_ship, "market:", ownership_record.market, "flex:", ownership_record.flex)

        ownership_record.total_ship = float(ownership_record.to_ship or 0) + float(ownership_record.market or 0) \
                                      + float(ownership_record.flex or 0)

        print("Computed total_ship:", ownership_record.total_ship)
        db.commit()
    else:
        print("No Ownership record found. Skipping total_ship update.")

    print("=== total_ship_calculation END ===\n")


@router.post('/update_contract_shrinkage_mkt_flex/growing_area_id/{growing_area_id}/crop/{crop_period}')
def update_contract_shrinkage_mkt_flex(payload: schemas.UpdateOwnershipGrowerGrowing,
                                       growing_area_id: int, crop_period: str,
                                       db: Session = Depends(get_db)):
    try:

        data = payload.PayloadOwnership
        print("Payload rows:", len(data))

        old_records = db.query(OwnershipGrowerGrowing) \
            .filter(OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                    OwnershipGrowerGrowing.crop_year == str(crop_period)).all()

        print("Old records found:", len(old_records))

        if old_records:
            db.execute(delete(OwnershipGrowerGrowing)
                       .filter(OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                               OwnershipGrowerGrowing.crop_year == crop_period))
            db.commit()
            print("Old records deleted and committed.")

        # Insert the records (UPDATED: always fill shrinkage percent from volume+contract)
        for idx, data_items in enumerate(data, start=1):
            item = data_items.dict()

            contract = float(item.get("contract") or 0)

            shrinkage_volume = item.get("shrinkage_volume")  # can be int/float
            shrinkage_percent = item.get("shrinkage")        # old percent

            print(f"\nInsert Row {idx}: grower_id={item.get('grower_id')} contract={contract} "
                  f"payload_shrinkage_volume={shrinkage_volume} payload_shrinkage%={shrinkage_percent}")

            # Decide shrinkage_volume value
            if shrinkage_volume is None:
                if shrinkage_percent is not None:
                    shrinkage_volume = contract * (float(shrinkage_percent) / 100)
                else: # pragma: no cover
                    shrinkage_volume = 0.0
            else:
                shrinkage_volume = float(shrinkage_volume)

            # ALWAYS compute shrinkage percent from volume + contract and store in shrinkage
            if contract == 0:
                item["shrinkage"] = 0.0
            else:
                item["shrinkage"] = (shrinkage_volume / contract) * 100

            # Store volume to new column (force float to avoid Decimal issues later)
            item["shrinkage_volume"] = float(shrinkage_volume)

            print(f"Computed -> shrinkage_volume={item['shrinkage_volume']} shrinkage%={item['shrinkage']}")

            new_records = OwnershipGrowerGrowing(**item)
            db.add(new_records)

        db.commit()
        print("\nNew records inserted and committed.")

        print("Calling calculate_to_ship...")
        calculate_to_ship(growing_area_id, crop_period, db)

        print("Calling calculate_market_and_flex...")
        calculate_market_and_flex(growing_area_id, crop_period, db)

        print("Calling total_ship_calculation...")
        total_ship_calculation(growing_area_id, crop_period, db)

        # Update OwnershipGrowerVariety table with market, flex, shrinkage values
        print("\nUpdating OwnershipGrowerVariety table...")
        for data_items in data:
            item = data_items.dict()
            contract = float(item.get("contract") or 0)
            shrinkage_volume = item.get("shrinkage_volume")  # can be int/float
            shrinkage_percent = item.get("shrinkage")        # old percent
            # Decide shrinkage_volume value
            if shrinkage_volume is None:
                if shrinkage_percent is not None:
                    shrinkage_volume = contract * (float(shrinkage_percent) / 100)
                else: # pragma: no cover
                    shrinkage_volume = 0.0
            else:
                shrinkage_volume = float(shrinkage_volume)

            # ALWAYS compute shrinkage percent from volume + contract and store in shrinkage
            if contract == 0:
                shrinkage_percent = 0.0
            else:
                shrinkage_percent = (shrinkage_volume / contract) * 100

            grower_id = data_items.grower_id
            market = float(data_items.market or 0)
            flex = float(data_items.flex or 0)
            shrinkage = shrinkage_percent
            shrinkage_volume = float(shrinkage_volume)
            
            # Update all variety records for this grower
            db.query(OwnershipGrowerVariety) \
                .filter(OwnershipGrowerVariety.growing_area_id == growing_area_id,
                        OwnershipGrowerVariety.grower_id == grower_id,
                        OwnershipGrowerVariety.crop_year == crop_period) \
                .update({
                    OwnershipGrowerVariety.market: market,
                    OwnershipGrowerVariety.flex: flex,
                    OwnershipGrowerVariety.shrinkage: shrinkage,
                    OwnershipGrowerVariety.shrinkage_volume: shrinkage_volume
                }, synchronize_session=False)
        
        db.commit()
        print("OwnershipGrowerVariety table updated successfully.")

        return {"status": "success",
                "message": f"Ownership is updated for this growing_area_id: {growing_area_id}"}

    except Exception as e: # pragma: no cover
        print("ERROR:", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get('/get_recent_extensions')
def get_extensions(db: Session = Depends(get_db)):
    """
    Fetch recent extension ownership records where total_value is non-zero.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: Response containing a list of extension records under key `record`.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        records =(db.query( func.concat(models.growing_area.growing_area_name, " | ", models.growing_area.growing_area_desc).label("growing_area"),
                            models.region.region_name.label("region_name"),
                            models.ExtensionOwnershipMapping.year,
                            models.ExtensionOwnershipMapping.period,
                            models.ExtensionOwnershipMapping.week,
                            func.concat(models.ExtensionOwnershipMapping.crop_type," ",models.ExtensionOwnershipMapping.crop_year).label("crop_type_year"),
                            models.ExtensionOwnershipMapping.total_value,
                            models.ExtensionOwnershipMapping.updated_time)
                    .select_from(models.ExtensionOwnershipMapping)
                    .join(models.growing_area,
                          models.growing_area.growing_area_id == models.ExtensionOwnershipMapping.growing_area_id)
                    .outerjoin(models.region,
                        models.region.region_id == models.growing_area.region)
           
                    .filter(models.ExtensionOwnershipMapping.total_value != 0).all())
        return {"record":records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/update_contract_variety_level/growing_area_id/{growing_area_id}/crop/{crop_period}')
def update_contract_variety_level(
    payload: schemas.UpdateOwnershipGrowerVariety,
    growing_area_id: int, 
    crop_period: str,
    db: Session = Depends(get_db)
): # pragma: no cover
    """
    PRIMARY ENDPOINT: Update ownership from variety-level data.
    
    Single atomic transaction flow:
    1. Save variety data
    2. Aggregate to grower level (helper function)
    3. Calculate ownership metrics (reuse existing helpers)
    """
    try:
        variety_data = payload.PayloadVariety
        
        # Step 1: Delete old variety records
        db.execute(delete(models.OwnershipGrowerVariety)
                   .filter(models.OwnershipGrowerVariety.growing_area_id == growing_area_id,
                           models.OwnershipGrowerVariety.crop_year == crop_period))
        
        # Step 2: Insert new variety records
        for data_items in variety_data:
            item = data_items.dict()
            contract = float(item.get("contract") or 0)
            shrinkage_volume = item.get("shrinkage_volume")
            shrinkage_percent = item.get("shrinkage")
            
            if shrinkage_volume is None:
                if shrinkage_percent is not None:
                    shrinkage_volume = contract * (float(shrinkage_percent) / 100)
                else:
                    shrinkage_volume = 0.0
            else:
                shrinkage_volume = float(shrinkage_volume)
            
            if contract == 0:
                item["shrinkage"] = 0.0
            else:
                item["shrinkage"] = (shrinkage_volume / contract) * 100
            
            item["shrinkage_volume"] = float(shrinkage_volume)
            new_record = models.OwnershipGrowerVariety(**item)
            db.add(new_record)

        db.commit()
        # Step 3: Aggregate (HELPER FUNCTION - not endpoint)
        aggregate_variety_to_grower(growing_area_id, crop_period, db)
        
        # Step 4: Calculate ownership (REUSE existing helpers)
        calculate_to_ship(growing_area_id, crop_period, db)
        calculate_market_and_flex(growing_area_id, crop_period, db)
        total_ship_calculation(growing_area_id, crop_period, db)

        return {
            "status": "success",
            "message": f"Variety-level ownership updated for growing_area_id: {growing_area_id}"
        }
        
    except Exception as e:
        db.rollback()  # Clean rollback on error
        raise HTTPException(status_code=400, detail=str(e)) from e


def aggregate_variety_to_grower(growing_area_id: int, crop_period: str, db: Session): # pragma: no cover
    """
    Internal helper: Aggregate variety → grower level.
    NOT exposed as an API endpoint.
    """
    # Delete old grower records
    db.execute(delete(models.OwnershipGrowerGrowing)
               .filter(models.OwnershipGrowerGrowing.growing_area_id == growing_area_id,
                       models.OwnershipGrowerGrowing.crop_year == crop_period))
    print("Old growing_grower records deleted.")
    # Aggregate variety data
    aggregated = (
        db.query(
            models.OwnershipGrowerVariety.growing_area_id,
            models.OwnershipGrowerVariety.grower_id,
            models.OwnershipGrowerVariety.ownership_id,
            models.OwnershipGrowerVariety.crop_year,
            models.OwnershipGrowerVariety.crop_type,
            models.OwnershipGrowerVariety.year,
            func.sum(models.OwnershipGrowerVariety.contract).label('total_contract'),
            func.max(models.OwnershipGrowerVariety.shrinkage_volume).label('total_shrinkage_volume'),
            func.max(models.OwnershipGrowerVariety.market).label('total_market'),
            func.max(models.OwnershipGrowerVariety.flex).label('total_flex'),
            func.max(models.OwnershipGrowerVariety.contract_erp).label('total_contract_erp')
        )
        .filter(
            models.OwnershipGrowerVariety.growing_area_id == growing_area_id,
            models.OwnershipGrowerVariety.crop_year == crop_period,
            models.OwnershipGrowerVariety.status == 'ACTIVE'
        )
        .group_by(
            models.OwnershipGrowerVariety.growing_area_id,
            models.OwnershipGrowerVariety.grower_id,
            models.OwnershipGrowerVariety.ownership_id,
            models.OwnershipGrowerVariety.crop_year,
            models.OwnershipGrowerVariety.crop_type,
            models.OwnershipGrowerVariety.year
        )
        .all()
    )
    
    print("Aggregated variety to grower records:", len(aggregated))
    # Insert aggregated grower records
    for agg in aggregated:
        total_contract = float(agg.total_contract or 0)
        total_shrinkage_volume = float(agg.total_shrinkage_volume or 0)
        
        if total_contract == 0:
            shrinkage_percent = 0.0
        else:
            shrinkage_percent = (total_shrinkage_volume / total_contract) * 100
        
        row_id = f"{agg.growing_area_id}#{agg.grower_id}#{agg.crop_year}"
        print(f"Inserting grower record: row_id={row_id}, contract={total_contract}")
        grower_record = OwnershipGrowerGrowing(
            row_id=row_id,
            growing_area_id=agg.growing_area_id,
            grower_id=agg.grower_id,
            ownership_id=agg.ownership_id,
            crop_year=agg.crop_year,
            crop_type=agg.crop_type,
            year=agg.year,
            contract=int(total_contract),
            shrinkage_volume=total_shrinkage_volume,
            shrinkage=shrinkage_percent,
            market=float(agg.total_market or 0),
            flex=float(agg.total_flex or 0),
            contract_erp=float(agg.total_contract_erp or 0),
            status='ACTIVE'
        )
        
        db.add(grower_record)
    
    db.commit()
    print("Aggregated grower records inserted.")


@router.get('/variety/year/{year}')
def get_ownership_variety(year: int, db: Session = Depends(get_db)):
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
    grower_growing = db.query(models.OwnershipGrowerVariety.row_id,
                              models.OwnershipGrowerVariety.ownership_id,
                              models.OwnershipGrowerVariety.growing_area_id,
                              models.OwnershipGrowerVariety.grower_id,
                              models.OwnershipGrowerVariety.variety_id,
                              models.growers.grower_name,
                              models.OwnershipGrowerVariety.shrinkage,
                              models.OwnershipGrowerVariety.shrinkage_volume,
                              models.OwnershipGrowerVariety.contract_erp,
                              models.OwnershipGrowerVariety.contract,
                              models.OwnershipGrowerVariety.market,
                              models.OwnershipGrowerVariety.flex,
                              models.OwnershipGrowerVariety.year,
                              models.OwnershipGrowerVariety.crop_type,
                              models.OwnershipGrowerVariety.crop_year,
                              models.OwnershipGrowerVariety.status)\
        .join(models.growers,
              models.OwnershipGrowerVariety.grower_id == models.growers.grower_id)\
        .filter(models.OwnershipGrowerVariety.status == "ACTIVE",
                or_(models.OwnershipGrowerVariety.year == year,
                    models.OwnershipGrowerVariety.year == year - 1)).all()
    if not grower_growing: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No mapping  found")
    return {"status": "success", "grower_growing": grower_growing}


@router.post("/migrate-ownership-variety-data")
def migrate_data(db: Session = Depends(get_db)): # pragma: no cover
    source_data = db.query(OwnershipGrowerGrowing).all()
    
    if not source_data:
        raise HTTPException(status_code=404, detail="No source data found")

    new_records = []
    variety_val = "Oracle"

    for row in source_data:
        updated_id = f"{row.row_id}#{variety_val}"
        new_row = OwnershipGrowerVariety(
            row_id=updated_id,
            variety_id=variety_val,
            **{col.name: getattr(row, col.name) 
               for col in row.__table__.columns if col.name != 'row_id'}
        )
        new_records.append(new_row)

    try:
        db.add_all(new_records)
        db.commit()
        return {"status": "success", "records_migrated": len(new_records)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))