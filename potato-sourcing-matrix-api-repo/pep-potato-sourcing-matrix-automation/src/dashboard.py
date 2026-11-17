"""Home - Dashboard API"""
from schemas import planVolumeUsagePayload
from sqlalchemy import func
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
import models
from models import pc_plan_volume_usage
import period_week_calc
from sqlalchemy.orm import Session
from dashboard_plan import _get_total_weeks, _get_compare_week
router = APIRouter()


@router.get('/dashboard_pc_plan_volume_usage/{year}')
def dashboard_pc_plan_volume_usage_year(year: int, db: Session = Depends(get_db)):
    """
    Fetch PC plan volume usage records for a specific year.

    Args:
        year (int): Plan year to fetch.
        db (Session): Database session.

    Returns:
        dict: Response with status and list of plan records
            under key ``pc_plan_volume_usage_year``.

    Raises:
        HTTPException: If the database query fails.
    """
    try:
        records = db.query(pc_plan_volume_usage.plan_volume_id,
                           pc_plan_volume_usage.crop_type,
                           models.category.category_name,
                           pc_plan_volume_usage.period,
                           func.concat('P', pc_plan_volume_usage.period).label("period_with_P"),
                           func.concat('p', pc_plan_volume_usage.period, "W",
                                       pc_plan_volume_usage.week).label("PxW"),
                           pc_plan_volume_usage.week,
                           pc_plan_volume_usage.year,
                           pc_plan_volume_usage.volume) \
            .join(models.category, models.category.crop_category == pc_plan_volume_usage.crop_type) \
            .filter(pc_plan_volume_usage.year == year) \
            .order_by(pc_plan_volume_usage.crop_type,
                      pc_plan_volume_usage.period,
                      pc_plan_volume_usage.week).all()
        return {"status": "success", "pc_plan_volume_usage_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/update_plan_volume_usage")
def update_volume_usage(payload: planVolumeUsagePayload, db: Session = Depends(get_db)):
    """
    Update existing PC plan volume usage records.

    Args:
        payload (planVolumeUsagePayload): Payload containing a list of
            plan volume IDs and updated volume values.
        db (Session): Database session.

    Returns:
        dict: Response with status and number of records updated
            under key ``records_updated``.

    Raises:
        HTTPException:
            - 404: If any given plan_volume_id is not found.
            - 400: If a database error occurs during update.
    """
    data = payload.data
    update_count = 0

    for item in data:
        result = db.query(pc_plan_volume_usage) \
            .filter(pc_plan_volume_usage.plan_volume_id == item.plan_volume_id) \
            .update({pc_plan_volume_usage.volume: item.volume}, synchronize_session=False)
        if result == 0:
            raise HTTPException(status_code=404, detail=f"No records found: {item.plan_volume_id}")
        update_count += 1
    db.commit()
    return {"status": "success", "records_updated": update_count}


@router.post("/create_new_plan_volume_usage/year/{year}")
def create_new_volume_usage(year: int, db: Session = Depends(get_db)): 
    """
    Generate next year's PC plan volume usage from previous year values.

    For each crop type, period, and week:
    - Reads last year's volume.
    - Applies the allocation index for the target year.
    - Inserts the computed volume as new plan data.

    Args:
        year (int): New plan year to generate data for.
        db (Session): Database session.

    Returns:
        dict: Response with status and number of new records created
            under key ``new_records_created``.

    Raises:
        HTTPException: If any error occurs while deleting existing records,
            reading allocation/index values, or inserting new rows.
    """
    new_records = 0
    try:
        # 1) Remove existing records for the given year (bulk delete)
        (
            db.query(pc_plan_volume_usage)
            .filter(pc_plan_volume_usage.year == year)
            .delete(synchronize_session=False)
        )

        # 2) Get all crop categories
        category_rows = db.query(
            models.category.crop_category,
            models.category.country,
            models.category.category_name,
        ).all()

        # 3) Loop over categories, periods, and weeks
        for crop_type, _country, category_name in category_rows:
            for period in range(1, 14):  # periods 1..13
                # Allocation index for current year + period + category
                index_row = (
                    db.query(models.allocation.value)
                    .filter(
                        models.allocation.category_name == category_name,
                        models.allocation.year == year,
                        models.allocation.period == period,
                    )
                    .first()
                )

                # How many weeks this period has (4 or 5)
                total_weeks = _get_total_weeks(year, period)

                for week in range(1, total_weeks + 1):
                    # Determine which week to use from last year
                    compare_week = _get_compare_week(week)

                    last_year_volume_row = (
                        db.query(pc_plan_volume_usage.volume)
                        .filter(
                            pc_plan_volume_usage.year == year - 1,
                            pc_plan_volume_usage.crop_type == crop_type,
                            pc_plan_volume_usage.period == period,
                            pc_plan_volume_usage.week == compare_week,
                        )
                        .first()
                    )

                    # Creating next year indexed plan volume
                    new_volume = (last_year_volume_row[0] * index_row.value) / 100

                    plan_volume_id = f"{crop_type}#{period}#{week}#{year}"

                    new_pc_volume = pc_plan_volume_usage(
                        plan_volume_id=plan_volume_id,
                        year=year,
                        crop_type=crop_type,
                        period=period,
                        week=week,
                        volume=new_volume,
                    )
                    db.add(new_pc_volume)
                    new_records += 1

        db.commit()
        return {"status": "success", "new_records_created": new_records}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
