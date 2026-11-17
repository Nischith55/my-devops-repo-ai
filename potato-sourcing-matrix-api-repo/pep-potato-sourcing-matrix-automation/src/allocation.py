from datetime import date
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models
import period_week_calc
import plant_mtrx
from pcusage import total_actual_volume_func,get_average_forecast_value
from sqlalchemy import func,and_

router = APIRouter()


def trim(string): # pragma: no cover
    """Strip all spaces from a string.

    This helper removes any space characters from the provided string and
    returns the resulting string. It is used by some functions when
    constructing values that must not contain whitespace (for example
    company country codes used in `allocation_id`).

    Parameters
    ----------
    string: str
        Input string to trim spaces from.

    Returns
    -------
    str
        The same string with all spaces removed.
    """
    return string.replace(" ", "")


@router.get('/year/{year}')
def get_filtered_allocation(year: int, db: Session = Depends(get_db)):
    """Retrieve allocation records for a given year.

    This endpoint queries the `allocation` table for all records that
    match the provided year and returns a list of selected columns.
    If no records are found, an HTTP 404 is raised. Unexpected errors
    will raise an HTTP 400 with the error message.

    Parameters
    ----------
    year: int
        The year to filter allocation records by.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Returns
    -------
    dict
        A JSON-like dict with a `status` key and `category` list that
        contains the matching allocations.
    """

    data = db.query(models.allocation.allocation_id,
                    models.allocation.category_name,
                    models.allocation.year,
                    models.allocation.country,
                    models.allocation.period,
                    models.allocation.value,
                    models.allocation.backend_value,
                    models.allocation.target_volume
                    ).filter(models.allocation.year == year).all()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Allocation is found for year {year}")
    return {"status": "success", "category": data}
    


def get_all_plants(year: int, category_name: str, db: Session = Depends(get_db)): 
    """Return plant IDs for a given category and year.

    The function looks up the crop category ID for `category_name`,
    then queries active plants associated with that crop category for
    the provided year using the `plant_status` table. It returns a list
    of plant IDs (integers).

    Parameters
    ----------
    year: int
        Target year used when looking up plant status.
    category_name: str
        The category (e.g. 'FLUS', 'FLC', 'Co-Man') to limit plants by.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Returns
    -------
    List[int]
        A list of plant IDs that match the filters for the given year
        and category.
    """
    try:
        crop_category_id = db.query(models.category.crop_category) \
            .filter(models.category.category_name == category_name) \
            .first()
        data = (db.query(models.Plant.plant_id,
                               models.Plant.region_id,
                               models.Plant.crop_category_id)
                        .join(models.plant_status,
                              models.plant_status.plant_id == models.Plant.plant_id)
                        .filter(models.plant_status.year == year,
                                models.Plant.crop_category_id == crop_category_id[0],
                                models.plant_status.status == 'ACTIVE').all())
        result_list = [t[0] for t in data]
        return result_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def update_only_allocation(allocation_id, volume, db: Session = Depends(get_db)): 
    """Update allocation `target_volume` and derived index fields.

    This function recalculates `value` (index) and `backend_value` for a
    specific allocation based on the prior year's actual volumes and
    the provided `volume`. It excludes inactive plants and adjusts for
    weekly non-zero averages and outliers when computing the new
    indexes. The updated fields are written to the `allocation` table.

    Parameters
    ----------
    allocation_id: str
        Identifier of the allocation record to update.
    volume: float | int
        New target volume to set on the allocation; used during
        recalculation of index values.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Side effects
    -----------
    Commits the updated allocation values into the database.

    Returns
    -------
    None
    """
    try:
        allocation_data = ( db.query(models.allocation)
                              .filter(models.allocation.allocation_id == allocation_id).first())
        period = allocation_data.period
        year = allocation_data.year
        category = allocation_data.category_name
        company_map = {"FLUS": "US-CORE","FLC": "CANADA-CORE","Co-Man": "CO-MAN"}
        company_name = company_map.get(category)

        py_volume_data = (db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'),
                                            models.View_forecast_pcusage.columns.year , 
                                            models.View_forecast_pcusage.columns.period)
                            .filter(models.View_forecast_pcusage.columns.year == year-1,
                                    models.View_forecast_pcusage.columns.company_name == company_name,
                                    models.View_forecast_pcusage.columns.period == period)
                            .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.period).all())

        py_volume = py_volume_data[0].total_actual_volume if py_volume_data else 0
        new_target_volume = float(volume)
        index = new_target_volume/py_volume * 100 if py_volume > 0 else 0
        index = 0 if index < 0 else index
        threshold = 0.3
        threshold_offset = 0

        plant_ids = (db.query(models.View_forecast_pcusage.columns.plant_id).distinct()
                     .filter(models.View_forecast_pcusage.columns.year == year-1,
                             models.View_forecast_pcusage.columns.company_name == company_name,
                             models.View_forecast_pcusage.columns.period == period).all())
        plant_ids = [item[0] for item in plant_ids]

        for plant_id in plant_ids:

            zero_count = (db.query(func.count(models.View_forecast_pcusage.columns.total_actual_value).label('count_zero_values'),
                                              models.View_forecast_pcusage.columns.year)
                            .filter(models.View_forecast_pcusage.columns.year == year-1,
                                    models.View_forecast_pcusage.columns.company_name == company_name,
                                    models.View_forecast_pcusage.columns.period == period,
                                    models.View_forecast_pcusage.columns.total_actual_value == 0,
                                    models.View_forecast_pcusage.columns.plant_id == plant_id)
                            .group_by(models.View_forecast_pcusage.columns.year).all())

            weekly_avg = (db.query(models.plant_weekly_average)
                            .filter(models.plant_weekly_average.plant_id == plant_id,
                                    models.plant_weekly_average.year == year-1).first())

            #Handling inactive plant
            plant_status = db.query(models.plant_status.status).filter(models.plant_status.plant_id==plant_id,
                                                                    models.plant_status.year==year).first()
            status = plant_status[0] if plant_status else 'ACTIVE'
            if status != 'ACTIVE':
                print(f"Plant ID {plant_id} is inactive for year {year}")
                offline_plant_value = (db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'),
                                                         models.View_forecast_pcusage.columns.year ,
                                                         models.View_forecast_pcusage.columns.period)
                                        .filter(models.View_forecast_pcusage.columns.year == year-1,
                                                models.View_forecast_pcusage.columns.company_name == company_name,
                                                models.View_forecast_pcusage.columns.period == period,
                                                models.View_forecast_pcusage.columns.plant_id == plant_id)
                                        .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.period).all())
                offline_value = offline_plant_value[0].total_actual_volume if offline_plant_value else 0
                print(f"Offline Plant ID {plant_id} Value: {offline_value}")
                py_volume -= offline_value
            if status == 'ACTIVE':
                new_target_volume -= (zero_count[0].count_zero_values * weekly_avg.value) if zero_count and weekly_avg else 0
                if zero_count and zero_count[0].count_zero_values>0:
                    week_data = (db.query(models.View_forecast_pcusage.columns.total_actual_value)
                                .filter(models.View_forecast_pcusage.columns.year == year-1,
                                        models.View_forecast_pcusage.columns.company_name == company_name,
                                        models.View_forecast_pcusage.columns.period == period,
                                        models.View_forecast_pcusage.columns.plant_id == plant_id,
                                        models.View_forecast_pcusage.columns.total_actual_value != 0).all())
                    week_data = [item[0] for item in week_data]

                    for week_value in week_data:
                        abs_diff = abs(week_value - weekly_avg.value) if weekly_avg else 0
                        if (abs_diff / weekly_avg.value) > threshold:
                            threshold_offset += weekly_avg.value
                            py_volume-=week_value
                    print(plant_id,threshold_offset)

        new_target_volume-=threshold_offset
        backend_value = new_target_volume / py_volume * 100 if py_volume > 0 else 0
        backend_value = 0 if backend_value < 0 else backend_value

        db.query(models.allocation) \
            .filter(models.allocation.allocation_id == allocation_id) \
            .update({models.allocation.target_volume: float(volume),
                     models.allocation.value : index,
                     models.allocation.backend_value : backend_value},
                    synchronize_session='fetch')
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_volume(is_actual_update, item, db: Session = Depends(get_db)):  
    """Update forecast and plant matrix (`plantMtrx`) based on allocation.

    Recalculates and updates forecasted weekly values in `pcusage` and,
    when `is_actual_update` is truthy, updates the associated
    `plantMtrx.value` records accordingly. This function uses the
    previous year's actuals and computed index values to determine the
    new forecast and adjusts plant-level weekly values using either a
    computed ratio or average-based corrections for outliers.

    Parameters
    ----------
    is_actual_update: int | bool
        Flag to indicate whether the update should also adjust
        `plantMtrx` values (1/True to apply, 0/False to only update
        forecast values).
    item: object
        Object that contains allocation context such as `allocation_id`,
        `category_name`, `period`, and `year`. Typically a schema
        object from the request payload.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Side effects
    -----------
    Mutates `pcusage.forecasted_value`, changes `plantMtrx.value`, and
    may call `plant_mtrx.update_extension` to update extension rows.

    Returns
    -------
    None
    """
    try:
        allocation_record = db.query(models.allocation).filter(models.allocation.allocation_id == item.allocation_id).first()
        new_index = float(allocation_record.backend_value)
        target_volume = float(allocation_record.target_volume)
        company_map = {"FLUS" : "US-CORE","FLC": "CANADA-CORE","Co-Man": "CO-MAN"}
        company_name= company_map.get(allocation_record.category_name)
        category_value = item.category_name
        period_value = int(item.period)
        current_year = int(item.year)
        previous_year= current_year-1
        threshold_value = 0.3
        plant_id_list = get_all_plants(current_year, category_value, db)
        actual_data = 0
        if is_actual_update==1:
            actual_data = (db.query(func.sum(models.plantMtrx.value))
                                      .join(models.Plant,
                                            models.Plant.plant_id == models.plantMtrx.plant_id)
                                      .join(models.plant_status,
                                            and_(models.plant_status.plant_id == models.plantMtrx.plant_id,models.plantMtrx.year == models.plant_status.year))
                                      .filter(models.plantMtrx.year == current_year,
                                              models.plantMtrx.period == period_value,
                                              models.plantMtrx.status == 'active',
                                              models.Plant.company_name == company_name,
                                              models.plant_status.status == 'active').scalar())
            removed_plant_volume =  (db.query(func.sum(models.plantMtrx.value))
                                            .join(models.Plant, 
                                                  models.Plant.plant_id == models.plantMtrx.plant_id)
                                            # Join Status Table on ID AND Year
                                            .join(models.plant_status, 
                                                  and_(
                                                      models.plant_status.plant_id == models.plantMtrx.plant_id,
                                                      models.plant_status.year == models.plantMtrx.year
                                                  ))
                                            .filter(
                                                models.plantMtrx.year == current_year,
                                                models.plantMtrx.period == period_value,
                                                models.plantMtrx.status == 'active',        # The matrix record itself is valid
                                                models.Plant.company_name == company_name,
                                                models.plant_status.status == 'inactive'    # The plant status is 'inactive'
                                            )
                                            .scalar()) or 0
            a_index = (target_volume-removed_plant_volume) / actual_data if actual_data and actual_data > 0 else 0
            print(f"Actual Data: {actual_data}, Target Volume: {target_volume}, A Index: {a_index}")

        for plant_id in plant_id_list:
            threshold = False
            lastyear_actual_list = {}
            lastyear_actuals = db.query(models.View_forecast_pcusage.columns.week,
                                        models.View_forecast_pcusage.columns.total_actual_value) \
                .filter(models.View_forecast_pcusage.columns.plant_id == plant_id,
                        models.View_forecast_pcusage.columns.year == current_year - 1,
                        models.View_forecast_pcusage.columns.period == period_value).all()
            if not lastyear_actuals: # pragma: no cover
                continue
            lastyear_actual_list = dict(lastyear_actuals)
            week_value = 1
            if period_week_calc.calculate_week_num(current_year, int(period_value)):
                no_of_week = 6
            else: # pragma: no cover
                no_of_week = 5
            while week_value < no_of_week:
                lastyear_actual_list.setdefault(week_value, 0)
                if week_value == 5:
                    forecasted_value = (lastyear_actual_list[week_value - 1] * new_index) / 100
                else:
                    forecasted_value = (lastyear_actual_list[week_value] * new_index) / 100
                if forecasted_value==0:
                    threshold = True
                week_value += 1

            avg_forecasted_value = 0
            filter_conditions_alloc = [models.View_forecast_pcusage.columns.plant_id== plant_id]
            if len(get_average_forecast_value(filter_conditions_alloc, previous_year,db))>0 and len(total_actual_volume_func(filter_conditions_alloc, previous_year,db))>0:
                non_zero_values= get_average_forecast_value(filter_conditions_alloc,
                                                                                        previous_year,db)[0].count_zero_values
                average_actual_value_prev_year = total_actual_volume_func(filter_conditions_alloc,
                                                                                        previous_year,db)[0].total_actual_volume
                avg_forecasted_value = average_actual_value_prev_year / non_zero_values if non_zero_values != 0 else 0
            week_value = 1

            while week_value < no_of_week:
                lastyear_actual_list.setdefault(week_value, 0)
                if week_value == 5:
                    ly_value = lastyear_actual_list[week_value - 1]
                    new_forecast_value = (lastyear_actual_list[week_value - 1] * new_index) / 100
                else:
                    ly_value = lastyear_actual_list[week_value]
                    new_forecast_value = (lastyear_actual_list[week_value] * new_index) / 100
                if threshold and avg_forecasted_value!=0 and ly_value!=0: # Handling threshold case
                    if (abs(ly_value - avg_forecasted_value) / avg_forecasted_value) > threshold_value:
                        if plant_id == 27:
                            print(f"Plant ID: {plant_id}, Week: {week_value}, Plant avg: {avg_forecasted_value}, index: {new_index},forecasted_value: {ly_value}, diff: {abs(ly_value - avg_forecasted_value)}, ratio: {(abs(ly_value - avg_forecasted_value) / avg_forecasted_value)}")
                        new_forecast_value=avg_forecasted_value
                if new_forecast_value==0: # Handling zero forecasted value
                    new_forecast_value=avg_forecasted_value
                    print(f"{plant_id}-{new_forecast_value}")
                forecast_record = db.query(models.pcusage) \
                    .filter(models.pcusage.plant_id == plant_id,
                            models.pcusage.year == current_year,
                            models.pcusage.period == period_value,
                            models.pcusage.week_no == week_value).first()
                if forecast_record is None: # pragma: no cover
                    week_value += 1
                    continue
                forecast_record.forecasted_value = new_forecast_value
                db.commit()
                if is_actual_update==1:
                    plant_matrix = db.query(models.plantMtrx) \
                        .filter(models.plantMtrx.plant_id == plant_id,
                                models.plantMtrx.year == current_year,
                                models.plantMtrx.period == period_value,
                                models.plantMtrx.week == week_value).all()

                    for items in plant_matrix:
                        ga_wise_data = (db.query(models.plantMtrx)
                                            .filter(models.plantMtrx.plant_id == items.plant_id,
                                                    models.plantMtrx.year == items.year,
                                                    models.plantMtrx.period == items.period,
                                                    models.plantMtrx.week == items.week,
                                                    models.plantMtrx.status == 'active',
                                                    models.plantMtrx.crop_type == items.crop_type,
                                                    models.plantMtrx.growing_area_id == items.growing_area_id)
                                            .first())
                        if not ga_wise_data:# pragma: no cover
                            continue
                        current_value = ga_wise_data.value
                        new_value = current_value*a_index   
                        items.value = new_value
                        print(f"Updating Plant ID: {items.plant_id}, GA ID: {items.growing_area_id}, Year: {items.year}, Period: {items.period}, Week: {items.week}, New Value: {new_value}")
                        db.commit()

                        """Update Extension values if present."""
                        if 6 < period_value < 9:
                            print("Entering if condition")
                            plant_mtrx.update_extension(items.growing_area_id,
                                                        current_year, period_value,
                                                        week_value, db)
                            print("Exiting if condition")
                        elif 10 < period_value < 13:# pragma: no cover
                            plant_mtrx.update_extension(items.growing_area_id,
                                                        current_year, period_value,
                                                        week_value, db)
                week_value += 1
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/updateAllocation')
def update_allocation(payload: schemas.AllocationPayload, db: Session = Depends(get_db)):
    """API endpoint: Update allocations and optionally forecast data.

    Iterate through the list of allocations provided in the payload and
    update each record's `target_volume`, `value`, and `backend_value`.
    Depending on the allocation year compared to the current period/year
    and the individual `actual_volume` flag for each item, `update_volume`
    may also be invoked to update forecast (`pcusage`) and `plantMtrx`
    records.

    Parameters
    ----------
    payload: schemas.AllocationPayload
        The request payload containing `data`, a list of allocation
        items to update.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Returns
    -------
    dict
        A JSON-like result with update status and `records_updated`.
    """
    today_date = date.today()
    res = period_week_calc.calculate_period_and_week(today_date.year, today_date)
    year_data = int(res['year'])
    data = payload.data
    update_count = 0
    try:
        for item in data:
            if int(item.year) > year_data:
                update_only_allocation(item.allocation_id, item.target_volume, db)
                update_count += 1
                """Below function updates forecast and plantMtrx volume."""
                update_volume(item.actual_volume, item, db)
            else:
                update_only_allocation(item.allocation_id, item.target_volume, db)
                update_count += 1
                """Below function updates forecast volume only."""
                update_volume(0, item, db)
        return {"status": "success", "records_updated": update_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/createNewAllocation/{year}')
def create_allocation(year: int, db: Session = Depends(get_db)):
    """Create default allocations for the specified year.

    Creates a new `allocation` record for each active category for every
    period (1..13) for the provided `year`. Index values and backend
    indexes are computed from prior-year actual volumes and plant
    activity; the initial `value` is set to 100 and the computed
    `backend_value` is persisted. Inactive plants are excluded from
    those calculations.

    Parameters
    ----------
    year: int
        Target year for which allocations should be created.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Returns
    -------
    dict
        A JSON-like status response describing how many new
        allocations were created.
    """
    records_count = 0
    category_table = db.query(models.category.category_name, models.category.country)\
        .filter(models.category.status == 'Active').all()
    for category_item in category_table:
        if category_item[0] =="FLUS":
            company_name="US-CORE"
        elif category_item[0]=="FLC":
            company_name="CANADA-CORE"
        elif category_item[0]=="Co-Man":
            company_name="CO-MAN"
        i = 1
        while i <= 13:  # No. of period
            allocation_id = category_item[0] + "#" + str(i) + "#" + str(year)
            total_actual_volume = (db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value)
                                   .label('total_actual_volume'), models.View_forecast_pcusage.columns.year , models.View_forecast_pcusage.columns.period)
                                   .filter(models.View_forecast_pcusage.columns.year == year-1,
                                           models.View_forecast_pcusage.columns.company_name == company_name,
                                           models.View_forecast_pcusage.columns.period == i)
                                   .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.period).all())
            volume = total_actual_volume[0].total_actual_volume if total_actual_volume else 0
            new_target_volume = volume
            py_volume = volume
            threshold = 0.3
            threshold_offset = 0
            plant_ids = (db.query(models.View_forecast_pcusage.columns.plant_id).distinct()
                         .filter(models.View_forecast_pcusage.columns.year == year-1,
                                 models.View_forecast_pcusage.columns.company_name == company_name,
                                 models.View_forecast_pcusage.columns.period == i).all())
            plant_ids = [item[0] for item in plant_ids]
            for plant_id in plant_ids:
                print(f"Processing Plant ID: {plant_id} for Category: {category_item[0]}, Period: {i}, Year: {year}")
                zero_count = (db.query(func.count(models.View_forecast_pcusage.columns.total_actual_value).label('count_zero_values'),
                                                  models.View_forecast_pcusage.columns.year)
                                .filter(models.View_forecast_pcusage.columns.year == year-1,
                                        models.View_forecast_pcusage.columns.company_name == company_name,
                                        models.View_forecast_pcusage.columns.period == i,
                                        models.View_forecast_pcusage.columns.total_actual_value == 0,
                                        models.View_forecast_pcusage.columns.plant_id == plant_id)
                                .group_by(models.View_forecast_pcusage.columns.year).all())
                weekly_avg = (db.query(models.plant_weekly_average)
                                .filter(models.plant_weekly_average.plant_id == plant_id,
                                        models.plant_weekly_average.year == year-1).first())
                #Handling inactive plant
                plant_status = db.query(models.plant_status.status).filter(models.plant_status.plant_id==plant_id,
                                                                models.plant_status.year==year).first()
                status = plant_status[0] if plant_status else 'ACTIVE'
                if status != 'ACTIVE':
                    print(f"Plant ID {plant_id} is inactive for year {year}")
                    offline_plant_value = (db.query(func.sum(models.View_forecast_pcusage.columns.total_actual_value).label('total_actual_volume'),
                                                             models.View_forecast_pcusage.columns.year ,
                                                             models.View_forecast_pcusage.columns.period)
                                            .filter(models.View_forecast_pcusage.columns.year == year-1,
                                                    models.View_forecast_pcusage.columns.company_name == company_name,
                                                    models.View_forecast_pcusage.columns.period == i,
                                                    models.View_forecast_pcusage.columns.plant_id == plant_id)
                                            .group_by(models.View_forecast_pcusage.columns.year, models.View_forecast_pcusage.columns.period).all())
                    offline_value = offline_plant_value[0].total_actual_volume if offline_plant_value else 0
                    print(f"Offline Plant ID {plant_id} Value: {offline_value}")
                    py_volume -= offline_value
                new_target_volume -= (zero_count[0].count_zero_values * weekly_avg.value) if zero_count and weekly_avg else 0
                if zero_count and zero_count[0].count_zero_values>0:
                    week_data = (db.query(models.View_forecast_pcusage.columns.total_actual_value)
                                .filter(models.View_forecast_pcusage.columns.year == year-1,
                                        models.View_forecast_pcusage.columns.company_name == company_name,
                                        models.View_forecast_pcusage.columns.period == i,
                                        models.View_forecast_pcusage.columns.plant_id == plant_id,
                                        models.View_forecast_pcusage.columns.total_actual_value != 0).all())
                    week_data = [item[0] for item in week_data]
                    for week_value in week_data:
                        abs_diff = abs(week_value - weekly_avg.value) if weekly_avg else 0
                        if (abs_diff / weekly_avg.value) > threshold:
                            threshold_offset += weekly_avg.value
                            py_volume-=week_value
                    print(plant_id,threshold_offset)
            new_target_volume-=threshold_offset
            print(f"new_target_volume: {new_target_volume}, py_volume: {py_volume}, period: {i}, year: {year}, category: {category_item[0]}")
            backend_value = new_target_volume / py_volume * 100 if py_volume > 0 else 0
            backend_value = 0 if backend_value < 0 else backend_value

            payload = {"allocation_id": allocation_id, "category_name": category_item[0], "year": year,
                       "country": trim(category_item[1]), "period": i, "value": 100, "target_volume": volume, "backend_value": backend_value}
            new_allocation = models.allocation(**payload)
            db.add(new_allocation)
            i += 1
            records_count += 1
    db.commit()
    return {"Status": "success", "new_records": records_count} 


@router.post('/createPlantMatrixWeeklyAvg/{year}')
def create_weekly_avg(year: int, db: Session = Depends(get_db)):
    """Compute and persist plant weekly averages for the given year.

    The function computes a per-plant weekly average value using the
    total actual volume and the count of non-zero weeks discovered in
    historical data. Any pre-existing `plant_weekly_average` records
    for the same year are deleted first. The new average values are
    stored in `plant_weekly_average` for later use in forecast
    calculations.

    Parameters
    ----------
    year: int
        The year for which to compute the weekly averages.
    db: Session, optional
        Database session dependency injected by FastAPI.

    Returns
    -------
    dict
        A JSON-like status response with the number of new records
        inserted.
    """

    try:
        plant_ids = db.query(models.Plant.plant_id).filter(models.Plant.status == "ACTIVE").distinct().all()
        plant_ids = [item[0] for item in plant_ids]
        new_plant_entries = []

        """Delete old data if present"""
        records_to_delete = db.query(models.plant_weekly_average).filter((models.plant_weekly_average.year == year)).all()
        for record in records_to_delete:
            db.delete(record)
        db.commit()

        for plant in plant_ids:
            filter_conditions_alloc = [models.View_forecast_pcusage.columns.plant_id== plant]

            non_zero_result = get_average_forecast_value(filter_conditions_alloc, year, db)
            total_volume_result = total_actual_volume_func(filter_conditions_alloc, year, db)

            non_zero_values = non_zero_result[0].count_zero_values if non_zero_result else 0
            total_actual_volume = total_volume_result[0].total_actual_volume if total_volume_result else 0

            plant_avg = total_actual_volume / non_zero_values if non_zero_values > 0 else 0

            new_plant_data = models.plant_weekly_average(
                plant_id=plant, 
                year=year,
                value=plant_avg
            )
            new_plant_entries.append(new_plant_data)

        db.add_all(new_plant_entries)
        db.commit()
        return {"Status": "success", "new_records": len(plant_ids)}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))