"""Home - Dashboard Plan API"""
from schemas import pcVolumePlanUsagePayload
from sqlalchemy import func
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
import models
from models import pc_volume_usage_plan
import period_week_calc
from sqlalchemy.orm import Session

router = APIRouter()


@router.get('/dashboard_pc_volume_usage_plan/{year}')
def dashboard_pc_volume_usage_plan_year(year: int, db: Session = Depends(get_db)):
    """
    Get PC volume usage plan for a given year.

    This endpoint returns all records from the ``pc_volume_usage_plan`` table
    for the specified year, including crop type, category name, period, week,
    year, and volume. It also returns formatted fields like ``period_with_P``
    (e.g., "P1") and ``PxW`` (e.g., "p1W3") for UI display.

    Args:
        year (int): Plan year for which data needs to be fetched.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        dict: A response object containing:
            - ``status`` (str): "success" if the query executed correctly.
            - ``pc_volume_usage_plan_year`` (list[tuple]): List of plan records
              for the given year.

    Raises:
        HTTPException: If any unexpected error occurs while querying the DB.

    Example:
        GET /dashboard_pc_volume_usage_plan/2025
    """
    try:
        records = db.query(pc_volume_usage_plan.pc_volume_plan_id,
                           pc_volume_usage_plan.crop_type,
                           models.category.category_name,
                           pc_volume_usage_plan.period,
                           func.concat('P', pc_volume_usage_plan.period).label("period_with_P"),
                           func.concat('p', pc_volume_usage_plan.period, "W",
                                       pc_volume_usage_plan.week).label("PxW"),
                           pc_volume_usage_plan.week,
                           pc_volume_usage_plan.year,
                           pc_volume_usage_plan.volume) \
            .join(models.category, models.category.crop_category == pc_volume_usage_plan.crop_type) \
            .filter(pc_volume_usage_plan.year == year) \
            .order_by(pc_volume_usage_plan.crop_type,
                      pc_volume_usage_plan.period,
                      pc_volume_usage_plan.week).all()
        return {"status": "success", "pc_volume_usage_plan_year": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/update_plan_volume_usage")
def update_plan_volume_usage(payload: pcVolumePlanUsagePayload, db: Session = Depends(get_db)): 
    """
    Bulk update existing PC volume usage plan records.

    This endpoint receives a list of records (identified by
    ``pc_volume_plan_id``) and updates their ``volume`` values.

    Args:
        payload (pcVolumePlanUsagePayload): Request body containing a ``data``
            list, where each item has:
            - ``pc_volume_plan_id`` (str): Identifier of the plan row to update.
            - ``volume`` (float): New volume value to be set.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        dict: A response object containing:
            - ``status`` (str): "success" if the update completed.
            - ``records_updated`` (int): Count of records successfully updated.

    Raises:
        HTTPException:
            - 404: If any provided ``pc_volume_plan_id`` does not exist.
            - 400: For any other DB or validation error.

    Example:
        POST /update_plan_volume_usage

        {
            "data": [
                {
                    "pc_volume_plan_id": "FRESH#1#1#2025",
                    "volume": 123.45
                }
            ]
        }
    """
    data = payload.data
    update_count = 0
    try:
        for item in data:
            result = db.query(pc_volume_usage_plan) \
                .filter(pc_volume_usage_plan.pc_volume_plan_id == item.pc_volume_plan_id) \
                .update({pc_volume_usage_plan.volume: item.volume}, synchronize_session=False)
            if result == 0:
                raise HTTPException(status_code=404, detail=f"No records found: {item.pc_volume_plan_id}")
            update_count += 1
        db.commit()
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

def _get_total_weeks(year: int, period: int) -> int: 
    """
    Determine the number of weeks in a period for a given year.

    Internally uses ``period_week_calc.calculate_week_num`` to decide whether
    the period has 4 or 5 weeks.

    Args:
        year (int): Calendar or plan year.
        period (int): Period number (1-13).

    Returns:
        int: Number of weeks in the period (4 or 5).
    """
    try:
        return 5 if period_week_calc.calculate_week_num(year, period) else 4
    except Exception as e:# pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

def _get_compare_week(week: int) -> int: 
    """
    Get the comparison week used to look up last year's volume.

    Business rule:
    - If ``week == 5``, use week 4 from the previous year.
    - Otherwise, use the same week number.

    Args:
        week (int): Current week number within the period.

    Returns:
        int: Week number to be used when reading last year's plan.
    """
    try:
        return 4 if week == 5 else week
    except Exception as e:# pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/create_new_plan_volume_usage/year/{year}")
def create_new_plan_volume_usage(year: int, db: Session = Depends(get_db)):
    """
    Create a new year's PC volume usage plan based on the previous year.

    This endpoint recreates the PC volume usage plan for the given year by:
    1. Deleting any existing records for that year.
    2. Reading category-wise allocation index for the year and period.
    3. Reading last year's volumes (same period/week, with special handling for week 5).
    4. Computing new volumes as: ``(last_year_volume * allocation_index) / 100``.
    5. Inserting one record per crop type, period, and week.

    Args:
        year (int): Target year for which new plan records should be generated.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        dict: A response object containing:
            - ``status`` (str): "success" if the operation completed.
            - ``new_records_created`` (int): Total number of new records inserted.

    Raises:
        HTTPException: If any error occurs while deleting old records,
            fetching allocation index, fetching last year volumes,
            or inserting new records.

    Example:
        POST /create_new_plan_volume_usage/year/2026
    """
    new_records = 0
    try:
        # 1) Remove existing records for the given year (bulk delete instead of loop)
        (
            db.query(pc_volume_usage_plan)
            .filter(pc_volume_usage_plan.year == year)
            .delete(synchronize_session=False)
        )
        # 2) Get all crop categories
        category_rows = db.query(
            models.category.crop_category,
            models.category.country,
            models.category.category_name,
        ).all()
        # 3) Loop over categories, periods and weeks
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
                    compare_week = _get_compare_week(week)
                    last_year_volume_row = (
                        db.query(pc_volume_usage_plan.volume)
                        .filter(
                            pc_volume_usage_plan.year == year - 1,
                            pc_volume_usage_plan.crop_type == crop_type,
                            pc_volume_usage_plan.period == period,
                            pc_volume_usage_plan.week == compare_week,
                        )
                        .first()
                    )
                    # Creating next year indexed plan volume
                    new_volume = (last_year_volume_row[0] * index_row.value) / 100
                    pc_volume_plan_id = f"{crop_type}#{period}#{week}#{year}"
                    new_pc_volume = pc_volume_usage_plan(
                        pc_volume_plan_id=pc_volume_plan_id,
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



