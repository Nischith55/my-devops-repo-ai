from typing import List, Set
from fastapi import Depends, File, UploadFile, HTTPException, status, APIRouter
from sqlalchemy import func,and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from io import StringIO, BytesIO
import models
import pandas as pd
from models import View_PlantMtrx_table,allocation,Plant,plantMtrx,pcusage
import schemas
import pytz
from datetime import datetime
from typing import List
import extensionMapping
import period_week_calc
from validator_logger import (
    _is_view_row_complete,
    _fetch_erp_null_rows_for_slice_sql,
    _upsert_null_log,
    _is_erp_row_corrected_for_log,
    _utcnow_naive,
    _refresh_null_logs_for_slice,
    _erp_row_has_required_null_from_mapping
)
from pcusage import create_new_pcusage
from database import SessionLocal
from fastapi import BackgroundTasks
from sqlalchemy.engine import Row

router = APIRouter()

def trim(string):
    """trim function"""
    try:
        return string.replace(" ", "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_plantmtrx_common(filter_conditions, name_or_id, year, db):
    try:
        position_data = db.query(models.View_PlantMtrx_position) \
            .filter(models.View_PlantMtrx_position.columns.year == year).all()

        data = db.query(View_PlantMtrx_table.columns.plant_matrix_id,
                        View_PlantMtrx_table.columns.plant_id,
                        View_PlantMtrx_table.columns.plant_name,
                        View_PlantMtrx_table.columns.period,
                        View_PlantMtrx_table.columns.period_with_P,
                        View_PlantMtrx_table.columns.week,
                        View_PlantMtrx_table.columns.year,
                        View_PlantMtrx_table.columns.crop_year,
                        View_PlantMtrx_table.columns.crop_type,
                        View_PlantMtrx_table.columns.value,
                        View_PlantMtrx_table.columns.growing_area_id,
                        View_PlantMtrx_table.columns.growing_area_name) \
            .filter(View_PlantMtrx_table.columns.year == year,
                    View_PlantMtrx_table.columns.status == 'active', *filter_conditions) \
            .order_by(View_PlantMtrx_table.columns.period,
                      View_PlantMtrx_table.columns.week).all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Plant Mtrx data not found for : {name_or_id}")

        return {"status": "success", "plant_mtrx": data, "position_data": position_data}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/plant/region_id/{region_id}/year/{year}')
def get_plantmtrx_by_region(region_id: int, year: int, db: Session = Depends(get_db)):
    """Get plantMtrx data based on region_id input."""
    filter_conditions = [
        View_PlantMtrx_table.columns.region_id == region_id
    ]
    return get_plantmtrx_common(filter_conditions, region_id, year, db)


@router.get('/plant/company_name/{name}/year/{year}')
def get_plantmtrx_by_company(name: str, year: int, db: Session = Depends(get_db)):
    """Get plantMtrx data based on company_name/country input."""
    filter_dict = {
        'US': 'US',
        'Canada': 'Canada',
        'US-Core': 'US-CORE',
        'Co-Man': 'CO-MAN',
        'Canada-Core': 'Canada'
    }
    filter_conditions = [
        View_PlantMtrx_table.columns.status == 'active',
        View_PlantMtrx_table.columns.country == filter_dict[name]
        if filter_dict[name] in ['US', 'Canada']
        else View_PlantMtrx_table.columns.company_name == filter_dict[name]
    ]
    return get_plantmtrx_common(filter_conditions, name, year, db)


def get_plant_mtrx_growingarea_common(filter_conditions, year, detail_message, db):
    try:
        data = db.query(func.concat(View_PlantMtrx_table.columns.growing_area_name, " | ",
                                    View_PlantMtrx_table.columns.growing_area_desc).label("growing_area_name"),
                        View_PlantMtrx_table.columns.growing_area_id,
                        View_PlantMtrx_table.columns.period,
                        View_PlantMtrx_table.columns.period_with_P,
                        View_PlantMtrx_table.columns.week,
                        View_PlantMtrx_table.columns.year,
                        View_PlantMtrx_table.columns.crop_year,
                        View_PlantMtrx_table.columns.crop_type,
                        func.sum(View_PlantMtrx_table.columns.value).label('total_value')) \
            .filter(View_PlantMtrx_table.columns.year == year,
                    *filter_conditions) \
            .group_by(View_PlantMtrx_table.columns.year,
                      View_PlantMtrx_table.columns.crop_year,
                      View_PlantMtrx_table.columns.crop_type,
                      View_PlantMtrx_table.columns.growing_area_desc,
                      View_PlantMtrx_table.columns.growing_area_id,
                      View_PlantMtrx_table.columns.growing_area_name,
                      View_PlantMtrx_table.columns.period_with_P,
                      View_PlantMtrx_table.columns.period,
                      View_PlantMtrx_table.columns.week) \
            .order_by(View_PlantMtrx_table.columns.period,
                      View_PlantMtrx_table.columns.week).all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message)
        return {"status": "success", "plant_mtrx": data}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/region/{region_id}/year/{year}')
def getplantmtrx_growingarea_by_region(region_id: int, year: int, db: Session = Depends(get_db)):
    filter_conditions = [View_PlantMtrx_table.columns.ga_region_id == region_id]
    detail_message = f"Plant Mtrx data not found for region: {region_id}"
    return get_plant_mtrx_growingarea_common(filter_conditions, year, detail_message, db)


@router.get('/growing_area/country/{name}/year/{year}')
def getplantmtrx_growingarea_by_country(name: str, year: int, db: Session = Depends(get_db)):
    filter_conditions = [View_PlantMtrx_table.columns.ga_country == name]
    detail_message = f"Plant Mtrx data not found for country: {name}"
    return get_plant_mtrx_growingarea_common(filter_conditions, year, detail_message, db)


@router.get('/growing_area/all_data/year/{year}')
def getplantmtrx_growingarea_all(year: int, db: Session = Depends(get_db)):
    filter_conditions = []
    detail_message = "Plant Mtrx data not found."
    return get_plant_mtrx_growingarea_common(filter_conditions, year, detail_message, db)


def get_plant_mtrx_growingarea_period_common(filter_conditions, year, detail_message, db):
    try:
        data = db.query(func.concat(View_PlantMtrx_table.columns.growing_area_name, " | ",
                                    View_PlantMtrx_table.columns.growing_area_desc).label("growing_area_name"),
                        View_PlantMtrx_table.columns.growing_area_id,
                        View_PlantMtrx_table.columns.period,
                        View_PlantMtrx_table.columns.period_with_P,
                        View_PlantMtrx_table.columns.year,
                        View_PlantMtrx_table.columns.crop_year,
                        View_PlantMtrx_table.columns.crop_type,
                        View_PlantMtrx_table.columns.year.label("week"),
                        func.sum(View_PlantMtrx_table.columns.value).label('total_value')) \
            .filter(View_PlantMtrx_table.columns.year == year,
                    *filter_conditions) \
            .group_by(View_PlantMtrx_table.columns.year,
                      View_PlantMtrx_table.columns.crop_year,
                      View_PlantMtrx_table.columns.crop_type,
                      View_PlantMtrx_table.columns.growing_area_desc,
                      View_PlantMtrx_table.columns.growing_area_id,
                      View_PlantMtrx_table.columns.growing_area_name,
                      View_PlantMtrx_table.columns.period_with_P,
                      View_PlantMtrx_table.columns.period) \
            .order_by(View_PlantMtrx_table.columns.period).all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_message)
        return {"status": "success", "plant_mtrx": data}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/growing_area/period/region/{region_id}/year/{year}')
def getplantmtrx_growingarea_by_region_period(region_id: int, year: int, db: Session = Depends(get_db)):
    filter_conditions = [View_PlantMtrx_table.columns.ga_region_id == region_id]
    detail_message = f"Plant Mtrx data not found for region: {region_id}"
    return get_plant_mtrx_growingarea_period_common(filter_conditions, year, detail_message, db)


@router.get('/growing_area/period/country/{name}/year/{year}')
def getplantmtrx_growingarea_by_country_period(name: str, year: int, db: Session = Depends(get_db)):
    filter_conditions = [View_PlantMtrx_table.columns.ga_country == name]
    detail_message = f"Plant Mtrx data not found for country: {name}"
    return get_plant_mtrx_growingarea_period_common(filter_conditions, year, detail_message, db)


@router.get('/growing_area/period/all_data/year/{year}')
def getplantmtrx_growingarea_all_period(year: int, db: Session = Depends(get_db)):
    filter_conditions = []
    detail_message = "Plant Mtrx data not found."
    return get_plant_mtrx_growingarea_period_common(filter_conditions, year, detail_message, db)


@router.get('/only_region_data/year/{year}')
def getplantmtrx_region(year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on region-wise."""
    try:
        data = db.query(View_PlantMtrx_table.columns.region_name,
                        View_PlantMtrx_table.columns.period,
                        View_PlantMtrx_table.columns.period_with_P,
                        View_PlantMtrx_table.columns.week,
                        View_PlantMtrx_table.columns.year,
                        func.sum(View_PlantMtrx_table.columns.value)
                        .label('totalValue_regionWise')) \
            .filter(View_PlantMtrx_table.columns.year == year,
                    View_PlantMtrx_table.columns.status == 'active') \
            .group_by(View_PlantMtrx_table.columns.year,
                      View_PlantMtrx_table.columns.region_id,
                      View_PlantMtrx_table.columns.region_name,
                      View_PlantMtrx_table.columns.period,
                      View_PlantMtrx_table.columns.period_with_P,
                      View_PlantMtrx_table.columns.week) \
            .order_by(View_PlantMtrx_table.columns.region_id,
                      View_PlantMtrx_table.columns.period,
                      View_PlantMtrx_table.columns.week).all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No data is found for this region")
        return {"status": "success", "plant_mtrx_regionWise": data}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/only_region_data/period-wise/year/{year}')
def getplantmtrx_region_period(year: int, db: Session = Depends(get_db)):
    """get plantMtrx data based on region-wise."""
    try:
        data = db.query(View_PlantMtrx_table.columns.region_name,
                        View_PlantMtrx_table.columns.period,
                        View_PlantMtrx_table.columns.period_with_P,
                        View_PlantMtrx_table.columns.year.label("week"),
                        View_PlantMtrx_table.columns.year,
                        func.sum(View_PlantMtrx_table.columns.value)
                        .label('totalValue_regionWise')) \
            .filter(View_PlantMtrx_table.columns.year == year,
                    View_PlantMtrx_table.columns.status == 'active') \
            .group_by(View_PlantMtrx_table.columns.year,
                      View_PlantMtrx_table.columns.region_id,
                      View_PlantMtrx_table.columns.region_name,
                      View_PlantMtrx_table.columns.period,
                      View_PlantMtrx_table.columns.period_with_P) \
            .order_by(View_PlantMtrx_table.columns.region_id,
                      View_PlantMtrx_table.columns.period).all()
        if not data: # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No data is found for this region:")
        return {"status": "success", "plant_mtrx_regionWise": data}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def func_getcrop_type(period, week, year, growing_area_id, db: Session = Depends(get_db)):
    fresh_arr = db.query(models.growing_area.fresh_period_start,
                         models.growing_area.fresh_week_start,
                         models.growing_area.fresh_period_end,
                         models.growing_area.fresh_week_end) \
        .filter(models.growing_area.growing_area_id == growing_area_id).first()

    if fresh_arr.fresh_period_start is not None and fresh_arr.fresh_week_start is not None:
        lower_limit = (fresh_arr.fresh_period_start * 4) + fresh_arr.fresh_week_start
        upper_limit = (fresh_arr.fresh_period_end * 4) + fresh_arr.fresh_week_end
    else:
        lower_limit = 22
        upper_limit = 44

    compare_value = (period * 4) + week

    if lower_limit <= compare_value <= upper_limit:
        crop_type = "Fresh"
        crop_year = str(year)
    elif compare_value < lower_limit:
        crop_type = "Storage"
        crop_year = str(year - 1) + "-" + str(year)[-2:]
    else:
        crop_type = "Storage"
        crop_year = str(year) + "-" + str(year + 1)[-2:]

    return crop_type, crop_year


def update_extension(growing_area_id, year, period, week,db: Session): # pragma: no cover
    """Update the extension value if actual volume is changed."""
    matrix_data_fresh = db.query(models.View_Matrix_growingarea.columns.value) \
        .filter(models.View_Matrix_growingarea.columns.growing_area_id == growing_area_id,
                models.View_Matrix_growingarea.columns.year == year,
                models.View_Matrix_growingarea.columns.period == period,
                models.View_Matrix_growingarea.columns.week == week).first()
            
    matrix_data_storage = db.query(models.View_Matrix_growingarea.columns.value) \
        .filter(models.View_Matrix_growingarea.columns.growing_area_id == growing_area_id,
                models.View_Matrix_growingarea.columns.year == year,
                models.View_Matrix_growingarea.columns.period == period,
                models.View_Matrix_growingarea.columns.week == week) .first()

       
    if 6 < period < 9:
        extensionMapping.update_extension_plantmtrx(growing_area_id, year - 1,
                                                    period, week,
                                                    matrix_data_storage[0], db)
    elif 10 < period < 13:
        extensionMapping.update_extension_plantmtrx(growing_area_id, year,
                                                    period, week,
                                                    matrix_data_fresh[0], db)


@router.post('/update_plantMtrx')
def update_plantmtrx(payload: schemas.PlantMtrxPayload, db: Session = Depends(get_db)): # pragma: no cover
    data = payload.data
    update_count = 0
    try:
        for item in data:
            region_id = db.query(models.Plant.region_id) \
                    .filter(models.Plant.plant_id == item.plant_id).first()
            crop_type, crop_year = func_getcrop_type(item.period, item.week, item.year,
                                                         item.growing_area_id, db)
            if item.update == 0:
                plantmtrx_id = str(item.plant_id) + "#" + str(region_id.region_id) + "#" + str(crop_year) + "#" + \
                           str(item.period) + "#" + str(item.week) + "#" + str(item.growing_area_id)
            else:
                plantmtrx_id = item.plant_matrix_id
            existing_record = db.query(models.plantMtrx).filter(
                models.plantMtrx.plant_matrix_id == plantmtrx_id).first()
            if existing_record is None:
                """New record is added to the plantMtrx."""
                payload = {"plant_matrix_id": plantmtrx_id,
                           "plant_id": item.plant_id, "region_id": region_id.region_id,
                           "growing_area_id": item.growing_area_id, "period": item.period,
                           "week": item.week, "year": item.year, "value": item.value,
                           "crop_type": crop_type, "crop_year": crop_year, "status": "active",
                           "type": "forecast"}
                new_record = models.plantMtrx(**payload)
                db.add(new_record)
            else:
                """Updating growing_area value to the plantMtrx."""
                existing_record.value = item.value
                if item.value == 0:
                    existing_record.status = 'inactive'
                else:
                    existing_record.status = 'active'
            db.commit()
            """Update the extension value if value is changed in extension window."""
            if (6 < item.period < 9) or (10 < item.period < 13):
                update_extension(item.growing_area_id, item.year, item.period, item.week, db)
            update_count += 1
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewMatrix/{year}')
def createnew_plantmatrix(year: int):  # pragma: no cover
    """for all plants generate the plant_mtrx data for Next year based on existing year data"""
    db = SessionLocal()
    try:
        record_count = 0
        existing_records = db.query(plantMtrx).filter(plantMtrx.year == year).all()
        if len(existing_records) != 0:
            for record in existing_records:
                db.delete(record)
            db.commit()
        plt_matx_ny = db.query(plantMtrx).filter(plantMtrx.year == year-1,
                                                 plantMtrx.status == 'active',
                                                 plantMtrx.plant_id != 26).all()
        for plant in plt_matx_ny:
            plant_id = plant.plant_id
            period = plant.period
            week = plant.week
            region_id = plant.region_id
            growing_area_id = plant.growing_area_id
            value = plant.value
            status = plant.status

            plant_status = db.query(models.plant_status.status).filter(models.plant_status.plant_id==plant_id,
                                                                models.plant_status.year==year).first()
            
            status = plant_status[0] if plant_status else 'ACTIVE'

            if status != 'ACTIVE':
                continue
            
            crop_type, crop_year = func_getcrop_type(period, week, year,growing_area_id, db)

            plantmtrx_id = str(plant_id) + "#" + str(region_id) + "#" + str(crop_year) + "#" + \
                           str(period) + "#" + str(week) + "#" + str(growing_area_id)

            # Multiplying CY value with allocation value
            plant_db = db.query(Plant.company_name).filter(Plant.plant_id==plant_id).first()
            company = ""
            if plant_db and plant_db.company_name=="US-CORE":
                company = "FLUS"
            elif plant_db and plant_db.company_name== "CO-MAN":
                company = "Co-Man"
            elif plant_db and plant_db.company_name=="CANADA-CORE":
                company = "FLC"
            try:
                allocation_db = db.query(allocation.backend_value).filter(allocation.year==year,
                                                        allocation.period==period,
                                                        allocation.category_name==company).first()
            except Exception as e:
                raise HTTPException(status_code=400, detail="Allocation data not found")

            final_value = (value*allocation_db.backend_value)/100

            existing_rec = db.query(models.plantMtrx).filter(models.plantMtrx.plant_matrix_id==plantmtrx_id).first()
            if not existing_rec:
                plantmtrx_payload = {"plant_matrix_id": plantmtrx_id,
                                     "region_id": region_id, 
                                     "plant_id": plant_id,
                                     "growing_area_id": growing_area_id,
                                     "period": period, 
                                     "week": week,
                                     "year": year, 
                                     "crop_type": crop_type,
                                     "crop_year": crop_year,
                                     "value": final_value,
                                     "status": status,
                                     "type": 'forecast'}
                newplantmtrx_record = models.plantMtrx(**plantmtrx_payload)
                db.add(newplantmtrx_record)
                db.commit()
                record_count+=1
            else:
                setattr(existing_rec,"value",existing_rec.value+final_value)
                db.commit()

            if period == 13 and week == 4:
                if period_week_calc.calculate_week_num(year, int(period)):
                    week = 5
                    plantmtrx_id = str(plant_id) + "#" + str(region_id) + "#" + str(crop_year) + "#" + \
                           str(period) + "#" + str(week) + "#" + str(growing_area_id)
                    plantmtrx_payload = {"plant_matrix_id": plantmtrx_id,
                                         "region_id": region_id, 
                                         "plant_id": plant_id,
                                         "growing_area_id": growing_area_id,
                                         "period": period, 
                                         "week": week,
                                         "year": year, 
                                         "crop_type": crop_type,
                                         "crop_year": crop_year,
                                         "value": final_value,
                                         "status": status,
                                         "type": 'forecast'}
                    newplantmtrx_record = models.plantMtrx(**plantmtrx_payload)
                    db.add(newplantmtrx_record)
                    record_count+=1
                    db.commit()

        #Handling Zero values
        pc_usage_ny = (db.query(pcusage).filter(pcusage.year==year,pcusage.forecasted_value!=0).all())
        handling_zero_values(pc_usage_ny,0,db)

        return {"status": "Success","record_count": record_count}
    
    except Exception as e:
        error_message = f"Error after creation stage: {e!r}"
        raise HTTPException(status_code=400, detail=error_message)

def handling_zero_values(pc_usage_ny,index,db: Session = Depends(get_db)): # pragma: no cover

    try:
        print("PC Usage data size",len(pc_usage_ny))
        handled_data = []
        for items in pc_usage_ny:

            plant_matrix_ny = (db.query(plantMtrx.plant_id,
                                    plantMtrx.year,
                                    plantMtrx.period,
                                    plantMtrx.week,
                                    plantMtrx.region_id,
                                    func.sum(plantMtrx.value).label('value'))
                             .group_by(plantMtrx.plant_id,
                                       plantMtrx.year,
                                       plantMtrx.period,
                                       plantMtrx.week,
                                       plantMtrx.region_id)
                             .having(and_(plantMtrx.plant_id==items.plant_id,
                                          plantMtrx.year == items.year,
                                          plantMtrx.period == items.period,
                                          plantMtrx.week == items.week_no))
                             .first())
            forecast_value = items.forecasted_value
            print("forecast_value:",forecast_value)
            print('year',items.year,'plant',items.plant_id,'period',items.period,'week',items.week_no)
            if plant_matrix_ny is None:
                handled_data.append((items.plant_id,items.period,items.forecasted_value,items.year))
                print('handling none')
                contribution_list = contribution_value(items.plant_id,items.year,items.period,forecast_value,db)
                for ga,val in contribution_list.items():
                    crop_type, crop_year = func_getcrop_type(items.period, items.week_no, items.year,ga, db)
                    print("cy,ct success")
                    region = db.query(Plant).filter(Plant.plant_id==items.plant_id).first()
                    print("region",region.region_id)
                    plantmtrx_id = str(items.plant_id) + "#" + str(region.region_id) + "#" + str(crop_year) + "#" + \
                           str(items.period) + "#" + str(items.week_no) + "#" + str(ga)
                    print('before payload')
                    if index==0:
                        val = val*1
                    else:
                        val = (val*index)/100
                    plantmtrx_payload = {"plant_matrix_id": plantmtrx_id,
                                     "region_id": region.region_id, 
                                     "plant_id": items.plant_id,
                                     "growing_area_id": ga,
                                     "period": items.period, 
                                     "week": items.week_no,
                                     "year": items.year, 
                                     "crop_type": crop_type,
                                     "crop_year": crop_year,
                                     "value": val,
                                     "status": 'active',
                                     "type": 'forecast'}
                    print('after payload')
                    newplantmtrx_record = models.plantMtrx(**plantmtrx_payload)
                    db.add(newplantmtrx_record)
                db.commit()
            elif plant_matrix_ny.value==0:
                handled_data.append((items.plant_id,items.period,items.forecasted_value,items.year))
                print('handling zero')
                deleting_rec = (db.query(plantMtrx)
                                  .filter(plantMtrx.plant_id==items.plant_id,
                                          plantMtrx.year==items.year,
                                          plantMtrx.period==items.period,
                                          plantMtrx.week==items.week_no)
                                 .all())
                for rec in deleting_rec:
                    db.delete(rec)
                db.commit()

                contribution_list = contribution_value(items.plant_id,items.year,items.period,forecast_value,db)
                for ga,val in contribution_list.items():
                    crop_type, crop_year = func_getcrop_type(items.period, items.week_no, items.year,ga, db)
                    print("cy,ct success")
                    plantmtrx_id = str(items.plant_id) + "#" + str(plant_matrix_ny.region_id) + "#" + str(crop_year) + "#" + \
                           str(items.period) + "#" + str(items.week_no) + "#" + str(ga)
                    print('before payload')
                    if index==0:
                        val = val*1
                    else:
                        val = (val*index)/100
                    plantmtrx_payload = {"plant_matrix_id": plantmtrx_id,
                                     "region_id": plant_matrix_ny.region_id, 
                                     "plant_id": items.plant_id,
                                     "growing_area_id": ga,
                                     "period": items.period, 
                                     "week": items.week_no,
                                     "year": items.year, 
                                     "crop_type": crop_type,
                                     "crop_year": crop_year,
                                     "value": val,
                                     "status": 'active',
                                     "type": 'forecast'}
                    print('after payload')
                    newplantmtrx_record = models.plantMtrx(**plantmtrx_payload)
                    db.add(newplantmtrx_record)
                db.commit()
        print("Handled Data:",handled_data)
        handling_threshold(handled_data,db)
    except Exception as e:
        error_message = f"Error after handling zero stage: {e!r}"
        raise HTTPException(status_code=400, detail=error_message)
    

def handling_threshold(handled_data, db: Session = Depends(get_db)): # pragma: no cover
    try:
        print("Threshold Handling Start")
        threshold = 0.3
        unique_handled_data = list(set(handled_data))
        print("Unique Handled Data:",unique_handled_data)
        new_unique_handled_data = []
        for plant_id, period, forecasted_value, year in unique_handled_data:
            total = db.query(func.sum(plantMtrx.value)).filter(plantMtrx.plant_id==plant_id,
                                                           plantMtrx.year==year-1,
                                                           plantMtrx.period==period).scalar()
            if total!=0:
                new_unique_handled_data.append((plant_id, period, forecasted_value, year))
        plant_id, period, forecasted_value, year = (None, None, None, None)
        for plant_id, period, forecasted_value, year in new_unique_handled_data:
            plant_mtrx_data = (db.query(models.plantMtrx.period,
                                     models.plantMtrx.week,
                                     func.sum(models.plantMtrx.value).label('value'))
                              .filter(models.plantMtrx.year == year-1,
                                      models.plantMtrx.period == period,
                                      models.plantMtrx.plant_id == plant_id)
                              .group_by(models.plantMtrx.period,
                                        models.plantMtrx.week).all())
            weekly_plant_avg = (db.query(func.sum(models.plant_weekly_average.value)).filter(models.plant_weekly_average.plant_id==plant_id,
                                                                                             models.plant_weekly_average.year==year-1).scalar())
            # Add this check
            if not weekly_plant_avg:  # This correctly handles both 0 and None
                print(f"Skipping threshold check for plant_id: {plant_id}, period: {period} (weekly_plant_avg is 0 or None)")
                continue
            for items in plant_mtrx_data:
                if items.value!=0:
                    abs_diff = abs(items.value - weekly_plant_avg) if weekly_plant_avg else 0
                    if (abs_diff / weekly_plant_avg) > threshold:
                        print("Threshold breached for plant_id:",plant_id,"period:",period,"week:",items.week)
                        contribution_list = contribution_value_threshold(plant_id,year,period,items.week,forecasted_value,db)
                        print("Contribution List:",contribution_list)
                        for ga,val in contribution_list.items():
                            plantmtrx_data_update = db.query(plantMtrx).filter(plantMtrx.plant_id==plant_id,
                                                                         plantMtrx.year==year,
                                                                         plantMtrx.period==period,
                                                                         plantMtrx.week==items.week,
                                                                         plantMtrx.growing_area_id==ga).first()
                            if plantmtrx_data_update:
                                plantmtrx_data_update.value = val
                                db.commit()
        print("Threshold Handling End")
    except Exception as e:
        error_message = f"Error in handling_threshold: {e!r} Data that was being processed: {plant_id, period, forecasted_value, year}"
        raise HTTPException(status_code=400, detail=error_message)

def contribution_value(plant_id:int,year:int,period:int,forecasted_value:float,db: Session = Depends(get_db)): # pragma: no cover
    try:
        total = db.query(func.sum(plantMtrx.value)).filter(plantMtrx.plant_id==plant_id,
                                                           plantMtrx.year==year-2,
                                                           plantMtrx.period==period).scalar()
        
        previous_yr_contribution = []
        if total and total != 0:
            previous_yr_contribution = (db.query(plantMtrx.plant_id,
                                             plantMtrx.year,
                                             plantMtrx.period,
                                             plantMtrx.growing_area_id,
                                             func.sum(plantMtrx.value).label('value'),
                                             (func.sum(plantMtrx.value)/total).label('contribution'))
                                      .group_by(plantMtrx.plant_id,plantMtrx.period,plantMtrx.year,plantMtrx.growing_area_id)
                                      .having(and_(plantMtrx.plant_id==plant_id,
                                                   plantMtrx.year==year-2,
                                                   plantMtrx.period==period))
                                      .all())

        if not previous_yr_contribution:

            total = db.query(func.sum(plantMtrx.value)).filter(plantMtrx.plant_id==plant_id,
                                                           plantMtrx.year==year-1).scalar()
            previous_yr_contribution = (db.query(plantMtrx.plant_id,
                                             plantMtrx.year,
                                             plantMtrx.growing_area_id,
                                             func.sum(plantMtrx.value).label('value'),
                                             (func.sum(plantMtrx.value)/total).label('contribution'))
                                      .group_by(plantMtrx.plant_id,plantMtrx.year,plantMtrx.growing_area_id)
                                      .having(and_(plantMtrx.plant_id==plant_id,
                                                   plantMtrx.year==year-1))
                                      .all())

        len_rec = len(previous_yr_contribution)
        normalized_list = []
        total_contribution = sum(items.contribution for items in previous_yr_contribution)
        for items in previous_yr_contribution:
            normalized_contribution = items.contribution / total_contribution
            normalized_list.append((items.growing_area_id, normalized_contribution))
        count = 1
        ga_split = {}
        alloted_value = 0
        for growing_area_id,contribution in normalized_list:
            if count==len_rec:
                ga_split[growing_area_id] = forecasted_value-alloted_value
            else:
                ga_split[growing_area_id] = contribution*forecasted_value
                alloted_value+=contribution*forecasted_value
                count+=1
        return ga_split
        
    except Exception as e:
        error_message = f"Error in contribution_value: {e!r}"
        raise HTTPException(status_code=400, detail=error_message)

def contribution_value_threshold(plant_id:int,year:int,period:int,week:int,forecasted_value:float,db: Session = Depends(get_db)): # pragma: no cover
    try:
        total = db.query(func.sum(plantMtrx.value)).filter(plantMtrx.plant_id==plant_id,
                                                           plantMtrx.year==year-1,
                                                           plantMtrx.period==period,
                                                           plantMtrx.week==week).scalar()

        py_contribution = (db.query(plantMtrx.plant_id,
                                             plantMtrx.year,
                                             plantMtrx.period,
                                             plantMtrx.week,
                                             plantMtrx.growing_area_id,
                                             func.sum(plantMtrx.value).label('value'),
                                             (func.sum(plantMtrx.value)/total).label('contribution'))
                                      .group_by(plantMtrx.plant_id,plantMtrx.period,plantMtrx.week,plantMtrx.year,plantMtrx.growing_area_id)
                                      .having(and_(plantMtrx.plant_id==plant_id,
                                                   plantMtrx.year==year-1,
                                                   plantMtrx.period==period,
                                                   plantMtrx.week==week))
                                      .all())

        len_rec = len(py_contribution)
        normalized_list = []
        total_contribution = sum(items.contribution for items in py_contribution)
        for items in py_contribution:
            normalized_contribution = items.contribution / total_contribution
            normalized_list.append((items.growing_area_id, normalized_contribution))
        count = 1
        ga_split = {}
        alloted_value = 0
        for growing_area_id,contribution in normalized_list:
            if count==len_rec:
                ga_split[growing_area_id] = forecasted_value-alloted_value
            else:
                ga_split[growing_area_id] = contribution*forecasted_value
                alloted_value+=contribution*forecasted_value
                count+=1
        return ga_split
        
    except Exception as e:
        error_message = f"Error in contribution_value_threshold: {e!r}"
        raise HTTPException(status_code=400, detail=error_message)


def update_first_period_data(
    current_period: int,
    current_week: int,
    current_year: int,
    new_record_count: int,
    db: Session,
) -> int:   # pragma: no cover
    """
    First-period specific logic (kept from your original, with slice-based null-log behavior).
    """
    # Delete existing slice
    if current_week == -1:
        total_week = 5 if period_week_calc.calculate_week_num(current_year, current_period) else 4
        existing = (
            db.query(models.plantMtrx)
            .filter(
                models.plantMtrx.period == current_period,
                models.plantMtrx.year == current_year,
            )
            .all()
        )
        for r in existing:
            db.delete(r)
        db.commit()
    else:
        existing = (
            db.query(models.plantMtrx)
            .filter(
                models.plantMtrx.year == current_year,
                models.plantMtrx.period == current_period,
                models.plantMtrx.week <= current_week,
            )
            .all()
        )
        if not existing:
            total_week = current_week
        else:
            for r in existing:
                db.delete(r)
            db.commit()
            total_week = current_week
    # Iterate weeks
    week = 1
    while week <= total_week:
        try:
            _refresh_null_logs_for_slice(
                db,
                period=current_period,
                week=week,
                year=current_year,
            )
        except Exception:
            db.rollback()
        rows = (
            db.query(models.View_plant_matrix_actual)
            .filter(
                models.View_plant_matrix_actual.columns.period_num == current_period,
                models.View_plant_matrix_actual.columns.week_num == week,
                models.View_plant_matrix_actual.columns.p_year == current_year,
                models.View_plant_matrix_actual.columns.region_id != 14,
            )
            .all()
        )
        if not rows:
            week += 1
            continue
        active_ga_ids = set()
        for item in rows:
            plant_id = int(item.Plant_Id)
            ga_id = int(item.growing_area_id)
            region_id = int(item.region_id) if item.region_id is not None else None
            plant_name = getattr(item, "plant_name", None)
            ga_name = getattr(item, "growing_area_name", None)
            if not _is_view_row_complete(item):
                try:
                    erp_rows = _fetch_erp_null_rows_for_slice_sql(
                        db,
                        plant_id=plant_id,   
                        ga_id=ga_id,
                        year=current_year,
                        period=current_period,
                        week=week,
                    )
                    touched = False
                    for r in erp_rows:
                        if not _erp_row_has_required_null_from_mapping(r):
                            continue
                        try:
                            was_insert = _upsert_null_log(
                                db,
                                erp_row=r,
                                region_id=region_id,
                                plant_name=plant_name,
                                ga_name=ga_name,
                            )
                            touched = touched or was_insert
                        except IntegrityError:
                            db.rollback()
                            try:
                                _upsert_null_log(
                                    db,
                                    erp_row=r,
                                    region_id=region_id,
                                    plant_name=plant_name,
                                    ga_name=ga_name,
                                )
                                touched = True
                            except Exception:
                                db.rollback()
                    if touched:
                        db.commit()
                except Exception:
                    db.rollback()
                # skip plantMtrx insert for this view row
                continue
            payload = {
                "plant_matrix_id": item.row_id,
                "region_id": item.region_id,
                "plant_id": item.Plant_Id,
                "growing_area_id": item.growing_area_id,
                "period": item.period_num,
                "week": item.week_num,
                "year": item.p_year,
                "crop_type": item.crop_type,
                "crop_year": item.storage_period,
                "value": item.sumof_rec_potato,
                "status": "active",
                "type": "actual",
            }
            existing_pm = db.get(models.plantMtrx, item.row_id)
            if not existing_pm:
                rec = models.plantMtrx(**payload)
                db.add(rec)
                try:
                    db.commit()
                    new_record_count += 1
                except IntegrityError:
                    db.rollback()
                except Exception:
                    db.rollback()
            active_ga_ids.add(item.growing_area_id)
        # extension logic
        for ga in active_ga_ids:
            if 6 < current_period < 9 or 10 < current_period < 13:
                try:
                    update_extension(ga, current_year, current_period, week, db)
                except Exception:
                    db.rollback()
        week += 1
    return new_record_count


@router.post("/load_actual_value")
def load_actual_value(db: Session = Depends(get_db)):   # pragma: no cover
    """
    Load actual values in Plant Matrix.
    Behavior:
      - For each slice (period/week) we touch:
          * First refresh null logs for that slice (ERP check).
      - Valid view rows -> insert into plantMtrx (skip if already exists).
      - Null view rows  -> upsert log record (active=1; no duplicates) based on required fields.
    """
    try:
        new_record_count = 0
        today_date = datetime.today()
        res = period_week_calc.calculate_period_and_week(
            today_date.year, today_date.date()
        )
        current_period = int(res["Period"])
        current_week = int(res["week"]) - 1
        current_year = int(res["year"])
        if current_period == 1:
            # first period logic
            new_record_count = update_first_period_data(
                13, -1, current_year - 1, new_record_count, db
            )
            new_record_count = update_first_period_data(
                1, current_week, current_year, new_record_count, db
            )
        else:
            # compute slice to delete
            lower_limit = (current_period - 1) * 5 + 1
            max_limit = current_period * 5 + current_week

            (
                db.query(models.plantMtrx)
                .filter(
                    (models.plantMtrx.period * 5) + models.plantMtrx.week >= lower_limit,
                    (models.plantMtrx.period * 5) + models.plantMtrx.week <= max_limit,
                    models.plantMtrx.year == today_date.year,
                )
                .delete(synchronize_session=False)
            )
            db.commit()
            period_value = current_period - 1
            while period_value <= current_period:
                week_value = 1
                while (period_value * 5 + week_value) <= (current_period * 5 + current_week):
                    try:
                        _refresh_null_logs_for_slice(
                            db,
                            period=period_value,
                            week=week_value,
                            year=current_year,
                        )
                    except Exception:
                        db.rollback()
                    # 2) fetch view rows for this slice
                    actual_rows = (
                        db.query(models.View_plant_matrix_actual)
                        .filter(
                            models.View_plant_matrix_actual.columns.p_year == today_date.year,
                            models.View_plant_matrix_actual.columns.period_num == period_value,
                            models.View_plant_matrix_actual.columns.week_num == week_value,
                            models.View_plant_matrix_actual.columns.region_id != 14,
                        )
                        .all()
                    )
                    if not actual_rows:
                        week_value += 1
                        continue
                    active_ga_ids: Set[int] = set()
                    for item in actual_rows:
                        plant_id = int(item.Plant_Id)
                        ga_id = int(item.growing_area_id)
                        region_id = int(item.region_id) if item.region_id is not None else None
                        plant_name = getattr(item, "plant_name", None)
                        ga_name = getattr(item, "growing_area_name", None)
                        if not _is_view_row_complete(item):
                            try:
                                erp_rows = _fetch_erp_null_rows_for_slice_sql(
                                    db,
                                    plant_id=plant_id,  
                                    ga_id=ga_id,
                                    year=current_year,
                                    period=period_value,
                                    week=week_value,
                                )
                                for r in erp_rows:
                                    if not _erp_row_has_required_null_from_mapping(r):
                                        continue
                                    try:
                                        _upsert_null_log(
                                            db,
                                            erp_row=r,
                                            region_id=region_id,
                                            plant_name=plant_name,
                                            ga_name=ga_name,
                                        )
                                    except IntegrityError:
                                        db.rollback()
                                        try:
                                            _upsert_null_log(
                                                db,
                                                erp_row=r,
                                                region_id=region_id,
                                                plant_name=plant_name,
                                                ga_name=ga_name,
                                            )
                                        except Exception:
                                            db.rollback()
                                db.commit()
                            except Exception:
                                db.rollback()
                            # skip plantMtrx insert for this view row
                            continue
                        payload = {
                            "plant_matrix_id": item.row_id,
                            "region_id": item.region_id,
                            "plant_id": item.Plant_Id,
                            "growing_area_id": item.growing_area_id,
                            "period": item.period_num,
                            "week": item.week_num,
                            "year": item.p_year,
                            "crop_type": item.crop_type,
                            "crop_year": item.storage_period,
                            "value": item.sumof_rec_potato,
                            "status": "active",
                            "type": "actual",
                        }
                        existing = db.get(models.plantMtrx, item.row_id)
                        if not existing:
                            rec = models.plantMtrx(**payload)
                            db.add(rec)
                            try:
                                db.commit()
                                new_record_count += 1
                            except IntegrityError:
                                db.rollback()
                            except Exception:
                                db.rollback()
                        active_ga_ids.add(item.growing_area_id)
                    # 3) Extension logic for this slice
                    for unique_ga_id in active_ga_ids:
                        if (6 < period_value < 9) or (10 < period_value < 13):
                            try:
                                update_extension(
                                    unique_ga_id,
                                    current_year,
                                    period_value,
                                    week_value,
                                    db,
                                )
                            except Exception:
                                db.rollback()
                    week_value += 1
                period_value += 1
        return {"status": "success", "record_updated": new_record_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/load_previous_data_week_wise")
def temp_insert_week_wise(
    period: int,
    week: int,
    year: int,
    db: Session = Depends(get_db),
):  # pragma: no cover
    try:
        # 1) Refresh existing logs for this slice
        try:
            _refresh_null_logs_for_slice(db, period=period, week=week, year=year)
        except Exception:
            db.rollback()
        new_record_count = 0
        # 2) Delete existing plantMtrx rows for this slice
        (
            db.query(models.plantMtrx)
            .filter(
                models.plantMtrx.period == period,
                models.plantMtrx.week == week,
                models.plantMtrx.year == year,
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        # 3) Fetch VIEW rows
        view_rows = (
            db.query(models.View_plant_matrix_actual)
            .filter(
                models.View_plant_matrix_actual.columns.period_num == period,
                models.View_plant_matrix_actual.columns.week_num == week,
                models.View_plant_matrix_actual.columns.p_year == year,
                models.View_plant_matrix_actual.columns.region_id != 14,
            )
            .all()
        )
        active_ga_ids = set()
        # 4) Process each VIEW row
        for item in view_rows:
            plant_id = int(item.Plant_Id)
            ga_id = int(item.growing_area_id)
            plant_name = getattr(item, "plant_name", None)
            ga_name = getattr(item, "growing_area_name", None)
            region_id = getattr(item, "region_id", None)
            if not _is_view_row_complete(item):
                try:
                    erp_rows = _fetch_erp_null_rows_for_slice_sql(
                        db,
                        plant_id=plant_id,     
                        ga_id=ga_id,    
                        year=year,
                        period=period,
                        week=week,
                    )
                    for erp_row in erp_rows:
                        if not _erp_row_has_required_null_from_mapping(erp_row):
                            continue
                        try:
                            _upsert_null_log(
                                db,
                                erp_row=erp_row,
                                region_id=region_id,
                                plant_name=plant_name,
                                ga_name=ga_name,
                            )
                        except IntegrityError:
                            db.rollback()
                            continue
                    db.commit()
                except Exception:
                    db.rollback()
                # Skip plantMtrx insert
                continue
            existing_pm = db.get(models.plantMtrx, item.row_id)
            if not existing_pm:
                payload = {
                    "plant_matrix_id": item.row_id,
                    "region_id": item.region_id,
                    "plant_id": item.Plant_Id,
                    "growing_area_id": item.growing_area_id,
                    "period": item.period_num,
                    "week": item.week_num,
                    "year": item.p_year,
                    "crop_type": item.crop_type,
                    "crop_year": item.storage_period,
                    "value": item.sumof_rec_potato,
                    "status": "active",
                    "type": "actual",
                }
                rec = models.plantMtrx(**payload)
                db.add(rec)
                try:
                    db.commit()
                    new_record_count += 1
                except Exception:
                    db.rollback()
            if item.growing_area_id:
                active_ga_ids.add(item.growing_area_id)
        # 4) Extension logic
        if view_rows:
            last = view_rows[-1]
            for ga in active_ga_ids:
                try:
                    if 6 < last.period_num < 9 or 10 < last.period_num < 13:
                        update_extension(
                            ga,
                            int(last.p_year),
                            int(last.period_num),
                            int(last.week_num),
                            db,
                        )
                except Exception:
                    db.rollback()
        return {"status": "success", "record_updated": new_record_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/load_previous_year_data')
def prev_year_insert(year: int, db: Session = Depends(get_db)):  # pragma: no cover
    try:
        new_record_count = 0
        period_value = 1
        while period_value <= 13:
            current_week = 1
            if period_week_calc.calculate_week_num(year, int(period_value)):
                no_of_week = 5
            else:
                no_of_week = 4
            while current_week <= no_of_week:
                # delete of forecast data
                records_to_delete = db.query(models.plantMtrx).filter(models.plantMtrx.period == period_value,
                                                                      models.plantMtrx.week == current_week,
                                                                      models.plantMtrx.year == year).all()
                for record in records_to_delete:
                    db.delete(record)
                db.commit()
                actual_data_current_week = db.query(models.View_plant_matrix_actual) \
                    .filter(models.View_plant_matrix_actual.columns.period_num == period_value,
                            models.View_plant_matrix_actual.columns.week_num == current_week,
                            models.View_plant_matrix_actual.columns.p_year == year,
                            models.View_plant_matrix_actual.columns.region_id != 14).all()
                for item in actual_data_current_week:
                    new_record_count += 1
                    plantmtrx_payload = {"plant_matrix_id": item.row_id,
                                         "region_id": item.region_id, "plant_id": item.Plant_Id,
                                         "growing_area_id": item.growing_area_id, "period": item.period_num,
                                         "week": item.week_num, "year": item.p_year, "crop_type": item.crop_type,
                                         "crop_year": item.storage_period, "value": item.sumof_rec_potato,
                                         "status": 'active', "type": 'actual'}
                    newplantmtrx_record = models.plantMtrx(**plantmtrx_payload)
                    db.add(newplantmtrx_record)

                db.commit()
                current_week += 1
            period_value += 1

        return {"status": "success", "record_updated": new_record_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload_file/")
async def upload_plant_matrix_file(file: UploadFile = File(...), db: Session = Depends(get_db)):  # pragma: no cover
    try:
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are allowed")
        contents = file.file.read()
        # Check the file type and read data accordingly
        if file.filename.lower().endswith(".csv"):
            s = str(contents, 'utf-8')
            data_byte = StringIO(s)
            df = pd.read_csv(data_byte)
        else:
            data_byte = BytesIO(contents)
            df = pd.read_excel(data_byte)
        print(df)

        df_unpivoted = df.melt(id_vars=['plant name', 'year'], var_name='period_week_number',
                               value_name='area_volume_string')

        # Extract period and week numbers from the period_week_number column
        df_unpivoted[['period', 'week']] = df_unpivoted['period_week_number'].str.split('x', expand=True)

        df_unpivoted['area_volume_string_single'] = df_unpivoted['area_volume_string'].str.split(',')
        # Explode the areas column to create separate rows for each area

        df_unpivoted = df_unpivoted.explode('area_volume_string_single')
        # Split the area_volume_string into separate columns

        df_unpivoted[['areas', 'volume']] = df_unpivoted['area_volume_string_single'] \
            .str.split(':', expand=True)

        # Reset index to ensure correct alignment
        df_unpivoted = df_unpivoted.reset_index(drop=True)

        df_final = df_unpivoted[['plant name', 'areas', 'year', 'period', 'week', 'volume']]

        print(df_final)
        for index, row in df_final.iterrows():
            # Assuming the plant name is in the first column of the DataFrame
            plant_name = row[0]

            # Query the plants table to get the plant ID based on the plant name
            plant_id = db.query(models.Plant.plant_id) \
                .filter(models.Plant.plant_name == plant_name).scalar()
            if not plant_id:
                raise HTTPException(status_code=404, detail=f"Plant '{plant_name}' not found")
            print(plant_id, row)
        return {"message": "Data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/plant_status/{current_year}')
def get_plants_online(current_year: int, db: Session = Depends(get_db)):
    """get api for plant status."""
    data = db.query(models.plant_status).filter(models.plant_status.year == current_year).all()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No plants found")
    return {"status": "success", "plants": data}


@router.post('/plant_status_update', status_code=status.HTTP_201_CREATED)
async def update_plant_status(payload: List[schemas.PlantStatusPayload],background_tasks: BackgroundTasks, db: Session = Depends(get_db)):# pragma: no cover
    
    # Updated time"
    cst = pytz.timezone("US/Central")
    updated_time = datetime.now(cst).strftime("%Y-%m-%d %H:%M")
    try:
        for plant_data in payload:
            db_record = db.query(models.plant_status).filter(
                models.plant_status.plant_id == plant_data.plant_id,
                models.plant_status.year == plant_data.year
            ).first()

            # If the record exists, update it
            if db_record:
                db_record.status = plant_data.status
                db_record.updated_time = updated_time
                db.commit()
            
            current_plant_data = (db.query(models.View_forecast_pcusage.columns.year,
                                          models.View_forecast_pcusage.columns.period,
                                          models.View_forecast_pcusage.columns.week,
                                          models.View_forecast_pcusage.columns.company_name,
                                          models.View_forecast_pcusage.columns.total_actual_value,
                                          models.View_forecast_pcusage.columns.forecasted_value )
                                    .filter(models.View_forecast_pcusage.columns.plant_id == plant_data.plant_id,
                                            models.View_forecast_pcusage.columns.year == plant_data.year).all())
            #background_tasks.add_task(handling_data,current_plant_data, plant_data.plant_id,plant_data.year)
            handling_data(current_plant_data, plant_data.plant_id,plant_data.year)
            return {"Status": "success", "message": "Volume has been successfully removed from the db"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def handling_data(data: List[Row], plant_id:int, year:int):# pragma: no cover  

    try:        
        db = SessionLocal()
        print("Year :", year)
        for record in data:
            print(f"Period : {record.period} , Week : {record.week}")
            print("PC_Usage Entering")
            # Handling PC Usage
            plan_data = (db.query(func.sum(models.View_forecast_pcusage.columns.forecasted_value))
                                .filter(models.View_forecast_pcusage.columns.period == record.period,
                                        models.View_forecast_pcusage.columns.week == record.week,
                                        models.View_forecast_pcusage.columns.year == record.year,
                                        models.View_forecast_pcusage.columns.company_name == record.company_name)
                                        .scalar())

            p_index = plan_data / (plan_data - record.forecasted_value) if (plan_data - record.forecasted_value) !=0 else 0
            print(f"p_index : {p_index}")
            pcusage_record = (db.query(models.pcusage)
                              .join(models.Plant,
                                    models.Plant.plant_id == models.pcusage.plant_id)
                                .filter(models.pcusage.year == record.year,
                                        models.pcusage.period == record.period,
                                        models.pcusage.week_no == record.week,
                                        models.Plant.company_name == record.company_name).all())
                 
            for pc_record in pcusage_record:
                print(f"Plant id {pc_record.plant_id}")
                if pc_record.plant_id == plant_id:
                    pc_record.forecasted_value = 0
                else:
                    pc_record.forecasted_value = pc_record.forecasted_value * p_index
            db.commit()
            print("PC_Usage Exiting")
            # Handling Plant Matrix
            print("PlantMtrx Entering")
            actual_data = (db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value))
                                .filter(models.View_forecast_pcusage.columns.period == record.period,
                                        models.View_forecast_pcusage.columns.week == record.week,
                                        models.View_forecast_pcusage.columns.year == record.year,
                                        models.View_forecast_pcusage.columns.company_name == record.company_name)
                                        .scalar())

            a_index = actual_data / (actual_data - record.total_actual_value) if (actual_data - record.total_actual_value) !=0 else 0

            print(f"a_index : {a_index}")
            plant_matrix = (db.query(models.plantMtrx)
                              .join(models.Plant,
                                    models.Plant.plant_id == models.plantMtrx.plant_id)
                              .filter(models.plantMtrx.year == record.year,
                                      models.plantMtrx.period == record.period,
                                      models.plantMtrx.week == record.week,
                                      models.plantMtrx.status == 'active',
                                      models.Plant.company_name == record.company_name).all())

            for items in plant_matrix:
                print(f"Plant id {items.plant_id}")
                if items.plant_id == plant_id:
                    items.value = 0
                else:
                    items.value = items.value * a_index
            db.commit()
            print("PlantMtrx Exiting")   
        return {"message": "Successfully updated the data"}
    except Exception as e:
        print(f"CRITICAL ERROR IN BACKGROUND TASK: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/plant_status_next_year/{year}', status_code=status.HTTP_201_CREATED)
async def plant_status_ny(year: int, db: Session = Depends(get_db)):# pragma: no cover
    try:
        # Define your mappings in a dictionary
        company_map = {"US-CORE" :"FLUS","CANADA-CORE": "FLC","CO-MAN": "Co-Man"}

        plant_status_cy = db.query(models.Plant).filter(
                models.Plant.status == 'Active',
                models.Plant.plant_id != 26
            ).all()
        
        plant_status_ny = []
        for records in plant_status_cy:
            ny_payload = models.plant_status(
                plant_id=records.plant_id,
                plant_name=records.plant_name,
                year=year,
                category_name= company_map.get(records.company_name),
                status=str.strip(records.status).upper()
                )
            plant_status_ny.append(ny_payload)
        db.add_all(plant_status_ny)
        db.commit()
        return {"message": f"Successfully created plant status for NY plants in {year}."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An error occurred during the update: {str(e)}")
      

@router.post("/refresh_null_logs_daily")
def refresh_null_logs_daily(db: Session = Depends(get_db)):  # pragma: no cover
    """Refresh active null logs by rechecking ERP and marking resolved when required ERP fields are present."""
    try:
        active_logs: List[models.PlantMtrxNullLog] = (
            db.query(models.PlantMtrxNullLog)
            .filter(models.PlantMtrxNullLog.active == True)
            .all()
        )
        if not active_logs:
            return {
                "status": "success",
                "checked": 0,
                "resolved": 0,
                "still_active": 0,
                "active_logs": [],
            }
        resolved = 0
        for log in active_logs:
            try:
                is_resolved = _is_erp_row_corrected_for_log(db, log)
                if is_resolved:
                    log.active = False
                    log.created_time = _utcnow_naive()
                    db.add(log)
                    resolved += 1
                else:
                    log.created_time = _utcnow_naive()
                    db.add(log)
            except Exception:
                db.rollback()
                continue
        db.commit()
        still_active_logs = (
            db.query(models.PlantMtrxNullLog)
            .filter(models.PlantMtrxNullLog.active == True)
            .all()
        )
        active_logs_payload = [
            {
                "log_id": log.log_id,
                "plant_id": log.plant_id,
                "plant_name": log.plant_name,
                "region_id": log.region_id,
                "growing_area_id": log.growing_area_id,
                "growing_area_name": log.growing_area_name,
                "period": log.period,
                "week": log.week,
                "year": log.year,
                "crop_type": log.crop_type,
                "crop_year": log.crop_year, 
                "bpa_number": log.bpa_number,
                "release_no": log.release_no,
                "shipment": log.shipment,
                "line_no": log.line_no,
                "active": log.active,
                "created_time": (
                    log.created_time.isoformat() if log.created_time else None
                ),
            }
            for log in still_active_logs
        ]
        return {
            "status": "success",
            "checked": len(active_logs),
            "resolved": resolved,
            "still_active": len(still_active_logs),
            "active_logs": active_logs_payload,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))