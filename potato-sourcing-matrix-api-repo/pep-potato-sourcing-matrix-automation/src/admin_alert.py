from models import View_erp_raw_alerts,admin_alert,Plant
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
from datetime import date
from sqlalchemy import or_,func, and_
from period_week_calc import calculate_period_and_week

router = APIRouter()
    
#Removed the old API
@router.get('/get_alerts_new', status_code=status.HTTP_201_CREATED)
async def get_erp_alerts_new(db: Session = Depends(get_db)): # pragma: no cover
    """
    Retrieve and process ERP alert data based on current period and week.
    
    This function queries the ERP raw alerts table for records with missing quantity data
    or other missing fields (vendor name, vendor site code, ship-to org, growing area) within
    a 4-week rolling window. It categorizes alerts into two types:
    1. "Volume missing" - records with null Quantity_Accepted_MCWT
    2. "Data missing" - records with null values in vendor, site, org, or growing area fields
    
    The function clears existing alerts before generating new ones and filters out records
    from plant_id 28 (Mexicali plant).
    
    Args:
        db (Session): SQLAlchemy database session dependency for querying the database.
    
    Returns:
        dict: A dictionary containing:
            - "message" (str): Status message indicating if null data was identified or "0" if none found
            - "vol_table" (list): List of tuples containing BPA numbers and counts for volume missing alerts
            - "other_table" (list): List of tuples containing detailed information for data missing alerts
                                    (bpa_number, plant_name, vendor_name, vendor_site_code, 
                                     growing_area, ship_to_org, count)
    
    Raises:
        HTTPException: Status 400 with detail "Error loading alert" if an exception occurs during execution.
    
    Note:
        - The function uses a 4-week rolling window based on the current period and week
        - For period 1 with week < 4, it checks period 13 of the previous year plus current period data
        - Excludes Mexicali plant (plant_id = 28) from all queries
    """

    #Getting current year and period
    today_date = date.today()
    year = int(today_date.year)
    period_week = calculate_period_and_week(year, today_date)
    period = int(period_week['Period'])
    week = int(period_week['week'])
    
    #Retrieving data
    try:
        existing_records = db.query(admin_alert).all()
        if len(existing_records) != 0:
            for record in existing_records:
                db.delete(record)
            db.commit()

        if int(period) ==1 and int(week)<4:
            data = (db.query(View_erp_raw_alerts)
                .filter(or_(
                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == 13,
                        View_erp_raw_alerts.columns.REC_DATE_WK >= int(week)+1,
                        View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year)-1),
                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == int(period),
                        View_erp_raw_alerts.columns.REC_DATE_WK <= int(week),
                        View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year))),
                        View_erp_raw_alerts.columns.plant_id != 28,
                        View_erp_raw_alerts.columns.Quantity_Accepted_MCWT== None).all())
        else:
            lower_limit = (int(period)*5)+int(week)-4
            upper_limit = (int(period)*5)+int(week)
            data = (db.query(View_erp_raw_alerts)
                .filter((View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK >= lower_limit,
                        (View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK <= upper_limit,
                         View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year),
                         View_erp_raw_alerts.columns.plant_id != 28,
                         View_erp_raw_alerts.columns.Quantity_Accepted_MCWT== None).all())
        
    
        null_volume = {}
        for record in data:
            bpa = str(record.BPA_Number)
            if bpa not in null_volume:
                null_volume[bpa]=1
            else:
                null_volume[bpa]+=1
    
        # Updating alert table
        for key,values in null_volume.items():

            admin_payload_1 = {"category": "Volume missing",
                             "bpa_number" : key,
                             "Quantity_Accepted_MCWT" : None,
                             "count": values,
                             "year" : year,
                             "period" : period}

            new_alert_record_1 = admin_alert(**admin_payload_1)
            db.add(new_alert_record_1)
        db.commit()

        vol_table = (db.query(admin_alert.bpa_number,admin_alert.count)
                     .filter(admin_alert.category=="Volume missing")
                     .all())
        
        #Category - 2
        if int(period) ==1 and int(week)<4:
            data = (db.query(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area,
                            func.count().label('count'))
                           .filter(or_(
                                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == 13,
                                             View_erp_raw_alerts.columns.REC_DATE_WK >= int(week)+1,
                                             View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year)-1),
                                        and_(View_erp_raw_alerts.columns.REC_DATE_PD == int(period),
                                             View_erp_raw_alerts.columns.REC_DATE_WK <= int(week),
                                             View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year))),
                                    View_erp_raw_alerts.columns.plant_id != 28, # Ignoring Mexicali plant
                                or_(View_erp_raw_alerts.columns.VENDOR_NAME == None,
                                    View_erp_raw_alerts.columns.VENDOR_SITE_CODE == None,
                                    View_erp_raw_alerts.columns.ShipToOrg == None,
                                    View_erp_raw_alerts.columns.growing_area == None))
                            .group_by(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area)
                            .all())
        else:
            lower_limit = (int(period)*5)+int(week)-4
            upper_limit = (int(period)*5)+int(week)
            data = (db.query(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area,
                            func.count().label('count'))
                           .filter((View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK >= lower_limit,
                                   (View_erp_raw_alerts.columns.REC_DATE_PD * 5) + View_erp_raw_alerts.columns.REC_DATE_WK <= upper_limit,
                                    View_erp_raw_alerts.columns.RECEIPT_YEAR == int(year),
                                    View_erp_raw_alerts.columns.plant_id != 28, # Ignoring Mexicali plant
                                or_(View_erp_raw_alerts.columns.VENDOR_NAME == None,
                                    View_erp_raw_alerts.columns.VENDOR_SITE_CODE == None,
                                    View_erp_raw_alerts.columns.ShipToOrg == None,
                                    View_erp_raw_alerts.columns.growing_area == None))
                            .group_by(View_erp_raw_alerts.columns.BPA_Number,
                            View_erp_raw_alerts.columns.plant_id,
                            View_erp_raw_alerts.columns.VENDOR_NAME,
                            View_erp_raw_alerts.columns.VENDOR_SITE_CODE,
                            View_erp_raw_alerts.columns.ShipToOrg,
                            View_erp_raw_alerts.columns.growing_area)
                            .all())
        
        for rows in data:
            plant_name = db.query(Plant.plant_name).filter(Plant.plant_id == rows.plant_id).first()
            admin_payload_2 = {"category": "Data missing",
                               "bpa_number" : rows.BPA_Number,
                               "plant_name": plant_name.plant_name,
                               "vendor_name": rows.VENDOR_NAME,
                               "vendor_site_code": rows.VENDOR_SITE_CODE,
                               "ship_to_org": rows.ShipToOrg,
                               "growing_area": rows.growing_area,
                               "count": rows.count,
                               "year" : year,
                               "period" : period}

            new_alert_record_2 = admin_alert(**admin_payload_2)
            db.add(new_alert_record_2)
        db.commit()

        other_table = (db.query(admin_alert.bpa_number,
                               admin_alert.plant_name,
                               admin_alert.vendor_name,
                               admin_alert.vendor_site_code,
                               admin_alert.growing_area,
                               admin_alert.ship_to_org,
                               admin_alert.count)
                         .filter(admin_alert.category=="Data missing")
                         .all())

        if len(vol_table)>0 or len(other_table)>0:
            return {"message":"Null data is identified in the erp data", 
                    "vol_table": vol_table,
                    "other_table": other_table}
        else:        
            return {"message":"0", 
                    "vol_table": vol_table,
                    "other_table":other_table}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error loading alert") from e