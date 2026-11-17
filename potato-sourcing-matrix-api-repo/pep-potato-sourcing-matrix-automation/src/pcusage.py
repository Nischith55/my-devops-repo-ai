from sqlalchemy import func
import models
from datetime import date
from models import View_forecast_pcusage
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from database import get_db
import period_week_calc
from database import SessionLocal


router = APIRouter()


def trim(string):
    """Remove all space characters from a string.

    Args:
        string (str): The string to trim.

    Returns:
        str: The input string with all spaces removed.
    """
    try:
        return string.replace(" ", "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def total_forcast_volume_func(filter_cond, year, db):
    """Calculate the total forecasted volume for a given year and filter.

    This helper queries the `View_forecast_pcusage` view to sum the
    `forecasted_value` column for the requested `year` and additional
    filter conditions.

    Args:
        filter_cond (list): Additional SQLAlchemy filter expressions to apply.
        year (int): The year to aggregate.
        db (Session): SQLAlchemy session used for the query.

    Returns:
        list: Query result list (usually one row) containing the total forecast
            volume and the year.
    """
    try:
        total_forecast_volume = db.query(func.sum(View_forecast_pcusage.columns.forecasted_value)
                                         .label('total_forecast_volume'), View_forecast_pcusage.columns.year) \
            .filter(View_forecast_pcusage.columns.year == year,
                    *filter_cond) \
            .group_by(View_forecast_pcusage.columns.year).all()

        return total_forecast_volume
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def total_actual_volume_func(filter_cond, year, db):
    """Calculate the total actual volume for a given year and filter.

    This helper queries the `View_forecast_pcusage` view to sum the
    `total_actual_value` column for the requested `year` and additional
    filter conditions.

    Args:
        filter_cond (list): Additional SQLAlchemy filter expressions to apply.
        year (int): The year to aggregate.
        db (Session): SQLAlchemy session used for the query.

    Returns:
        list: Query result list (usually one row) containing the total actual
            volume and the year.
    """
    try:
        total_actual_volume = db.query(func.sum(View_forecast_pcusage.columns.total_actual_value)
                                       .label('total_actual_volume'), View_forecast_pcusage.columns.year) \
            .filter(View_forecast_pcusage.columns.year == year,
                    *filter_cond) \
            .group_by(View_forecast_pcusage.columns.year).all()
        return total_actual_volume
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def get_filtered_usage_week_common(db, filter_conditions, year, detail_message=None):
    """Fetch weekly PC usage records and aggregate volumes for a filter and year.

    This shared helper is used by multiple API endpoints to fetch weekly
    `View_forecast_pcusage` rows filtered by `filter_conditions` and `year`.

    Args:
        db (Session): Database session dependency.
        filter_conditions (list): Additional SQLAlchemy filter expressions.
        year (int): The year to query.
        detail_message (Optional[str]): Optional message to include in errors.

    Returns:
        dict: A response dictionary with keys:
            - status: 'success' on success.
            - pcusage: List of returned rows ordered by period and week.
            - total_forecast_volume: Aggregated forecast volume for the filter.
            - total_actual_volume: Aggregated actual volume for the filter.

    Raises:
        HTTPException: 400 with details if any database error occurs.
    """
    try:
        result = db.query(View_forecast_pcusage) \
            .filter(View_forecast_pcusage.columns.year == year,
                    *filter_conditions) \
            .order_by(View_forecast_pcusage.columns.period,
                      View_forecast_pcusage.columns.week).all()

        total_forecast_volume = total_forcast_volume_func(filter_conditions, year, db)

        total_actual_volume = total_actual_volume_func(filter_conditions, year, db)

        return {"status": "success", "pcusage": result,
                "total_forecast_volume": total_forecast_volume,
                "total_actual_volume": total_actual_volume}

    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e) or detail_message or "Error processing request")

def get_average_forecast_value(filter_cond, year, db): # pragma: no cover
    """Count the non-zero actual value occurrences for averaging purposes.

    This helper counts the number of non-zero `total_actual_value` entries in
    `View_forecast_pcusage` for a given year and filter. The result is used by
    forecast generation logic to compute averages.

    Args:
    filter_cond (list): Additional SQLAlchemy filter expressions.
    year (int): The year to query.
    db (Session): SQLAlchemy session used for the query.

    Returns:
    list: Query result list containing the count of non-zero actual values grouped by year.
    """
    try:
        average_non_zero_volume = db.query(func.count(View_forecast_pcusage.columns.total_actual_value)
                                       .label('count_zero_values'), View_forecast_pcusage.columns.year) \
            .filter(View_forecast_pcusage.columns.year == year, View_forecast_pcusage.columns.total_actual_value!=0,
                    *filter_cond) \
            .group_by(View_forecast_pcusage.columns.year).all()
        return average_non_zero_volume
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/company_name/{name}/year/{year}')
def get_filtered_usage_by_company_name(name: str, year: int, db: Session = Depends(get_db)):
    """API endpoint: get weekly PC usage filtered by company name.

    Maps the provided `name` to the internal company/country identifier used
    in `View_forecast_pcusage`, builds filter conditions and delegates to
    `get_filtered_usage_week_common`.

    Args:
        name (str): Company name key from the API path.
        year (int): Year to query.
        db (Session): Database session dependency.

    Returns:
        dict: Same structure returned by `get_filtered_usage_week_common`.
    """
    try:
        filter_dict = {
            'US': 'US',
            'US-Core': 'US-CORE',
            'Co-Man': 'CO-MAN',
            'Canada-Core': 'Canada'
        }
        if filter_dict[name] == 'CO-MAN' or filter_dict[name] == 'US-CORE':
            filter_conditions = [View_forecast_pcusage.columns.company_name == filter_dict[name]]
        else:
            filter_conditions = [View_forecast_pcusage.columns.country == filter_dict[name]]
        return get_filtered_usage_week_common(db, filter_conditions, year,
                                          f"Plant Mtrx data not found for company name: {name}")
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/region_id/{region_id}/year/{year}')
def get_filtered_usage_by_region_id(region_id: int, year: int, db: Session = Depends(get_db)):
    """API endpoint: get weekly PC usage filtered by region ID.

    Args:
        region_id (int): Region identifier to filter by.
        year (int): Year to query.
        db (Session): Database session dependency.

    Returns:
        dict: Same structure returned by `get_filtered_usage_week_common`.
    """
    try:
        filter_conditions = [View_forecast_pcusage.columns.region_id == region_id]
        return get_filtered_usage_week_common(db, filter_conditions, year,
                                          f"Plant Mtrx data not found for region ID: {region_id}")
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/all_week_data/year/{year}')
def get_week_usage_all_data(year: int, db: Session = Depends(get_db)):
    """API endpoint: retrieve weekly PC usage for all plants/countries for a year.

    Args:
        year (int): Year to query.
        db (Session): Database session dependency.

    Returns:
        dict: Same structure returned by `get_filtered_usage_week_common`.
    """
    try:
        filter_conditions = []
        return get_filtered_usage_week_common(db, filter_conditions, year,
                                          "Plant Mtrx data not found")
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


def get_filtered_usage_period_common(db, filter_conditions, year, detail_message=None):
    """Fetch period-aggregated PC usage and aggregate volumes for a filter and year.

    Shared helper used by period-wise API endpoints. Returns aggregated
    forecast and actual values per plant and period for the requested year
    and filter.

    Args:
        db (Session): Database session dependency.
        filter_conditions (list): Additional SQLAlchemy filter expressions.
        year (int): The year to query.
        detail_message (Optional[str]): Optional message to include in errors.

    Returns:
        dict: A response dictionary with keys:
            - status: 'success' on success.
            - pcusage: List of aggregated rows per plant and period.
            - total_forecast_volume: Aggregated forecast volume for the filter.
            - total_actual_volume: Aggregated actual volume for the filter.

    Raises:
        HTTPException: 400 with details if any database error occurs.
    """
    try:
        result = db.query(View_forecast_pcusage.columns.plant_id,
                          View_forecast_pcusage.columns.plant_name,
                          View_forecast_pcusage.columns.year,
                          View_forecast_pcusage.columns.period,
                          View_forecast_pcusage.columns.Period_with_P,
                          View_forecast_pcusage.columns.year.label("week"),
                          func.sum(View_forecast_pcusage.columns.forecasted_value).label('total_forecast_value'),
                          func.sum(View_forecast_pcusage.columns.total_actual_value).label('total_actual_value')) \
            .filter(View_forecast_pcusage.columns.year == year,
                    *filter_conditions) \
            .group_by(View_forecast_pcusage.columns.year,
                      View_forecast_pcusage.columns.Period_with_P,
                      View_forecast_pcusage.columns.plant_name,
                      View_forecast_pcusage.columns.period, View_forecast_pcusage.columns.plant_id) \
            .order_by(View_forecast_pcusage.columns.period).all()

        total_forecast_volume = total_forcast_volume_func(filter_conditions, year, db)

        total_actual_volume = total_actual_volume_func(filter_conditions, year, db)

        return {"status": "success", "pcusage": result,
                "total_forecast_volume": total_forecast_volume,
                "total_actual_volume": total_actual_volume}

    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e) or detail_message or "Error processing request")


@router.get('/period_wise/company_name/{name}/year/{year}')
def getusage_company_periodwise(name: str, year: int, db: Session = Depends(get_db)):
    """API endpoint: retrieve period-wise PC usage filtered by company name.

    Maps the provided `name` to the internal company/country identifier used
    in `View_forecast_pcusage`, builds filter conditions and delegates to
    `get_filtered_usage_period_common`.

    Args:
        name (str): Company name key from the API path.
        year (int): Year to query.
        db (Session): Database session dependency.

    Returns:
        dict: Same structure returned by `get_filtered_usage_period_common`.
    """
    try:
        filter_dict = {
            'US': 'US',
            'US-Core': 'US-CORE',
            'Co-Man': 'CO-MAN',
            'Canada-Core': 'Canada'
        }
        if filter_dict[name] == 'CO-MAN' or filter_dict[name] == 'US-CORE':
            filter_conditions = [View_forecast_pcusage.columns.company_name == filter_dict[name]]
        else:
            filter_conditions = [View_forecast_pcusage.columns.country == filter_dict[name]]
        return get_filtered_usage_period_common(db, filter_conditions, year,
                                                f"Plant Mtrx data not found for company name: {name}")
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/period_wise/region_id/{region_id}/year/{year}')
def getusage_periodwise(region_id: int, year: int, db: Session = Depends(get_db)):
    """API endpoint: retrieve period-wise PC usage filtered by region ID.

    Args:
        region_id (int): Region identifier to filter by.
        year (int): Year to query.
        db (Session): Database session dependency.

    Returns:
        dict: Same structure returned by `get_filtered_usage_period_common`.
    """
    try:
        filter_conditions = [View_forecast_pcusage.columns.region_id == region_id]
        return get_filtered_usage_period_common(db, filter_conditions, year,
                                            f"Plant Mtrx data not found for region ID: {region_id}")
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/all_period_data/year/{year}')
def get_week_usage_all_data(year: int, db: Session = Depends(get_db)):
    """API endpoint: retrieve period-aggregated PC usage for all plants/countries for a year.

    Note: This function shares the same name as the weekly endpoint. It is
    used by the period-wise route and returns period-aggregated results.

    Args:
        year (int): Year to query.
        db (Session): Database session dependency.

    Returns:
        dict: Same structure returned by `get_filtered_usage_period_common`.
    """
    try:
        filter_conditions = []
        return get_filtered_usage_period_common(db, filter_conditions, year,
                                            "Plant Mtrx data not found")
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_next_year_or_update/{year}')
def create_new_pcusage(year: int):  # pragma: no cover
    """Create or update PC usage forecast records for a given year.

    This endpoint generates forecast `pcusage` records for the provided `year`
    based on previous year actuals, plant allocations and index values. If
    records for the target year already exist they are removed and regenerated.

    The algorithm:
        - Deletes existing `pcusage` records for the target year if present.
        - Fetches active plants for the target year (excluding a hard-coded
          plant id 26).
        - For each plant and period, computes weekly forecast values using a
          period index and previous year actuals. Handles thresholding and
          average fallbacks for zero or anomalous values.
        - Writes generated records in bulk to the database.

    Args:
        year (int): Target year for which to create/update forecast data.

    Returns:
        dict: A success message on completion.

    Raises:
        HTTPException: 400 with details if an error occurs during processing.
    """
    db = SessionLocal()
    try:
        existing_records = db.query(models.pcusage).filter(models.pcusage.year == year).all()
        threshold_value = 0.3
        if len(existing_records) != 0:
            for record in existing_records:
                db.delete(record)
            db.commit()

        previous_year = year - 1

        plants = (db.query(models.Plant.plant_id,
                           models.Plant.region_id,
                           models.Plant.crop_category_id)
                    .join(models.plant_status,
                          models.plant_status.plant_id == models.Plant.plant_id)
                    .filter(models.plant_status.year == year,
                            models.plant_status.status == 'ACTIVE',
                            models.plant_status.plant_id!=26)
                    .all())
        next_year_records = []
        for item in plants:
            print(item[0])
            category_id = item[2]
            category_name = db.query(models.category.category_name).filter(
                models.category.crop_category == category_id).first()
            country = db.query(models.region.country).filter(models.region.region_id == item[1]).first()

            index_value = db.query(models.allocation.period, models.allocation.backend_value).filter(
                models.allocation.category_name == category_name[0], models.allocation.year == year).all()

            index_dict = dict(index_value)
            previous_year = year-1
            period_value = 1
            while period_value < 14:  # Period_Value
                threshold = False
                last_year_actual = db.query(View_forecast_pcusage.columns.week,
                                            View_forecast_pcusage.columns.total_actual_value) \
                    .filter(View_forecast_pcusage.columns.year == previous_year,
                            View_forecast_pcusage.columns.plant_id == item[0],
                            View_forecast_pcusage.columns.period == period_value).all()
                previous_actual_dict = dict(last_year_actual)
                # get the last year actual value
                week_value = 1
                if period_week_calc.calculate_week_num(year, int(period_value)):
                    no_of_week = 6
                else:
                    no_of_week = 5
                while week_value < no_of_week:
                    previous_actual_dict.setdefault(week_value, 0)
                    if week_value == 5:
                        forecasted_value = (previous_actual_dict[week_value - 1] * index_dict[period_value]) / 100
                    else:
                        forecasted_value = (previous_actual_dict[week_value] * index_dict[period_value]) / 100
                    if forecasted_value==0:
                        threshold = True
                    week_value += 1
                
                avg_forecasted_value = 0
                if item[0] and trim(country[0]):
                    filter_conditions = [View_forecast_pcusage.columns.plant_id == item[0], View_forecast_pcusage.columns.country
                                         == trim(country[0])]
                    if len(get_average_forecast_value(filter_conditions, previous_year, db)) > 0 and len(total_actual_volume_func(filter_conditions, previous_year, db)) > 0:
                        non_zero_values = get_average_forecast_value(filter_conditions, previous_year, db)[0].count_zero_values
                        average_actual_value_prev_year = total_actual_volume_func(filter_conditions, previous_year, db)[0].total_actual_volume
                        avg_forecasted_value = average_actual_value_prev_year / non_zero_values if non_zero_values != 0 else 0
                week_value = 1
                while week_value < no_of_week:
                    previous_actual_dict.setdefault(week_value, 0)
                    if week_value == 5:
                        forecasted_value = (previous_actual_dict[week_value - 1] * index_dict[period_value]) / 100
                    else:
                        forecasted_value = (previous_actual_dict[week_value] * index_dict[period_value]) / 100
                    if threshold and avg_forecasted_value!=0: # Handling threshold case
                        if (abs((forecasted_value/index_dict[period_value])*100 - avg_forecasted_value) / avg_forecasted_value) > threshold_value:  
                            forecasted_value=avg_forecasted_value               
                    if forecasted_value==0: # Handling zero forecasted value
                        forecasted_value=avg_forecasted_value if avg_forecasted_value!=0 else 0
                    
                    # Calculate the forecast value
                    pc_usage_id = str(item[0]) + "#" + str(year) + "#" + str(period_value) + "#" + str(week_value)
                    payload = {"pcusage_id": pc_usage_id, "year": year, "period": period_value, "plant_id": item[0],
                               "forecasted_value": forecasted_value, "country": trim(country[0]), "week_no": week_value}
                    new_forecast_record = models.pcusage(**payload)
                    next_year_records.append(new_forecast_record)
                    # db.add(new_forecast_record)
                    week_value += 1
                    # db.commit()
                period_value += 1
        db.add_all(next_year_records)
        db.commit()
        return {"status": "success", "message": "New forecast records are generated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/create_new_plant_forcast/{plant_id}')
def create_new_plant_forecast(plant_id : int, db: Session = Depends(get_db)):  # pragma: no cover
    """Generate placeholder forecast records for a newly added plant.

    Creates forecast records with zero values for the current year for the
    given `plant_id`. This is used to initialize forecasting for newly added
    plants and ensures downstream processes have rows to work with.

    Args:
        plant_id (int): The plant identifier for which to create forecast rows.
        db (Session): Database session dependency.

    Returns:
        dict: A status message indicating success.

    Raises:
        HTTPException: 400 with details if an error occurs during processing.
    """
    try:
        current_year = date.today().year
        old_records = db.query(models.pcusage)\
            .filter(models.pcusage.plant_id == plant_id, models.pcusage.year >= current_year)\
            .all()
        if len(old_records) != 0:
            db.delete(old_records)
            db.commit()
        # delete junk data for new plant_id if present.
        plant_country = db.query(models.region.country)\
            .join(models.Plant, models.Plant.region_id == models.region.region_id)\
            .filter(models.Plant.plant_id == plant_id).scalar()
        period_value = 1
        while period_value <= 13:
            week_value = 1
            if period_week_calc.calculate_week_num(current_year, int(period_value)):
                no_of_week = 5
            else:
                no_of_week = 4
            while week_value <= no_of_week:
                pc_usage_id = str(plant_id) + "#" + str(current_year) + "#" + str(period_value) + "#" + str(week_value)
                payload = {"pcusage_id": pc_usage_id, "year": current_year, "period": period_value,
                           "plant_id": plant_id, "forecasted_value": 0, "country": trim(plant_country),
                           "week_no": week_value}
                new_forecast_record = models.pcusage(**payload)
                db.add(new_forecast_record)
                week_value += 1
            db.commit()
            period_value += 1
        return {"status": "success", "message": "Forecast data for new plant is generated for current year."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))