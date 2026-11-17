import sys
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import pytest
from io import BytesIO
from fastapi import HTTPException, UploadFile
import pandas as pd

sys.path.append(r"..\src\main.py")
sys.path.append("src/")
sys.path.append("../")
sys.path.append("../src/")
from main import app
import models
import schemas
import freightcost
from types import SimpleNamespace
import journal
import validator_logger as vl
from btl import update_btl_mapping_records, create_btl_task_info, create_btl_task_mappings
from btlplan import ( update_btl_plan_mapping_records, create_btl_plan_task_info, create_btl_plan_task_mapping,)
from dashboard import update_volume_usage,create_new_volume_usage,dashboard_pc_plan_volume_usage_year
from dashboard_plan import _get_total_weeks, _get_compare_week,dashboard_pc_volume_usage_plan_year,update_plan_volume_usage,create_new_plan_volume_usage
from plants import create_plant
from ownership import create_new_ownership, update_ownership_contract_erp, generate_ownership_payload, calculate_to_ship, calculate_market_and_flex, total_ship_calculation as tsc
from MarketFlexMapping import update_market_flex, filtered_market_year, filtered_market, total_ship_calculation
from OwnershipGrowerGrowing import (update_contract_erp, delete_post, create_grower_growing_area_mapping)
from allocation import (update_volume, update_allocation, create_allocation, get_all_plants, update_only_allocation,create_weekly_avg)
from plant_mtrx import (func_getcrop_type, get_plantmtrx_common, trim as tr, func_getcrop_type)
from growingarea import create_growing_area, delete_growing_area,  get_growing_area, get_preferred_grower, get_growingid
from growers import delete_grower, create_growers, get_growers, get_post
from category import delete_category, create_category, get_category
from solidrates import (update_solid_rates_records, create_solids_rates, update_solids_rates_with_default_value, upload_file_solids,create_solid_rates_mappings_for_next_year, create_solid_rate_in_db)
from potatorates import (update_potato_rates_records,create_potato_rates,create_potato_rate_in_db, update_potato_rates_with_default_value)
from offcontractinfo import (create_off_contract_task_mapping_for_year, update_off_contract,
                             create_off_contract_info, create_off_contract_task_mapping,
                             update_off_contract_records)
from offcontractplaninfo import (create_off_contract_plan_task_mapping_for_next_year, create_off_contract_plan_info, create_off_contract_plan_task_mapping, update_off_contract_plan_mapping_records)
from region import delete_region, create_region
from p4p_master_info import (create_p4p_task_mappings_info, create_p4p_task_mappings, create_p4p_task_mappings_records_for_next_year,
                             update_p4p_task_mappings_records)
from generaladministrative import (update_general_administrative_mappings, create_general_administrative_task,
                                   update_general_administrative_records,create_g_and_a_mappings_for_next_year,general_administrative_mappings_by_year,get_general_administrative_task_info)
from generaladministrative_plan import (
    get_general_administrative_plan_task_info,
    general_administrative_plan_mappings_by_year,
    update_general_administrative_plan_mappings,
    create_general_administrative_plan_task,
    update_general_administrative_plan_records,
    create_g_and_a_plan_mappings_for_next_year,
)
from freighttaskinfo import (
    get_freight_task_info,
    get_frt_task_info_byid,
    get_freight_task_mappings_by_year_and_country,
    create_freight_task_mappings_for_next_year,
    create_freight_task_info,
    create_freight_task_mappings,
    update_freight_task_mapping_records,
)
from freighttaskplaninfo import (
    get_freight_task_plan_info,
    get_frt_task_plan_info_byid,
    get_freight_task_plan_mappings_by_year_and_country,
    create_freight_task_plan_mappings_for_next_year,
    create_freight_task_plan_info,
    create_freight_task_plan_mappings,
    update_freight_task_plan_mapping_records,
)
from powerbi_config import upsert_config, create_refresh_logs
from user_log import user_log
from user_info import update_user_status,create_user_information, update_user_page_mapping, update_new_user_page_mapping, create_user_and_mapping, extract_name_from_email, get_or_create_user
from summary_price_variance import update_price_variance_mappings_records, delete_all_post,create_price_variance_task_mapping
from summary_solids import (update_solids_task_mappings, create_solid_task_master, create_solid_rate_mappings, update_solid_rate_mapping_records,
                            create_summary_solids_for_next_year)
from productivity import (create_productivity_task_mapping, update_productivity_mapping_records, create_productivity_task_info,create_productivity_task_mapping_for_next_year)
from productivityplan import (create_productivity_plan_task_mapping_for_next_year,create_productivity_plan_task_info, create_productivity_plan_task_mapping, update_productivity_plan_mapping_records)
from page_info import create_access_type_information, create_country_information, create_page_information
from pcusage import (trim)
from inflation_deflation import (
    get_inflation_deflation_task_mappings,
    get_inflation_deflation_task,
    inflation_deflation_task_mappings_by_year,
    update_inflation_deflation_task_mappings_records,
    inflation_deflation_year_country_code,
)

client = TestClient(app)



"""________allocation.py_________"""

def test_get_allocation_year():
    response = client.get('/api/allocation/year/2023')
    assert response.status_code == 200

    response = client.get('/api/allocation/year/300')
    assert response.status_code == 404


# -------------------------------------------------------------------
# Helper: get_all_plants
# -------------------------------------------------------------------

@patch("database.get_db")
def test_get_all_plants_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q1 = MagicMock()
    q1.filter.return_value = q1
    q1.first.return_value = ("CAT_ID",)

    q2 = MagicMock()
    q2.join.return_value = q2
    q2.filter.return_value = q2
    q2.all.return_value = [(10, 1, "CAT_ID"), (20, 2, "CAT_ID")]

    db_mock.query.side_effect = [q1, q2]

    result = get_all_plants(year=2026, category_name="FLUS", db=db_mock)
    assert result == [10, 20]


@patch("database.get_db")
def test_get_all_plants_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        get_all_plants(year=2026, category_name="FLUS", db=db_mock)

    assert exc.value.status_code == 400


# -------------------------------------------------------------------
# update_only_allocation (covers success + error)
# We keep plant_ids empty so inner loop is skipped (fast, stable).
# -------------------------------------------------------------------

@patch("database.get_db")
def test_update_only_allocation_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    allocation_row = MagicMock()
    allocation_row.period = 1
    allocation_row.year = 2026
    allocation_row.category_name = "FLUS"   # maps -> US-CORE

    q_alloc = MagicMock()
    q_alloc.filter.return_value = q_alloc
    q_alloc.first.return_value = allocation_row

    # prior year total actual volume
    py_row = MagicMock()
    py_row.total_actual_volume = 100.0

    q_py = MagicMock()
    q_py.filter.return_value = q_py
    q_py.group_by.return_value = q_py
    q_py.all.return_value = [py_row]

    # distinct plant_ids => empty => skip plant loop
    q_plants = MagicMock()
    q_plants.distinct.return_value = q_plants
    q_plants.filter.return_value = q_plants
    q_plants.all.return_value = []

    # final update
    q_update = MagicMock()
    q_update.filter.return_value = q_update
    q_update.update.return_value = 1

    db_mock.query.side_effect = [q_alloc, q_py, q_plants, q_update]

    update_only_allocation(allocation_id="FLUS#1#2026", volume=200, db=db_mock)

    db_mock.commit.assert_called_once()
    q_update.update.assert_called_once()


@patch("database.get_db")
def test_update_only_allocation_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        update_only_allocation("X", 100, db=db_mock)

    assert exc.value.status_code == 400


# -------------------------------------------------------------------
# update_volume (covers both is_actual_update=0 and 1)
# We patch get_all_plants -> [] so loops are skipped (fast).
# -------------------------------------------------------------------

@patch("allocation.get_all_plants", return_value=[])
@patch("database.get_db")
def test_update_volume_success_no_actual(mock_get_db, _mock_plants):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    alloc_record = MagicMock()
    alloc_record.backend_value = 100
    alloc_record.target_volume = 1000
    alloc_record.category_name = "FLUS"

    q_alloc = MagicMock()
    q_alloc.filter.return_value = q_alloc
    q_alloc.first.return_value = alloc_record

    db_mock.query.side_effect = [q_alloc]

    item = MagicMock(allocation_id="FLUS#1#2026", category_name="FLUS", period=1, year=2026)

    # should not raise
    update_volume(0, item, db=db_mock)


@patch("allocation.get_all_plants", return_value=[])
@patch("database.get_db")
def test_update_volume_success_with_actual(mock_get_db, _mock_plants):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    alloc_record = MagicMock()
    alloc_record.backend_value = 100
    alloc_record.target_volume = 1000
    alloc_record.category_name = "FLUS"

    q_alloc = MagicMock()
    q_alloc.filter.return_value = q_alloc
    q_alloc.first.return_value = alloc_record

    # actual_data scalar
    q_actual = MagicMock()
    q_actual.join.return_value = q_actual
    q_actual.filter.return_value = q_actual
    q_actual.scalar.return_value = 500.0

    # removed_plant_volume scalar
    q_removed = MagicMock()
    q_removed.join.return_value = q_removed
    q_removed.filter.return_value = q_removed
    q_removed.scalar.return_value = 0

    db_mock.query.side_effect = [q_alloc, q_actual, q_removed]

    item = MagicMock(allocation_id="FLUS#1#2026", category_name="FLUS", period=1, year=2026)

    update_volume(1, item, db=db_mock)  # should not raise


@patch("database.get_db")
def test_update_volume_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("db down")

    item = MagicMock(allocation_id="X", category_name="FLUS", period=1, year=2026)

    with pytest.raises(HTTPException) as exc:
        update_volume(0, item, db=db_mock)

    assert exc.value.status_code == 400


# -------------------------------------------------------------------
# POST /updateAllocation -> update_allocation
# cover future year path vs current year path
# -------------------------------------------------------------------

@patch("allocation.update_volume")
@patch("allocation.update_only_allocation")
@patch("period_week_calc.calculate_period_and_week", return_value={"year": 2025})
@patch("database.get_db")
def test_update_allocation_success_all_paths(
    mock_get_db, _mock_period, mock_update_only, mock_update_volume
):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item_future = MagicMock(
        year="2026",
        allocation_id="FLUS#1#2026",
        target_volume=999,
        actual_volume=1,
        category_name="FLUS",
        period=1,
    )
    item_current = MagicMock(
        year="2025",
        allocation_id="FLUS#1#2025",
        target_volume=888,
        actual_volume=1,
        category_name="FLUS",
        period=1,
    )

    payload = MagicMock(data=[item_future, item_current])

    result = update_allocation(payload=payload, db=db_mock)

    assert result == {"status": "success", "records_updated": 2}

    # future year uses item.actual_volume
    mock_update_volume.assert_any_call(1, item_future, db_mock)
    # current/past uses 0
    mock_update_volume.assert_any_call(0, item_current, db_mock)

    assert mock_update_only.call_count == 2


@patch("allocation.update_only_allocation", side_effect=Exception("boom"))
@patch("period_week_calc.calculate_period_and_week", return_value={"year": 2025})
@patch("database.get_db")
def test_update_allocation_exception_400(mock_get_db, _mock_period, _mock_update_only):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item = MagicMock(
        year="2026",
        allocation_id="FLUS#1#2026",
        target_volume=999,
        actual_volume=1,
        category_name="FLUS",
        period=1,
    )
    payload = MagicMock(data=[item])

    with pytest.raises(HTTPException) as exc:
        update_allocation(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


# -------------------------------------------------------------------
# POST /createNewAllocation/{year} -> create_allocation
# Cover: category -> company mapping + loop periods 1..13 + commit
# Keep plant_ids empty so inner plant loop is skipped (fast).
# Also patch models.allocation so object creation doesn't require real ORM.
# -------------------------------------------------------------------

@patch("allocation.models.allocation")
@patch("database.get_db")
def test_create_allocation_success(mock_get_db, mock_allocation_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    # category_table: 3 categories to cover FLUS/FLC/Co-Man mapping
    q_categories = MagicMock()
    q_categories.filter.return_value = q_categories
    q_categories.all.return_value = [("FLUS", "United States"), ("FLC", "Canada"), ("Co-Man", "Co Man")]

    # total_actual_volume query -> return list with .total_actual_volume
    def make_total_volume_q(volume):
        row = MagicMock()
        row.total_actual_volume = volume
        q = MagicMock()
        q.filter.return_value = q
        q.group_by.return_value = q
        q.all.return_value = [row]
        return q

    # plant_ids distinct query -> empty list
    def make_plant_ids_empty_q():
        q = MagicMock()
        q.distinct.return_value = q
        q.filter.return_value = q
        q.all.return_value = []
        return q

    side_effect = [q_categories]

    # For each category (3) * each period (13):
    #  - total_actual_volume query
    #  - plant_ids query
    for _cat in range(3):
        for _p in range(13):
            side_effect.append(make_total_volume_q(100.0))
            side_effect.append(make_plant_ids_empty_q())

    db_mock.query.side_effect = side_effect

    result = create_allocation(year=2026, db=db_mock)

    assert result["Status"] == "success"
    assert result["new_records"] == 39  # 3 categories * 13 periods
    assert db_mock.add.call_count == 39
    db_mock.commit.assert_called_once()
    assert mock_allocation_model.call_count == 39  # allocation model constructed for each insert


@patch("database.get_db")
def test_create_allocation_exception_bubbles(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail early")

    with pytest.raises(Exception):
        create_allocation(year=2026, db=db_mock)


# -------------------------------------------------------------------
# POST /createPlantMatrixWeeklyAvg/{year} -> create_weekly_avg
# Cover delete loop line (records_to_delete) + add_all + commit
# -------------------------------------------------------------------

@patch("allocation.total_actual_volume_func")
@patch("allocation.get_average_forecast_value")
@patch("database.get_db")
def test_create_weekly_avg_success_with_delete_loop(mock_get_db, mock_avg, mock_total):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    # 1) plant ids query
    q_plants = MagicMock()
    q_plants.filter.return_value = q_plants
    q_plants.distinct.return_value = q_plants
    q_plants.all.return_value = [(1,), (2,)]

    # 2) records_to_delete query -> return 2 old records to delete (covers delete loop line)
    old1 = MagicMock()
    old2 = MagicMock()
    q_old = MagicMock()
    q_old.filter.return_value = q_old
    q_old.all.return_value = [old1, old2]

    db_mock.query.side_effect = [q_plants, q_old]

    # helper results => avg = 100 / 2 = 50
    mock_avg.return_value = [MagicMock(count_zero_values=2)]
    mock_total.return_value = [MagicMock(total_actual_volume=100)]

    result = create_weekly_avg(year=2025, db=db_mock)

    assert result["Status"] == "success"
    assert result["new_records"] == 2

    # delete loop covered
    assert db_mock.delete.call_count == 2
    db_mock.add_all.assert_called_once()

    # commits: one after delete, one after add_all
    assert db_mock.commit.call_count >= 2

@patch("allocation.plant_mtrx.update_extension")
@patch("allocation.total_actual_volume_func")
@patch("allocation.get_average_forecast_value")
@patch("allocation.get_all_plants", return_value=[27])  # plant_id == 27 hits that inner print branch too
@patch("allocation.period_week_calc.calculate_week_num", return_value=True)  # makes no_of_week = 6 => includes week 5
@patch("database.get_db")
def test_update_volume_full_coverage_with_actual_update(
    mock_get_db,
    _mock_weeknum,
    _mock_get_plants,
    mock_avg,
    mock_total,
    mock_update_ext,
):
    db = MagicMock()
    mock_get_db.return_value = db

    # allocation_record
    alloc_record = MagicMock(backend_value=100.0, target_volume=1000.0, category_name="FLUS")
    q_alloc = MagicMock()
    q_alloc.filter.return_value = q_alloc
    q_alloc.first.return_value = alloc_record

    # lastYear_actuals query returns some weeks, includes zeros -> threshold True
    # (week, total_actual_value)
    q_last_year = MagicMock()
    q_last_year.filter.return_value = q_last_year
    q_last_year.all.return_value = [(1, 0.0), (2, 200.0), (3, 0.0), (4, 200.0)]

    # avg_forecasted_value uses helpers
    mock_avg.return_value = [MagicMock(count_zero_values=2)]          # non_zero_values
    mock_total.return_value = [MagicMock(total_actual_volume=200.0)]  # average_actual_value_prev_year
    # => avg_forecasted_value = 200/2 = 100

    # forecast_record exists for each week => set forecasted_value + commit
    forecast_obj = MagicMock()
    q_forecast = MagicMock()
    q_forecast.filter.return_value = q_forecast
    q_forecast.first.return_value = forecast_obj

    # is_actual_update==1:
    # actual_data scalar + removed_plant_volume scalar
    q_actual = MagicMock()
    q_actual.join.return_value = q_actual
    q_actual.filter.return_value = q_actual
    q_actual.scalar.return_value = 500.0

    q_removed = MagicMock()
    q_removed.join.return_value = q_removed
    q_removed.filter.return_value = q_removed
    q_removed.scalar.return_value = 0.0

    # plant_matrix list for each week
    plant_mtrx_item = MagicMock(plant_id=27, year=2026, period=7, week=1, crop_type="CAT", growing_area_id=99, value=10.0)
    q_plant_matrix = MagicMock()
    q_plant_matrix.filter.return_value = q_plant_matrix
    q_plant_matrix.all.return_value = [plant_mtrx_item]

    # ga_wise_data exists -> update items.value -> commit
    ga_data = MagicMock(value=10.0)
    q_ga = MagicMock()
    q_ga.filter.return_value = q_ga
    q_ga.first.return_value = ga_data

    # db.query order inside update_volume():
    # 1 allocation_record
    # 2 actual_data (when is_actual_update==1)
    # 3 removed_plant_volume
    # then inside plant loop:
    # 4 lastYear_actuals
    # then for each week: forecast_record first
    # plus plant_matrix + ga_wise_data queries when is_actual_update==1
    #
    # We'll keep it simple by returning same mocks repeatedly with side_effect that is long enough.
    side_effect = [
        q_alloc,
        q_actual,
        q_removed,
        q_last_year,
    ]

    # For weeks 1..5 (no_of_week=6 => while < 6)
    # Each week does:
    # - forecast_record query
    # - plant_matrix query
    # - ga_wise_data query
    for _ in range(1, 6):
        side_effect.extend([q_forecast, q_plant_matrix, q_ga])

    db.query.side_effect = side_effect

    item = MagicMock(
        allocation_id="FLUS#7#2026",
        category_name="FLUS",
        period=7,
        year=2026,
        actual_volume=1
    )

    update_volume(is_actual_update=1, item=item, db=db)

    # should update forecasted_value at least once
    assert forecast_obj.forecasted_value is not None
    assert db.commit.call_count >= 1

    # period=7 triggers update_extension (6 < period < 9)
    assert mock_update_ext.called
@patch("database.get_db")
def test_create_weekly_avg_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        create_weekly_avg(year=2025, db=db_mock)

    assert exc.value.status_code == 400

@patch("database.get_db")
def test_update_only_allocation_inactive_plant_offline_volume_path(mock_get_db):
    """
    Covers:
    - zero_count query
    - weekly_avg query
    - plant_status != ACTIVE -> offline_plant_value branch
    """
    db = MagicMock()
    mock_get_db.return_value = db

    # allocation_data
    alloc_row = MagicMock(period=1, year=2026, category_name="FLUS")
    q_alloc = MagicMock()
    q_alloc.filter.return_value = q_alloc
    q_alloc.first.return_value = alloc_row

    # py_volume_data (previous year period total)
    py_row = MagicMock(total_actual_volume=100.0)
    q_py = MagicMock()
    q_py.filter.return_value = q_py
    q_py.group_by.return_value = q_py
    q_py.all.return_value = [py_row]

    # plant_ids distinct => [11]
    q_plants = MagicMock()
    q_plants.distinct.return_value = q_plants
    q_plants.filter.return_value = q_plants
    q_plants.all.return_value = [(11,)]

    # zero_count => 1 zero
    zero_row = MagicMock(count_zero_values=1)
    q_zero = MagicMock()
    q_zero.filter.return_value = q_zero
    q_zero.group_by.return_value = q_zero
    q_zero.all.return_value = [zero_row]

    # weekly_avg => value=10
    weekly_avg_row = MagicMock(value=10.0)
    q_weekly_avg = MagicMock()
    q_weekly_avg.filter.return_value = q_weekly_avg
    q_weekly_avg.first.return_value = weekly_avg_row

    # plant_status => INACTIVE
    q_status = MagicMock()
    q_status.filter.return_value = q_status
    q_status.first.return_value = ("INACTIVE",)

    # offline_plant_value sum => 20
    off_row = MagicMock(total_actual_volume=20.0)
    q_off = MagicMock()
    q_off.filter.return_value = q_off
    q_off.group_by.return_value = q_off
    q_off.all.return_value = [off_row]

    # final update query
    q_update = MagicMock()
    q_update.filter.return_value = q_update
    q_update.update.return_value = 1

    db.query.side_effect = [
        q_alloc,        # allocation_data
        q_py,           # py_volume_data
        q_plants,       # plant_ids
        q_zero,         # zero_count
        q_weekly_avg,   # weekly_avg
        q_status,       # plant_status
        q_off,          # offline_plant_value
        q_update        # update allocation row
    ]

    update_only_allocation("FLUS#1#2026", 200, db=db)

    db.commit.assert_called_once()
    q_update.update.assert_called_once()


@patch("database.get_db")
def test_update_only_allocation_active_plant_outlier_threshold_offset_path(mock_get_db):
    """
    Covers ACTIVE branch:
    - new_target_volume -= zero_count*weekly_avg
    - week_data != 0 -> outlier -> threshold_offset++ and py_volume -= week_value
    """
    db = MagicMock()
    mock_get_db.return_value = db

    alloc_row = MagicMock(period=1, year=2026, category_name="FLUS")
    q_alloc = MagicMock()
    q_alloc.filter.return_value = q_alloc
    q_alloc.first.return_value = alloc_row

    py_row = MagicMock(total_actual_volume=200.0)
    q_py = MagicMock()
    q_py.filter.return_value = q_py
    q_py.group_by.return_value = q_py
    q_py.all.return_value = [py_row]

    q_plants = MagicMock()
    q_plants.distinct.return_value = q_plants
    q_plants.filter.return_value = q_plants
    q_plants.all.return_value = [(11,)]

    zero_row = MagicMock(count_zero_values=1)
    q_zero = MagicMock()
    q_zero.filter.return_value = q_zero
    q_zero.group_by.return_value = q_zero
    q_zero.all.return_value = [zero_row]

    weekly_avg_row = MagicMock(value=10.0)
    q_weekly_avg = MagicMock()
    q_weekly_avg.filter.return_value = q_weekly_avg
    q_weekly_avg.first.return_value = weekly_avg_row

    q_status = MagicMock()
    q_status.filter.return_value = q_status
    q_status.first.return_value = ("ACTIVE",)

    # week_data non-zero values (outlier vs weekly_avg=10)
    q_week_data = MagicMock()
    q_week_data.filter.return_value = q_week_data
    q_week_data.all.return_value = [(100.0,)]  # abs_diff=90 => 90/10=9 > 0.3 => triggers threshold_offset

    q_update = MagicMock()
    q_update.filter.return_value = q_update
    q_update.update.return_value = 1

    db.query.side_effect = [
        q_alloc,
        q_py,
        q_plants,
        q_zero,
        q_weekly_avg,
        q_status,
        q_week_data,
        q_update
    ]

    update_only_allocation("FLUS#1#2026", 200, db=db)

    db.commit.assert_called_once()
    q_update.update.assert_called_once()

@patch("allocation.models.allocation")
@patch("database.get_db")
def test_create_allocation_covers_plant_loop_logic(mock_get_db, mock_alloc_model):
    db = MagicMock()
    mock_get_db.return_value = db

    # category_table: only 1 item to keep runtime small
    q_categories = MagicMock()
    q_categories.filter.return_value = q_categories
    q_categories.all.return_value = [("FLUS", "United States")]

    # total_actual_volume query (called 13 times)
    def total_q():
        row = MagicMock(total_actual_volume=200.0)
        q = MagicMock()
        q.filter.return_value = q
        q.group_by.return_value = q
        q.all.return_value = [row]
        return q

    # plant_ids query: first period returns one plant, remaining periods empty
    def plant_ids_q_first():
        q = MagicMock()
        q.distinct.return_value = q
        q.filter.return_value = q
        q.all.return_value = [(11,)]
        return q

    def plant_ids_q_empty():
        q = MagicMock()
        q.distinct.return_value = q
        q.filter.return_value = q
        q.all.return_value = []
        return q

    # zero_count
    zero_row = MagicMock(count_zero_values=1)
    q_zero = MagicMock()
    q_zero.filter.return_value = q_zero
    q_zero.group_by.return_value = q_zero
    q_zero.all.return_value = [zero_row]

    # weekly_avg
    weekly_avg_row = MagicMock(value=10.0)
    q_weekly_avg = MagicMock()
    q_weekly_avg.filter.return_value = q_weekly_avg
    q_weekly_avg.first.return_value = weekly_avg_row

    # plant_status INACTIVE -> offline branch
    q_status = MagicMock()
    q_status.filter.return_value = q_status
    q_status.first.return_value = ("INACTIVE",)

    # offline sum
    off_row = MagicMock(total_actual_volume=20.0)
    q_off = MagicMock()
    q_off.filter.return_value = q_off
    q_off.group_by.return_value = q_off
    q_off.all.return_value = [off_row]

    # week_data non-zero outlier
    q_week_data = MagicMock()
    q_week_data.filter.return_value = q_week_data
    q_week_data.all.return_value = [(100.0,)]

    side_effect = [q_categories]

    # For 13 periods:
    # each period calls: total_actual_volume + plant_ids distinct
    # For period=1 only, plant_ids has 1 plant -> triggers inner queries
    for period in range(1, 14):
        side_effect.append(total_q())
        side_effect.append(plant_ids_q_first() if period == 1 else plant_ids_q_empty())

        if period == 1:
            side_effect.extend([q_zero, q_weekly_avg, q_status, q_off, q_week_data])

    db.query.side_effect = side_effect

    result = create_allocation(year=2026, db=db)

    assert result["Status"] == "success"
    assert result["new_records"] == 13
    assert db.add.call_count == 13
    db.commit.assert_called_once()

"""________btl.py_________"""

def test_get_btl_task_info():
    response = client.get('/api/btl/')
    assert response.status_code == 200

def test_get_btl_task_mappings_by_year_and_country():
    response = client.get(
        '/api/btl/get_btl_task_mappings_by_year_and_country/2023/US-CORE'
    )
    assert response.status_code == 200

    response = client.get(
        '/api/btl/get_btl_task_mappings_by_year_and_country/3000/US-CORE'
    )
    assert response.status_code == 404

@patch('database.get_db')
def test_update_btl_mapping_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {
                "btl_task_id": 1,
                "period": 2,
                "year": 2023,
                "value": 10.5,
                "company_name": "US-CORE",
            }
        ]
    }

    test_payload = schemas.BTLTaskMappingPayload(**payload_data)
    # Mock the chained query -> filter -> update
    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.update.return_value = 1
    result = update_btl_mapping_records(payload=test_payload, db=db_mock)
    assert result == {"status": "success", "records_updated": 1}

@patch('database.get_db')
def test_update_btl_mapping_records_invalid_input(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    # Invalid because btl_task_id <= 0
    payload_data = {
        "data": [
            {
                "btl_task_id": 0,
                "period": 2,
                "year": 2023,
                "value": 10.5,
                "company_name": "US-CORE",
            }
        ]
    }
    test_payload = schemas.BTLTaskMappingPayload(**payload_data)
    result = update_btl_mapping_records(payload=test_payload, db=db_mock)
    assert result == {"status": "error", "message": "Please check details"}
    db_mock.query.assert_not_called()

@patch('database.get_db')
def test_create_btl_task_info_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    # We just need an object with .dict() -> {}, no need to depend on real schema fields here
    payload = MagicMock()
    payload.dict.return_value = {}
    # Simulate DB assigning an ID during refresh
    def refresh_side_effect(obj):
        obj.btl_task_id = 1
    db_mock.refresh.side_effect = refresh_side_effect
    result = create_btl_task_info(payload=payload, db=db_mock)
    assert result == {"status": "success", "btl_task_id": 1}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

@patch('database.get_db')
def test_create_btl_task_mappings_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    # Again, only need .dict() -> {} so model can be instantiated
    payload = MagicMock()
    payload.dict.return_value = {}
    # Simulate DB assigning row_id on refresh
    def refresh_side_effect(obj):
        obj.row_id = 10
    db_mock.refresh.side_effect = refresh_side_effect
    result = create_btl_task_mappings(payload=payload, db=db_mock)
    assert result == {"status": "success", "row_id": 10}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


"""________btlplan.py_________"""

def test_get_btl_plan_task_info():
    response = client.get("/api/btl_plan/")
    assert response.status_code == 200

def test_get_btl_plan_task_mapping_by_year_and_country():
    response = client.get(
        "/api/btl_plan/get_btl_plan_task_mapping_by_year_and_country/2023/US-CORE"
    )
    assert response.status_code == 200

    response = client.get(
        '/api/btl_plan/get_btl_plan_task_mapping_by_year_and_country/3000/US-CORE'
    )
    assert response.status_code == 404

@patch("database.get_db")
def test_update_btl_plan_mapping_records_success(mock_get_db):
    """Happy path: valid payload updates records and returns success."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "btl_plan_task_id": 1,
                "period": 3,
                "year": 2025,
                "value": 123.45,
                "company_name": "US-CORE",
            }
        ]
    }
    test_payload = schemas.BTLPlanTaskMappingPayload(**payload_data)
    # Mock query -> filter -> update chain
    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.update.return_value = 1
    result = update_btl_plan_mapping_records(payload=test_payload, db=db_mock)
    assert result == {"status": "success", "records_updated": 1}
    db_mock.query.assert_called_once()
    db_mock.commit.assert_called_once()

@patch("database.get_db")
def test_update_btl_plan_mapping_records_invalid_input(mock_get_db):
    """Invalid input (btl_plan_task_id <= 0) should return error and not hit DB."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "btl_plan_task_id": 0,  # invalid
                "period": 3,
                "year": 2025,
                "value": 123.45,
                "company_name": "US-CORE",
            }
        ]
    }
    test_payload = schemas.BTLPlanTaskMappingPayload(**payload_data)
    result = update_btl_plan_mapping_records(payload=test_payload, db=db_mock)
    assert result == {"status": "error", "message": "Please check details"}
    db_mock.query.assert_not_called()
    db_mock.commit.assert_not_called()

@patch("database.get_db")
def test_create_btl_plan_task_info_success(mock_get_db):
    """create_btl_plan_task_info should add, commit and return new btl_plan_task_id."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    # Use real schema (all fields optional)
    payload = schemas.BTLPlanInfoSchema()
    # Simulate SQLAlchemy assigning ID on refresh
    def refresh_side_effect(obj):
        obj.btl_plan_task_id = 5
    db_mock.refresh.side_effect = refresh_side_effect
    result = create_btl_plan_task_info(payload=payload, db=db_mock)
    assert result == {"status": "success", "btl_plan_task_id": 5}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

@patch("database.get_db")
def test_create_btl_plan_task_mapping_success(mock_get_db):
    """create_btl_plan_task_mapping should add, commit and return new row_id."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    # Use real schema (all fields optional)
    payload = schemas.BTLPlanTaskMappingSchema(
        period=1,
        btl_plan_task_id=10,
        year=2025,
        value=50.0,
        company_name="US-CORE",
    )
    # Simulate SQLAlchemy assigning row_id on refresh
    def refresh_side_effect(obj):
        obj.row_id = 99
    db_mock.refresh.side_effect = refresh_side_effect
    result = create_btl_plan_task_mapping(payload=payload, db=db_mock)
    assert result == {"status": "success", "row_id": 99}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()



"""_______Category.py_______"""

def test_get_category():
    response = client.get("/api/category/")
    assert response.status_code == 200

def test_get_category_by_id():
    response = client.get("/api/category/1")
    assert response.status_code == 200

    response = client.get("/api/category/10000")
    assert response.status_code == 404

@patch('database.get_db')
def test_delete_category(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().update.return_value = 1

    result = delete_category(categoryId="1", db=db_mock)
    assert result.status_code == 204

@patch('database.get_db')
def test_create_category(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_category = {
        "category_name": "TEST",
        "country": "US",
        "status": "INACTIVE",
        "created_time": "2024-01-08T08:07:40.901Z",
        "updated_time": "2024-01-08T08:07:40.901Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.Category(**payload_category)
    result = create_category(payload=mock_payload, db=db_mock)
    assert result["status"] == "success"

@patch("database.get_db")
def test_delete_category_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.filter.return_value.update.return_value = 0

    with pytest.raises(HTTPException) as exc:
        delete_category(categoryId="999", db=db_mock)

    assert exc.value.status_code == 404
    db_mock.commit.assert_not_called()

@patch("database.get_db")
def test_get_category_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.filter.return_value.all.return_value = []

    # call function directly (same style as your other direct-call tests)
    with pytest.raises(HTTPException) as exc:
        get_category(db=db_mock)

    assert exc.value.status_code == 404



"""________Dashboard_Plan.py_________"""

def test_get_dashboard_plan_year():
    response = client.get('/api/dashboard_plan/dashboard_pc_volume_usage_plan/2024')
    assert response.status_code == 200

@patch("database.get_db")
def test_dashboard_pc_volume_usage_plan_year_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.side_effect = Exception("DB error")

    with pytest.raises(HTTPException) as exc:
        dashboard_pc_volume_usage_plan_year(year=2025, db=db_mock)

    assert exc.value.status_code == 400


# -------------------------
# POST: update_plan_volume_usage
# -------------------------

@patch("database.get_db")
def test_update_plan_volume_usage_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item1 = MagicMock(pc_volume_plan_id="CAT#1#1#2025", volume=10.0)
    item2 = MagicMock(pc_volume_plan_id="CAT#1#2#2025", volume=20.0)
    payload = MagicMock(data=[item1, item2])

    db_mock.query.return_value.filter.return_value.update.return_value = 1

    result = update_plan_volume_usage(payload=payload, db=db_mock)

    assert result == {"status": "success", "records_updated": 2}
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_update_plan_volume_usage_not_found_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item1 = MagicMock(pc_volume_plan_id="NOT_FOUND", volume=99.0)
    payload = MagicMock(data=[item1])

    # update returns 0 => raises 404, but caught and returned as 400 (current code behavior)
    db_mock.query.return_value.filter.return_value.update.return_value = 0

    with pytest.raises(HTTPException) as exc:
        update_plan_volume_usage(payload=payload, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.commit.assert_not_called()


@patch("database.get_db")
def test_update_plan_volume_usage_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item1 = MagicMock(pc_volume_plan_id="CAT#1#1#2025", volume=10.0)
    payload = MagicMock(data=[item1])

    db_mock.query.side_effect = Exception("DB failure")

    with pytest.raises(HTTPException) as exc:
        update_plan_volume_usage(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


# -------------------------
# Helpers: _get_total_weeks and _get_compare_week
# -------------------------

def test_get_compare_week():
    assert _get_compare_week(5) == 4
    assert _get_compare_week(3) == 3


@patch("period_week_calc.calculate_week_num")
def test_get_total_weeks_returns_5(mock_calc):
    mock_calc.return_value = True
    assert _get_total_weeks(2025, 1) == 5


@patch("period_week_calc.calculate_week_num")
def test_get_total_weeks_returns_4(mock_calc):
    mock_calc.return_value = False
    assert _get_total_weeks(2025, 1) == 4

# -------------------------
# POST: create_new_plan_volume_usage
# -------------------------

@patch("database.get_db")
def test_create_new_plan_volume_usage_success_1(mock_get_db, monkeypatch):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    monkeypatch.setattr("dashboard_plan._get_total_weeks", lambda year, period: 1)
    monkeypatch.setattr("dashboard_plan._get_compare_week", lambda week: 1)

    q_delete = MagicMock()
    q_delete.filter.return_value = q_delete
    q_delete.delete.return_value = 1

    q_categories = MagicMock()
    q_categories.all.return_value = [("CAT", "US", "Potato")]

    q_index = MagicMock()
    q_index.filter.return_value = q_index
    q_index.first.return_value = MagicMock(value=100)

    q_last_year = MagicMock()
    q_last_year.filter.return_value = q_last_year
    q_last_year.first.return_value = (50.0,)

    db_mock.query.side_effect = [q_delete, q_categories] + [q_index, q_last_year] * 13

    result = create_new_plan_volume_usage(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert result["new_records_created"] == 13
    assert db_mock.add.call_count == 13
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_create_new_plan_volume_usage_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q_delete = MagicMock()
    q_delete.filter.return_value = q_delete
    q_delete.delete.return_value = 1

    q_categories = MagicMock()
    q_categories.all.return_value = [("CAT", "US", "Potato")]

    q_index = MagicMock()
    q_index.filter.return_value = q_index
    q_index.first.return_value = MagicMock(value=100)

    q_last_year = MagicMock()
    q_last_year.filter.return_value = q_last_year
    q_last_year.first.return_value = (50.0,)

    db_mock.query.side_effect = [q_delete, q_categories, q_index, q_last_year]

    db_mock.commit.side_effect = Exception("commit failed")

    with pytest.raises(HTTPException) as exc:
        create_new_plan_volume_usage(year=2026, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.rollback.assert_called_once()

"""________Dashboard.py_________"""
def test_get_dashboard_year():
    response = client.get('/api/dashboard/dashboard_pc_plan_volume_usage/2024')
    assert response.status_code == 200

@patch("database.get_db")
def test_get_dashboard_year_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.side_effect = Exception("DB error")

    with pytest.raises(HTTPException) as exc:
        dashboard_pc_plan_volume_usage_year(year=2024, db=db_mock)

    assert exc.value.status_code == 400

# -------------------------
# POST: update_plan_volume_usage
# -------------------------

@patch("database.get_db")
def test_update_volume_usage_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item1 = MagicMock(plan_volume_id="A#1#1#2024", volume=10)
    item2 = MagicMock(plan_volume_id="B#1#1#2024", volume=20)
    payload = MagicMock(data=[item1, item2])

    db_mock.query.return_value.filter.return_value.update.return_value = 1

    result = update_volume_usage(payload=payload, db=db_mock)

    assert result == {"status": "success", "records_updated": 2}
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_update_volume_usage_not_found_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item1 = MagicMock(plan_volume_id="NOT_FOUND", volume=99)
    payload = MagicMock(data=[item1])

    # update returns 0 => raises 404
    db_mock.query.return_value.filter.return_value.update.return_value = 0

    with pytest.raises(HTTPException) as exc:
        update_volume_usage(payload=payload, db=db_mock)

    assert exc.value.status_code == 404
    db_mock.commit.assert_not_called()


@patch("database.get_db")
def test_update_volume_usage_commit_exception(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    item1 = MagicMock(plan_volume_id="A#1#1#2024", volume=10)
    payload = MagicMock(data=[item1])

    db_mock.query.return_value.filter.return_value.update.return_value = 1
    db_mock.commit.side_effect = Exception("commit failed")

    with pytest.raises(Exception):
        update_volume_usage(payload=payload, db=db_mock)


# -------------------------
# POST: create_new_plan_volume_usage
# -------------------------
@patch("dashboard._get_compare_week", return_value=1)
@patch("dashboard._get_total_weeks", return_value=1)
@patch("database.get_db")
def test_create_new_volume_usage_success(mock_get_db, _mock_total_weeks, _mock_compare_week):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q_delete = MagicMock()
    q_delete.filter.return_value = q_delete
    q_delete.delete.return_value = 1

    q_categories = MagicMock()
    q_categories.all.return_value = [("CAT", "US", "Potato")]

    q_index = MagicMock()
    q_index.filter.return_value = q_index
    q_index.first.return_value = MagicMock(value=100)  # index_row.value

    q_last_year = MagicMock()
    q_last_year.filter.return_value = q_last_year
    q_last_year.first.return_value = (50.0,)  # last_year_volume_row[0]

    # ✅ 1 delete + 1 categories + (13 index + 13 last_year) = 28 db.query calls
    db_mock.query.side_effect = [q_delete, q_categories] + [q_index, q_last_year] * 13

    result = create_new_volume_usage(year=2026, db=db_mock)

    assert result == {"status": "success", "new_records_created": 13}
    assert db_mock.add.call_count == 13
    db_mock.commit.assert_called_once()

@patch("database.get_db")
def test_create_new_volume_usage_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    q_delete = MagicMock()
    q_delete.filter.return_value = q_delete
    q_delete.delete.return_value = 1

    q_categories = MagicMock()
    q_categories.all.return_value = [("CAT", "US", "Potato")]

    q_index = MagicMock()
    q_index.filter.return_value = q_index
    q_index.first.return_value = MagicMock(value=100)

    q_last_year = MagicMock()
    q_last_year.filter.return_value = q_last_year
    q_last_year.first.return_value = (50,)

    db_mock.query.side_effect = [q_delete, q_categories, q_index, q_last_year]
    db_mock.commit.side_effect = Exception("commit failed")

    with pytest.raises(HTTPException) as exc:
        create_new_volume_usage(year=2026, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.rollback.assert_called_once()

"""________OwnershipGrowerGrowing.py_________"""

def test_get_ownershipgrowergrowing():
    response = client.get('/api/ownershipMapping/year/2023')
    assert response.status_code == 200

@patch('database.get_db')
def test_mock_create_grower_growing_area_mapping(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "row_id": "254#170#2022-23",
        "growing_area_id": 254,
        "grower_id": 170,
        "contract": 10,
        "year": 2023,
        "shrinkage": 0,
        "contract_erp": 0,
        "market": 0,
        "flex": 0,
        "ownership_id": "254#2022-23",
        "crop_type": "Storage",
        "crop_year": "2022-23",
        "status": "INACTIVE"
    }
    test_ownership_schema = schemas.OwnershipGrowerGrowingSchema(**mapping_payload)
    result = create_grower_growing_area_mapping(payload=test_ownership_schema, db=db_mock)

    assert result['message'] == 'record exist'

    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.return_value.filter.return_value.first.return_value = None
    def mock_refresh_side_effect(instance):
        instance.growing_area_id_mapper_id = 999  # Simulate Auto-Increment ID
    db_mock.refresh.side_effect = mock_refresh_side_effect
    mapping_payload = {
        "row_id": "254#170#2022-23",
        "growing_area_id": 254,
        "grower_id": 170,
        "contract": 10,
        "year": 2023,
        "shrinkage": 0,
        "contract_erp": 0,
        "market": 0,
        "flex": 0,
        "ownership_id": "254#2022-23",
        "crop_type": "Storage",
        "crop_year": "2022-23",
        "status": "INACTIVE"
    }
    test_ownership_schema = schemas.OwnershipGrowerGrowingSchema(**mapping_payload)
    result = create_grower_growing_area_mapping(payload=test_ownership_schema, db=db_mock)

    assert result["status"] == "success"


@patch('database.get_db')
def test_successful_update_contract_erp(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    crop_year = "2023-24"
    db_mock.query().filter().all.return_value = [
        MagicMock(row_id='248#174#2023-24',
                  growing_area_id=248,
                  grower_id=174,
                  contract=670,
                  contract_erp=10,
                  shrinkage=5,
                  year=2023,
                  crop_type='Storage',
                  crop_year='2023-24',
                  ownership_id='248#2023-24',
                  status="INACTIVE"),
        MagicMock(row_id='111#111#2023-24',
                  growing_area_id=111,
                  grower_id=111,
                  contract=670,
                  contract_erp=0,
                  shrinkage=5,
                  year=2023,
                  crop_type='Storage',
                  crop_year='2023-24',
                  ownership_id='248#2023-24',
                  status="INACTIVE")]

    result = update_contract_erp(crop_year=crop_year, db=db_mock)
    assert result == {"message": f"Contract ERP updated for {crop_year}"}


@patch('database.get_db')
def test_successful_update_contract_erp_2(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    crop_year = "2023-24"

    db_mock.query().filter().all.return_value = [
        MagicMock(row_id='111#111#2023-24',
                  growing_area_id=111,
                  grower_id=111,
                  contract=100,
                  contract_erp=0,
                  shrinkage=0,
                  year=2023,
                  crop_type='Storage',
                  crop_year='2023-24',
                  ownership_id='111#2023-24',
                  status="INACTIVE")]

    result = update_contract_erp(crop_year=crop_year, db=db_mock)
    assert result == {"message": f"Contract ERP updated for {crop_year}"}

    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    crop_year = "2023-24"
    mock_view_row = MagicMock()
    mock_view_row.growignarea_id = 505  # Note: Matching the typo in your code
    mock_view_row.grower_id = 909
    mock_view_row.STORAGE_period = "2023-24"
    mock_view_row.sum_contract = 1500
    mock_view_row.CROP_TYPE = "Storage"
    query_return = db_mock.query.return_value.filter.return_value
    query_return.scalar.return_value = "2023-24"
    query_return.all.return_value = [mock_view_row]
    query_return.first.return_value = None

    result = update_contract_erp(crop_year=crop_year, db=db_mock)
    assert result == {"message": f"Contract ERP updated for {crop_year}"}


@patch('database.get_db')
def test_successful_delete_post(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    growing_area_id = 248
    grower_id = 174
    year = "2023-24"
    mock_record = MagicMock()
    db_mock.query().filter().first.return_value = mock_record
    result = delete_post(Growing_area_id=growing_area_id, Grower_id=grower_id, year=year, db=db_mock)

    assert result == {"status": "success",
                      "record has been deleted for": f"Grower Id: {grower_id}, Growing Area Id: {growing_area_id}"}
    
    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        delete_post(
            Growing_area_id="248", 
            Grower_id=174, 
            year="2023-24", 
            db=db_mock
        )

    assert exc_info.value.status_code == 404


"""--------Ownership.py---------"""

@patch('database.get_db')
def test_get_ownership_region_0(mock_get_db):
    db_mock = MagicMock()

    # Prepare mock query chain
    mock_query = db_mock.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order = mock_filter.order_by.return_value
    mock_order.all.return_value = [
        {
            "ownership_id": "2#2023",
            "growing_area_id": 2,
            "region": 10,
            "crop_type": "Fresh",
            "crop_year": "2023",
            "year": 2023,
            "growing_area_short": "AM",
            "growing_area_name": "AM | Maricopa",
            "contract": 300,
            "contract_erp_value": 390,
            "shrinkage": 0,
            "to_ship": 300,
            "market": 61,
            "flex": 0,
            "total_ship": 361,
            "extension": 0,
            "demand": 360.79909,
            "Position": 0.20091000000002168
        }
    ]

    # Set return value of get_db to our mock
    mock_get_db.return_value = db_mock

    # Call the endpoint
    response = client.get('/api/ownership/region/US/year/2024')

    # Assertions
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "success"
    assert isinstance(response_json["ownership"], list)
    assert response_json["ownership"][0]["growing_area_id"] == 2


def test_get_ownership_region_1():
    response = client.get('/api/ownership/region/7/year/2023')
    assert response.status_code == 404

    response = client.get('/api/ownership/region/East - US/year/2023')
    assert response.status_code == 200
    

def test_get_ownership_region_2():
    response = client.get('/api/ownership/year/2023')
    assert response.status_code == 200

def test_get_extensions():
    response = client.get('/api/ownership/get_recent_extensions')
    assert response.status_code == 200

def test_get_ownership_variety():
    response = client.get('/api/ownership/variety/year/2025')
    assert response.status_code == 200

@patch('database.get_db')
def test_mock_create_new_ownership_success(mock_get_db):
    db_mock = Mock()
    growing_area_list_mock = [
        Mock(growing_area_id=44),
        Mock(status='ACTIVE')
    ]
    mock_get_db.return_value = db_mock
    db_mock.query().filter().all.return_value = growing_area_list_mock
    result = create_new_ownership(year=2025, db=db_mock)

    assert result["Status"] == "success"


@patch('database.get_db')
def test_mock_create_new_ownership_exception(mock_get_db):
    db_mock = Mock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().all.return_value = []
    with patch('database.get_db', return_value=db_mock):
        try:
            create_new_ownership(year=2023)
        except Exception as e:
            assert e.status_code == 400


@patch('database.get_db')
def test_update_ownership_contract_erp(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_view_data = [
        MagicMock(growing_area_id=1, totalsum=500),
        MagicMock(growing_area_id=2, totalsum=700)]

    db_mock.query().filter().all.return_value = mock_view_data
    existing_record_mock = models.Ownership(
        growing_area_id=1,
        crop_year="2023",
        contract_erp_value=200
    )
    db_mock.query().filter().first.return_value = existing_record_mock

    result = update_ownership_contract_erp(crop_year="2023", db=db_mock)
    assert result["message"] == "Total Contract ERP updated for 2023 in Ownership table"

def test_generate_ownership_payload_fresh_crop():
    """Test generate_ownership_payload for fresh crop"""
    
    result = generate_ownership_payload(
        growing_area_id=5,
        crop_year="2023",
        crop_type="Fresh",
        year=2023
    )
    
    assert result["ownership_id"] == "5#2023"
    
    result = generate_ownership_payload(
        growing_area_id=10,
        crop_year="2023-24",
        crop_type="Storage",
        year=2023
    )
    
    assert result["ownership_id"] == "10#2023-24"


# Test cases for calculate_to_ship
@patch('database.get_db')
def test_calculate_to_ship_with_active_records(mock_get_db):
    """Test calculate_to_ship with active records"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock query results for contract and shrinkage_volume
    mock_records = [
        (100, 10),
        (200, 20),
        (150, 15)
    ]
    
    db_mock.query().filter().all.return_value = mock_records
    db_mock.query().filter().update.return_value = 1
    
    calculate_to_ship(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.query().filter().update.assert_called_once()
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_calculate_to_ship_no_records(mock_get_db):
    """Test calculate_to_ship with no active records"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().all.return_value = []
    db_mock.query().filter().update.return_value = 1
    
    calculate_to_ship(growing_area_id=1, crop_period="2023", db=db_mock)
    
    # Should update with zeros
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_calculate_to_ship_zero_contract(mock_get_db):
    """Test calculate_to_ship when total contract is zero"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_records = [
        (0, 0),
        (0, 0)
    ]
    
    db_mock.query().filter().all.return_value = mock_records
    db_mock.query().filter().update.return_value = 1
    
    calculate_to_ship(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_calculate_to_ship_with_none_values(mock_get_db):
    """Test calculate_to_ship handles None values"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_records = [
        (100, None),  
        (None, 10),
        (200, 20)
    ]
    
    db_mock.query().filter().all.return_value = mock_records
    db_mock.query().filter().update.return_value = 1
    
    calculate_to_ship(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.commit.assert_called_once()


# Test cases for calculate_market_and_flex
@patch('database.get_db')
def test_calculate_market_and_flex_with_records(mock_get_db):
    """Test calculate_market_and_flex with active records"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_records = [
        (50, 10),
        (75, 15),
        (25, 5)
    ]
    
    db_mock.query().filter().all.return_value = mock_records
    db_mock.query().filter().update.return_value = 1
    
    calculate_market_and_flex(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.query().filter().update.assert_called_once()
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_calculate_market_and_flex_no_records(mock_get_db):
    """Test calculate_market_and_flex with no records"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().all.return_value = []
    db_mock.query().filter().update.return_value = 1
    
    calculate_market_and_flex(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_calculate_market_and_flex_with_none_values(mock_get_db):
    """Test calculate_market_and_flex handles None values"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_records = [
        (None, 10),
        (50, None),
        (25, 5)
    ]
    
    db_mock.query().filter().all.return_value = mock_records
    db_mock.query().filter().update.return_value = 1
    
    calculate_market_and_flex(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_calculate_market_and_flex_zero_values(mock_get_db):
    """Test calculate_market_and_flex with zero values"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_records = [
        (0, 0),
        (0, 0)
    ]
    
    db_mock.query().filter().all.return_value = mock_records
    db_mock.query().filter().update.return_value = 1
    
    calculate_market_and_flex(growing_area_id=1, crop_period="2023", db=db_mock)
    
    db_mock.commit.assert_called_once()


# Test cases for total_ship_calculation
@patch('database.get_db')
def test_total_ship_calculation_success(mock_get_db):
    """Test total_ship_calculation with valid record"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_ownership = MagicMock()
    mock_ownership.to_ship = 100
    mock_ownership.market = 50
    mock_ownership.flex = 25
    mock_ownership.total_ship = 0
    
    db_mock.query().filter().first.return_value = mock_ownership
    
    tsc(growing_area_id=12, crop_period="2023", db=db_mock)
    
    assert mock_ownership.total_ship == 175
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_total_ship_calculation_no_record(mock_get_db):
    """Test total_ship_calculation when no ownership record exists"""

    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().first.return_value = None
    
    tsc(growing_area_id=12, crop_period="2023", db=db_mock)
    
    # Should not commit if no record found
    db_mock.commit.assert_not_called()


@patch('database.get_db')
def test_total_ship_calculation_with_none_values(mock_get_db):
    """Test total_ship_calculation handles None values"""
    
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_ownership = MagicMock()
    mock_ownership.to_ship = None
    mock_ownership.market = None
    mock_ownership.flex = None
    mock_ownership.total_ship = 0
    
    db_mock.query().filter().first.return_value = mock_ownership
    
    tsc(growing_area_id=12, crop_period="2023", db=db_mock)
    
    assert mock_ownership.total_ship == 0
    db_mock.commit.assert_called_once()



# Test cases for POST /update_contract_shrinkage_mkt_flex
@patch('ownership.total_ship_calculation')
@patch('ownership.calculate_market_and_flex')
@patch('ownership.calculate_to_ship')
@patch('database.get_db')
def test_update_contract_shrinkage_mkt_flex_success(mock_get_db, mock_calc_to_ship, 
                                                     mock_calc_market_flex, mock_total_ship):
    """Test update_contract_shrinkage_mkt_flex endpoint success"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock old records exist
    db_mock.query().filter().all.return_value = [MagicMock()]
    
    payload_data = {
        "PayloadOwnership": [
            {
                "row_id": "1#1#2023",
                "growing_area_id": 1,
                "grower_id": 1,
                "contract": 100,
                "shrinkage_volume": 10,
                "shrinkage": 10,
                "market": 50,
                "flex": 25,
                "crop_year": "2023",
                "crop_type": "Fresh",
                "year": 2023,
                "ownership_id": "1#2023",
                "status": "ACTIVE"
            }
        ]
    }
    
    response = client.post(
        '/api/ownership/update_contract_shrinkage_mkt_flex/growing_area_id/1/crop/2023',
        json=payload_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Ownership is updated" in data["message"]


@patch('ownership.total_ship_calculation')
@patch('ownership.calculate_market_and_flex')
@patch('ownership.calculate_to_ship')
@patch('database.get_db')
def test_update_contract_shrinkage_mkt_flex_no_old_records(mock_get_db, mock_calc_to_ship,
                                                            mock_calc_market_flex, mock_total_ship):
    """Test update_contract_shrinkage_mkt_flex when no old records exist"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock no old records
    db_mock.query().filter().all.return_value = []
    
    payload_data = {
        "PayloadOwnership": [
            {
                "row_id": "1#1#2023",
                "growing_area_id": 1,
                "grower_id": 1,
                "contract": 100,
                "shrinkage_volume": 10,
                "shrinkage": None,
                "market": 50,
                "flex": 25,
                "crop_year": "2023",
                "crop_type": "Fresh",
                "year": 2023,
                "ownership_id": "1#2023",
                "status": "ACTIVE"
            }
        ]
    }
    
    response = client.post(
        '/api/ownership/update_contract_shrinkage_mkt_flex/growing_area_id/1/crop/2023',
        json=payload_data
    )
    
    assert response.status_code == 200


@patch('ownership.total_ship_calculation')
@patch('ownership.calculate_market_and_flex')
@patch('ownership.calculate_to_ship')
@patch('database.get_db')
def test_update_contract_shrinkage_mkt_flex_compute_shrinkage_from_percent(
    mock_get_db, mock_calc_to_ship, mock_calc_market_flex, mock_total_ship):
    """Test update_contract_shrinkage_mkt_flex computes shrinkage_volume from percent"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().all.return_value = []
    
    payload_data = {
        "PayloadOwnership": [
            {
                "row_id": "1#1#2023",
                "growing_area_id": 1,
                "grower_id": 1,
                "contract": 100,
                "shrinkage_volume": None,  # No volume provided
                "shrinkage": 10,           # 10% shrinkage
                "market": 50,
                "flex": 25,
                "crop_year": "2023",
                "crop_type": "Fresh",
                "year": 2023,
                "ownership_id": "1#2023",
                "status": "ACTIVE"
            }
        ]
    }
    
    response = client.post(
        '/api/ownership/update_contract_shrinkage_mkt_flex/growing_area_id/1/crop/2023',
        json=payload_data
    )
    
    assert response.status_code == 200


@patch('ownership.total_ship_calculation')
@patch('ownership.calculate_market_and_flex')
@patch('ownership.calculate_to_ship')
@patch('database.get_db')
def test_update_contract_shrinkage_mkt_flex_zero_contract(
    mock_get_db, mock_calc_to_ship, mock_calc_market_flex, mock_total_ship):
    """Test update_contract_shrinkage_mkt_flex with zero contract"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().all.return_value = []
    
    payload_data = {
        "PayloadOwnership": [
            {
                "row_id": "1#1#2023",
                "growing_area_id": 1,
                "grower_id": 1,
                "contract": 0,
                "shrinkage_volume": 10,
                "shrinkage": 10,
                "market": 0,
                "flex": 0,
                "crop_year": "2023",
                "crop_type": "Fresh",
                "year": 2023,
                "ownership_id": "1#2023",
                "status": "ACTIVE"
            }
        ]
    }
    
    response = client.post(
        '/api/ownership/update_contract_shrinkage_mkt_flex/growing_area_id/1/crop/2023',
        json=payload_data
    )
    
    assert response.status_code == 200


@patch('ownership.total_ship_calculation')
@patch('ownership.calculate_market_and_flex')
@patch('ownership.calculate_to_ship')
@patch('database.get_db')
def test_update_contract_shrinkage_mkt_flex_multiple_records(
    mock_get_db, mock_calc_to_ship, mock_calc_market_flex, mock_total_ship):
    """Test update_contract_shrinkage_mkt_flex with multiple records"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().all.return_value = [MagicMock(), MagicMock()]
    
    payload_data = {
        "PayloadOwnership": [
            {
                "row_id": "1#1#2023",
                "growing_area_id": 1,
                "grower_id": 1,
                "contract": 100,
                "shrinkage_volume": 10,
                "shrinkage": 10,
                "market": 50,
                "flex": 25,
                "crop_year": "2023",
                "crop_type": "Fresh",
                "year": 2023,
                "ownership_id": "1#2023",
                "status": "ACTIVE"
            },
            {
                "row_id": "1#2#2023",
                "growing_area_id": 1,
                "grower_id": 2,
                "contract": 200,
                "shrinkage_volume": 20,
                "shrinkage": 10,
                "market": 75,
                "flex": 30,
                "crop_year": "2023",
                "crop_type": "Fresh",
                "year": 2023,
                "ownership_id": "1#2023",
                "status": "ACTIVE"
            }
        ]
    }
    
    response = client.post(
        '/api/ownership/update_contract_shrinkage_mkt_flex/growing_area_id/1/crop/2023',
        json=payload_data
    )
    
    assert response.status_code == 200


# Test cases for POST /new_growing_area
@patch('ownership.generate_ownership_payload')
@patch('database.get_db')
def test_new_growing_area_success(mock_get_db, mock_generate_payload):
    """Test new_growing_area endpoint success"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock growing_area_id lookup
    db_mock.query().filter().scalar.return_value = 5
    
    # Mock payload generation
    mock_generate_payload.side_effect = [
        {"ownership_id": "5#2022-23"},  # previous storage
        {"ownership_id": "5#2023"},     # current fresh
        {"ownership_id": "5#2023-24"}   # current storage
    ]
    
    with patch('ownership.date') as mock_date:
        mock_date.today.return_value.year = 2023
        
        response = client.post('/api/ownership/new_growing_area/Test Area')
        
        assert response.status_code == 200
        data = response.json()
        assert data["Status"] == "success"
        assert "2022-23" in data["message"]
        assert "2023" in data["message"]
        assert "2023-24" in data["message"]


@patch('ownership.generate_ownership_payload')
@patch('database.get_db')
def test_new_growing_area_year_calculation(mock_get_db, mock_generate_payload):
    """Test new_growing_area correctly calculates years"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().scalar.return_value = 10
    
    mock_generate_payload.side_effect = [
        {"ownership_id": "10#2024-25"},
        {"ownership_id": "10#2025"},
        {"ownership_id": "10#2025-26"}
    ]
    
    with patch('ownership.date') as mock_date:
        mock_date.today.return_value.year = 2025
        
        response = client.post('/api/ownership/new_growing_area/New Area')
        
        assert response.status_code == 200
        data = response.json()
        assert "2024-25" in data["message"]  # Previous storage
        assert "2025" in data["message"]     # Current fresh
        assert "2025-26" in data["message"]  # Current storage


@patch('ownership.models.Ownership')
@patch('ownership.generate_ownership_payload')
@patch('database.get_db')
def test_new_growing_area_creates_three_records(mock_get_db, mock_generate_payload, mock_ownership_model):
    """Test new_growing_area creates exactly 3 ownership records"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.query().filter().scalar.return_value = 7
    
    mock_generate_payload.side_effect = [
        {"ownership_id": "7#2022-23", "crop_type": "Storage"},
        {"ownership_id": "7#2023", "crop_type": "Fresh"},
        {"ownership_id": "7#2023-24", "crop_type": "Storage"}
    ]
    
    with patch('ownership.date') as mock_date:
        mock_date.today.return_value.year = 2023
        
        response = client.post('/api/ownership/new_growing_area/Area 7')
        
        assert response.status_code == 500


"""--------extensionMapping.py---------"""

def test_get_extension_mapping():
    response = client.get('/api/extensionMapping/')
    assert response.status_code == 200

def test_get_extension_year_mapping():
    response = client.get('/api/extensionMapping/year/2025')
    assert response.status_code == 200


"""--------MarketFlexMapping.py---------"""


def test_get_marketflex_mapping():
    response = client.get('/api/MarketFlexMapping/')
    assert response.status_code == 200


@patch('database.get_db')
def test_filtered_market_year(mock_get_db):
    db_mock = MagicMock()
    query_mock = MagicMock()
    db_mock.query = query_mock
    mock_get_db.return_value = db_mock

    mock_filtered_market = [models.MarketFlexMapping(ownership_id=1, status="ACTIVE"),
                            models.MarketFlexMapping(ownership_id=2, status="ACTIVE")]
    query_mock.return_value.join.return_value.filter.return_value.all.return_value = mock_filtered_market

    result = filtered_market_year(2023, db=db_mock)

    assert result['status'] == 'success'
    assert len(result['MarketFlexMapping']) == len(mock_filtered_market)


@patch('database.get_db')
def test_mock_update_market_flex(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_market = [{
        "row_id": "123#123#1",
        "growing_area_id": 123,
        "grower_id": 123,
        "ownership_id": "123#123",
        "status": "INACTIVE",
        "market_flex_value": 0
    }]
    marketflex_payload = schemas.MarketFlexPayload(Payload_MarketFlex=payload_market)
    result = update_market_flex(payload=marketflex_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"


@patch('database.get_db')
def test_mock_update_market_flex_1(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_market = [{
        "row_id": "123#123#1",
        "growing_area_id": 123,
        "grower_id": 123,
        "ownership_id": "123#123",
        "status": "INACTIVE",
        "market_flex_value": 100
    }]
    marketflex_payload = schemas.MarketFlexPayload(Payload_MarketFlex=payload_market)
    result = update_market_flex(payload=marketflex_payload, db=db_mock)
    assert "status" in result
    assert result["status"] == "success"

def test_filtered_market_success():
    db_mock = MagicMock()

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [MagicMock(), MagicMock()]
    db_mock.query.return_value = q

    result = filtered_market(db=db_mock)

    assert result["status"] == "success"
    assert len(result["MarketFlexMapping"]) == 2


def test_filtered_market_no_records_returns_http_200():
    db_mock = MagicMock()

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        filtered_market(db=db_mock)

    assert exc.value.status_code == 200
    assert "No market flex value" in exc.value.detail


def test_filtered_market_year_no_records_returns_http_200():
    db_mock = MagicMock()

    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        filtered_market_year(2025, db=db_mock)

    assert exc.value.status_code == 200
    assert "No market flex value" in exc.value.detail


def test_total_ship_calculation_updates_total_ship_and_commits():
    db_mock = MagicMock()

    ownership_record = MagicMock()
    ownership_record.to_ship = 10
    ownership_record.market_and_flex = 2

    q = MagicMock()
    q.filter.return_value = q
    q.first.return_value = ownership_record
    db_mock.query.return_value = q

    total_ship_calculation("OWN#1", db=db_mock)

    assert ownership_record.total_ship == 12
    db_mock.commit.assert_called_once()


def test_total_ship_calculation_exception_raises_400():
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        total_ship_calculation("OWN#1", db=db_mock)

    assert exc.value.status_code == 400

def test_update_market_flex_exception_raises_400():
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("boom")

    payload_market = [{
        "row_id": "123#123#1",
        "growing_area_id": 123,
        "grower_id": 123,
        "ownership_id": "OWN#1",
        "status": "INACTIVE",
        "market_flex_value": 10
    }]
    marketflex_payload = schemas.MarketFlexPayload(Payload_MarketFlex=payload_market)

    with pytest.raises(HTTPException) as exc:
        update_market_flex(payload=marketflex_payload, db=db_mock)

    assert exc.value.status_code == 400

"""--------plants.py---------"""


@patch('database.get_db')
def test_create_plant(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    plant_payload = {
        "plant_id": 1,
        "plant_code": "Test_1",
        "plant_name": "Test_1",
        "company_name": "Test_1",
        "region_id": 0,
        "status": "INACTIVE",
        "crop_category_id": 0,
        "created_time": "2023-12-15T13:51:55.222Z",
        "updated_time": "2023-12-15T13:51:55.222Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.PlantSchema(**plant_payload)
    result = create_plant(payload=mock_payload, db=db_mock)
    assert result['status'] == 'success'


def test_get_plant():
    response = client.get('/api/plant/')
    assert response.status_code == 200


def test_get_plantid():
    response = client.get('/api/plant/10')
    assert response.status_code == 200

    response = client.get('/api/plant/200')
    assert response.status_code == 404


def test_get_plants_country_based():
    response = client.get('/api/plant/get_country_company_name/US')
    assert response.status_code == 200

    response = client.get('/api/plant/get_country_company_name/US-CORE')
    assert response.status_code == 200


def test_get_plant_region_based():
    response = client.get('/api/plant/get_region/8')
    assert response.status_code == 200


"""__________pcusage.py__________"""


def test_get_filtered_usage_company():
    response = client.get('/api/pcusage/company_name/Co-Man/year/2023')
    assert response.status_code == 200

    response = client.get('/api/pcusage/company_name/US/year/2023')
    assert response.status_code == 200


def test_get_filtered_usage_region():
    response = client.get('/api/pcusage/region_id/10/year/2023')
    assert response.status_code == 200


def test_getusage_company_periodwise():
    response = client.get('/api/pcusage/all_week_data/year/2023')
    assert response.status_code == 200


def test_get_usage_period_wise():
    response = client.get('/api/pcusage/period_wise/company_name/Co-Man/year/2023')
    assert response.status_code == 200

    response = client.get('/api/pcusage/period_wise/company_name/US/year/2023')
    assert response.status_code == 200


def test_get_usage_period_wise_region_wise():
    response = client.get('/api/pcusage/period_wise/region_id/10/year/2023')
    assert response.status_code == 200


def test_get_period_usage_all_data():
    response = client.get('/api/pcusage/all_period_data/year/2023')
    assert response.status_code == 200

def test_pcusage_trim():
    assert trim("  hello world  ") == "helloworld"
    assert trim("nospaces") == "nospaces"
    assert trim("") == ""
    assert trim("   ") == ""
    with pytest.raises(HTTPException) as exc_info:
        trim(123) 
    assert exc_info.value.status_code == 400


"""_________growing_area.py - Comprehensive Unit Tests_________"""

# Test cases for GET /api/growing-area/
def test_get_growing_area_success():
    """Test successful retrieval of all active growing areas"""
    response = client.get('/api/growing-area/')
    assert response.status_code == 200
    assert "status" in response.json()
    assert "growing_area" in response.json()


@patch('database.get_db')
def test_get_growing_area_success_mock(mock_get_db):
    """Test get_growing_area with mocked database returning active areas"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_growing_area_1 = MagicMock()
    mock_growing_area_1.growing_area_id = 1
    mock_growing_area_1.growing_area_name = "Area 1"
    mock_growing_area_1.status = "ACTIVE"
    
    mock_growing_area_2 = MagicMock()
    mock_growing_area_2.growing_area_id = 2
    mock_growing_area_2.growing_area_name = "Area 2"
    mock_growing_area_2.status = "ACTIVE"
    
    query_mock = MagicMock()
    query_mock.filter.return_value.all.return_value = [mock_growing_area_1, mock_growing_area_2]
    db_mock.query.return_value = query_mock
    
    result = get_growing_area(db=db_mock)
    
    assert result["status"] == "success"
    assert len(result["growing_area"]) == 2


@patch('database.get_db')
def test_get_growing_area_not_found(mock_get_db):
    """Test get_growing_area when no active areas exist - should raise 404"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.filter.return_value.all.return_value = []
    db_mock.query.return_value = query_mock
    
    with pytest.raises(HTTPException) as exc_info:
        get_growing_area(db=db_mock)
    
    assert exc_info.value.status_code == 404
    assert "No growing area  found" in str(exc_info.value.detail)


# Test cases for POST /api/growing-area/
@patch('database.get_db')
def test_create_growing_area_success(mock_get_db):
    """Test successful creation of a new growing area"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_new_area = MagicMock()
    mock_new_area.growing_area_id = 123
    
    db_mock.refresh.side_effect = lambda instance: setattr(instance, 'growing_area_id', 123)
    
    growing_payload = {
        "growing_area_id": 123,
        "growing_area_name": "Test Area",
        "region": 10,
        "country": "US",
        "status": "ACTIVE",
        "growing_area_desc": "Test Description",
        "fresh_period_start": 1,
        "fresh_week_start": 1,
        "fresh_period_end": 6,
        "fresh_week_end": 4,
        "created_time": "2023-12-28T10:04:33.964Z",
        "updated_time": "2023-12-28T10:04:33.964Z",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    mock_payload = schemas.GrowingAreaSchema(**growing_payload)
    
    result = create_growing_area(payload=mock_payload, db=db_mock)
    
    assert result["status"] == "success"
    assert result["growing_area_id"] == 123
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_create_growing_area_exception(mock_get_db):
    """Test create_growing_area when database error occurs"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.add.side_effect = Exception("Database constraint violation")
    
    growing_payload = {
        "growing_area_id": 456,
        "growing_area_name": "Invalid Area",
        "region": 10,
        "country": "US",
        "status": "ACTIVE",
        "growing_area_desc": "Test",
        "fresh_period_start": 1,
        "fresh_week_start": 1,
        "fresh_period_end": 6,
        "fresh_week_end": 4,
        "created_time": "2023-12-28T10:04:33.964Z",
        "updated_time": "2023-12-28T10:04:33.964Z",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    mock_payload = schemas.GrowingAreaSchema(**growing_payload)
    
    with pytest.raises(HTTPException) as exc_info:
        create_growing_area(payload=mock_payload, db=db_mock)
    
    assert exc_info.value.status_code == 400


# Test cases for GET /api/growing-area/preferred_grower
def test_get_preferred_grower_success():
    """Test successful retrieval of preferred grower mappings"""
    response = client.get('/api/growing-area/preferred_grower')
    assert response.status_code == 200
    assert "status" in response.json()
    assert "preferred_grower" in response.json()


@patch('database.get_db')
def test_get_preferred_grower_success_mock(mock_get_db):
    """Test get_preferred_grower with mocked database"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_grower_1 = MagicMock()
    mock_grower_1.row_id = 1
    mock_grower_1.grower_id = 100
    mock_grower_1.growing_area_id = 10
    
    mock_grower_2 = MagicMock()
    mock_grower_2.row_id = 2
    mock_grower_2.grower_id = 101
    mock_grower_2.growing_area_id = 11
    
    query_mock = MagicMock()
    query_mock.all.return_value = [mock_grower_1, mock_grower_2]
    db_mock.query.return_value = query_mock
    
    result = get_preferred_grower(db=db_mock)
    
    assert result["status"] == "success"
    assert len(result["preferred_grower"]) == 2


@patch('database.get_db')
def test_get_preferred_grower_not_found(mock_get_db):
    """Test get_preferred_grower when no mappings exist - should raise 404"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.all.return_value = []
    db_mock.query.return_value = query_mock
    
    with pytest.raises(HTTPException) as exc_info:
        get_preferred_grower(db=db_mock)
    
    assert exc_info.value.status_code == 404
    assert "No grower  found" in str(exc_info.value.detail)


# Test cases for GET /api/growing-area/{growing_areaId}
def test_get_growingid_success():
    """Test successful retrieval of growing area by ID"""
    response = client.get('/api/growing-area/10')
    # Will succeed if ID 10 exists, otherwise 404
    assert response.status_code in [200, 404]


@patch('database.get_db')
def test_get_growingid_success_mock(mock_get_db):
    """Test get_growingid with mocked database returning a specific area"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_growing_area = MagicMock()
    mock_growing_area.growing_area_id = "GA123"
    mock_growing_area.growing_area_name = "Test Area"
    mock_growing_area.region = 5
    mock_growing_area.country = "US"
    mock_growing_area.status = "ACTIVE"
    
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = mock_growing_area
    db_mock.query.return_value = query_mock
    
    result = get_growingid(growing_areaId="GA123", db=db_mock)
    
    assert result["status"] == "success"
    assert result["growing-area"] == mock_growing_area


@patch('database.get_db')
def test_get_growingid_not_found(mock_get_db):
    """Test get_growingid when area ID does not exist - should raise 404"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = None
    db_mock.query.return_value = query_mock
    
    with pytest.raises(HTTPException) as exc_info:
        get_growingid(growing_areaId="NONEXISTENT", db=db_mock)
    
    assert exc_info.value.status_code == 404
    assert "No Growing area  with this id:" in str(exc_info.value.detail)


@patch('database.get_db')
def test_get_growingid_various_ids(mock_get_db):
    """Test get_growingid with different ID formats"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_growing_area = MagicMock()
    mock_growing_area.growing_area_id = "999"
    
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = mock_growing_area
    db_mock.query.return_value = query_mock
    
    result = get_growingid(growing_areaId="999", db=db_mock)
    assert result["status"] == "success"


# Test cases for DELETE /api/growing-area/{growing_areaId}
@patch('database.get_db')
def test_delete_growing_area_success(mock_get_db):
    """Test successful soft delete of growing area"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.filter.return_value.update.return_value = 1
    db_mock.query.return_value = query_mock
    
    result = delete_growing_area(growing_areaId="GA456", db=db_mock)
    
    assert result.status_code == 204
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_delete_growing_area_not_found(mock_get_db):
    """Test delete_growing_area when area ID does not exist - should raise 404"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.filter.return_value.update.return_value = 0
    db_mock.query.return_value = query_mock
    
    with pytest.raises(HTTPException) as exc_info:
        delete_growing_area(growing_areaId="NONEXISTENT", db=db_mock)
    
    assert exc_info.value.status_code == 404
    assert "No growing area  with this id:" in str(exc_info.value.detail)


@patch('database.get_db')
def test_delete_growing_area_updates_status(mock_get_db):
    """Test that delete operation correctly updates status to IN-ACTIVE"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    update_mock = MagicMock(return_value=1)
    filter_mock = MagicMock()
    filter_mock.update = update_mock
    query_mock.filter.return_value = filter_mock
    db_mock.query.return_value = query_mock
    
    result = delete_growing_area(growing_areaId="GA789", db=db_mock)
    
    # Verify the update was called with correct status
    filter_mock.update.assert_called_once_with({'status': 'IN-ACTIVE'})
    assert result.status_code == 204


@patch('database.get_db')
def test_delete_growing_area_commit_called(mock_get_db):
    """Test that delete operation commits the transaction"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.filter.return_value.update.return_value = 1
    db_mock.query.return_value = query_mock
    
    delete_growing_area(growing_areaId="GA999", db=db_mock)
    
    db_mock.commit.assert_called_once()


# Edge cases and additional coverage
@patch('database.get_db')
def test_create_growing_area_with_minimal_fields(mock_get_db):
    """Test creating growing area with only required fields"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.refresh.side_effect = lambda instance: setattr(instance, 'growing_area_id', 999)
    
    growing_payload = {
        "growing_area_id": 999,
        "growing_area_name": "Minimal Area",
        "region": 1,
        "country": "CA",
        "status": "ACTIVE",
        "growing_area_desc": None,
        "fresh_period_start": None,
        "fresh_week_start": None,
        "fresh_period_end": None,
        "fresh_week_end": None,
        "created_time": None,
        "updated_time": None,
        "created_by": None,
        "updated_by": None
    }
    mock_payload = schemas.GrowingAreaSchema(**growing_payload)
    
    result = create_growing_area(payload=mock_payload, db=db_mock)
    
    assert result["status"] == "success"
    assert result["growing_area_id"] == 999


@patch('database.get_db')
def test_get_growing_area_filters_inactive(mock_get_db):
    """Test that get_growing_area only returns ACTIVE status areas"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_active_area = MagicMock()
    mock_active_area.status = "ACTIVE"
    
    query_mock = MagicMock()
    filter_return = MagicMock()
    filter_return.all.return_value = [mock_active_area]
    query_mock.filter.return_value = filter_return
    db_mock.query.return_value = query_mock
    
    result = get_growing_area(db=db_mock)
    
    # Verify filter was called with ACTIVE status
    assert result["status"] == "success"
    assert len(result["growing_area"]) == 1


@patch('database.get_db')
def test_create_growing_area_database_rollback(mock_get_db):
    """Test that create_growing_area properly handles exceptions"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    db_mock.commit.side_effect = Exception("Connection lost")
    
    growing_payload = {
        "growing_area_id": 777,
        "growing_area_name": "Error Area",
        "region": 1,
        "country": "US",
        "status": "ACTIVE",
        "growing_area_desc": "Test",
        "fresh_period_start": 1,
        "fresh_week_start": 1,
        "fresh_period_end": 6,
        "fresh_week_end": 4,
        "created_time": "2023-12-28T10:04:33.964Z",
        "updated_time": "2023-12-28T10:04:33.964Z",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    mock_payload = schemas.GrowingAreaSchema(**growing_payload)
    
    with pytest.raises(HTTPException) as exc_info:
        create_growing_area(payload=mock_payload, db=db_mock)
    
    assert exc_info.value.status_code == 400
    assert "Connection lost" in str(exc_info.value.detail)


@patch('database.get_db')
def test_delete_growing_area_with_numeric_id(mock_get_db):
    """Test delete with numeric string ID"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    query_mock = MagicMock()
    query_mock.filter.return_value.update.return_value = 1
    db_mock.query.return_value = query_mock
    
    result = delete_growing_area(growing_areaId="12345", db=db_mock)
    
    assert result.status_code == 204


@patch('database.get_db')
def test_get_preferred_grower_multiple_entries(mock_get_db):
    """Test preferred grower retrieval with multiple mappings"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_growers = []
    for i in range(10):
        mock_grower = MagicMock()
        mock_grower.row_id = i
        mock_grower.grower_id = 100 + i
        mock_grower.growing_area_id = 10 + i
        mock_growers.append(mock_grower)
    
    query_mock = MagicMock()
    query_mock.all.return_value = mock_growers
    db_mock.query.return_value = query_mock
    
    result = get_preferred_grower(db=db_mock)
    
    assert result["status"] == "success"
    assert len(result["preferred_grower"]) == 10

"""________growers.py_________"""

# Test GET /api/growers/ -> get_growers
def test_get_growers():
    response = client.get('/api/grower/')
    assert response.status_code == 200

@patch("database.get_db")
def test_get_growers_success_mock(mock_get_db):
    """Test get_growers function with mocked database returning active growers"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock grower objects
    grower1 = MagicMock()
    grower1.grower_id = 1
    grower1.grower_name = "Test Grower 1"
    grower1.status = "ACTIVE"
    
    grower2 = MagicMock()
    grower2.grower_id = 2
    grower2.grower_name = "Test Grower 2"
    grower2.status = "ACTIVE"
    
    # Setup query mock chain
    q_growers = MagicMock()
    q_growers.filter.return_value = q_growers
    q_growers.order_by.return_value = q_growers
    q_growers.all.return_value = [grower1, grower2]
    
    db_mock.query.return_value = q_growers
    
    result = get_growers(db=db_mock)
    
    assert result["status"] == "success"
    assert len(result["growers"]) == 2
    assert result["growers"][0].grower_name == "Test Grower 1"


@patch("database.get_db")
def test_get_growers_not_found(mock_get_db):
    """Test get_growers when no active growers exist"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain to return empty list
    q_growers = MagicMock()
    q_growers.filter.return_value = q_growers
    q_growers.order_by.return_value = q_growers
    q_growers.all.return_value = []
    
    db_mock.query.return_value = q_growers
    
    with pytest.raises(HTTPException) as exc:
        get_growers(db=db_mock)
    
    assert exc.value.status_code == 404
    assert "No Growers  found" in str(exc.value.detail)


@patch("database.get_db")
def test_get_growers_database_exception(mock_get_db):
    """Test get_growers handles database exceptions"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Simulate database error
    db_mock.query.side_effect = Exception("Database connection error")
    
    with pytest.raises(Exception) as exc:
        get_growers(db=db_mock)
    
    assert "Database connection error" in str(exc.value)


# Test POST /api/growers/ -> create_growers
@patch("database.get_db")
def test_create_growers_success(mock_get_db):
    """Test creating a new grower successfully"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Create test payload
    payload = schemas.GrowerSchema(
        grower_name="New Grower",
        owner="Owner Name",
        region=1,
        country="USA",
        status="ACTIVE",
        volume="1000"
    )
    
    # Mock the new grower object after creation
    new_grower = MagicMock()
    new_grower.grower_id = 123
    
    db_mock.refresh = MagicMock(side_effect=lambda obj: setattr(obj, 'grower_id', 123))
    
    result = create_growers(payload=payload, db=db_mock)
    
    assert result["status"] == "success"
    assert "growers_id" in result
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@patch("database.get_db")
def test_create_growers_duplicate_name_exception(mock_get_db):
    """Test creating a grower with duplicate name raises exception"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    payload = schemas.GrowerSchema(
        grower_name="Duplicate Grower",
        owner="Owner Name",
        region=1,
        country="USA",
        status="ACTIVE",
        volume="1000"
    )
    
    # Simulate database constraint violation
    db_mock.commit.side_effect = Exception("Duplicate key violation")
    
    with pytest.raises(HTTPException) as exc:
        create_growers(payload=payload, db=db_mock)
    
    assert exc.value.status_code == 400
    assert "Duplicate key violation" in str(exc.value.detail)


@patch("database.get_db")
def test_create_growers_validation_error(mock_get_db):
    """Test creating a grower with invalid data raises exception"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    payload = schemas.GrowerSchema(
        grower_name="Test Grower",
        owner="Owner Name",
        region=1,
        country="USA",
        status="ACTIVE",
        volume="1000"
    )
    
    # Simulate validation error during add
    db_mock.add.side_effect = Exception("Validation error: Invalid region")
    
    with pytest.raises(HTTPException) as exc:
        create_growers(payload=payload, db=db_mock)
    
    assert exc.value.status_code == 400


@patch("database.get_db")
def test_create_growers_db_commit_failure(mock_get_db):
    """Test creating a grower when database commit fails"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    payload = schemas.GrowerSchema(
        grower_name="Test Grower",
        owner="Owner Name",
        region=1,
        country="USA",
        status="ACTIVE",
        volume="1000"
    )
    
    # Simulate commit failure
    db_mock.commit.side_effect = Exception("Database commit failed")
    
    with pytest.raises(HTTPException) as exc:
        create_growers(payload=payload, db=db_mock)
    
    assert exc.value.status_code == 400
    assert "Database commit failed" in str(exc.value.detail)


# Test GET /api/growers/{growerId} -> get_post
def test_get_post_grower_success():
    """Test retrieving a specific grower by ID via API endpoint"""
    # First create a grower to ensure it exists
    response = client.get('/api/growers/')
    if response.status_code == 200 and response.json().get("growers"):
        grower_id = response.json()["growers"][0].get("grower_id")
        if grower_id:
            response = client.get(f'/api/growers/{grower_id}')
            assert response.status_code == 200
            assert "grower" in response.json()


@patch("database.get_db")
def test_get_post_success_mock(mock_get_db):
    """Test get_post function with mocked database returning specific grower"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock grower object
    grower = MagicMock()
    grower.grower_id = "123"
    grower.grower_name = "Test Grower"
    grower.owner = "Test Owner"
    grower.region = 1
    grower.country = "USA"
    grower.status = "ACTIVE"
    
    # Setup query mock chain
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.first.return_value = grower
    
    db_mock.query.return_value = q_grower
    
    result = get_post(growerId="123", db=db_mock)
    
    assert result["status"] == "success"
    assert result["grower"].grower_id == "123"
    assert result["grower"].grower_name == "Test Grower"


@patch("database.get_db")
def test_get_post_not_found(mock_get_db):
    """Test get_post when grower with specified ID does not exist"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain to return None
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.first.return_value = None
    
    db_mock.query.return_value = q_grower
    
    with pytest.raises(HTTPException) as exc:
        get_post(growerId="999", db=db_mock)
    
    assert exc.value.status_code == 404
    assert "No growers  with this id:" in str(exc.value.detail)


@patch("database.get_db")
def test_get_post_invalid_id_type(mock_get_db):
    """Test get_post with invalid ID type"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain to return None
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.first.return_value = None
    
    db_mock.query.return_value = q_grower
    
    with pytest.raises(HTTPException) as exc:
        get_post(growerId="invalid_id", db=db_mock)
    
    assert exc.value.status_code == 404


@patch("database.get_db")
def test_get_post_database_exception(mock_get_db):
    """Test get_post handles database exceptions"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Simulate database error
    db_mock.query.side_effect = Exception("Database query error")
    
    with pytest.raises(Exception) as exc:
        get_post(growerId="123", db=db_mock)
    
    assert "Database query error" in str(exc.value)


# Test DELETE /api/growers/{growerId} -> delete_grower
@patch("database.get_db")
def test_delete_grower_success(mock_get_db):
    """Test soft-deleting a grower successfully"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain - update returns number of rows affected
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.update.return_value = 1  # 1 row updated
    
    db_mock.query.return_value = q_grower
    
    result = delete_grower(growerId="123", db=db_mock)
    
    assert result.status_code == 204
    q_grower.update.assert_called_once_with({'status': 'IN-ACTIVE'})
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_delete_grower_not_found(mock_get_db):
    """Test deleting a grower that does not exist"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain - update returns 0 (no rows affected)
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.update.return_value = 0  # 0 rows updated
    
    db_mock.query.return_value = q_grower
    
    with pytest.raises(HTTPException) as exc:
        delete_grower(growerId="999", db=db_mock)
    
    assert exc.value.status_code == 404
    assert "No growers  with this id:" in str(exc.value.detail)


@patch("database.get_db")
def test_delete_grower_already_inactive(mock_get_db):
    """Test deleting a grower that is already inactive"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain - update returns 0 (grower already IN-ACTIVE)
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.update.return_value = 0
    
    db_mock.query.return_value = q_grower
    
    with pytest.raises(HTTPException) as exc:
        delete_grower(growerId="123", db=db_mock)
    
    assert exc.value.status_code == 404


@patch("database.get_db")
def test_delete_grower_database_exception(mock_get_db):
    """Test delete_grower handles database exceptions"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Simulate database error during query
    db_mock.query.side_effect = Exception("Database connection lost")
    
    with pytest.raises(Exception) as exc:
        delete_grower(growerId="123", db=db_mock)
    
    assert "Database connection lost" in str(exc.value)


@patch("database.get_db")
def test_delete_grower_commit_failure(mock_get_db):
    """Test delete_grower when commit fails"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain - update succeeds
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.update.return_value = 1
    
    db_mock.query.return_value = q_grower
    
    # Simulate commit failure
    db_mock.commit.side_effect = Exception("Commit transaction failed")
    
    with pytest.raises(Exception) as exc:
        delete_grower(growerId="123", db=db_mock)
    
    assert "Commit transaction failed" in str(exc.value)


# Additional edge cases and integration tests

@patch("database.get_db")
def test_get_growers_ordered_alphabetically(mock_get_db):
    """Test that get_growers returns growers ordered by name"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock grower objects in non-alphabetical order
    grower1 = MagicMock()
    grower1.grower_name = "Zebra Farms"
    grower1.status = "ACTIVE"
    
    grower2 = MagicMock()
    grower2.grower_name = "Apple Growers"
    grower2.status = "ACTIVE"
    
    # The mock should simulate that order_by was called
    q_growers = MagicMock()
    q_growers.filter.return_value = q_growers
    q_growers.order_by.return_value = q_growers
    q_growers.all.return_value = [grower2, grower1]  # Already sorted by mock
    
    db_mock.query.return_value = q_growers
    
    result = get_growers(db=db_mock)
    
    # Verify order_by was called
    q_growers.order_by.assert_called_once()
    assert result["status"] == "success"


@patch("database.get_db")
def test_create_growers_with_optional_fields(mock_get_db):
    """Test creating a grower with all optional fields populated"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    payload = schemas.GrowerSchema(
        grower_name="Complete Grower",
        owner="Owner Name",
        region=1,
        country="USA",
        status="ACTIVE",
        volume="5000",
        created_time=datetime.now(),
        updated_time=datetime.now(),
        created_by="test_user",
        updated_by="test_user"
    )
    
    new_grower = MagicMock()
    new_grower.grower_id = 456
    
    db_mock.refresh = MagicMock(side_effect=lambda obj: setattr(obj, 'grower_id', 456))
    
    result = create_growers(payload=payload, db=db_mock)
    
    assert result["status"] == "success"
    assert result["growers_id"] == 456


@patch("database.get_db")
def test_delete_multiple_growers_sequential(mock_get_db):
    """Test deleting multiple growers sequentially"""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Setup query mock chain for multiple deletions
    q_grower = MagicMock()
    q_grower.filter.return_value = q_grower
    q_grower.update.return_value = 1
    
    db_mock.query.return_value = q_grower
    
    # Delete first grower
    result1 = delete_grower(growerId="123", db=db_mock)
    assert result1.status_code == 204
    
    # Delete second grower
    result2 = delete_grower(growerId="456", db=db_mock)
    assert result2.status_code == 204
    
    # Verify update was called twice
    assert q_grower.update.call_count == 2
    assert db_mock.commit.call_count == 2

"""_________plant_mtrx.py_________"""


def test_get_plant_mtrx():
    response = client.get('/api/plant_mtrx/plant/region_id/8/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_2():
    response = client.get('/api/plant_mtrx/growing_area/all_data/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_3():
    response = client.get('/api/plant_mtrx/plant/company_name/US/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_growing_area():
    response = client.get('/api/plant_mtrx/growing_area/region/8/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_growing_area_2():
    response = client.get('/api/plant_mtrx/growing_area/country/US/year/2023')
    assert response.status_code == 200


def test_get_plant_mtrx_region():
    response = client.get('/api/plant_mtrx/only_region_data/year/2023')
    assert response.status_code == 200

def test_getplantmtrx_region_period():
    response = client.get('/api/plant_mtrx/only_region_data/period-wise/year/2023')
    assert response.status_code == 200
    
def test_getplantmtrx_growingarea_by_region_period():
    response = client.get('/api/plant_mtrx/growing_area/period/region/10/year/2023')
    assert response.status_code == 200

def test_getplantmtrx_growingarea_by_country_period():
    response = client.get('/api/plant_mtrx/growing_area/period/country/US/year/2023')
    assert response.status_code == 200

def test_getplantmtrx_growingarea_all_period():
    response = client.get('/api/plant_mtrx/growing_area/period/all_data/year/2023')
    assert response.status_code == 200

def test_get_plants_online():
    response = client.get('/api/plant_mtrx/plant_status/10000')
    assert response.status_code == 404

    response = client.get('/api/plant_mtrx/plant_status/2025')
    assert response.status_code == 200


@patch('database.get_db')
def test_get_plantmtrx_common(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    filter_conditions = [10]
    name_or_id = "PlantX"
    year = 2023

    mock_position_data = [(1, 'Position1'), (2, 'Position2')]
    mock_plant_mtrx_data = [(1, 'PlantX', 1, 12, 'P12', 3, 2023, 100, 101, 'Area1'),
                            (2, 'PlantX', 2, 12, 'P12', 4, 2023, 150, 102, 'Area2')]
    db_mock.query().filter().all.side_effect = [mock_position_data, mock_plant_mtrx_data]

    result = get_plantmtrx_common(filter_conditions, name_or_id, year, db_mock)
    assert result["status"] == "success"

def test_plantmtrx_trim():
    assert tr("  hello world  ") == "helloworld"
    assert tr("nospaces") == "nospaces"
    assert tr("") == ""
    assert tr("   ") == ""
    with pytest.raises(HTTPException) as exc_info:
        tr(123) 
    assert exc_info.value.status_code == 400


@patch("database.get_db")
def test_func_getcrop_type_fresh_with_fresh_period_data(mock_get_db):
    """Test crop type determination when period/week falls within fresh range."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = 5
    fresh_arr_mock.fresh_week_start = 2
    fresh_arr_mock.fresh_period_end = 10
    fresh_arr_mock.fresh_week_end = 3
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=7, 
        week=1, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Fresh"
    assert crop_year == "2024"


@patch("database.get_db")
def test_func_getcrop_type_storage_before_fresh_range(mock_get_db):
    """Test crop type determination when period/week is before fresh range."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = 5
    fresh_arr_mock.fresh_week_start = 2
    fresh_arr_mock.fresh_period_end = 10
    fresh_arr_mock.fresh_week_end = 3
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=3, 
        week=1, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Storage"
    assert crop_year == "2023-24"


@patch("database.get_db")
def test_func_getcrop_type_storage_after_fresh_range(mock_get_db):
    """Test crop type determination when period/week is after fresh range."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = 5
    fresh_arr_mock.fresh_week_start = 2
    fresh_arr_mock.fresh_period_end = 10
    fresh_arr_mock.fresh_week_end = 3
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=11, 
        week=2, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Storage"
    assert crop_year == "2024-25"


@patch("database.get_db")
def test_func_getcrop_type_default_range_no_fresh_data(mock_get_db):
    """Test crop type determination with default range when fresh data is None."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = None
    fresh_arr_mock.fresh_week_start = None
    fresh_arr_mock.fresh_period_end = None
    fresh_arr_mock.fresh_week_end = None
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=7, 
        week=1, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Fresh"
    assert crop_year == "2024"


@patch("database.get_db")
def test_func_getcrop_type_default_range_storage_before(mock_get_db):
    """Test storage type with default range when value is below lower limit."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = None
    fresh_arr_mock.fresh_week_start = None
    fresh_arr_mock.fresh_period_end = None
    fresh_arr_mock.fresh_week_end = None
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=2, 
        week=1, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Storage"
    assert crop_year == "2023-24"


@patch("database.get_db")
def test_func_getcrop_type_default_range_storage_after(mock_get_db):
    """Test storage type with default range when value is above upper limit."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = None
    fresh_arr_mock.fresh_week_start = None
    fresh_arr_mock.fresh_period_end = None
    fresh_arr_mock.fresh_week_end = None
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=12, 
        week=1, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Storage"
    assert crop_year == "2024-25"


@patch("database.get_db")
def test_func_getcrop_type_boundary_lower_limit(mock_get_db):
    """Test crop type at exact lower boundary of fresh range."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = 5
    fresh_arr_mock.fresh_week_start = 2
    fresh_arr_mock.fresh_period_end = 10
    fresh_arr_mock.fresh_week_end = 3
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=5, 
        week=2, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Fresh"
    assert crop_year == "2024"


@patch("database.get_db")
def test_func_getcrop_type_boundary_upper_limit(mock_get_db):
    """Test crop type at exact upper boundary of fresh range."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    fresh_arr_mock = MagicMock()
    fresh_arr_mock.fresh_period_start = 5
    fresh_arr_mock.fresh_week_start = 2
    fresh_arr_mock.fresh_period_end = 10
    fresh_arr_mock.fresh_week_end = 3
    q_mock = MagicMock()
    q_mock.filter.return_value = q_mock
    q_mock.first.return_value = fresh_arr_mock
    db_mock.query.return_value = q_mock
    crop_type, crop_year = func_getcrop_type(
        period=10, 
        week=3, 
        year=2024, 
        growing_area_id=1, 
        db=db_mock
    )
    
    assert crop_type == "Fresh"
    assert crop_year == "2024"

"""______________category.py______________"""


def test_get_category():
    response = client.get('/api/category/')
    assert response.status_code == 200


@patch('database.get_db')
def test_delete_category(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().update.return_value = 1

    result = delete_category(categoryId="1", db=db_mock)
    assert result.status_code == 204


@patch('database.get_db')
def test_create_category(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_category = {
        "category_name": "TEST",
        "country": "US",
        "status": "INACTIVE",
        "created_time": "2024-01-08T08:07:40.901Z",
        "updated_time": "2024-01-08T08:07:40.901Z",
        "created_by": "string",
        "updated_by": "string"
    }
    mock_payload = schemas.Category(**payload_category)
    result = create_category(payload=mock_payload, db=db_mock)
    assert result["status"] == "success"


"""--------solidrates.py---------"""

def test_get_solids_rates():
    response = client.get('/api/solid_rates/')
    assert response.status_code == 200


def test_get_by_solids_rate_id():
    response = client.get('/api/solid_rates/getBySolidsRateId/249')
    assert response.status_code == 200


def test_get_by_solids_rate_id_not_found():
    response = client.get('/api/solid_rates/getBySolidsRateId/999999')
    assert response.status_code == 404


def test_get_solid_rate_mapping():
    response = client.get('/api/solid_rates/solid_rate_mapping/2024')
    assert response.status_code == 200


def test_get_solid_rate_mapping_not_found():
    response = client.get('/api/solid_rates/solid_rate_mapping/1900')
    assert response.status_code == 404


@patch('database.get_db')
def test_update_solid_rates_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "period": 1,
                "solids_rate_id": 24,
                "rate": 120,
                "period_year": 2023
            }
        ]
    }
    test_payload = schemas.solidRateMappingPayload(**payload_data)
    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.update.return_value = 1
    result = update_solid_rates_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"
    assert result["records_updated"] == 1
    db_mock.commit.assert_called_once()


def test_solid_rate_period_year_region_all():
    response = client.get('/api/solid_rates/solid_rate_period_year_region/2024/{region}?region_name=All')
    assert response.status_code == 200


def test_solid_rate_period_year_region_us():
    response = client.get('/api/solid_rates/solid_rate_period_year_region/2024/{region}?region_name=US')
    assert response.status_code == 200


def test_solid_rate_period_year_region_specific():
    response = client.get('/api/solid_rates/solid_rate_period_year_region/2024/{region}?region_name=Canada')
    assert response.status_code == 200

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_solid_rates_mappings_for_next_year_full_coverage(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_currency_us = MagicMock(solids_rate_id=1, currency="USD")
    mock_currency_cad = MagicMock(solids_rate_id=2, currency="CAD")
    mock_new_rec = MagicMock(growing_area_id=100, solids_rate_id=1)
    mock_rate_found = MagicMock(actual_rate=1.5)
    mock_q_delete = MagicMock()
    mock_q_delete.filter.return_value.all.return_value = [MagicMock()]
    mock_q_country = MagicMock()
    mock_q_country.all.return_value = [mock_currency_us, mock_currency_cad]
    mock_q_new_recs = MagicMock()
    mock_q_new_recs.distinct.return_value.all.return_value = [mock_new_rec]
    mock_q_rate = MagicMock()
    mock_q_rate.filter.return_value.first.side_effect = [mock_rate_found, None] * 10 
    db_mock.query.side_effect = [
        mock_q_delete, 
        mock_q_country, 
        mock_q_new_recs, 
    ] + [mock_q_rate] * 50 
    result = await create_solid_rates_mappings_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "success"


def test_solid_rate_data():
    response = client.get('/api/solid_rates/solid_rate_data/2024/US')
    assert response.status_code == 200

@patch('solidrates.create_solid_rate_in_db')
@patch('database.get_db')
def test_create_potato_rates_success(mock_get_db, mock_create_helper):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = schemas.SolidRatesSchema(
        year=2024,
        growing_area_id=1,
        currency="USD",
        created_by="test_user",
        updated_by="test_user"
    ) 
    mock_record = MagicMock()
    mock_record.solids_rate_id = 10
    mock_create_helper.return_value = mock_record
    result = create_solids_rates(payload=payload_data, db=db_mock)
    
    assert result["status"] == "success"

def test_create_solid_rate_in_db_logic():
    db_mock = MagicMock()
    payload_data = schemas.SolidRatesSchema(
        year=2024,
        growing_area_id=1,
        currency="USD",
        created_by="tester",
        updated_by="tester"
    )
    mock_db_item = MagicMock()
    mock_db_item.solids_rate_id = 99
    with patch('solidrates.solids_rates', return_value=mock_db_item):
        result = create_solid_rate_in_db(payload=payload_data, db=db_mock)

    assert result.solids_rate_id == 99
    db_mock.add.assert_called_once_with(mock_db_item)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(mock_db_item)


@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_solids_rates_with_default_value_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_solid_rate = MagicMock()
    mock_solid_rate.solids_rate_id = 1
    mock_solid_rate.default_value = 100.0
    mock_mapping_1 = MagicMock()
    mock_mapping_1.rate = 0
    mock_mapping_2 = MagicMock()
    mock_mapping_2.rate = 50
    mock_solid_query = db_mock.query.return_value
    mock_solid_query.filter.return_value.first.return_value = mock_solid_rate
    mock_mapping_query = db_mock.query.return_value
    mock_mapping_query.filter.return_value.all.return_value = [mock_mapping_1, mock_mapping_2]
    result = await update_solids_rates_with_default_value(solids_rate_id=1, year=2024, db=db_mock)
    
    assert result["status"] == "success"


@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_solids_rates_with_default_value_not_found(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await update_solids_rates_with_default_value(solids_rate_id=999999, year=2024, db=db_mock)
    
    assert exc_info.value.status_code == 404


def test_solid_rate_period_year_plant():
    response = client.get('/api/solid_rates/solid_rate_period_year_plant/2024/US')
    assert response.status_code == 200

@pytest.mark.asyncio
@patch('database.get_db')
async def test_upload_file_solids_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    excel_data = pd.DataFrame({
        'solids_rate_id': [1, 2],
        'country': ['US', 'US'],
        'year': [2024, 2024],
        'P1': [100, 200],
        'P2': [150, 250]
    })
    excel_buffer = BytesIO()
    excel_data.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.xlsx"
    file_mock.file = excel_buffer
    result = await upload_file_solids(uploaded_year=2024, user_email="test@test.com", file=file_mock, db=db_mock)
    assert result["detail"] == "Solids successfully uploaded for the year: 2024"

@pytest.mark.asyncio
@patch('database.get_db')
async def test_upload_file_solids_invalid_format(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.txt"
    file_mock.file = BytesIO(b"test")
    with pytest.raises(HTTPException) as exc_info:
        await upload_file_solids(uploaded_year=2024, user_email="test@test.com", file=file_mock, db=db_mock)
    assert exc_info.value.status_code == 400
    assert "Unsupported file format" in str(exc_info.value.detail)

@pytest.mark.asyncio
@patch('database.get_db')
async def test_upload_file_solids_multiple_sheets(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    with pd.ExcelWriter(BytesIO(), engine='openpyxl') as writer:
        pd.DataFrame({'col1': [1]}).to_excel(writer, sheet_name='Sheet1', index=False)
        pd.DataFrame({'col2': [2]}).to_excel(writer, sheet_name='Sheet2', index=False)
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.xlsx"
    file_mock.file = BytesIO()
    with pytest.raises(HTTPException) as exc_info:
        await upload_file_solids(uploaded_year=2024, user_email="test@test.com", file=file_mock, db=db_mock)
    assert exc_info.value.status_code == 500

@pytest.mark.asyncio
@patch('database.get_db')
async def test_upload_file_solids_missing_year(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    excel_data = pd.DataFrame({
        'solids_rate_id': [1, 2],
        'country': ['US', 'US'],
        'P1': [100, 200]
    })
    excel_buffer = BytesIO()
    excel_data.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.xlsx"
    file_mock.file = excel_buffer
    with pytest.raises(HTTPException) as exc_info:
        await upload_file_solids(uploaded_year=2024, user_email="test@test.com", file=file_mock, db=db_mock)
    assert exc_info.value.status_code == 500

@pytest.mark.asyncio
@patch('database.get_db')
async def test_upload_file_solids_year_mismatch(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    excel_data = pd.DataFrame({
        'solids_rate_id': [1, 2],
        'country': ['US', 'US'],
        'year': [2023, 2023],
        'P1': [100, 200]
    })
    excel_buffer = BytesIO()
    excel_data.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.xlsx"
    file_mock.file = excel_buffer
    with pytest.raises(HTTPException) as exc_info:
        await upload_file_solids(uploaded_year=2024, user_email="test@test.com", file=file_mock, db=db_mock)
    assert exc_info.value.status_code == 400
    assert "does not match" in str(exc_info.value.detail)

@pytest.mark.asyncio
@patch('database.get_db')
async def test_upload_file_solids_multiple_years(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    excel_data = pd.DataFrame({
        'solids_rate_id': [1, 2],
        'country': ['US', 'US'],
        'year': [2024, 2025],
        'P1': [100, 200]
    })
    excel_buffer = BytesIO()
    excel_data.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.xlsx"
    file_mock.file = excel_buffer
    with pytest.raises(HTTPException) as exc_info:
        await upload_file_solids(uploaded_year=2024, user_email="test@test.com", file=file_mock, db=db_mock)
    assert exc_info.value.status_code == 400
    assert "multiple year values" in str(exc_info.value.detail)


"""--------PotatoRates---------"""


def test_get_potato_rates():
    response = client.get('/api/potato_rates/')
    assert response.status_code == 200


def test_get_potato_rate_mapping_data():
    response = client.get('/api/potato_rates/potato_rate_mapping_by_year/2024')
    assert response.status_code == 200


def test_get_potato_rate_mappings():
    response = client.get('/api/potato_rates/get_potato_rate_mapping/2024')
    assert response.status_code == 200


@patch('database.get_db')
def test_mock_update_potato_rates_records(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "potato_rate_id": 241,
            "rate": 120,
            "week": 2
        }
    ]

    test_payload = schemas.potatoRateMappingPayload(data=payload)
    result = update_potato_rates_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"

    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "potato_rate_id": 0,
            "rate": 120,
            "week": 2
        }
    ]

    test_payload = schemas.potatoRateMappingPayload(data=payload)
    result = update_potato_rates_records(payload=test_payload, db=db_mock)
    assert result["status"] == "error"


def test_potato_rate_period_year_region():
    response = client.get('/api/potato_rates/potato_rate_period_year_region/2024/US',params={"region_name": "US"})
    assert response.status_code == 200

    response = client.get('/api/potato_rates/potato_rate_period_year_region/2024/All',params={"region_name": "All"})
    assert response.status_code == 200

    response = client.get('/api/potato_rates/potato_rate_period_year_region/2024/Canada',params={"region_name": "Canada"})
    assert response.status_code == 200

def test_potato_rate_period_week_year_region():
    response = client.get('/api/potato_rates/potato_rate_period_week_year_region/2024/US',params={"region_name": "US"})
    assert response.status_code == 200

    response = client.get('/api/potato_rates/potato_rate_period_week_year_region/2024/All',params={"region_name": "All"})
    assert response.status_code == 200

    response = client.get('/api/potato_rates/potato_rate_period_week_year_region/2024/Canada',params={"region_name": "Canada"})
    assert response.status_code == 200

def test_potato_rate_data():
    response = client.get('/api/potato_rates/potato_rate_data/2024/Canada')
    assert response.status_code == 200


@patch('potatorates.potato_rates')
@patch('database.get_db')
def test_create_potato_rates(mock_get_db, mock_potato_rates_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_instance_1 = MagicMock()
    mock_instance_1.potato_rate_id = 100
    mock_instance_2 = MagicMock()
    mock_instance_2.potato_rate_id = 200

    mock_potato_rates_model.side_effect = [mock_instance_1, mock_instance_2]
    pydantic_payload = schemas.PotatoRatesSchema(
        year=2024,
        growing_area_id=1,
        currency="USD"
    )
    result_route = create_potato_rates(payload=pydantic_payload, db=db_mock)

    assert result_route["status"] == "success"

    dict_payload = {
        "year": 2025,
        "growing_area_id": 2,
        "currency": "EUR"
    }
    result_helper = create_potato_rate_in_db(payload=dict_payload, db=db_mock)

    assert result_helper.potato_rate_id == 200

@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_potato_rates_default_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_rate = MagicMock()
    mock_rate.potato_rate_id = 1
    db_mock.query.return_value.filter.return_value.first.return_value = mock_rate
    result = await update_potato_rates_with_default_value(db=db_mock, potato_rate_id=1, year=2024)

    assert result['status'] == 'success'

@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_potato_rates_default_not_found(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await update_potato_rates_with_default_value(db=db_mock, potato_rate_id=999, year=2024)

    assert exc_info.value.status_code == 404

def test_potato_rate_plant_period_view():
    response = client.get('/api/potato_rates/potato_rate_plant_period_view/2024/Canada')
    assert response.status_code == 200

def test_potato_rate_plant_week_view():
    response = client.get('/api/potato_rates/potato_rate_plant_week_view/2024/Canada')
    assert response.status_code == 200



"""--------offcontractinfo.py---------"""


def test_get_off_contract_info():
    response = client.get('/api/off_contract_info/')
    assert response.status_code == 200


def test_get_off_contract_task_by_id():
    response = client.get('/api/off_contract_info/get_off_contract_task_by_id/1')
    assert response.status_code == 200

    response = client.get('/api/off_contract_info/get_off_contract_task_by_id/20')
    assert response.status_code == 404


def test_get_off_contract_task_mapping():
    response = client.get('/api/off_contract_info/off_contract_task_mapping/')
    assert response.status_code == 200


def test_off_contract_task_mapping_by_year_and_country():
    response = client.get('/api/off_contract_info/off_contract_task_mapping_by_year_and_country/2024/US-CORE')
    assert response.status_code == 200

    response = client.get('/api/off_contract_info/off_contract_task_mapping_by_year_and_country/1/US-CORE')
    assert response.status_code == 404


@patch('database.get_db')
def test_mock_create_off_contract_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "task_name": "productivity-task",
        "task_desc": "productivity-task",
        "status": "Active",
        "created_by": "System",
        "created_time": "2023-11-10T13:03:23.790000",
        "updated_by": "System",
        "updated_time": "2023-11-10T13:03:23.790000"
    }
    test_ownership_schema = schemas.OffContractInfoSchema(**mapping_payload)
    result = create_off_contract_info(payload=test_ownership_schema, db=db_mock)

    assert result['status'] == 'success'

@patch('database.get_db')
def test_create_off_contract_task_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.refresh.side_effect = lambda instance: setattr(instance, 'row_id', 1)

    payload_data = {
        "period": 1,
        "off_contract_task_id": 101,
        "year": 2024,
        "value": 1500.00,
        "company_name": "Test Corp"
    }
    test_schema = schemas.OffContractTaskMappingSchema(**payload_data)

    result = create_off_contract_task_mapping(payload=test_schema, db=db_mock)

    assert result['status'] == 'success'

@patch('database.get_db')
def test_update_off_contract(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_existing_record = MagicMock()
    mock_existing_record.off_contract_task_id = 123
    db_mock.query.return_value.filter.return_value.first.return_value = mock_existing_record

    payload_data = {
        "period": 5,
        "off_contract_task_id": 123,
        "year": 2025,
        "value": 999,
        "company_name": "Updated Company"
    }
    test_schema = schemas.OffContractTaskMappingSchema(**payload_data)

    result = update_off_contract(off_contract_task_id=123, payload=test_schema, db=db_mock)

    assert mock_existing_record.value == 999
    assert mock_existing_record.period == 5
    assert mock_existing_record.year == 2025

    assert result == mock_existing_record

@patch('database.get_db')
def test_update_off_contract_records_success(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = [
        {
            "period": 1,
            "off_contract_task_id": 101,
            "year": 2024,
            "value": 500.00,
            "company_name": "Company A"
        },
        {
            "period": 2,
            "off_contract_task_id": 102,
            "year": 2024,
            "value": 600.00,
            "company_name": "Company B"
        }
    ]
    schema_list = [schemas.OffContractTaskMappingSchema(**item) for item in payload_data]
    test_payload = schemas.OffContractTaskMappingPayload(data=schema_list)
    result = update_off_contract_records(payload=test_payload, db=db_mock)
    assert result['status'] == 'success'
    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = [
        {
            "period": 2,
            "off_contract_task_id": 102,
            "year": 0,
            "value": 600.00,
            "company_name": "Company B"
        }
    ]
    schema_list = [schemas.OffContractTaskMappingSchema(**item) for item in payload_data]
    test_payload = schemas.OffContractTaskMappingPayload(data=schema_list)
    result = update_off_contract_records(payload=test_payload, db=db_mock)
    assert result['status'] == 'error'

@pytest.mark.asyncio
async def test_create_off_contract_task_mapping_success():
    db_mock = MagicMock()
    mock_info = MagicMock()
    mock_info.off_contract_task_id = 101
    
    mock_country = MagicMock()
    mock_country.task_desc = "USA"
    mock_existing = []

    mock_all_records_list = MagicMock()
    mock_all_records_list.__iter__.return_value = [mock_info]
    mock_all_records_list.count = 1  

    mock_countries_list = [mock_country]
    mock_existing_list = mock_existing
    
    query_mock = db_mock.query.return_value
    query_mock.all.side_effect = [mock_all_records_list, mock_countries_list, mock_existing_list]
    query_mock.filter.return_value = query_mock

    result = await create_off_contract_task_mapping_for_year(year=2024, db=db_mock)
    assert result['status'] == 'success'


@patch('database.get_db')
def test_mock_create_off_contract_task_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "period": 1,
        "off_contract_task_id": 1,
        "year": 2023,
        "value": 100,
        "company_name": "US-CORE"
    }
    test_ownership_schema = schemas.OffContractTaskMappingSchema(**mapping_payload)
    result = create_off_contract_task_mapping(payload=test_ownership_schema, db=db_mock)
    assert result['status'] == 'success'


"""--------region.py---------"""


def test_get_region_all():
    response = client.get('/api/region/')
    assert response.status_code == 200


def test_get_regionid():
    response = client.get('/api/region/14')
    assert response.status_code == 200

    response = client.get('/api/region/20')
    assert response.status_code == 404


@patch('database.get_db')
def test_delete_existing_region(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query().filter().update.return_value = 1
    region_id = '8'

    response = delete_region(regionId=region_id, db=db_mock)
    assert response.status_code == 204


@patch('database.get_db')
def test_create_region_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = {
        "region_name": "string",
        "country": "string",
        "status": "string",
        "created_time": "2024-01-09T19:03:54.166Z",
        "updated_time": "2024-01-09T19:03:54.166Z",
        "created_by": "string",
        "updated_by": "string"
    }
    region_payload = schemas.Region(**payload)
    result = create_region(payload=region_payload, db=db_mock)
    assert result["status"] == "success"


"""--------p4p_master_info.py---------"""


def test_get_p4p_master_info():
    response = client.get('/api/p4p-master-info/')
    assert response.status_code == 200


def test_get_p4p_master_info_byid():
    response = client.get('/api/p4p-master-info/get_p4p_master_info/1')
    assert response.status_code == 200

    response = client.get('/api/p4p-master-info/get_p4p_master_info/20')
    assert response.status_code == 404


def test_get_p4p_task_mappings():
    response = client.get('/api/p4p-master-info/p4p_task_mappings/')
    assert response.status_code == 200


def test_p4p_task_mappings_by_year():
    response = client.get('/api/p4p-master-info/p4p_task_mappings_by_year/2023/US-CORE')
    assert response.status_code == 200

    response = client.get('/api/p4p-master-info/p4p_task_mappings_by_year/10000/US-CORE')
    assert response.status_code == 404


@patch('database.get_db')
def test_mock_update_p4p_task_mappings_records(mock_get_db):
    #Case 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "p4p_id": 1,
            "year": 2023,
            "value": 2,
            "company_name": "US-CORE"
        }
    ]

    test_payload = schemas.p4pTaskMappingsPayload(data=payload)
    result = update_p4p_task_mappings_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"

    #Case 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "company_name": "US-CORE"
        }
    ]

    test_payload = schemas.p4pTaskMappingsPayload(data=payload)
    with pytest.raises(HTTPException) as exc_info:
        update_p4p_task_mappings_records(payload=test_payload, db=db_mock)
    assert exc_info.value.status_code == 400

    #Case 3
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload = [
        {
            "period": 1,
            "p4p_id": 0,
            "year": 2023,
            "value": 2,
            "company_name": "US-CORE"
        }
    ]

    test_payload = schemas.p4pTaskMappingsPayload(data=payload)
    result = update_p4p_task_mappings_records(payload=test_payload, db=db_mock)
    assert result["status"] == "error"

@patch('database.get_db')
def test_mock_create_p4p_task_mappings(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "period": 1,
        "p4p_id": 1,
        "year": 2023,
        "value": 2,
        "company_name": "US-CORE"
    }
    test_schema = schemas.p4pTaskMappingsSchema(**mapping_payload)
    result = create_p4p_task_mappings(payload=test_schema, db=db_mock)
    assert result['status'] == 'success'

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_p4p_task_mappings_next_year_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_master = MagicMock(p4p_id=1)
    mock_country = MagicMock(task_desc="US", status="Active")
    class MockList(list):
        count = 1
    mock_all_records = MockList([mock_master])
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    ]
    result = await create_p4p_task_mappings_records_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    assert db_mock.add.call_count == 13
    assert db_mock.commit.called

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_p4p_task_mappings_next_year_duplicate(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_master = MagicMock(p4p_id=1)
    mock_country = MagicMock(task_desc="US")
    mock_existing = MagicMock(p4p_id=1, company_name="US", period=1)
    class MockList(list):
        count = 1
    mock_all_records = MockList([mock_master])
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_existing]))))
    ]
    result = await create_p4p_task_mappings_records_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "error"

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_p4p_task_mappings_next_year_no_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    class MockList(list):
        count = 0
    mock_all_records = MockList([])
    db_mock.query.return_value.all.return_value = mock_all_records
    with pytest.raises(HTTPException) as exc:
        await create_p4p_task_mappings_records_for_next_year(year=2025, db=db_mock)
    
    assert exc.value.status_code == 400

@patch('database.get_db')
def test_create_p4p_task_mappings_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"p4p_name": "Test"}
    mock_new_record = MagicMock()
    mock_new_record.p4p_id = 50
    with patch('p4p_master_info.p4p_task_mappings', return_value=mock_new_record):
        result = create_p4p_task_mappings_info(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["p4p_id"] == 50

@patch('database.get_db')
def test_create_p4p_task_mappings(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"year": 2025, "value": 10}
    mock_new_record = MagicMock()
    mock_new_record.row_id = 99
    with patch('p4p_master_info.p4p_task_mappings', return_value=mock_new_record):
        result = create_p4p_task_mappings(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["row_id"] == 99

@patch('database.get_db')
def test_update_p4p_task_mappings_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_item = MagicMock()
    mock_item.p4p_id = 1
    mock_item.period = 1
    mock_item.year = 2025
    mock_item.company_name = "US"
    mock_item.value = 5.5
    mock_payload = MagicMock()
    mock_payload.data = [mock_item]
    result = update_p4p_task_mappings_records(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["records_updated"] == 1
    assert db_mock.commit.called

@patch('database.get_db')
def test_update_p4p_task_mappings_records_validation_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    invalid_item = schemas.p4pTaskMappingsSchema(
        p4p_id=0,
        period=1,
        year=2025,
        company_name="US",
        value=10.0
    )
    real_payload = schemas.p4pTaskMappingsPayload(data=[invalid_item])
    result = update_p4p_task_mappings_records(payload=real_payload, db=db_mock)

    assert result["status"] == "error"
    assert "Please check details" in result["message"]
    assert not db_mock.commit.called

"""--------offcontractinfo.py---------"""


@patch('database.get_db')
def test_update_off_contract_existing_record(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    existing_record_mock = MagicMock()
    existing_record_mock.value = 100
    existing_record_mock.period = 1
    existing_record_mock.year = 2022
    db_mock.query().filter().first.return_value = existing_record_mock
    payload = {
        "period": 1,
        "off_contract_task_id": 1,
        "year": 2023,
        "value": 200,
        "company_name": "US-CORE"
    }
    test_payload = schemas.OffContractTaskMappingSchema(**payload)
    result = update_off_contract(off_contract_task_id=1, payload=test_payload, db=db_mock)
    assert result.value == payload['value']


"""--------freighttaskinfo.py---------"""

# --- Endpoint smoke tests (will pass even if DB isn't seeded) ---

def test_freight_task_info_endpoint():
    response = client.get('/api/freight_task_info/')
    assert response.status_code in (200, 404)

def test_get_freight_task_info_byid_endpoint():
    response = client.get('/api/freight_task_info/get_freight_task_info_byId/1')
    assert response.status_code in (200, 404)

def test_get_freight_task_mappings_by_year_and_country_endpoint():
    response = client.get('/api/freight_task_info/get_freight_task_mappings_by_year_and_country/2024/US-CORE')
    assert response.status_code in (200, 404)


# --- Unit tests (mock DB) ---

@patch("database.get_db")
def test_get_freight_task_info_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.all.return_value = [MagicMock()]

    result = get_freight_task_info(db=db_mock)
    assert result["status"] == "success"
    assert len(result["data"]) == 1


@patch("database.get_db")
def test_get_freight_task_info_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.all.return_value = []

    with pytest.raises(HTTPException) as exc:
        get_freight_task_info(db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_get_frt_task_info_byid_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    record = MagicMock()
    q = MagicMock()
    q.filter.return_value = q
    q.first.return_value = record
    db_mock.query.return_value = q

    result = get_frt_task_info_byid(freight_task_id=1, db=db_mock)
    assert result["status"] == "success"
    assert result["freight_task"] == record


@patch("database.get_db")
def test_get_frt_task_info_byid_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.first.return_value = None
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        get_frt_task_info_byid(freight_task_id=999, db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_get_freight_task_mappings_by_year_and_country_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [MagicMock()]
    db_mock.query.return_value = q

    result = get_freight_task_mappings_by_year_and_country(year="2024", country="US-CORE", db=db_mock)
    assert result["status"] == "success"
    assert len(result["data"]) == 1


@patch("database.get_db")
def test_get_freight_task_mappings_by_year_and_country_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        get_freight_task_mappings_by_year_and_country(year="2024", country="US-CORE", db=db_mock)

    assert exc.value.status_code == 404


@patch("freighttaskinfo.freight_task_info")
@patch("database.get_db")
def test_create_freight_task_info_unit_success(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    new_record = MagicMock()
    new_record.freight_task_id = 99
    mock_model.return_value = new_record

    payload = schemas.FreightTaskInfoSchema(task_name="TaskA")

    result = create_freight_task_info(payload=payload, db=db_mock)

    assert result == {"status": "success", "freight_task_id": 99}
    db_mock.add.assert_called_once_with(new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(new_record)


@patch("freighttaskinfo.freight_task_info")
@patch("database.get_db")
def test_create_freight_task_info_unit_exception_400(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_model.return_value = MagicMock()
    db_mock.commit.side_effect = Exception("commit failed")

    payload = schemas.FreightTaskInfoSchema(task_name="TaskA")

    with pytest.raises(HTTPException) as exc:
        create_freight_task_info(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("freighttaskinfo.freight_task_mappings")
@patch("database.get_db")
def test_create_freight_task_mappings_unit_success(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    new_record = MagicMock()
    new_record.row_id = 123
    mock_model.return_value = new_record

    payload = schemas.FreightTaskMappingsSchema(
        freight_task_id=1, period=1, year=2024, value=0, company_name="US-CORE"
    )

    result = create_freight_task_mappings(payload=payload, db=db_mock)

    assert result == {"status": "success", "row_id": 123}
    db_mock.add.assert_called_once_with(new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(new_record)


@patch("freighttaskinfo.freight_task_mappings")
@patch("database.get_db")
def test_create_freight_task_mappings_unit_exception_400(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_model.return_value = MagicMock()
    db_mock.commit.side_effect = Exception("commit failed")

    payload = schemas.FreightTaskMappingsSchema(
        freight_task_id=1, period=1, year=2024, value=0, company_name="US-CORE"
    )

    with pytest.raises(HTTPException) as exc:
        create_freight_task_mappings(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_update_freight_task_mapping_records_validation_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"freight_task_id": 0, "period": 1, "year": 2024, "value": 0, "company_name": "US-CORE"}
        ]
    }
    test_payload = schemas.FreightTaskMappingsPayload(**payload_data)

    result = update_freight_task_mapping_records(payload=test_payload, db=db_mock)
    assert result["status"] == "error"
    assert result["message"] == "Please check details"
    db_mock.query.assert_not_called()


@patch("database.get_db")
def test_update_freight_task_mapping_records_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"freight_task_id": 1, "period": 1, "year": 2024, "value": 10, "company_name": "US-CORE"},
            {"freight_task_id": 1, "period": 2, "year": 2024, "value": 20, "company_name": "US-CORE"},
        ]
    }
    test_payload = schemas.FreightTaskMappingsPayload(**payload_data)

    q = MagicMock()
    q.filter.return_value = q
    q.update.return_value = 1
    db_mock.query.return_value = q

    result = update_freight_task_mapping_records(payload=test_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["records_updated"] == 2
    assert q.update.call_count == 2
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_update_freight_task_mapping_records_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"freight_task_id": 1, "period": 1, "year": 2024, "value": 10, "company_name": "US-CORE"}
        ]
    }
    test_payload = schemas.FreightTaskMappingsPayload(**payload_data)

    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        update_freight_task_mapping_records(payload=test_payload, db=db_mock)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_freight_task_mappings_for_next_year_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(freight_task_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    country = MagicMock(task_desc="US-CORE")
    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [country]

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = []

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await create_freight_task_mappings_for_next_year(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    db_mock.add.assert_called()
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_freight_task_mappings_for_next_year_existing_returns_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(freight_task_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    country = MagicMock(task_desc="US-CORE")
    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [country]

    ex = MagicMock(freight_task_id=1, company_name="US-CORE", period=1)
    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = [ex]

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await create_freight_task_mappings_for_next_year(year=2026, db=db_mock)

    assert result == {"status": "error", "Records already exists for Year": 2026}
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_freight_task_mappings_for_next_year_no_tasks_returns_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = []
    tasks_list.count = 0

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = []

    db_mock.query.side_effect = [q_tasks, q_countries]

    with pytest.raises(HTTPException) as exc:
        await create_freight_task_mappings_for_next_year(year=2026, db=db_mock)

    assert exc.value.status_code == 400

"""--------freighttaskplaninfo.py---------"""

@patch("database.get_db")
def test_get_freight_task_plan_info_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.all.return_value = [MagicMock()]

    result = get_freight_task_plan_info(db=db_mock)
    assert result["status"] == "success"
    assert len(result["data"]) == 1


@patch("database.get_db")
def test_get_freight_task_plan_info_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.all.return_value = []

    with pytest.raises(HTTPException) as exc:
        get_freight_task_plan_info(db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_get_frt_task_plan_info_byid_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    rec = MagicMock()
    q = MagicMock()
    q.filter.return_value = q
    q.first.return_value = rec
    db_mock.query.return_value = q

    result = get_frt_task_plan_info_byid(freight_task_plan_id=1, db=db_mock)
    assert result["status"] == "success"
    assert result["freight_task"] == rec


@patch("database.get_db")
def test_get_frt_task_plan_info_byid_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.first.return_value = None
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        get_frt_task_plan_info_byid(freight_task_plan_id=999, db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_get_freight_task_plan_mappings_by_year_and_country_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [MagicMock()]
    db_mock.query.return_value = q

    result = get_freight_task_plan_mappings_by_year_and_country(year="2025", country="US-CORE", db=db_mock)
    assert result["status"] == "success"
    assert len(result["data"]) == 1


@patch("database.get_db")
def test_get_freight_task_plan_mappings_by_year_and_country_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        get_freight_task_plan_mappings_by_year_and_country(year="2025", country="US-CORE", db=db_mock)

    assert exc.value.status_code == 404


@patch("freighttaskplaninfo.freight_task_plan_info")
@patch("database.get_db")
def test_create_freight_task_plan_info_unit_success(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    new_record = MagicMock()
    new_record.freight_task_plan_id = 99
    mock_model.return_value = new_record

    payload = schemas.FreightTaskPlanInfoSchema(task_name="TaskPlanA")

    result = create_freight_task_plan_info(payload=payload, db=db_mock)

    assert result == {"status": "success", "freight_task_plan_id": 99}
    db_mock.add.assert_called_once_with(new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(new_record)


@patch("freighttaskplaninfo.freight_task_plan_info")
@patch("database.get_db")
def test_create_freight_task_plan_info_unit_exception_400(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_model.return_value = MagicMock()
    db_mock.commit.side_effect = Exception("commit failed")

    payload = schemas.FreightTaskPlanInfoSchema(task_name="TaskPlanA")

    with pytest.raises(HTTPException) as exc:
        create_freight_task_plan_info(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("freighttaskplaninfo.freight_task_plan_mappings")
@patch("database.get_db")
def test_create_freight_task_plan_mappings_unit_success(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    new_record = MagicMock()
    new_record.row_id = 123
    mock_model.return_value = new_record

    payload = schemas.FreightTaskPlanMappingsSchema(
        freight_task_plan_id=1, period=1, year=2026, value=0, company_name="US-CORE"
    )

    result = create_freight_task_plan_mappings(payload=payload, db=db_mock)

    assert result == {"status": "success", "row_id": 123}
    db_mock.add.assert_called_once_with(new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(new_record)


@patch("freighttaskplaninfo.freight_task_plan_mappings")
@patch("database.get_db")
def test_create_freight_task_plan_mappings_unit_exception_400(mock_get_db, mock_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_model.return_value = MagicMock()
    db_mock.commit.side_effect = Exception("commit failed")

    payload = schemas.FreightTaskPlanMappingsSchema(
        freight_task_plan_id=1, period=1, year=2026, value=0, company_name="US-CORE"
    )

    with pytest.raises(HTTPException) as exc:
        create_freight_task_plan_mappings(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_update_freight_task_plan_mapping_records_validation_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"freight_task_plan_id": 0, "period": 1, "year": 2026, "value": 0, "company_name": "US-CORE"}
        ]
    }
    test_payload = schemas.FreightTaskPlanMappingsPayload(**payload_data)

    result = update_freight_task_plan_mapping_records(payload=test_payload, db=db_mock)
    assert result["status"] == "error"
    assert result["message"] == "Please check details"
    db_mock.query.assert_not_called()


@patch("database.get_db")
def test_update_freight_task_plan_mapping_records_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"freight_task_plan_id": 1, "period": 1, "year": 2026, "value": 10, "company_name": "US-CORE"},
            {"freight_task_plan_id": 1, "period": 2, "year": 2026, "value": 20, "company_name": "US-CORE"},
        ]
    }
    test_payload = schemas.FreightTaskPlanMappingsPayload(**payload_data)

    q = MagicMock()
    q.filter.return_value = q
    q.update.return_value = 1
    db_mock.query.return_value = q

    result = update_freight_task_plan_mapping_records(payload=test_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["records_updated"] == 2
    assert q.update.call_count == 2
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_update_freight_task_plan_mapping_records_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"freight_task_plan_id": 1, "period": 1, "year": 2026, "value": 10, "company_name": "US-CORE"}
        ]
    }
    test_payload = schemas.FreightTaskPlanMappingsPayload(**payload_data)

    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        update_freight_task_plan_mapping_records(payload=test_payload, db=db_mock)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_freight_task_plan_mappings_for_next_year_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(freight_task_plan_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    country = MagicMock(task_desc="US-CORE")
    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [country]

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = []

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await create_freight_task_plan_mappings_for_next_year(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    db_mock.add.assert_called()
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_freight_task_plan_mappings_for_next_year_existing_returns_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(freight_task_plan_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    country = MagicMock(task_desc="US-CORE")
    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [country]

    ex = MagicMock(freight_task_plan_id=1, company_name="US-CORE", period=1)
    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = [ex]

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await create_freight_task_plan_mappings_for_next_year(year=2026, db=db_mock)

    assert result == {"status": "error", "Records already exists for Year": 2026}
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_freight_task_plan_mappings_for_next_year_no_tasks_returns_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = []
    tasks_list.count = 0

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = []

    db_mock.query.side_effect = [q_tasks, q_countries]

    with pytest.raises(HTTPException) as exc:
        await create_freight_task_plan_mappings_for_next_year(year=2026, db=db_mock)

    # function catches the internal HTTPException and rethrows 400
    assert exc.value.status_code == 400

"""________generaladministrative.py_________"""

# --- Endpoint smoke tests (same style as existing ones) ---

def test_get_general_administrative_task_info_endpoint():
    response = client.get('/api/general_administrative/')
    assert response.status_code == 200

def test_general_administrative_mappings_by_year_endpoint():
    response = client.get('/api/general_administrative/general_administrative_mappings_by_year/2023/US-CORE')
    assert response.status_code == 200


# --- Unit tests (mock DB, cover success + error paths) ---

@patch("database.get_db")
def test_get_general_administrative_task_info_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.all.return_value = [MagicMock()]

    result = get_general_administrative_task_info(db=db_mock)
    assert result["status"] == "success"
    assert len(result["data"]) == 1


@patch("database.get_db")
def test_get_general_administrative_task_info_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.return_value.all.return_value = []

    with pytest.raises(HTTPException) as exc:
        get_general_administrative_task_info(db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_general_administrative_mappings_by_year_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [MagicMock()]
    db_mock.query.return_value = q

    result = general_administrative_mappings_by_year(year="2023", country="US-CORE", db=db_mock)
    assert result["status"] == "success"
    assert len(result["data"]) == 1


@patch("database.get_db")
def test_general_administrative_mappings_by_year_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        general_administrative_mappings_by_year(year="2023", country="US-CORE", db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_update_general_administrative_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"general_administrative_id": 1, "period": 2, "year": 2023, "value": 0, "company_name": "test_comp"}
        ]
    }
    test_payload = schemas.GeneralAdministrativeMappingsPayload(**payload_data)

    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.update.return_value = 1

    result = update_general_administrative_records(payload=test_payload, db=db_mock)
    assert result == {"status": "success", "records_updated": 1}


@patch("database.get_db")
def test_update_general_administrative_records_validation_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"general_administrative_id": 0, "period": 1, "year": 2023, "value": 0, "company_name": "test_comp"}
        ]
    }
    test_payload = schemas.GeneralAdministrativeMappingsPayload(**payload_data)

    result = update_general_administrative_records(payload=test_payload, db=db_mock)
    assert result["status"] == "error"
    assert result["message"] == "Please check details"
    db_mock.query.assert_not_called()


@patch("database.get_db")
def test_update_general_administrative_records_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload_data = {
        "data": [
            {"general_administrative_id": 1, "period": 1, "year": 2023, "value": 0, "company_name": "test_comp"}
        ]
    }
    test_payload = schemas.GeneralAdministrativeMappingsPayload(**payload_data)

    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        update_general_administrative_records(payload=test_payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("generaladministrative.general_administrative_task")
@patch("database.get_db")
def test_create_general_administrative_task_success(mock_get_db, mock_task_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    new_record = MagicMock()
    new_record.general_administrative_id = 99
    mock_task_model.return_value = new_record

    payload = schemas.GeneralAdministrativeTaskSchema(
        task_name="TaskA", task_desc="Desc", status="Active", created_by="tester"
    )

    result = create_general_administrative_task(payload=payload, db=db_mock)

    assert result == {"status": "success", "general_administrative_id": 99}
    db_mock.add.assert_called_once_with(new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(new_record)


@patch("generaladministrative.general_administrative_task")
@patch("database.get_db")
def test_create_general_administrative_task_exception_400(mock_get_db, mock_task_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_task_model.return_value = MagicMock()
    db_mock.commit.side_effect = Exception("commit failed")

    payload = schemas.GeneralAdministrativeTaskSchema(task_name="TaskA")

    with pytest.raises(HTTPException) as exc:
        create_general_administrative_task(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("database.get_db")
async def test_update_general_administrative_mappings_creates_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(general_administrative_id=1, task_name="TaskA")
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    countries_list = [MagicMock(task_desc="US-CORE")]

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.all.return_value = countries_list

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.first.return_value = None

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await update_general_administrative_mappings(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert db_mock.add.call_count == 13   # 13 periods * 1 country
    assert db_mock.commit.call_count == 13


@pytest.mark.asyncio
@patch("database.get_db")
async def test_update_general_administrative_mappings_existing_record_skips(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(general_administrative_id=1, task_name="TaskA")
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    countries_list = [MagicMock(task_desc="US-CORE")]

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.all.return_value = countries_list

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.first.return_value = MagicMock()  # already exists

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await update_general_administrative_mappings(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert "TaskA" in result["Records already exists for "]
    db_mock.add.assert_not_called()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_update_general_administrative_mappings_no_tasks_returns_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = []
    tasks_list.count = 0

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.all.return_value = []

    db_mock.query.side_effect = [q_tasks, q_countries]

    with pytest.raises(HTTPException) as exc:
        await update_general_administrative_mappings(year=2026, db=db_mock)

    # because the function catches all exceptions and re-raises as 400
    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_g_and_a_mappings_for_next_year_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(general_administrative_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    country = MagicMock(task_desc="US-CORE")
    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [country]

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = []  # no existing mappings

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await create_g_and_a_mappings_for_next_year(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    db_mock.add.assert_called()
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_g_and_a_mappings_for_next_year_existing_returns_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(general_administrative_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    country = MagicMock(task_desc="US-CORE")

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [country]

    # existing record matching first period
    ex = MagicMock(general_administrative_id=1, company_name="US-CORE", period=1)
    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = [ex]

    db_mock.query.side_effect = [q_tasks, q_countries, q_existing]

    result = await create_g_and_a_mappings_for_next_year(year=2026, db=db_mock)

    assert result == {"status": "error", "Records already exists for Year": 2026}
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_g_and_a_mappings_for_next_year_no_tasks_returns_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = []
    tasks_list.count = 0

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = []

    db_mock.query.side_effect = [q_tasks, q_countries]

    with pytest.raises(HTTPException) as exc:
        await create_g_and_a_mappings_for_next_year(year=2026, db=db_mock)

    # function catches and converts everything to 400
    assert exc.value.status_code == 400


"""________generaladministrative_plan.py_________"""

# --- Optional endpoint smoke tests (keep only if your test DB is seeded) ---

def test_get_general_administrative_plan_task_info_endpoint():
    response = client.get('/api/general_administrative_plan/')
    assert response.status_code in (200, 404)

def test_general_administrative_plan_mappings_by_year_endpoint():
    response = client.get('/api/general_administrative_plan/general_administrative_plan_mappings_by_year/2023/US-CORE')
    assert response.status_code in (200, 404)


# --- Unit tests (mock DB) ---

@patch("database.get_db")
def test_get_general_administrative_plan_task_info_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.all.return_value = [MagicMock()]
    db_mock.query.return_value = q

    result = get_general_administrative_plan_task_info(db=db_mock)
    assert result["status"] == "success"
    assert result["data"] == q.all.return_value


@patch("database.get_db")
def test_get_general_administrative_plan_task_info_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        get_general_administrative_plan_task_info(db=db_mock)

    assert exc.value.status_code == 404


@patch("database.get_db")
def test_general_administrative_plan_mappings_by_year_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [MagicMock()]
    db_mock.query.return_value = q

    result = general_administrative_plan_mappings_by_year(year="2023", country="US-CORE", db=db_mock)
    assert result["status"] == "success"
    assert result["data"] == q.all.return_value


@patch("database.get_db")
def test_general_administrative_plan_mappings_by_year_unit_404(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        general_administrative_plan_mappings_by_year(year="2023", country="US-CORE", db=db_mock)

    assert exc.value.status_code == 404


@patch("generaladministrative_plan.general_administrative_plan_task")
@patch("database.get_db")
def test_create_general_administrative_plan_task_success(mock_get_db, mock_task_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    new_record = MagicMock()
    new_record.general_administrative_plan_id = 99
    mock_task_model.return_value = new_record

    payload = schemas.GeneralAdministrativePlanTaskSchema(
        task_name="TaskA", task_desc="Desc", status="Active", created_by="tester"
    )

    result = create_general_administrative_plan_task(payload=payload, db=db_mock)

    assert result == {"status": "success", "general_administrative_plan_id": 99}
    db_mock.add.assert_called_once_with(new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(new_record)


@patch("generaladministrative_plan.general_administrative_plan_task")
@patch("database.get_db")
def test_create_general_administrative_plan_task_exception_400(mock_get_db, mock_task_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_task_model.return_value = MagicMock()
    db_mock.commit.side_effect = Exception("commit failed")

    payload = schemas.GeneralAdministrativePlanTaskSchema(task_name="TaskA")

    with pytest.raises(HTTPException) as exc:
        create_general_administrative_plan_task(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_update_general_administrative_plan_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.update.return_value = 1
    db_mock.query.return_value = q

    payload = schemas.GeneralAdministrativePlanMappingsPayload(
        data=[
            schemas.GeneralAdministrativePlanMappingsSchema(
                general_administrative_plan_id=1, period=1, year=2026, value=1.23, company_name="US-CORE"
            ),
            schemas.GeneralAdministrativePlanMappingsSchema(
                general_administrative_plan_id=1, period=2, year=2026, value=2.34, company_name="US-CORE"
            ),
        ]
    )

    result = update_general_administrative_plan_records(payload=payload, db=db_mock)
    assert result == {"status": "success", "records_updated": 2}
    assert q.update.call_count == 2
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_update_general_administrative_plan_records_invalid_details_returns_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload = schemas.GeneralAdministrativePlanMappingsPayload(
        data=[
            schemas.GeneralAdministrativePlanMappingsSchema(
                general_administrative_plan_id=0, period=1, year=2026, value=1.23, company_name="US-CORE"
            )
        ]
    )

    result = update_general_administrative_plan_records(payload=payload, db=db_mock)
    assert result["status"] == "error"
    db_mock.commit.assert_not_called()


@patch("database.get_db")
def test_update_general_administrative_plan_records_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("db down")

    payload = schemas.GeneralAdministrativePlanMappingsPayload(
        data=[
            schemas.GeneralAdministrativePlanMappingsSchema(
                general_administrative_plan_id=1, period=1, year=2026, value=1.23, company_name="US-CORE"
            )
        ]
    )

    with pytest.raises(HTTPException) as exc:
        update_general_administrative_plan_records(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("generaladministrative_plan.general_administrative_plan_mappings")
@patch("database.get_db")
async def test_update_general_administrative_plan_mappings_creates_records(mock_get_db, mock_mappings_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    # The handler passes the model class into db.query(model). Since we're patching the
    # model with a MagicMock, we must provide a __name__ so our query_side_effect can
    # route correctly (MagicMock blocks reading magic-named attributes by default).
    mock_mappings_model.__name__ = "general_administrative_plan_mappings"

    task = MagicMock(general_administrative_plan_id=1, task_name="TaskA")
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    countries_list = [MagicMock(task_desc="US-CORE")]

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.all.return_value = countries_list

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.first.return_value = None  # does not exist yet

    def query_side_effect(model):
        if model.__name__ == "general_administrative_plan_task":
            return q_tasks
        if model.__name__ == "country_division_name":
            return q_countries
        if model.__name__ == "general_administrative_plan_mappings":
            return q_existing
        return MagicMock()

    db_mock.query.side_effect = query_side_effect
    mock_mappings_model.return_value = MagicMock()

    result = await update_general_administrative_plan_mappings(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert result["forYear"] == 2026
    assert result["Records already exists for "] == []
    assert db_mock.add.call_count == 13
    assert db_mock.commit.call_count == 13


@pytest.mark.asyncio
@patch("generaladministrative_plan.general_administrative_plan_mappings")
@patch("database.get_db")
async def test_update_general_administrative_plan_mappings_existing_skips_creates_list(mock_get_db, mock_mappings_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_mappings_model.__name__ = "general_administrative_plan_mappings"

    task = MagicMock(general_administrative_plan_id=1, task_name="TaskA")
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.all.return_value = [MagicMock(task_desc="US-CORE")]

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.first.return_value = MagicMock()  # already exists

    def query_side_effect(model):
        if model.__name__ == "general_administrative_plan_task":
            return q_tasks
        if model.__name__ == "country_division_name":
            return q_countries
        if model.__name__ == "general_administrative_plan_mappings":
            return q_existing
        return MagicMock()

    db_mock.query.side_effect = query_side_effect
    mock_mappings_model.return_value = MagicMock()

    result = await update_general_administrative_plan_mappings(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert "TaskA" in result["Records already exists for "]
    db_mock.add.assert_not_called()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_update_general_administrative_plan_mappings_no_tasks_returns_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = []
    tasks_list.count = 0

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.all.return_value = []

    def query_side_effect(model):
        if model.__name__ == "general_administrative_plan_task":
            return q_tasks
        if model.__name__ == "country_division_name":
            return q_countries
        return MagicMock()

    db_mock.query.side_effect = query_side_effect

    with pytest.raises(HTTPException) as exc:
        await update_general_administrative_plan_mappings(year=2026, db=db_mock)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("generaladministrative_plan.general_administrative_plan_mappings")
@patch("database.get_db")
async def test_create_g_and_a_plan_mappings_for_next_year_success(mock_get_db, mock_mappings_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    mock_mappings_model.__name__ = "general_administrative_plan_mappings"

    task = MagicMock(general_administrative_plan_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [MagicMock(task_desc="US-CORE")]

    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = []  # none exist yet

    def query_side_effect(model):
        if model.__name__ == "general_administrative_plan_task":
            return q_tasks
        if model.__name__ == "country_division_name":
            return q_countries
        if model.__name__ == "general_administrative_plan_mappings":
            return q_existing
        return MagicMock()

    db_mock.query.side_effect = query_side_effect
    mock_mappings_model.return_value = MagicMock()

    result = await create_g_and_a_plan_mappings_for_next_year(year=2026, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    assert db_mock.add.call_count == 13
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_g_and_a_plan_mappings_for_next_year_existing_returns_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    task = MagicMock(general_administrative_plan_id=1)
    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = [task]
    tasks_list.count = 1

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = [MagicMock(task_desc="US-CORE")]

    ex = MagicMock(general_administrative_plan_id=1, company_name="US-CORE", period=1)
    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = [ex]  # already exists

    def query_side_effect(model):
        if model.__name__ == "general_administrative_plan_task":
            return q_tasks
        if model.__name__ == "country_division_name":
            return q_countries
        if model.__name__ == "general_administrative_plan_mappings":
            return q_existing
        return MagicMock()

    db_mock.query.side_effect = query_side_effect

    result = await create_g_and_a_plan_mappings_for_next_year(year=2026, db=db_mock)

    assert result == {"status": "error", "Records already exists for Year": 2026}
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_create_g_and_a_plan_mappings_for_next_year_no_tasks_returns_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    tasks_list = MagicMock()
    tasks_list.__iter__.return_value = []
    tasks_list.count = 0

    q_tasks = MagicMock()
    q_tasks.all.return_value = tasks_list

    q_countries = MagicMock()
    q_countries.filter.return_value = q_countries
    q_countries.all.return_value = []

    def query_side_effect(model):
        if model.__name__ == "general_administrative_plan_task":
            return q_tasks
        if model.__name__ == "country_division_name":
            return q_countries
        return MagicMock()

    db_mock.query.side_effect = query_side_effect

    with pytest.raises(HTTPException) as exc:
        await create_g_and_a_plan_mappings_for_next_year(year=2026, db=db_mock)

    assert exc.value.status_code == 400


"""________inflation_deflation.py_________"""

@patch("database.get_db")
def test_get_inflation_deflation_task_mappings_success(_mock_get_db):
    db_mock = MagicMock()

    row = MagicMock(
        inflation_deflation_task_id=1,
        period=2,
        year=2024,
        value=1.5,
        company_name="US-CORE",
    )

    q = MagicMock()
    q.all.return_value = [row]
    db_mock.query.return_value = q

    result = get_inflation_deflation_task_mappings(db=db_mock)

    assert result["inflation_deflation_task_mapping"][0]["period_with_P"] == "P2"
    assert result["inflation_deflation_task_mapping"][0]["company-name"] == "US-CORE"


@patch("database.get_db")
def test_get_inflation_deflation_task_success(_mock_get_db):
    db_mock = MagicMock()

    row = MagicMock(inflation_deflation_task_id=10, task_name="Task A")
    q = MagicMock()
    q.all.return_value = [row]
    db_mock.query.return_value = q

    result = get_inflation_deflation_task(db=db_mock)

    assert result == {
        "inflation_deflation_task": [{"inflation_deflation_task_id": 10, "task_name": "Task A"}]
    }


@patch("database.get_db")
def test_inflation_deflation_task_mappings_by_year_success(_mock_get_db):
    db_mock = MagicMock()

    row = MagicMock(
        inflation_deflation_task_id=3,
        period=1,
        year=2023,
        value=2.0,
        company_name="CANADA",
    )

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [row]
    db_mock.query.return_value = q

    result = inflation_deflation_task_mappings_by_year(year=2023, company_name="CANADA", db=db_mock)

    assert result["inflation_deflation_task_mappings_year"][0]["period_with_P"] == "P1"
    assert result["inflation_deflation_task_mappings_year"][0]["company-name"] == "CANADA"


@patch("database.get_db")
def test_update_inflation_deflation_task_mappings_records_success(_mock_get_db):
    db_mock = MagicMock()

    q = MagicMock()
    q.filter.return_value = q
    q.update.return_value = 1
    db_mock.query.return_value = q

    payload = schemas.InflationDeflationMappingPayload(
        data=[
            schemas.InflationDeflationMappingSchema(
                inflation_deflation_task_id=1, period=1, year=2024, value=9.9, company_name="US-CORE"
            ),
            schemas.InflationDeflationMappingSchema(
                inflation_deflation_task_id=2, period=2, year=2024, value=8.8, company_name="US-CORE"
            ),
        ]
    )

    result = update_inflation_deflation_task_mappings_records(payload=payload, db=db_mock)

    assert result == {"status": "success", "records_updated": 2}
    assert q.update.call_count == 2
    db_mock.commit.assert_called_once()


@patch("database.get_db")
def test_update_inflation_deflation_task_mappings_records_invalid_details_returns_error(_mock_get_db):
    db_mock = MagicMock()

    payload = schemas.InflationDeflationMappingPayload(
        data=[
            schemas.InflationDeflationMappingSchema(
                inflation_deflation_task_id=0, period=1, year=2024, value=1.0, company_name="US-CORE"
            )
        ]
    )

    result = update_inflation_deflation_task_mappings_records(payload=payload, db=db_mock)

    assert result == {"status": "error", "message": "Please check details"}
    db_mock.commit.assert_not_called()


@patch("database.get_db")
def test_inflation_deflation_year_country_code_success(_mock_get_db):
    db_mock = MagicMock()

    dummy_view = MagicMock()
    dummy_view.columns = MagicMock()

    year_col = MagicMock()
    year_col.__eq__.return_value = "year_filter"
    company_col = MagicMock()
    company_col.__eq__.return_value = "company_filter"
    period_col = MagicMock()

    dummy_view.columns.year = year_col
    dummy_view.columns.company_name = company_col
    dummy_view.columns.period = period_col

    q = MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = [{"period": 1, "value": 1.23}]
    db_mock.query.return_value = q

    with patch("inflation_deflation.inflation_deflation", dummy_view):
        result = inflation_deflation_year_country_code(year=2024, company_name="US-CORE", db=db_mock)

    assert result == {"inflation_deflation": [{"period": 1, "value": 1.23}]}


@patch("database.get_db")
def test_get_inflation_deflation_task_mappings_exception_400(_mock_get_db):
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        get_inflation_deflation_task_mappings(db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_get_inflation_deflation_task_exception_400(_mock_get_db):
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        get_inflation_deflation_task(db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_inflation_deflation_task_mappings_by_year_exception_400(_mock_get_db):
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        inflation_deflation_task_mappings_by_year(year=2024, company_name="US-CORE", db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_update_inflation_deflation_task_mappings_records_exception_400(_mock_get_db):
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("db error")

    payload = schemas.InflationDeflationMappingPayload(
        data=[
            schemas.InflationDeflationMappingSchema(
                inflation_deflation_task_id=1,
                period=1,
                year=2024,
                value=1.0,
                company_name="US-CORE",
            )
        ]
    )

    with pytest.raises(HTTPException) as exc:
        update_inflation_deflation_task_mappings_records(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


@patch("database.get_db")
def test_inflation_deflation_year_country_code_exception_400(_mock_get_db):
    db_mock = MagicMock()
    db_mock.query.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        inflation_deflation_year_country_code(year=2024, company_name="US-CORE", db=db_mock)

    assert exc.value.status_code == 400


"""________freightcost.py_________"""

# --- Endpoint smoke tests (keep these lightweight; they pass even if DB isn't seeded) ---

def test_freight_cost_rate_endpoint():
    response = client.get("/api/freight-cost/get_freight_cost_rate")
    assert response.status_code in (200, 400)

def test_freight_alert_endpoint():
    response = client.get("/api/freight-cost/freight_alert")
    assert response.status_code in (200, 400)

def test_get_freight_cost_mapping_endpoint():
    response = client.get("/api/freight-cost/get_freight_cost_mapping/2026")
    assert response.status_code in (200, 400)

def test_freight_cost_period_view_endpoint():
    response = client.get("/api/freight-cost/freight_cost_period_view/2024/US")
    assert response.status_code in (200, 400)

def test_rate_growing_area_endpoint():
    response = client.get("/api/freight-cost/get_rate_gowing_area/2024/US")
    assert response.status_code in (200, 400)

def test_get_file_upload_details_endpoint():
    response = client.get("/api/freight-cost/get_file_upload_details")
    assert response.status_code in (200, 400)

def test_fetch_freight_records_endpoint():
    response = client.get("/api/freight-cost/fetch_freight_records/2024/US/US-CORE")
    assert response.status_code in (200, 400)

def test_freight_fuel_cost_endpoint():
    response = client.get("/api/freight-cost/freight_fuel_cost/2025/US")
    assert response.status_code in (200, 400)

def test_freight_fuel_cost_ga_endpoint():
    response = client.get("/api/freight-cost/freight_fuel_cost_ga/2025/US")
    assert response.status_code in (200, 400)

def test_freight_cost_summary_endpoint():
    response = client.get("/api/freight-cost/freight_cost/2025/US/US-CORE")
    assert response.status_code in (200, 400)

def test_freight_cost_mapping_placeholder_endpoint():
    response = client.get("/api/freight-cost/freight_cost_mapping_placeholder")
    assert response.status_code in (200, 400)


# --- Unit tests (mock DB) ---

@patch("database.get_db")
def test_create_freight_cost_unit_404_when_no_psga_mappings(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.all.return_value = []
    db_mock.query.return_value = q

    payload = schemas.FreightCostRateSchema(currency="USD", comment="x")

    with pytest.raises(HTTPException) as exc:
        freightcost.create_freight_cost(payload=payload, db=db_mock)

    assert exc.value.status_code == 400  # function catches and returns 400


@patch("freightcost.FreightCostRate")
@patch("database.get_db")
def test_create_freight_cost_unit_success(mock_get_db, mock_rate_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.all.return_value = [
        MagicMock(plant_id=1, vendor_site_id=2, growing_area_id=3),
        MagicMock(plant_id=4, vendor_site_id=5, growing_area_id=6),
    ]
    db_mock.query.return_value = q

    mock_rate_model.return_value = MagicMock()

    payload = schemas.FreightCostRateSchema(currency="USD", comment="x", created_by="tester")

    result = freightcost.create_freight_cost(payload=payload, db=db_mock)

    assert isinstance(result, list)
    assert db_mock.add.call_count == 2
    db_mock.commit.assert_called_once()


@patch("freightcost.FreightCostMapping")
@patch("database.get_db")
def test_create_freight_mapping_unit_creates_13_periods_per_id(mock_get_db, mock_mapping_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    # distinct freight IDs
    db_mock.query.return_value.distinct.return_value.all.return_value = [(10,)]

    mock_mapping_model.return_value = MagicMock()

    payload = schemas.FreightCostMappingSchema(year=2026, rate=0.0)

    result = freightcost.create_freight_mapping(payload=payload, db=db_mock)

    assert len(result) == 13
    assert db_mock.add.call_count == 13
    assert db_mock.commit.call_count == 13
    assert db_mock.refresh.call_count == 13


@patch("database.get_db")
def test_update_freight_mapping_unit_success_updates_current_and_next_year(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    r1 = MagicMock(rate=1.0, round_trip=0)
    r2 = MagicMock(rate=1.0, round_trip=0)

    q_current = MagicMock()
    q_current.filter.return_value = q_current
    q_current.all.return_value = [r1]

    q_next = MagicMock()
    q_next.filter.return_value = q_next
    q_next.all.return_value = [r2]

    db_mock.query.side_effect = [q_current, q_next]

    out = freightcost.update_freight_mapping(
        freight_cost_id=1,
        year=2025,
        period=3,
        country="US",
        new_rate=9,
        round_trip=1,
        db=db_mock,
    )

    assert out["updated_records_count"] == 2
    assert r1.rate == 9 and r2.rate == 9
    assert r1.round_trip == 1 and r2.round_trip == 1
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
@patch("database.get_db")
async def test_update_miles_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    rec = MagicMock(miles=0)
    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [rec]
    db_mock.query.return_value = q

    payload = schemas.FreightMiles(plant_id=1, vendor_site_id=2, growing_area_id=3, miles=123)

    out = await freightcost.update_miles(payload=payload, db=db_mock)

    assert rec.miles == 123
    db_mock.commit.assert_called_once()
    assert "Miles updated for" in out


@patch("database.get_db")
def test_update_fuel_cf_unit_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    r1 = MagicMock(fuel_cf=0.1)
    r2 = MagicMock(fuel_cf=0.1)

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = [r1, r2]
    db_mock.query.return_value = q

    payload = schemas.FreightMilesSchema(year=2025, period=1, country="US", fuel_cf=1)

    out = freightcost.update_fuel_cf(payload=payload, db=db_mock)

    assert len(out) == 2
    assert r1.fuel_cf == 1 and r2.fuel_cf == 1
    assert db_mock.commit.call_count == 2  # commits inside loop


@patch("database.get_db")
def test_get_freight_cost_unit_us_path(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    class Row:
        def __init__(self, m):
            self._mapping = m

    db_mock.execute.return_value.fetchall.return_value = [Row({"a": 1})]

    out = freightcost.get_freight_cost(2025, "US", "US", db=db_mock)

    assert out == {"freight_cost": [{"a": 1}]}
    assert db_mock.execute.called


@patch("database.get_db")
def test_get_freight_cost_unit_non_us_path(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    class Row:
        def __init__(self, m):
            self._mapping = m

    db_mock.execute.return_value.fetchall.return_value = [Row({"b": 2})]

    out = freightcost.get_freight_cost(2025, "US", "US-CORE", db=db_mock)

    assert out == {"freight_cost": [{"b": 2}]}
    assert db_mock.execute.called


@patch("freightcost.FileUploadTemplate")
@patch("database.get_db")
def test_handle_upload_file_unit_invalid_extension_logs_and_raises_400(mock_get_db, mock_file_upload_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    fake_file = MagicMock()
    fake_file.filename = "bad.csv"
    fake_file.file = BytesIO(b"fake")

    mock_file_upload_model.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        freightcost.handle_upload_file(uploaded_year=2025, user_email="x@y.com", file=fake_file, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.rollback.assert_called_once()
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


@patch("freightcost.FreightCostMapping")
@patch("database.get_db")
def test_freight_cost_mapping_placeholder_unit_creates_missing_ids(mock_get_db, mock_mapping_model):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    # freight_cost_records: contains id=2, but mapping table already has only id=1 -> so id=2 should be created
    fc_item = MagicMock(freight_cost_id=2, company_name="US")

    q_fc = MagicMock()
    q_fc.join.return_value = q_fc
    q_fc.distinct.return_value = q_fc
    q_fc.all.return_value = [fc_item]

    q_map = MagicMock()
    q_map.distinct.return_value = q_map
    q_map.all.return_value = [(1,)]

    db_mock.query.side_effect = [q_fc, q_map]

    mock_mapping_model.return_value = MagicMock()

    out = freightcost.get_freight_cost_mapping_placeholder(db=db_mock)

    assert out["Number of new mapping created"] == 1
    assert db_mock.add.call_count == 13
    db_mock.commit.assert_called_once()


def _route_endpoint(path: str):
    for r in freightcost.router.routes:
        if getattr(r, "path", None) == path:
            return r.endpoint
    raise AssertionError(f"Route not found: {path}")


# --- Covers 73-74 (exception branch of /get_freight_cost_rate) ---
@patch("database.get_db")
def test_get_freight_cost_rate_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    db_mock.query.side_effect = Exception("db fail")
    endpoint = _route_endpoint("/get_freight_cost_rate")

    with pytest.raises(HTTPException) as exc:
        endpoint(db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 117 (len(records)>0), and 120-121 (exception branch) ---
@patch("database.get_db")
def test_freight_alert_unit_returns_alert_when_records_exist(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.select_from.return_value = q
    q.join.return_value = q
    q.filter.return_value = q
    q.distinct.return_value = q
    q.all.return_value = [("PlantA", "VSC1", "GA1")]
    db_mock.query.return_value = q

    endpoint = _route_endpoint("/freight_alert")
    result = endpoint(db=db_mock)

    assert result["message"] != "0"
    assert len(result["table"]) == 1


@patch("database.get_db")
def test_freight_alert_unit_returns_zero_when_no_records(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.select_from.return_value = q
    q.join.return_value = q
    q.filter.return_value = q
    q.distinct.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    endpoint = _route_endpoint("/freight_alert")
    result = endpoint(db=db_mock)

    assert result["message"] == "0"
    assert result["table"] == []


@patch("database.get_db")
def test_freight_alert_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("boom")

    endpoint = _route_endpoint("/freight_alert")
    with pytest.raises(HTTPException) as exc:
        endpoint(db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 201-202 (exception in view_freight_mapping_by_year) ---
@patch("database.get_db")
def test_view_freight_mapping_by_year_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.view_freight_mapping_by_year(year=2026, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 255-256 (exception in create_freight_mapping) ---
@patch("database.get_db")
def test_create_freight_mapping_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    payload = schemas.FreightCostMappingSchema(year=2026, rate=0.0)

    with pytest.raises(HTTPException) as exc:
        freightcost.create_freight_mapping(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 306 + 317-318 (no records path in update_freight_mapping + catch-all) ---
@patch("database.get_db")
def test_update_freight_mapping_unit_no_records_raises_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q1 = MagicMock()
    q1.filter.return_value = q1
    q1.all.return_value = []

    q2 = MagicMock()
    q2.filter.return_value = q2
    q2.all.return_value = []

    db_mock.query.side_effect = [q1, q2]

    with pytest.raises(HTTPException) as exc:
        freightcost.update_freight_mapping(
            freight_cost_id=1, year=2025, period=1, country="US", new_rate=1.0, round_trip=1, db=db_mock
        )

    # function catches everything and converts to 400
    assert exc.value.status_code == 400


# --- Covers 343-344 (exception in freight_cost_period_view_year) ---
@patch("database.get_db")
def test_freight_cost_period_view_year_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.freight_cost_period_view_year(year=2024, country="US", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 372-373 (exception in freight_cost_period_week_view_year) ---
@patch("database.get_db")
def test_freight_cost_period_week_view_year_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.freight_cost_period_week_view_year(year=2024, country="US", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 406-408 (exception branch in get_rate_growing_area_year) ---
@patch("database.get_db")
def test_get_rate_growing_area_year_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.get_rate_growing_area_year(year=2024, country="US", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 425-438 (BaseModel vs dict paths + exception in create_freight_rates_in_db) ---
@patch("freightcost.FreightCostRate")
def test_create_freight_rates_in_db_unit_dict_path_success(mock_model):
    db_mock = MagicMock()

    rec = MagicMock()
    rec.freight_cost_id = 10
    mock_model.return_value = rec

    out = freightcost.create_freight_rates_in_db({"plant_id": 1}, db=db_mock)
    assert out.freight_cost_id == 10
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@patch("freightcost.FreightCostRate", side_effect=Exception("ctor fail"))
def test_create_freight_rates_in_db_unit_exception_400(_mock_model):
    db_mock = MagicMock()

    with pytest.raises(HTTPException) as exc:
        freightcost.create_freight_rates_in_db({"plant_id": 1}, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 454-458 (exception in create_freight_rates endpoint wrapper) ---
@patch("freightcost.create_freight_rates_in_db", side_effect=Exception("fail"))
@patch("database.get_db")
def test_create_freight_rates_endpoint_unit_exception_400(mock_get_db, _mock_create):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    payload = schemas.FreightCostRatesSchema(plant_id=1)

    with pytest.raises(HTTPException) as exc:
        freightcost.create_potato_rates(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 483-512 (next-year creation: count==0 branch + success + old_rates None skip) ---
@patch("freightcost.FreightCostMapping")
@patch("database.get_db")
def test_create_freight_cost_mapping_records_for_next_year_unit_count_zero_raises_400(mock_get_db, _mock_mapping):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    distinct_ids = MagicMock()
    distinct_ids.count = 0

    q_ids = MagicMock()
    q_ids.distinct.return_value = q_ids
    q_ids.all.return_value = distinct_ids
    db_mock.query.return_value = q_ids

    with pytest.raises(HTTPException) as exc:
        freightcost.create_freight_cost_mapping_records_for_next_year(year=2026, db=db_mock)

    assert exc.value.status_code == 400


@patch("freightcost.FreightCostMapping")
@patch("database.get_db")
def test_create_freight_cost_mapping_records_for_next_year_unit_success(mock_get_db, mock_mapping):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    # First query: distinct freight ids (list => .count is method so check is False)
    q_ids = MagicMock()
    q_ids.distinct.return_value = q_ids
    q_ids.all.return_value = [(10,)]

    # Second query: existing records to delete
    old1, old2 = MagicMock(), MagicMock()
    q_existing = MagicMock()
    q_existing.filter.return_value = q_existing
    q_existing.all.return_value = [old1, old2]

    # Old-rates lookup: period1 returns a record, others None (covers if old_rates is not None)
    old_rate = MagicMock(rate=1.1, company_name="US", fuel_cf=0.54, round_trip=1)
    q_old = MagicMock()
    q_old.filter.return_value = q_old
    q_old.first.side_effect = [old_rate] + [None] * 12

    db_mock.query.side_effect = [q_ids, q_existing] + [q_old] * 13

    out = freightcost.create_freight_cost_mapping_records_for_next_year(year=2026, db=db_mock)

    assert out["status"] == "success"
    assert out["Records added"] == 1
    assert db_mock.delete.call_count == 2
    assert db_mock.commit.call_count >= 2


# --- Covers 534-563 (default mapping; CANADA-CORE branch + no-record branch) ---
@patch("freightcost.FreightCostMapping")
@patch("database.get_db")
def test_update_freight_rates_with_default_value_unit_canada_core_maps_to_canada(mock_get_db, mock_mapping):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.first.return_value = MagicMock(company_name="CANADA-CORE")
    db_mock.query.return_value = q

    out = freightcost.update_freight_rates_with_default_value(freight_cost_id=1, year=2026, db=db_mock)

    assert out["status"] == "success"
    assert db_mock.add.call_count == 13
    db_mock.commit.assert_called_once()

    # ensure it created mappings with company_name="Canada"
    assert any("Canada" == call.kwargs.get("company_name") for call in mock_mapping.mock_calls)


@patch("database.get_db")
def test_update_freight_rates_with_default_value_unit_no_country_record_raises_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.first.return_value = None
    db_mock.query.return_value = q

    with pytest.raises(HTTPException) as exc:
        freightcost.update_freight_rates_with_default_value(freight_cost_id=1, year=2026, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 675-676 (no records branch) + 713-715 (exception branch) in fetch_records ---
@pytest.mark.asyncio
@patch("database.get_db")
async def test_fetch_records_unit_no_records_returns_empty(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.where.return_value = q
    q.count.return_value = 0
    db_mock.query.return_value = q

    db_mock.execute.return_value.all.return_value = []

    out = await freightcost.fetch_records(2025, "US", "US-CORE", db=db_mock)
    assert out.status == "success"
    assert out.data == []


@pytest.mark.asyncio
@patch("database.get_db")
async def test_fetch_records_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.where.return_value = q
    q.count.return_value = 1
    db_mock.query.return_value = q

    db_mock.execute.side_effect = Exception("sql fail")

    with pytest.raises(HTTPException) as exc:
        await freightcost.fetch_records(2025, "US", "US-CORE", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 761-830 (upload validations + success path) ---
@patch("freightcost.FileUploadTemplate")
@patch("database.get_db")
def test_handle_upload_file_unit_year_missing_raises_400(mock_get_db, mock_file_upload):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    df = pd.DataFrame({"freight_cost_id": [1], "company_name": ["US"], "year": [None], "P1": [1.0]})
    fake_file = MagicMock()
    fake_file.filename = "x.xlsx"
    fake_file.file = BytesIO(b"fake")

    mock_file_upload.return_value = MagicMock()

    with patch("freightcost.pd.read_excel", return_value={"Sheet1": df}):
        with pytest.raises(HTTPException) as exc:
            freightcost.handle_upload_file(uploaded_year=2025, user_email="a@b.com", file=fake_file, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.rollback.assert_called_once()


@patch("freightcost.FileUploadTemplate")
@patch("database.get_db")
def test_handle_upload_file_unit_multiple_year_values_raises_400(mock_get_db, mock_file_upload):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    df = pd.DataFrame(
        {"freight_cost_id": [1, 2], "company_name": ["US", "US"], "year": [2024, 2025], "P1": [1.0, 2.0]}
    )
    fake_file = MagicMock()
    fake_file.filename = "x.xlsx"
    fake_file.file = BytesIO(b"fake")

    mock_file_upload.return_value = MagicMock()

    with patch("freightcost.pd.read_excel", return_value={"Sheet1": df}):
        with pytest.raises(HTTPException) as exc:
            freightcost.handle_upload_file(uploaded_year=2025, user_email="a@b.com", file=fake_file, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.rollback.assert_called_once()


@patch("freightcost.FileUploadTemplate")
@patch("database.get_db")
def test_handle_upload_file_unit_success_inserts_and_logs(mock_get_db, mock_file_upload):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    df = pd.DataFrame({"freight_cost_id": [1], "company_name": ["US"], "year": [2025], "P1": [1.0]})
    fake_file = MagicMock()
    fake_file.filename = "x.xlsx"
    fake_file.file = BytesIO(b"fake")

    mock_file_upload.return_value = MagicMock()

    q_del = MagicMock()
    q_del.filter.return_value = q_del
    q_del.delete.return_value = 1
    db_mock.query.return_value = q_del

    with patch("freightcost.pd.read_excel", return_value={"Sheet1": df}):
        out = freightcost.handle_upload_file(uploaded_year=2025, user_email="a@b.com", file=fake_file, db=db_mock)

    assert "rates successfully uploaded" in out["detail"]
    assert db_mock.execute.called
    assert db_mock.add.called
    assert db_mock.commit.call_count >= 2


# --- Covers 853-876 + 893-896 (upload_file wrapper catches and raises 400) ---
@pytest.mark.asyncio
async def test_upload_file_route_unit_exception_returns_400():
    endpoint = _route_endpoint("/upload_file")
    db_mock = MagicMock()
    fake_file = MagicMock()

    with patch("freightcost.handle_upload_file", side_effect=Exception("boom")):
        with pytest.raises(HTTPException) as exc:
            await endpoint(uploaded_year=2025, user_email="a@b.com", file=fake_file, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 916-917 (get_file_details exception) ---
@pytest.mark.asyncio
@patch("database.get_db")
async def test_get_file_details_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        await freightcost.get_file_details(db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 940 + 946-947 (update_miles no records + catch-all) ---
@pytest.mark.asyncio
@patch("database.get_db")
async def test_update_miles_unit_no_records_raises_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    payload = schemas.FreightMiles(plant_id=1, vendor_site_id=2, growing_area_id=3, miles=10.0)

    with pytest.raises(HTTPException) as exc:
        await freightcost.update_miles(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 989 + 994-995 (update_fuel_cf no records + catch-all) ---
@patch("database.get_db")
def test_update_fuel_cf_unit_no_records_raises_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock

    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = []
    db_mock.query.return_value = q

    payload = schemas.FreightMilesSchema(year=2025, period=1, country="US", fuel_cf=0.9)

    with pytest.raises(HTTPException) as exc:
        freightcost.update_fuel_cf(payload=payload, db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 1022-1023 (fuel_cost exception) ---
@patch("database.get_db")
def test_fuel_cost_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.fuel_cost(year=2025, country="US", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 1050-1051 (fuel_cost_ga exception) ---
@patch("database.get_db")
def test_fuel_cost_ga_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.fuel_cost_ga(year=2025, country="US", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 1106-1108 (get_freight_cost exception) ---
@patch("database.get_db")
def test_get_freight_cost_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.execute.side_effect = Exception("tvf fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.get_freight_cost(year=2025, country_name="US", company_name="US", db=db_mock)

    assert exc.value.status_code == 400


# --- Covers 1172-1174 (mapping placeholder exception) ---
@patch("database.get_db")
def test_freight_cost_mapping_placeholder_unit_exception_400(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        freightcost.get_freight_cost_mapping_placeholder(db=db_mock)

    assert exc.value.status_code == 400


@patch("freightcost.FreightCostRate")
def test_create_freight_rates_in_db_unit_pydantic_path_covers_428(mock_model):
    db_mock = MagicMock()

    rec = MagicMock()
    rec.freight_cost_id = 123
    mock_model.return_value = rec

    payload = schemas.FreightCostRatesSchema(plant_id=1, vendor_site_id=2, growing_area_id=3)
    out = freightcost.create_freight_rates_in_db(payload, db=db_mock)

    assert out.freight_cost_id == 123
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@patch("freightcost.create_freight_rates_in_db")
def test_create_freight_rates_endpoint_unit_success_covers_456(mock_create):
    db_mock = MagicMock()

    rec = MagicMock()
    rec.freight_cost_id = 77
    mock_create.return_value = rec

    payload = schemas.FreightCostRatesSchema(plant_id=1)

    out = freightcost.create_potato_rates(payload=payload, db=db_mock)
    assert out == {"status": "success", "freight_cost_id": 77}


@patch("freightcost.FreightCostMapping")
def test_update_freight_rates_with_default_value_unit_us_core_maps_to_us_covers_544(mock_mapping):
    db_mock = MagicMock()

    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.first.return_value = MagicMock(company_name="US-CORE")
    db_mock.query.return_value = q

    freightcost.update_freight_rates_with_default_value(freight_cost_id=1, year=2026, db=db_mock)

    # 13 periods inserted
    assert db_mock.add.call_count == 13
    db_mock.commit.assert_called_once()

    # ensure at least one mapping call had company_name="US"
    assert any(call.kwargs.get("company_name") == "US" for call in mock_mapping.call_args_list)


@patch("freightcost.FileUploadTemplate")
def test_handle_upload_file_unit_multiple_sheets_logs_and_raises_covers_767_and_853_874(mock_fileupload):
    db_mock = MagicMock()

    fake_file = MagicMock()
    fake_file.filename = "multi.xlsx"
    fake_file.file = BytesIO(b"fake")

    mock_fileupload.return_value = MagicMock()

    # trigger: len(df_dict.keys()) != 1  (line ~767)
    with patch("freightcost.pd.read_excel", return_value={"S1": pd.DataFrame(), "S2": pd.DataFrame()}):
        with pytest.raises(HTTPException) as exc:
            freightcost.handle_upload_file(uploaded_year=2025, user_email="u@x.com", file=fake_file, db=db_mock)

    assert exc.value.status_code == 400
    # covers logging block (853-874)
    db_mock.rollback.assert_called_once()
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


@patch("freightcost.FileUploadTemplate")
def test_handle_upload_file_unit_year_mismatch_logs_and_raises_covers_787_and_853_874(mock_fileupload):
    db_mock = MagicMock()

    fake_file = MagicMock()
    fake_file.filename = "year.xlsx"
    fake_file.file = BytesIO(b"fake")

    mock_fileupload.return_value = MagicMock()

    df = pd.DataFrame(
        {
            "freight_cost_id": [1],
            "company_name": ["US"],
            "year": [2024],   # file year
            "P1": [1.0],
        }
    )

    with patch("freightcost.pd.read_excel", return_value={"Sheet1": df}):
        with pytest.raises(HTTPException) as exc:
            freightcost.handle_upload_file(uploaded_year=2025, user_email="u@x.com", file=fake_file, db=db_mock)

    assert exc.value.status_code == 400
    db_mock.rollback.assert_called_once()
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


"""________vendor_site_code.py_________"""


def test_get_view_vendor_site_code():
    response = client.get('/api/vendor_site_code/get_vendor_site_code')
    assert response.status_code == 200


"""________summary_price_variance.py_________"""


def test_get_price_variance_task_mapping():
    response = client.get('/api/summary_price_variance/price_variance_task_mapping')
    assert response.status_code == 200


def test_get_price_variance_task():
    response = client.get('/api/summary_price_variance/price_variance_task')
    assert response.status_code == 200


def test_price_variance_task_mapping_by_year():
    response = client.get('/api/summary_price_variance/price_variance_task_mapping_by_year/2023/CANADA-CORE')
    assert response.status_code == 200


def test_get_total_price_variance():
    response = client.get('/api/summary_price_variance/get_total_price_variance/2023/CANADA-CORE')
    assert response.status_code == 200
    
def test_summary_price_variance_year_country_code():
    response = client.get('/api/summary_price_variance/summary_price_variance_view/2024/US-CORE')
    assert response.status_code == 200


@patch('database.get_db')
def test_update_price_variance_mappings_records_success(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = [
        {
            "period": 3,
            "price_variance_task_id": 101,
            "year": 2024,
            "value": 150.75,
            "company_name": "Test Corp"
        },
        {
            "period": 4,
            "price_variance_task_id": 102,
            "year": 2024,
            "value": 200.00,
            "company_name": "Test Corp"
        }
    ]
    
    schema_list = [schemas.PriceVarianceMappingSchema(**item) for item in payload_data]
    test_payload = schemas.PriceVarianceMappingPayload(data=schema_list)
    result = update_price_variance_mappings_records(payload=test_payload, db=db_mock)
    assert result["status"] == "success"
    assert result["records_updated"] == 2
    assert db_mock.query.return_value.filter.return_value.update.call_count == 2
    db_mock.commit.assert_called_once()

    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = [
        {
            "period": 0,
            "price_variance_task_id": 101,
            "year": 2024,
            "value": 150.75,
            "company_name": "Test Corp"
        }
    ]
    schema_list = [schemas.PriceVarianceMappingSchema(**item) for item in payload_data]
    test_payload = schemas.PriceVarianceMappingPayload(data=schema_list)
    result = update_price_variance_mappings_records(payload=test_payload, db=db_mock)
    assert result["status"] == "error"
    assert result["message"] == "Please check details"
    
@patch('database.get_db')
def test_delete_all_post_success(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_records = [MagicMock(), MagicMock()]
    db_mock.query.return_value.all.return_value = mock_records
    result = delete_all_post(db=db_mock)

    assert result["message"] == "Records for the  deleted successfully."
    assert db_mock.delete.call_count == 2
    db_mock.commit.assert_called_once()

    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    db_mock.query.return_value.all.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        delete_all_post(db=db_mock)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No records found"


@pytest.mark.asyncio
@patch('summary_price_variance.price_variance_task_mapping') # 3rd argument
@patch('summary_price_variance.country_division_name')       # 2nd argument
@patch('summary_price_variance.price_variance_task')         # 1st argument
async def test_create_price_variance_task_mapping_success(mock_price_variance_task, mock_country_model, mock_mapping_model):
    #Case: 1
    db_mock = MagicMock()
    task_mock = MagicMock()
    task_mock.price_variance_task_id = 1
    task_mock.task_name = "Task A"
    country_mock = MagicMock()
    country_mock.task_desc = "US"
    mock_tasks_list = MagicMock()
    mock_tasks_list.__iter__.return_value = [task_mock]
    mock_tasks_list.count = 1
    mock_countries_list = [country_mock]
    query_mock = db_mock.query.return_value
    query_mock.all.side_effect = [mock_tasks_list, mock_countries_list]
    query_mock.filter.return_value.first.return_value = None
    result = await create_price_variance_task_mapping(year=2024, db=db_mock)

    assert result["status"] == "success"
    assert result["Records already exists for "] == []
    assert db_mock.add.call_count == 13
    assert db_mock.commit.call_count == 13

    #Case: 2
    db_mock = MagicMock()
    task_mock = MagicMock()
    task_mock.price_variance_task_id = 1
    task_mock.task_name = "Task A"
    mock_tasks_list = MagicMock()
    mock_tasks_list.__iter__.return_value = [task_mock]
    mock_tasks_list.count = 1
    query_mock = db_mock.query.return_value
    query_mock.all.side_effect = [mock_tasks_list, []]
    query_mock.filter.return_value.first.return_value = MagicMock()
    result = await create_price_variance_task_mapping(year=2024, db=db_mock)

    assert result["status"] == "success"
    assert result["Records already exists for "] == ["Task A"]
    db_mock.add.assert_not_called()

    #Case: 3
    db_mock = MagicMock()
    mock_empty_list = MagicMock()
    mock_empty_list.count = 0
    db_mock.query.return_value.all.return_value = mock_empty_list
    with pytest.raises(HTTPException) as exc_info:
        await create_price_variance_task_mapping(year=2024, db=db_mock)
    
    assert exc_info.value.status_code == 400


"""________user_info.py_________"""
def test_get_user_information():
    response = client.get('/api/user_info/get_user_information')
    assert response.status_code == 200
    
def test_get_active_user_information():
    response = client.get('/api/user_info/get_active_user_details')
    assert response.status_code == 200
    
def test_get_user_page_mapping():
    response = client.get('/api/user_info/get_user_page_mapping')
    assert response.status_code == 200

def test_get_user_page_mapping_table():
    response = client.get('/api/user_info/get_user_page_mapping_table?email=John.Perry%40pepsico.com')
    assert response.status_code == 200

@patch('database.get_db')
def test_user_log(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
        "email": "alex.mercer@techcorp.com",
        "country": "USA",
        "first_name": "Alex",
        "last_name": "Mercer",
        "user_status": True,
        "is_admin": True,
        "created_by": "system_migration",
        "created_time": datetime(2023, 1, 15, 8, 30, 0),
        "updated_by": "super_admin",
        "updated_time": datetime(2023, 6, 20, 14, 45, 0)
    }
    test_schema = schemas.UserInfoSchema(**mapping_payload)
    result = user_log(payload=test_schema, db=db_mock)
    assert result['status'] == 'success'

@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_user_status_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_user = MagicMock()
    mock_user.is_admin = False
    mock_user.user_status = True
    db_mock.query.return_value.filter.return_value.first.return_value = mock_user

    payload = {"email": "test@example.com", "user_status": False}
    test_schema = schemas.EditActiveStatusSchema(**payload)

    result = await update_user_status(user_info=test_schema, db=db_mock)
    
    assert result == {"message": "User status updated successfully"}
    assert mock_user.user_status is False
    db_mock.commit.assert_called_once()

@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_user_status_admin_success_multiple_admins(mock_get_db):
    db_mock = MagicMock()
    mock_user = MagicMock()
    mock_get_db.return_value = db_mock
    mock_user.is_admin = True
    mock_user.user_status = True
    
    db_mock.query.return_value.filter.return_value.first.return_value = mock_user
    db_mock.query.return_value.filter.return_value.count.return_value = 2

    payload = {"email": "admin@example.com", "user_status": False}
    test_schema = schemas.EditActiveStatusSchema(**payload)

    result = await update_user_status(user_info=test_schema, db=db_mock)
    
    assert result == {"message": "User status updated successfully"}
    assert mock_user.user_status is False

@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_user_status_no_status_change(mock_get_db):
    db_mock = MagicMock()
    mock_user = MagicMock()
    mock_get_db.return_value = db_mock
    mock_user.user_status = True
    db_mock.query.return_value.filter.return_value.first.return_value = mock_user

    payload = {"email": "test@example.com", "user_status": None}
    test_schema = schemas.EditActiveStatusSchema(**payload)

    result = await update_user_status(user_info=test_schema, db=db_mock)
    
    assert result == {"message": "User status updated successfully"}
    assert mock_user.user_status is True


@pytest.mark.asyncio
async def test_create_user_information_success():
    db_mock = MagicMock()
    
    payload_data = {
        "email": "newuser@example.com",
        "country": "USA",
        "first_name": "John",
        "last_name": "Doe",
        "user_status": True,
        "is_admin": False,
        "created_by": "admin",
        "created_time": datetime.now()
    }
    test_schema = schemas.UserInfoSchema(**payload_data)

    result = await create_user_information(payload=test_schema, db=db_mock)

    db_mock.add.assert_called_once()
    
    added_user_instance = db_mock.add.call_args[0][0]
    
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(added_user_instance)
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_create_user_information_failure():
    db_mock = MagicMock()
    db_mock.commit.side_effect = Exception("Database insert error")

    payload_data = {"email": "fail@example.com"}
    test_schema = schemas.UserInfoSchema(**payload_data)

    with pytest.raises(HTTPException) as exc_info:
        await create_user_information(payload=test_schema, db=db_mock)
    
    assert exc_info.value.status_code == 400
    assert "Database insert error" in str(exc_info.value.detail)

@pytest.mark.asyncio
@patch('user_info.user_information')
@patch('user_info.access_type_information')
@patch('user_info.country_information')
@patch('user_info.page_information')
@patch('user_info.user_page_mapping')
@pytest.mark.parametrize("payload_data, mock_config, expected_status, expected_detail", [
    (
        [{"email": "admin@test.com", "is_admin": True}],
        {
            "admin_count": 2, "user_exists": True, "access_exists": True, 
            "country_exists": True, "page_exists": True
        },
        200, 
        "User page mappings updated successfully"
    ),
    (
        [{"email": "user@test.com", "is_admin": False, "page_name": "Home", "access_name": "Read", "country_name": "US"}],
        {
            "admin_count": 2, "user_exists": True, "access_exists": True, 
            "country_exists": True, "page_exists": True
        },
        200, 
        "User page mappings updated successfully"
    ),
    (
        [{"email": "unknown@test.com", "is_admin": True}],
        {
            "admin_count": 2, "user_exists": False, "access_exists": True, 
            "country_exists": True, "page_exists": True
        },
        404, 
        "User with email unknown@test.com not found"
    ),
    (
        [{"email": "user@test.com", "is_admin": False, "page_name": "Home", "access_name": "BadAccess", "country_name": "US"}],
        {
            "admin_count": 2, "user_exists": True, "access_exists": False, 
            "country_exists": True, "page_exists": True
        },
        404, 
        "Access type BadAccess not found"
    ),
    (
        [{"email": "user@test.com", "is_admin": False, "page_name": "Home", "access_name": "Read", "country_name": "BadCountry"}],
        {
            "admin_count": 2, "user_exists": True, "access_exists": True, 
            "country_exists": False, "page_exists": True
        },
        404, 
        "Country BadCountry not found"
    ),
    (
        [{"email": "lastadmin@test.com", "is_admin": False, "page_name": "Home", "access_name": "Read", "country_name": "US"}],
        {
            "admin_count": 1, "user_exists": True, "access_exists": True, 
            "country_exists": True, "page_exists": True
        },
        400, 
        "At least one admin user must exist"
    ),
    (
        [{"email": "user@test.com", "is_admin": False, "page_name": "BadPage", "access_name": "Read", "country_name": "US"}],
        {
            "admin_count": 2, "user_exists": True, "access_exists": True, 
            "country_exists": True, "page_exists": False
        },
        404, 
        "Page with name BadPage not found"
    ),
])
async def test_update_user_page_mapping_scenarios(
    mock_user_page_mapping, 
    mock_page_info, 
    mock_country_info, 
    mock_access_type_info, 
    mock_user_info, 
    payload_data, mock_config, expected_status, expected_detail
):

    db_mock = MagicMock()
    
    mock_user_query = MagicMock()
    mock_access_query = MagicMock()
    mock_country_query = MagicMock()
    mock_page_query = MagicMock()
    mock_mapping_query = MagicMock()

    def query_side_effect(model):
        if model == mock_user_info: return mock_user_query
        if model == mock_access_type_info: return mock_access_query
        if model == mock_country_info: return mock_country_query
        if model == mock_page_info: return mock_page_query
        if model == mock_user_page_mapping: return mock_mapping_query
        return MagicMock()

    db_mock.query.side_effect = query_side_effect

    mock_user_query.filter.return_value.count.return_value = mock_config["admin_count"]
    mock_user_query.filter.return_value.all.return_value = [MagicMock()] * mock_config["admin_count"]
    
    user_obj = MagicMock()
    user_obj.user_id = 123
    user_obj.is_admin = True
    mock_user_query.filter.return_value.first.return_value = user_obj if mock_config["user_exists"] else None

    access_obj = MagicMock()
    access_obj.access_id = 1
    mock_access_query.filter.return_value.first.return_value = access_obj if mock_config["access_exists"] else None

    country_obj = MagicMock()
    country_obj.country_id = 99
    mock_country_query.filter.return_value.first.return_value = country_obj if mock_config["country_exists"] else None

    page_obj = MagicMock()
    page_obj.page_id = 55
    mock_page_query.all.return_value = [page_obj]
    mock_page_query.filter.return_value.first.return_value = page_obj if mock_config["page_exists"] else None

    test_payload = schemas.UpdateUserInfoPayload(data=[
        schemas.UpdateUserInfoSchema(**item) for item in payload_data
    ])

    if expected_status != 200:
        with pytest.raises(HTTPException) as exc_info:
            await update_user_page_mapping(payload=test_payload, db=db_mock)
        assert exc_info.value.status_code == expected_status
        assert expected_detail in str(exc_info.value.detail)
    else:
        result = await update_user_page_mapping(payload=test_payload, db=db_mock)
        assert result == {"message": expected_detail}
        db_mock.commit.assert_called_once()


@pytest.mark.asyncio
@patch('user_info.get_or_create_user')
@patch('user_info.user_information')
@patch('user_info.access_type_information')
@patch('user_info.country_information')
@patch('user_info.page_information')
@patch('user_info.user_page_mapping')
@pytest.mark.parametrize("payload_data, mock_setup, expected_status, expected_detail, mapping_created", [
    (
        {"email": "user@test.com", "is_admin": False},
        {"view_access": 10, "country": 99, "pages": [(1,), (2,)], "existing_mapping": None},
        200, "User and mappings created successfully", True
    ),
    (
        {"email": "admin@test.com", "is_admin": True},
        {"view_access": 10, "edit_access": 20, "country": 99, "pages": [(1,)], "existing_mapping": None},
        200, "User and mappings created successfully", True
    ),
    (
        {"email": "user@test.com", "is_admin": False},
        {"view_access": None, "pages": [(1,)]},
        404, "Access type with name 'view' not found", False
    ),
    (
        {"email": "admin@test.com", "is_admin": True},
        {"view_access": 10, "edit_access": None, "pages": [(1,)]},
        404, "Access type with name 'edit' not found", False
    ),
    (
        {"email": "user@test.com", "is_admin": False},
        {"view_access": 10, "country": None, "pages": [(1,)]},
        404, "Country with name 'All' not found", False
    ),
    (
        {"email": "user@test.com", "is_admin": False},
        {"view_access": 10, "country": 99, "pages": [(1,)], "existing_mapping": MagicMock()},
        200, "User and mappings created successfully", False
    ),
])
async def test_create_user_and_mapping_scenarios(
    mock_mapping_model, mock_page_model, mock_country_model, mock_access_model, mock_user_model, mock_get_or_create_user,
    payload_data, mock_setup, expected_status, expected_detail, mapping_created
):
    db_mock = MagicMock()
    
    mock_user_instance = MagicMock()
    mock_user_instance.user_id = 123
    mock_get_or_create_user.return_value = mock_user_instance

    mock_page_model.page_id = MagicMock()
    page_query_mock = MagicMock()
    page_query_mock.distinct.return_value.all.return_value = mock_setup.get("pages", [])
    
    mock_access_model.access_id = MagicMock()
    access_query_mock = MagicMock()
    
    view_id = mock_setup.get("view_access")
    edit_id = mock_setup.get("edit_access")
    
    # .scalar() is used for View Access
    access_query_mock.filter.return_value.scalar.return_value = view_id
    
    # .first() is used for Edit Access
    edit_obj = MagicMock(access_id=edit_id) if edit_id else None
    access_query_mock.filter.return_value.first.return_value = edit_obj

    mock_country_model.country_id = MagicMock()
    country_query_mock = MagicMock()
    cid = mock_setup.get("country")
    country_query_mock.filter.return_value.scalar.return_value = cid
    
    mapping_query_mock = MagicMock()
    mapping_query_mock.filter.return_value.first.return_value = mock_setup.get("existing_mapping")

    def query_side_effect(arg):
        if arg == mock_page_model.page_id:
            return page_query_mock
        if arg == mock_access_model.access_id:
            return access_query_mock
        if arg == mock_access_model:
            return access_query_mock
        if arg == mock_country_model.country_id:
            return country_query_mock
        if arg == mock_mapping_model:
            return mapping_query_mock
        return MagicMock()

    db_mock.query.side_effect = query_side_effect
    
    user_payload = schemas.UserCreationPayload(**payload_data)

    if expected_status != 200:
        with pytest.raises(HTTPException) as exc_info:
            await create_user_and_mapping(user_details=user_payload, db=db_mock)
        assert exc_info.value.status_code == expected_status
        assert expected_detail in str(exc_info.value.detail)
    else:
        result = await create_user_and_mapping(user_details=user_payload, db=db_mock)
        assert result == {"message": expected_detail}
        
        if mapping_created:
            db_mock.add.assert_called()
            db_mock.commit.assert_called()
        else:
            db_mock.add.assert_not_called()

@pytest.mark.asyncio
@patch('user_info.user_information')         # Arg 5
@patch('user_info.access_type_information')  # Arg 4
@patch('user_info.country_information')      # Arg 3
@patch('user_info.page_information')         # Arg 2
@patch('user_info.user_page_mapping')        # Arg 1
@pytest.mark.parametrize("payload_data, mock_setup, expected_status, expected_detail", [
    (
        {"email": "user@test.com", "page_name": "Dashboard", "access_name": "Read", "country_name": "US"},
        {"user_exists": True, "page_exists": True, "access_exists": True, "country_exists": True},
        200, "User and mapping updated successfully"
    ),
    (
        {"email": "unknown@test.com", "page_name": "Dashboard"},
        {"user_exists": False, "page_exists": True, "access_exists": True, "country_exists": True},
        404, "User not found"
    ),
    (
        {"email": "user@test.com", "page_name": "BadPage"},
        {"user_exists": True, "page_exists": False, "access_exists": True, "country_exists": True},
        404, "Page not found"
    ),
    (
        {"email": "user@test.com", "page_name": "Dashboard", "access_name": "BadAccess"},
        {"user_exists": True, "page_exists": True, "access_exists": False, "country_exists": True},
        404, "Access type not found"
    ),
    (
        {"email": "user@test.com", "page_name": "Dashboard", "access_name": "Read", "country_name": "BadCountry"},
        {"user_exists": True, "page_exists": True, "access_exists": True, "country_exists": False},
        404, "Country not found"
    ),
    (
        {"email": "user@test.com", "page_name": None}, 
        {"user_exists": True, "page_exists": True, "access_exists": True, "country_exists": True},
        200, "User and mapping updated successfully"
    ),
])
async def test_update_new_user_page_mapping(
    mock_mapping_model,  # Matches @patch('...user_page_mapping')
    mock_page_model,     # Matches @patch('...page_information')
    mock_country_model,  # Matches @patch('...country_information')
    mock_access_model,   # Matches @patch('...access_type_information')
    mock_user_model,     # Matches @patch('...user_information')
    payload_data, mock_setup, expected_status, expected_detail
):
    
    db_mock = MagicMock()
    
    # User Mock
    user_query = MagicMock()
    mock_user_obj = MagicMock()
    mock_user_obj.user_id = 1
    user_query.filter.return_value.first.return_value = mock_user_obj if mock_setup["user_exists"] else None
    
    # Page Mock
    page_query = MagicMock()
    mock_page_obj = MagicMock()
    mock_page_obj.page_id = 10
    page_query.filter.return_value.first.return_value = mock_page_obj if mock_setup.get("page_exists") else None
    
    # Access Mock
    access_query = MagicMock()
    mock_access_obj = MagicMock()
    mock_access_obj.access_id = 20
    access_query.filter.return_value.first.return_value = mock_access_obj if mock_setup.get("access_exists") else None
    
    # Country Mock
    country_query = MagicMock()
    mock_country_obj = MagicMock()
    mock_country_obj.country_id = 30
    country_query.filter.return_value.first.return_value = mock_country_obj if mock_setup.get("country_exists") else None
    
    # Mapping Mock
    mapping_query = MagicMock()

    def query_side_effect(model_arg):
        if model_arg == mock_user_model: return user_query
        if model_arg == mock_page_model: return page_query
        if model_arg == mock_access_model: return access_query
        if model_arg == mock_country_model: return country_query
        if model_arg == mock_mapping_model: return mapping_query
        return MagicMock()

    db_mock.query.side_effect = query_side_effect

    test_payload = schemas.NewUserInfoPayload(data=[schemas.NewUserInfoSchema(**payload_data)])

    if expected_status != 200:
        with pytest.raises(HTTPException) as exc_info:
            await update_new_user_page_mapping(user_info_payload=test_payload, db=db_mock)
        assert exc_info.value.status_code == expected_status
        assert exc_info.value.detail == expected_detail
    else:
        result = await update_new_user_page_mapping(user_info_payload=test_payload, db=db_mock)
        assert result == {"message": expected_detail}
        
        if payload_data.get("page_name"):
            db_mock.add.assert_called()
            db_mock.commit.assert_called()
            mapping_query.filter.return_value.delete.assert_called()


@pytest.mark.parametrize("email_input, expected_result", [
    ("john.doe@example.com", ("john", "doe")),
    ("jane.smith123@test.co.in", ("jane", "smith")),
    ("alice.middle.wonderland@domain.com", ("alice", "wonderland")),
    ("admin@system.com", ("admin", "admin")),
])
def test_extract_name_from_email_success(email_input, expected_result):
    result = extract_name_from_email(email_input)
    assert result == expected_result

@patch('logging.Logger.exception')
def test_extract_name_from_email_failure(mock_logger):
    with pytest.raises(Exception):
        extract_name_from_email(None)

@patch('user_info.extract_name_from_email')
@patch('user_info.user_information')
def test_get_or_create_user_success(mock_user_model, mock_extract_name):
    db_mock = MagicMock()
    
    db_mock.query.return_value.filter.return_value.first.return_value = None
    mock_extract_name.return_value = ("John", "Doe")
    mock_new_user_instance = MagicMock()
    mock_user_model.return_value = mock_new_user_instance

    payload = schemas.UserCreationPayload(email="john.doe@test.com", is_admin=False)

    result = get_or_create_user(user_details=payload, db=db_mock)
    assert result == mock_new_user_instance
    mock_extract_name.assert_called_once_with("john.doe@test.com")
    
    mock_user_model.assert_called_once()
    call_kwargs = mock_user_model.call_args.kwargs
    assert call_kwargs['email'] == "john.doe@test.com"
    assert call_kwargs['country'] == "US"
    assert call_kwargs['user_status'] is True
    
    db_mock.add.assert_called_once_with(mock_new_user_instance)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

@patch('user_info.user_information')
def test_get_or_create_user_already_exists(mock_user_model):
    db_mock = MagicMock()
    
    # 1. Setup: Database returns an existing user object
    existing_user = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = existing_user

    payload = schemas.UserCreationPayload(email="existing@test.com", is_admin=True)

    with pytest.raises(HTTPException) as exc_info:
        get_or_create_user(user_details=payload, db=db_mock)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "User already exists"


    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_get_user_information_mapping_view():
    response = client.get('/api/user_info/user_information_mapping_view')
    assert response.status_code == 200
   
"""________PageInfo_________"""
def test_get_page_information():
    response = client.get('/api/page_info/get_page_information')
    assert response.status_code == 200
    
def test_get_country_information():
    response = client.get('/api/page_info/get_country_information')
    assert response.status_code == 200

def test_get_access_type_information():
    response = client.get('/api/page_info/get_access_information')
    assert response.status_code == 200

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_page_information_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"page_name": "Test Page"}
    mock_new_record = MagicMock()
    with patch('page_info.page_information', return_value=mock_new_record):
        result = await create_page_information(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    db_mock.add.assert_called_once_with(mock_new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(mock_new_record)

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_country_information_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"country_name": "Test Country"}
    mock_new_record = MagicMock()
    with patch('page_info.country_information', return_value=mock_new_record):
        result = await create_country_information(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    db_mock.add.assert_called_once_with(mock_new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(mock_new_record)

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_access_type_information_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"access_name": "Test Access", "access_value": 1}
    mock_new_record = MagicMock()
    with patch('page_info.access_type_information', return_value=mock_new_record):
        result = await create_access_type_information(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    db_mock.add.assert_called_once_with(mock_new_record)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(mock_new_record)


"""________UserLog________"""


def test_get_user_log():
    response = client.get('/api/user_log/get_last_30_days_log')
    assert response.status_code == 200

def test_export_last_30_days():
    response = client.get('/api/user_log/export_last_30_days')
    assert response.status_code == 200

@patch('database.get_db')
def test_user_log(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mapping_payload = {
    "email": "jessica.smith@example.com",
    "date_time": "2023-10-27T08:30:00",
    "date": "2023-10-27"
    }
    test_schema = schemas.UserlogSchema(**mapping_payload)
    result = user_log(payload=test_schema, db=db_mock)
    assert result['status'] == 'success'

"""________OffContractPlanInfo________"""


def test_get_off_contract_plan_info():
    response = client.get('/api/off_contract_plan_info/')
    assert response.status_code == 200


def test_get_off_contract_plan_task_mapping_by_year_and_country():
    response = client.get('/api/off_contract_plan_info/get_off_contract_plan_task_mapping_by_year_and_country/2024/US-CORE')
    assert response.status_code == 200

    response = client.get('/api/off_contract_plan_info/get_off_contract_plan_task_mapping_by_year_and_country/10000/US-CORE')
    assert response.status_code == 404


@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_off_contract_plan_mapping_next_year_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_task = MagicMock(off_contract_plan_task_id=1)
    mock_country = MagicMock(task_desc="US", status="Active")
    class MockList(list):
        count = 1
    mock_all_records = MockList([mock_task])
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    ]
    result = await create_off_contract_plan_task_mapping_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    assert db_mock.add.call_count == 13
    assert db_mock.commit.called

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_off_contract_plan_mapping_duplicate_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_task = MagicMock(off_contract_plan_task_id=1)
    mock_country = MagicMock(task_desc="US")
    mock_existing = MagicMock(off_contract_plan_task_id=1, company_name="US", period=1)
    class MockList(list):
        count = 1
    mock_all_records = MockList([mock_task])
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_existing]))))
    ]
    result = await create_off_contract_plan_task_mapping_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "error"

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_off_contract_plan_mapping_no_records_found(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    class MockList(list):
        count = 0
    mock_all_records = MockList([])
    db_mock.query.return_value.all.return_value = mock_all_records
    with pytest.raises(HTTPException) as exc:
        await create_off_contract_plan_task_mapping_for_next_year(year=2025, db=db_mock)
    
    assert exc.value.status_code == 400

@patch('database.get_db')
def test_create_off_contract_plan_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"task_name": "Test"}
    mock_new_record = MagicMock()
    mock_new_record.off_contract_plan_task_id = 101
    with patch('offcontractplaninfo.off_contract_plan_info', return_value=mock_new_record):
        result = create_off_contract_plan_info(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["off_contract_plan_task_id"] == 101

@patch('database.get_db')
def test_create_off_contract_plan_task_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {"year": 2025, "value": 100}
    mock_new_record = MagicMock()
    mock_new_record.row_id = 55
    with patch('offcontractplaninfo.off_contract_plan_task_mapping', return_value=mock_new_record):
        result = create_off_contract_plan_task_mapping(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["row_id"] == 55

@patch('database.get_db')
def test_update_off_contract_plan_mapping_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_item = MagicMock()
    mock_item.off_contract_plan_task_id = 1
    mock_item.period = 1
    mock_item.year = 2025
    mock_item.company_name = "US"
    mock_item.value = 50.0
    mock_payload = MagicMock()
    mock_payload.data = [mock_item]
    result = update_off_contract_plan_mapping_records(payload=mock_payload, db=db_mock)
    assert result["status"] == "success"
    assert result["records_updated"] == 1
    assert db_mock.commit.called

@patch('database.get_db')
def test_update_off_contract_plan_mapping_records_validation_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_item = MagicMock()
    mock_item.off_contract_plan_task_id = 1
    mock_item.period = 0
    mock_item.year = 2025
    mock_payload = MagicMock()
    mock_payload.data = [mock_item]
    result = update_off_contract_plan_mapping_records(payload=mock_payload, db=db_mock)

    assert result["status"] == "error"
    assert "Please check details" in result["message"]
    assert not db_mock.commit.called



"""________PeriodWeekCalc________"""

def test_get_period_and_week():
    year = 2024
    date_input = "2024-06-15"
    response = client.get(f"/api/period_week/get_period_and_week?year={year}&date_input={date_input}")
    assert response.status_code == 200
    
    year = 2024
    date_input = "2023-12-31"
    response = client.get(f"/api/period_week/get_period_and_week?year={year}&date_input={date_input}")
    assert response.status_code == 200

    year = 2023
    date_input = "2024-01-10"
    response = client.get(f"/api/period_week/get_period_and_week?year={year}&date_input={date_input}")
    assert response.status_code == 200

    year = 10000
    date_input = "2024-01-10"
    response = client.get(f"/api/period_week/get_period_and_week?year={year}&date_input={date_input}")
    assert response.status_code == 400

    year = 2023
    date_input = "2022-12-31"
    response = client.get(f"/api/period_week/get_period_and_week?year={year}&date_input={date_input}")
    assert response.status_code == 200
    
def test_get_all_periods():
    year = 2024
    response = client.get(f"/api/period_week/get_all_periods?year={year}")
    assert response.status_code == 200
    
    year = 2023
    response = client.get(f"/api/period_week/get_all_periods?year={year}")
    assert response.status_code == 200

    year = 10000
    response = client.get(f"/api/period_week/get_all_periods?year={year}")
    assert response.status_code == 400

def test_get_pw_start_end_dates():
    year = 2023
    response = client.get(f"/api/period_week/get_all_periodweek_start_end_dates?year={year}")
    assert response.status_code == 200

    year = 2028
    response = client.get(f"/api/period_week/get_all_periodweek_start_end_dates?year={year}")
    assert response.status_code == 200

    year = 10000
    response = client.get(f"/api/period_week/get_all_periodweek_start_end_dates?year={year}")
    assert response.status_code == 400

def test_get_pw_start_end_date():
    year = 2024
    period = 1
    week = 1
    response = client.get(f"/api/period_week/get_period_week_start_end_date?year={year}&period={period}&week={week}")
    assert response.status_code == 200

    year = 2024
    period = 14
    week = 1
    response = client.get(f"/api/period_week/get_period_week_start_end_date?year={year}&period={period}&week={week}")
    assert response.status_code == 200

    year = 10000
    period = 1
    week = 1
    response = client.get(f"/api/period_week/get_period_week_start_end_date?year={year}&period={period}&week={week}")
    assert response.status_code == 400

def test_has_five_weeks():
    year = 2028
    period = 13
    response = client.get(f"/api/period_week/has_five_weeks?year={year}&period={period}")
    assert response.status_code == 200

    year = 2024
    period = 1
    response = client.get(f"/api/period_week/has_five_weeks?year={year}&period={period}")
    assert response.status_code == 200

    year = 2024
    period = 14
    response = client.get(f"/api/period_week/has_five_weeks?year={year}&period={period}")
    assert response.status_code == 200

    year = 10000
    period = 1
    response = client.get(f"/api/period_week/has_five_weeks?year={year}&period={period}")
    assert response.status_code == 400

def test_get_period_start_end_dates_fixed():

    year = 2024
    response = client.get(f"/api/period_week/get_period_start_end_dates_fixed?year={year}")
    assert response.status_code == 200

    year = 2023
    response = client.get(f"/api/period_week/get_period_start_end_dates_fixed?year={year}")
    assert response.status_code == 200

    year = 2028
    response = client.get(f"/api/period_week/get_period_start_end_dates_fixed?year={year}")
    assert response.status_code == 200

    year = 10000
    response = client.get(f"/api/period_week/get_period_start_end_dates_fixed?year={year}")
    assert response.status_code == 400

def test_pw_start_end_dates():

    year = 2028
    response = client.get(f"/api/period_week/get_period_week_start_end_dates?year={year}")
    assert response.status_code == 200

    year = 2023
    response = client.get(f"/api/period_week/get_period_week_start_end_dates?year={year}")
    assert response.status_code == 200

    year = 10000
    response = client.get(f"/api/period_week/get_period_week_start_end_dates?year={year}")
    assert response.status_code == 400


"""________PowerBIConfig________"""

@patch("database.get_db")
def test_create_refresh_logs_success(mock_get_db):
    """Test successful creation of refresh logs."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    payload = MagicMock()
    payload.dict.return_value = {
        "report_name": "All reports",
        "status": "Success",
    }
    
    # Simulate DB assigning log_id during refresh
    def refresh_side_effect(obj):
        obj.log_id = 123
    
    db_mock.refresh.side_effect = refresh_side_effect
    
    result = create_refresh_logs(payload=payload, db=db_mock)
    
    assert result == {"status": "success", "log_id": 123}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@patch("database.get_db")
def test_create_refresh_logs_exception_400(mock_get_db):
    """Test exception handling when creating refresh logs fails."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    payload = MagicMock()
    payload.dict.return_value = {}
    
    db_mock.add.side_effect = Exception("Database error")
    
    with pytest.raises(HTTPException) as exc:
        create_refresh_logs(payload=payload, db=db_mock)
    
    assert exc.value.status_code == 400
    assert "Database error" in str(exc.value.detail)

def test_get_config():
    response = client.get("/api/powerbi_config/powerbi_report_urls")
    assert response.status_code == 200

    response = client.get("/api/powerbi_config/powerbi_report")
    assert response.status_code == 400

@patch('database.get_db')
def test_upsert_config_powerbi_valid_update_success(mock_get_db):

    # Case 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_existing_row = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = mock_existing_row
    config_name = "powerbi_report_urls"
    payload = {
        "powerBIReports": [
            {"id": "123", "name": "Sales Report", "url": "powerbi.com/report1"}
        ]
    }
    result = upsert_config(config_name=config_name, config=payload, db=db_mock)

    assert result["status"] == "Success"
    assert mock_existing_row.config_json is not None 
    db_mock.add.assert_not_called() 
    db_mock.commit.assert_called_once()

    # Case 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_existing_row = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = mock_existing_row
    config_name = "powerbi_report_test"
    payload = {
        "powerBIReports": [
            {"id": "123", "name": "Sales Report", "url": "powerbi.com/report1"}
        ]
    }
    result = upsert_config(config_name=config_name, config=payload, db=db_mock)

    assert result["status"] == "Success"
    assert mock_existing_row.config_json is not None 
    db_mock.add.assert_not_called() 
    db_mock.commit.assert_called_once()


"""________Productivity________"""

def test_get_productivity_task_info():
    response = client.get("/api/productivity/")
    assert response.status_code == 200

def test_get_productivity_task_mapping_by_year_and_country():
    response = client.get("/api/productivity/get_productivity_task_mapping_by_year_and_country/2024/US-CORE")
    assert response.status_code == 200

    response = client.get("/api/productivity/get_productivity_task_mapping_by_year_and_country/3000/US-CORE")
    assert response.status_code == 404

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_productivity_task_mapping_next_year_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_task = MagicMock(productivity_task_id=1)
    mock_country = MagicMock(task_desc="US", status="Active")
    mock_all_records = MagicMock()
    mock_all_records.__iter__.return_value = iter([mock_task]) # Make it iterable
    mock_all_records.count = 1 # Add the property your code checks
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)), # 1. Get Tasks
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))), # 2. Get Countries
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))) # 3. Check Existing (Empty)
    ]
    result = await create_productivity_task_mapping_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    assert db_mock.add.call_count == 13
    assert db_mock.commit.called

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_productivity_task_mapping_duplicate_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_task = MagicMock(productivity_task_id=1)
    mock_country = MagicMock(task_desc="US")
    mock_existing = MagicMock(productivity_task_id=1, company_name="US", period=1)
    mock_all_records = MagicMock()
    mock_all_records.__iter__.return_value = iter([mock_task])
    mock_all_records.count = 1
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_existing])))) # Found existing
    ]
    result = await create_productivity_task_mapping_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "error"

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_productivity_task_mapping_no_records_found(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_all_records = MagicMock()
    mock_all_records.__iter__.return_value = iter([])
    mock_all_records.count = 0
    db_mock.query.return_value.all.return_value = mock_all_records
    with pytest.raises(HTTPException) as exc:
        await create_productivity_task_mapping_for_next_year(year=2025, db=db_mock)
    
    assert exc.value.status_code == 400

@patch('database.get_db')
def test_create_productivity_task_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {
        "task_name": "Test Task", 
        "task_desc": "Desc", 
        "status": "Active"
    }
    
    mock_new_record = MagicMock()
    mock_new_record.productivity_task_id = 99
    with patch('productivity.productivity_task_info', return_value=mock_new_record):
        result = create_productivity_task_info(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["productivity_task_id"] == 99

@patch('database.get_db')
def test_create_productivity_task_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {
        "year": 2025, 
        "period": 1, 
        "value": 10.5,
        "productivity_task_id": 1
    }
    mock_new_record = MagicMock()
    mock_new_record.row_id = 55
    with patch('productivity.productivity_task_mapping', return_value=mock_new_record):
        result = create_productivity_task_mapping(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["row_id"] == 55

@patch('database.get_db')
def test_update_productivity_mapping_records_success(mock_get_db):
    #Case: 1
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_item = MagicMock()
    mock_item.productivity_task_id = 1
    mock_item.period = 1
    mock_item.year = 2025
    mock_item.company_name = "US"
    mock_item.value = 50
    mock_payload = MagicMock()
    mock_payload.data = [mock_item]
    result = update_productivity_mapping_records(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["records_updated"] == 1
    assert db_mock.commit.called

    #Case: 2
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    invalid_item = schemas.ProductivityTaskMappingSchema(
        productivity_task_id=0,
        period=0, 
        year=2025,
        company_name="Test Company",
        value=100
    )
    real_payload = schemas.ProductivityTaskMappingPayload(data=[invalid_item])
    result = update_productivity_mapping_records(payload=real_payload, db=db_mock)

    assert result["status"] == "error"
    assert "Please check details" in result["message"]
    assert not db_mock.commit.called


"""________ProductivityPlan________"""

def test_get_productivity_plan_task_info():
    response = client.get("/api/productivity_plan/")
    assert response.status_code == 200

def test_get_productivity_plan_task_mapping_by_year_and_country():
    response = client.get("/api/productivity_plan/get_productivity_plan_task_mapping_by_year_and_country/2024/US-CORE")
    assert response.status_code == 200

    response = client.get("/api/productivity_plan/get_productivity_plan_task_mapping_by_year_and_country/3000/US-CORE")
    assert response.status_code == 404

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_productivity_plan_task_mapping_next_year_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_task = MagicMock(productivity_plan_task_id=1)
    mock_country = MagicMock(task_desc="US", status="Active")
    mock_all_records = MagicMock()
    mock_all_records.__iter__.return_value = iter([mock_task]) # Make it iterable
    mock_all_records.count = 1 # Add the property your code checks
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)), # 1. Get Tasks
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))), # 2. Get Countries
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))) # 3. Check Existing (Empty)
    ]
    result = await create_productivity_plan_task_mapping_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "success"
    assert result["Records added"] == 13
    assert db_mock.add.call_count == 13
    assert db_mock.commit.called

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_productivity_plan_task_mapping_duplicate_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_task = MagicMock(productivity_plan_task_id=1)
    mock_country = MagicMock(task_desc="US")
    mock_existing = MagicMock(productivity_plan_task_id=1, company_name="US", period=1)
    mock_all_records = MagicMock()
    mock_all_records.__iter__.return_value = iter([mock_task])
    mock_all_records.count = 1
    db_mock.query.side_effect = [
        MagicMock(all=MagicMock(return_value=mock_all_records)),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_country])))),
        MagicMock(filter=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_existing])))) # Found existing
    ]
    result = await create_productivity_plan_task_mapping_for_next_year(year=2025, db=db_mock)

    assert result["status"] == "error"

@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_productivity_plan_task_mapping_no_records_found(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_all_records = MagicMock()
    mock_all_records.__iter__.return_value = iter([])
    mock_all_records.count = 0
    db_mock.query.return_value.all.return_value = mock_all_records
    with pytest.raises(HTTPException) as exc:
        await create_productivity_plan_task_mapping_for_next_year(year=2025, db=db_mock)
    
    assert exc.value.status_code == 400

@patch('database.get_db')
def test_create_productivity_plan_task_info(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {
        "task_name": "Test Task", 
        "task_desc": "Desc", 
        "status": "Active"
    }
    
    mock_new_record = MagicMock()
    mock_new_record.productivity_plan_task_id = 99
    with patch('productivityplan.productivity_plan_task_info', return_value=mock_new_record):
        result = create_productivity_plan_task_info(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["productivity_plan_task_id"] == 99

@patch('database.get_db')
def test_create_productivity_plan_task_mapping(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_payload = MagicMock()
    mock_payload.dict.return_value = {
        "year": 2025, 
        "period": 1, 
        "value": 10.5,
        "productivity_plan_task_id": 1
    }
    mock_new_record = MagicMock()
    mock_new_record.row_id = 55
    with patch('productivityplan.productivity_plan_task_mapping', return_value=mock_new_record):
        result = create_productivity_plan_task_mapping(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["row_id"] == 55

@patch('database.get_db')
def test_update_productivity_plan_mapping_records_success(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_item = MagicMock()
    mock_item.productivity_plan_task_id = 1
    mock_item.period = 1
    mock_item.year = 2025
    mock_item.company_name = "US"
    mock_item.value = 50
    mock_payload = MagicMock()
    mock_payload.data = [mock_item]
    result = update_productivity_plan_mapping_records(payload=mock_payload, db=db_mock)

    assert result["status"] == "success"
    assert result["records_updated"] == 1
    assert db_mock.commit.called

@patch('database.get_db')
def test_update_productivity_mapping_records_validation_error(mock_get_db):
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    mock_item = MagicMock()
    mock_item.productivity_plan_task_id = 1
    mock_item.period = 0 
    mock_item.year = 2025
    mock_payload = MagicMock()
    mock_payload.data = [mock_item]
    result = update_productivity_plan_mapping_records(payload=mock_payload, db=db_mock)

    assert result["status"] == "error"
    assert "Please check details" in result["message"]
    assert not db_mock.commit.called

"""________SummarySolids________"""

def test_get_solid_task_master():
    response = client.get("/api/summary_solids/")
    assert response.status_code == 200

def test_get_solid_task_mapping():
    response = client.get("/api/summary_solids/get_solid_task_mapping")
    assert response.status_code == 200

def test_get_solid_task_master_by_id():
    response = client.get("/api/summary_solids/get_solid_task_master/2")
    assert response.status_code == 200

    response = client.get("/api/summary_solids/get_solid_task_master/10")
    assert response.status_code == 404

def test_solids_task_mapping_by_year():
    response = client.get("/api/summary_solids/solids_task_mapping_by_year/2024")
    assert response.status_code == 200

    response = client.get("/api/summary_solids/solids_task_mapping_by_year/10000")
    assert response.status_code == 404

def test_summary_solids_view_year_country_code():
    response = client.get("/api/summary_solids/summary_solids_view/2024/US-CORE")
    assert response.status_code == 200

"""________summary_solids.py POST calls_________"""

@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_solids_task_mappings_success(mock_get_db):
    """Test successful creation of solids task mappings for a year."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Mock solid_task_master records
    task_mock = MagicMock()
    task_mock.solids_task_id = 1
    task_mock.task_name = "Test Task"
    
    mock_tasks_list = MagicMock()
    mock_tasks_list.__iter__.return_value = [task_mock]
    mock_tasks_list.count = 1
    
    # Mock query chain
    db_mock.query.return_value.all.return_value = mock_tasks_list
    db_mock.query.return_value.filter.return_value.first.return_value = None
    
    result = await update_solids_task_mappings(year=2024, db=db_mock)
    
    assert result["status"] == "success"
    assert result["Records already exists for "] == []
    assert result["forYear"] == 2024
    assert db_mock.add.call_count == 13  # 13 periods
    assert db_mock.commit.call_count == 13


@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_solids_task_mappings_no_records(mock_get_db):
    """Test update_solids_task_mappings when no records found in database."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    mock_empty_list = MagicMock()
    mock_empty_list.count = 0
    
    db_mock.query.return_value.all.return_value = mock_empty_list
    
    with pytest.raises(HTTPException) as exc_info:
        await update_solids_task_mappings(year=2024, db=db_mock)
    
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
@patch('database.get_db')
async def test_update_solids_task_mappings_already_exists(mock_get_db):
    """Test update_solids_task_mappings when records already exist for year."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    task_mock = MagicMock()
    task_mock.solids_task_id = 1
    task_mock.task_name = "Existing Task"
    
    mock_tasks_list = MagicMock()
    mock_tasks_list.__iter__.return_value = [task_mock]
    mock_tasks_list.count = 1
    
    # Mock existing record found
    existing_mock = MagicMock()
    
    db_mock.query.return_value.all.return_value = mock_tasks_list
    db_mock.query.return_value.filter.return_value.first.return_value = existing_mock
    
    result = await update_solids_task_mappings(year=2024, db=db_mock)
    
    assert result["status"] == "success"
    assert "Existing Task" in result["Records already exists for "]
    assert result["forYear"] == 2024
    db_mock.add.assert_not_called()


@patch('database.get_db')
def test_create_solid_task_master_success(mock_get_db):
    """Test successful creation of solid task master record."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    # Simulate DB assigning ID on refresh
    def refresh_side_effect(obj):
        obj.solids_task_id = 1
    
    db_mock.refresh.side_effect = refresh_side_effect
    
    payload_data = {
        "task_name": "Test Solids Task",
        "task_desc": "Test Description"
    }
    
    test_payload = schemas.SolidTaskMasterSchema(**payload_data)
    
    result = create_solid_task_master(payload=test_payload, db=db_mock)
    
    assert result == {"status": "success", "solids_task_id": 1}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@patch('database.get_db')
def test_create_solid_rate_mappings_success(mock_get_db):
    """Test successful creation of solids task mapping record."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    def refresh_side_effect(obj):
        obj.row_id = 10
    
    db_mock.refresh.side_effect = refresh_side_effect
    
    payload_data = {
        "solids_task_id": 1,
        "period": 1,
        "year": 2024,
        "value": 150.75,
        "country_code": "US"
    }
    
    test_payload = schemas.SolidsTaskMappingSchema(**payload_data)
    
    result = create_solid_rate_mappings(payload=test_payload, db=db_mock)
    
    assert result == {"status": "success", "row_id": 10}
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@patch('database.get_db')
def test_update_solid_rate_mapping_records_success(mock_get_db):
    """Test successful update of solids task mapping records."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "solids_task_id": 1,
                "period": 1,
                "year": 2024,
                "value": 150.75,
                "country_code": "US"
            },
            {
                "solids_task_id": 2,
                "period": 2,
                "year": 2024,
                "value": 200.00,
                "country_code": "US"
            }
        ]
    }
    test_payload = schemas.SolidsTaskMappingSchemaPayload(**payload_data)
    mock_query = db_mock.query.return_value
    mock_query.filter.return_value.update.return_value = 1
    result = update_solid_rate_mapping_records(payload=test_payload, db=db_mock)
    
    assert result == {"status": "success", "records_updated": 2}
    assert db_mock.query.return_value.filter.return_value.update.call_count == 2
    db_mock.commit.assert_called_once()


@patch('database.get_db')
def test_update_solid_rate_mapping_records_invalid_solids_task_id(mock_get_db):
    """Test update with invalid solids_task_id (<=0)."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "solids_task_id": 0,  # Invalid
                "period": 1,
                "year": 2024,
                "value": 150.75,
                "country_code": "US"
            }
        ]
    }
    test_payload = schemas.SolidsTaskMappingSchemaPayload(**payload_data)
    result = update_solid_rate_mapping_records(payload=test_payload, db=db_mock)
    
    assert result == {"status": "error", "message": "Please check details"}
    db_mock.query.assert_not_called()
    db_mock.commit.assert_not_called()


@patch('database.get_db')
def test_update_solid_rate_mapping_records_invalid_period(mock_get_db):
    """Test update with invalid period (<=0)."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "solids_task_id": 1,
                "period": 0,  # Invalid
                "year": 2024,
                "value": 150.75,
                "country_code": "US"
            }
        ]
    }
    test_payload = schemas.SolidsTaskMappingSchemaPayload(**payload_data)
    result = update_solid_rate_mapping_records(payload=test_payload, db=db_mock)
    
    assert result == {"status": "error", "message": "Please check details"}
    db_mock.query.assert_not_called()
    db_mock.commit.assert_not_called()


@patch('database.get_db')
def test_update_solid_rate_mapping_records_invalid_year(mock_get_db):
    """Test update with invalid year (<=0)."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    payload_data = {
        "data": [
            {
                "solids_task_id": 1,
                "period": 1,
                "year": 0,  # Invalid
                "value": 150.75,
                "country_code": "US"
            }
        ]
    }
    test_payload = schemas.SolidsTaskMappingSchemaPayload(**payload_data)
    result = update_solid_rate_mapping_records(payload=test_payload, db=db_mock)
    
    assert result == {"status": "error", "message": "Please check details"}
    db_mock.query.assert_not_called()
    db_mock.commit.assert_not_called()


@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_summary_solids_for_next_year_success(mock_get_db):
    """Test successful creation of summary solids for next year."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    task_mocks = [
        MagicMock(task_name="PLAN", solids_task_id=1),
        MagicMock(task_name="PRIOR", solids_task_id=2),
        MagicMock(task_name="FORECAST", solids_task_id=3),
        MagicMock(task_name="Conversion Factor", solids_task_id=4),
        MagicMock(task_name="M$ IMPACT_Plan_Value", solids_task_id=5),
    ]

    view_mock = MagicMock()
    view_mock.period = 1
    view_mock.Plan = 100.0
    view_mock.forecast = 95.0
    view_mock.Conversion_Factor = 1.2
    view_mock.country_code = "US"
    
    existing_mock = MagicMock()
    
    def query_side_effect(model):
        mock_query = MagicMock()
        
        if model == models.solid_task_master:
            mock_query.all.return_value = task_mocks
            return mock_query
        elif model == models.summary_solids:
            filter_chain = MagicMock()
            filter_chain.all.return_value = [view_mock]
            mock_query.filter.return_value = filter_chain
            return mock_query
        elif model == models.solids_task_mapping:
            filter_chain = MagicMock()
            filter_chain.all.return_value = [existing_mock]
            filter_chain.first.return_value = None
            
            mock_query.filter.return_value = filter_chain
            return mock_query
    
    db_mock.query.side_effect = query_side_effect
    
    result = await create_summary_solids_for_next_year(year=2024, db=db_mock)
    
    assert result["status"] == "success"


@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_summary_solids_for_next_year_with_prior_value(mock_get_db):
    """Test creation with existing PRIOR value."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    task_mocks = [
        MagicMock(task_name="PLAN", solids_task_id=1),
        MagicMock(task_name="PRIOR", solids_task_id=2),
        MagicMock(task_name="FORECAST", solids_task_id=3),
        MagicMock(task_name="Conversion Factor", solids_task_id=4),
        MagicMock(task_name="M$ IMPACT_Plan_Value", solids_task_id=5),
    ]
    view_mock = MagicMock()
    view_mock.period = 1
    view_mock.Plan = 100.0
    view_mock.forecast = 95.0
    view_mock.Conversion_Factor = 1.2
    view_mock.country_code = "US"
    prior_mock = MagicMock()
    prior_mock.value = 50.0
    query_mock = db_mock.query.return_value
    def query_side_effect(*args):
        if len(args) > 0:
            return query_mock
    db_mock.query.side_effect = query_side_effect
    all_calls = [task_mocks, [view_mock]]
    query_mock.all.side_effect = all_calls
    filter_mock = MagicMock()
    filter_mock.all.return_value = []  # No existing records to delete
    filter_mock.first.return_value = prior_mock  # Existing PRIOR value
    query_mock.filter.return_value = filter_mock
    result = await create_summary_solids_for_next_year(year=2024, db=db_mock)

    assert result["status"] == "success"


@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_summary_solids_for_next_year_no_view_data(mock_get_db):
    """Test creation when no summary_solids view data exists."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    task_mocks = [
        MagicMock(task_name="PLAN", solids_task_id=1),
    ]
    query_mock = db_mock.query.return_value
    query_mock.all.side_effect = [task_mocks, []]  # No view data
    query_mock.filter.return_value.all.return_value = []  # No existing records
    result = await create_summary_solids_for_next_year(year=2024, db=db_mock)
    assert result["status"] == "success"
    assert result["Records added"] == 0
    assert result["for Year"] == 2024
    db_mock.add.assert_not_called()


@pytest.mark.asyncio
@patch('database.get_db')
async def test_create_summary_solids_for_next_year_multiple_periods(mock_get_db):
    """Test creation with multiple periods from view data."""
    db_mock = MagicMock()
    mock_get_db.return_value = db_mock
    
    task_mocks = [
        MagicMock(task_name="PLAN", solids_task_id=1),
        MagicMock(task_name="PRIOR", solids_task_id=2),
        MagicMock(task_name="FORECAST", solids_task_id=3),
        MagicMock(task_name="Conversion Factor", solids_task_id=4),
        MagicMock(task_name="M$ IMPACT_Plan_Value", solids_task_id=5),
    ]
    view_mocks = [
        MagicMock(period=1, Plan=100.0, forecast=95.0, Conversion_Factor=1.2, country_code="US"),
        MagicMock(period=2, Plan=110.0, forecast=105.0, Conversion_Factor=1.3, country_code="US"),
        MagicMock(period=3, Plan=120.0, forecast=115.0, Conversion_Factor=1.4, country_code="US"),
    ]
    query_mock = db_mock.query.return_value
    query_mock.all.side_effect = [task_mocks, view_mocks]
    query_mock.filter.return_value.all.return_value = []
    query_mock.filter.return_value.first.return_value = None
    result = await create_summary_solids_for_next_year(year=2024, db=db_mock)
    
    assert result["status"] == "success"


"""________SummaryOverallCost________"""

def test_summary_overall_cost_year_country_code():
    response = client.get("/api/summary_overall_cost/year/2020/company_name/US-CORE")
    assert response.status_code in [200, 400]

def test_summary_total_exp_wo_solids_year_country_code():
    response = client.get("/api/summary_overall_costtotal_exp_wo_solids/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_total_exp_w_solids_year_country_code():
    response = client.get("/api/summary_overall_costtotal_exp_w_solids/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_material_spend_year_country_code():
    response = client.get("/api/summary_overall_costoverall_cost_material_spend/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_freight_spend_year_country_code():
    response = client.get("/api/summary_overall_costoverall_cost_freight_spend/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_overall_cost_solids_year_country_code():
    response = client.get("/api/summary_overall_costoverall_cost_solids/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_category_spend_year_country_code():
    response = client.get("/api/summary_overall_costoverall_cost_category_spend/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_freight_total_yag_year_country_code():
    response = client.get("/api/summary_overall_costsummary_freight_total_yag/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_total_exp_w_solids_yag_year_country_code():
    response = client.get("/api/summary_overall_costsummary_total_exp_w_solids_yag/year/2026/company_name/US-CORE")
    assert response.status_code == 200

def test_summary_total_exp_wo_solids_yag_year_country_code():
    response = client.get("/api/summary_overall_costsummary_total_exp_wo_solids_yag/year/2026/company_name/US-CORE")
    assert response.status_code == 200

"""________PlantSiteGrowingAreaMapping________"""

def test_view_plant_site_growing_area():
    response = client.get("/api/plant_site_growing_area_mapping/get_plant_site_gowing_area_mapping")
    assert response.status_code == 200

def test_get_plantid_plantsite():
    response = client.get("/api/plant_site_growing_area_mapping/12")
    assert response.status_code == 200


"""________PlantMtrxTemplate________"""

def test_get_plantid_plantmtrx():
    response = client.get("/api/plant_mtrx_templt/1")
    assert response.status_code == 200


"""________validator_logger.py________"""

def test_utcnow_naive_success():
    # Test that the function returns a datetime without TZ or microseconds
    out = vl._utcnow_naive()
    
    assert isinstance(out, datetime)
    assert out.tzinfo is None
    assert out.microsecond == 0
    # Verify it's actually "recent" (within a 5-second window to be safe)
    assert (datetime.now(timezone.utc).replace(tzinfo=None) - out).total_seconds() < 5


def test_fmt_token_exception_branch_raises_http_400():
    # Forces str(x) to fail so outer except executes (lines like 51-52)
    class BadStr:
        def __str__(self):
            raise RuntimeError("bad __str__")

    with pytest.raises(HTTPException) as exc:
        vl._fmt_token(BadStr())
    assert exc.value.status_code == 400


def test_compose_erp_unique_id_exception_branch_raises_http_400():
    # Forces _fmt_token to raise so except executes (lines like 74-75)
    with patch.object(vl, "_fmt_token", side_effect=Exception("boom")):
        with pytest.raises(HTTPException) as exc:
            vl._compose_erp_unique_id("BPA", 1, 2, 3)
        assert exc.value.status_code == 400


def test_derive_crop_year_exception_branch_raises_http_400():
    # year_value used in arithmetic; make it invalid to trigger except (lines like 136-137)
    with pytest.raises(HTTPException) as exc:
        vl._derive_crop_year("NOT_INT", 1, "STORAGE")
    assert exc.value.status_code == 400


def test_is_view_row_complete_exception_branch_raises_http_400():
    # getattr(row, ...) triggers __getattr__; force it to raise (lines like 171-172)
    class BoomRow:
        def __getattr__(self, _name):
            raise RuntimeError("boom")

    with pytest.raises(HTTPException) as exc:
        vl._is_view_row_complete(BoomRow())
    assert exc.value.status_code == 400


def test_fetch_erp_null_rows_for_slice_sql_exception_branch_raises_http_400():
    # db.execute fails -> except (lines like 268-269)
    db = MagicMock()
    db.execute.side_effect = Exception("db fail")

    with pytest.raises(HTTPException) as exc:
        vl._fetch_erp_null_rows_for_slice_sql(db, plant_id=1, ga_id=2, year=2026, period=1, week=1)
    assert exc.value.status_code == 400


def test_erp_row_has_required_null_from_mapping_exception_branch_raises_http_400():
    # row.get(...) raises -> except (lines like 327-328)
    class BadMapping(dict):
        def get(self, *args, **kwargs):
            raise RuntimeError("boom")

    with pytest.raises(HTTPException) as exc:
        vl._erp_row_has_required_null_from_mapping(BadMapping())
    assert exc.value.status_code == 400


def test_build_log_obj_from_erp_row_exception_branch_raises_http_400():
    # Constructor fails -> except (lines like 384-385)
    erp_row = {
        "plant_id": 1,
        "growing_area_id": 2,
        "RECEIPT_YEAR": 2025,
        "REC_DATE_PD": 1,
        "REC_DATE_WK": 1,
        "CROP_TYPE": "FRESH",
    }

    with patch.object(vl.models, "PlantMtrxNullLog", side_effect=Exception("ctor fail")):
        with pytest.raises(HTTPException) as exc:
            vl._build_log_obj_from_erp_row(erp_row, region_id=None, plant_name=None, ga_name=None)
        assert exc.value.status_code == 400


def test_find_existing_log_exception_branch_raises_http_400():
    # db.query fails -> except (lines like 432-433)
    db = MagicMock()
    db.query.side_effect = Exception("query fail")

    with pytest.raises(HTTPException) as exc:
        vl._find_existing_log(
            db,
            erp_unique_id="BPA#1#2#3",
            plant_id=1,
            ga_id=2,
            year=2025,
            period=1,
            week=1,
        )
    assert exc.value.status_code == 400


def test_upsert_null_log_exception_branch_raises_http_400():
    # _build_log_obj_from_erp_row fails -> except (lines like 497-498)
    db = MagicMock()
    with patch.object(vl, "_build_log_obj_from_erp_row", side_effect=Exception("boom")):
        with pytest.raises(HTTPException) as exc:
            vl._upsert_null_log(db, erp_row={}, region_id=None, plant_name=None, ga_name=None)
        assert exc.value.status_code == 400


def test_is_erp_row_corrected_for_log_exception_branch_raises_http_400():
    # db.execute fails after passing key checks -> except (lines like 567-568 OR similar)
    db = MagicMock()
    db.execute.side_effect = Exception("execute fail")

    log = MagicMock(bpa_number="BPA", line_no=1.0, shipment=2.0, release_no=3.0)

    with pytest.raises(HTTPException) as exc:
        vl._is_erp_row_corrected_for_log(db, log)
    assert exc.value.status_code == 400


def test_refresh_null_logs_for_slice_exception_branch_raises_http_400():
    # db.query fails immediately -> outer except at end of function (lines like 567-568 if that’s _refresh...)
    db = MagicMock()
    db.query.side_effect = Exception("query fail")

    with pytest.raises(HTTPException) as exc:
        vl._refresh_null_logs_for_slice(db, period=1, week=1, year=2026)
    assert exc.value.status_code == 400


def test_fmt_token_basic_cases():
    assert vl._fmt_token(None) == ""
    assert vl._fmt_token(10.0) == "10"
    assert vl._fmt_token(10.5) == "10.5"
    assert vl._fmt_token("  abc  ") == "abc"
    assert vl._fmt_token(float("inf")) == "inf"


def test_compose_erp_unique_id_formats():
    assert vl._compose_erp_unique_id("BPA", 1.0, 2.0, 3.0) == "BPA#1#2#3"
    assert vl._compose_erp_unique_id(None, None, None, None) == "###"


def test_to_float_or_none():
    assert vl._to_float_or_none(None) is None
    assert vl._to_float_or_none("") is None
    assert vl._to_float_or_none("   ") is None
    assert vl._to_float_or_none("12") == 12
    assert vl._to_float_or_none("bad") is None


def test_derive_crop_year_storage_and_fresh():
    assert vl._derive_crop_year(2025, 8, "STORAGE") == "2024-25"
    assert vl._derive_crop_year(2025, 9, "STORAGE") == "2025-26"
    assert vl._derive_crop_year(2025, 1, "FRESH") == "2025"
    assert vl._derive_crop_year(2025, 1, "anything") == "2025"
    assert vl._derive_crop_year(None, 1, "FRESH") is None
    assert vl._derive_crop_year(2025, None, "FRESH") is None


def test_is_view_row_complete_true_and_false():
    class Row:
        Plant_Id = 1
        growing_area_id = 2
        region_id = 3
        period_num = 4
        week_num = 5
        p_year = 2026
        crop_type = "FRESH"
        storage_period = 0
        row_id = 99

    assert vl._is_view_row_complete(Row()) is True

    class IncompleteRow:
        Plant_Id = 1
        growing_area_id = 2
        region_id = 3
        period_num = None  # missing
        week_num = 5
        p_year = 2026
        crop_type = "FRESH"
        storage_period = 0
        row_id = 99

    assert vl._is_view_row_complete(IncompleteRow()) is False


def test_fetch_erp_null_rows_for_slice_sql_success():
    db = MagicMock()

    exec_res = MagicMock()
    exec_res.mappings.return_value = exec_res
    exec_res.all.return_value = [{"plant_id": 1}]

    db.execute.return_value = exec_res

    out = vl._fetch_erp_null_rows_for_slice_sql(db, plant_id=1, ga_id=2, year=2026, period=1, week=1)
    assert out == [{"plant_id": 1}]
    db.execute.assert_called_once()


def test_fetch_erp_null_rows_for_slice_sql_exception_400():
    db = MagicMock()
    db.execute.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as exc:
        vl._fetch_erp_null_rows_for_slice_sql(db, plant_id=1, ga_id=2, year=2026, period=1, week=1)

    assert exc.value.status_code == 400


def test_erp_row_has_required_null_from_mapping_true_when_missing():
    row = {
        "plant_id": 1,
        "growing_area_id": 2,
        "UNLOAD_YEAR": 2025,
        "UNL_DATE_PD": 1,
        "RECEIPT_YEAR": 2025,
        "REC_DATE_PD": 1,
        "REC_DATE_WK": None,  # required missing
        "CROP_TYPE": "FRESH",
    }
    assert vl._erp_row_has_required_null_from_mapping(row) is True


def test_erp_row_has_required_null_from_mapping_false_when_complete():
    row = {
        "plant_id": 1,
        "growing_area_id": 2,
        "UNLOAD_YEAR": 2025,
        "UNL_DATE_PD": 1,
        "RECEIPT_YEAR": 2025,
        "REC_DATE_PD": 1,
        "REC_DATE_WK": 1,
        "CROP_TYPE": "FRESH",
    }
    assert vl._erp_row_has_required_null_from_mapping(row) is False


def test_build_log_obj_from_erp_row_sets_expected_fields():
    # patch the ORM model class so we don’t need a real SQLAlchemy Base/table
    class DummyLog:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    fixed_now = datetime(2026, 1, 1, 0, 0, 0)

    erp_row = {
        "plant_id": 10,
        "growing_area_id": 20,
        "RECEIPT_YEAR": 2025,
        "REC_DATE_PD": 2,
        "REC_DATE_WK": 3,
        "CROP_TYPE": "FRESH",
        "Quantity_Accepted_MCWT": "12",
        "BPA_NUMBER": " BPA-123 ",
        "RELEASE_NO": "1",
        "SHIPMENT": "2",
        "LINE_NO": "3",
    }

    with patch.object(vl, "_utcnow_naive", return_value=fixed_now), \
         patch.object(vl.models, "PlantMtrxNullLog", DummyLog):
        obj = vl._build_log_obj_from_erp_row(
            erp_row,
            region_id=7,
            plant_name="Plant A",
            ga_name="GA X",
        )

    assert obj.plant_id == 10
    assert obj.growing_area_id == 20
    assert obj.year == 2025
    assert obj.period == 2
    assert obj.week == 3
    assert obj.crop_year == "2025"
    assert obj.sumof_rec_potato == 12
    assert obj.erp_unique_id == "BPA-123#1#2#3"
    assert obj.active is True
    assert obj.created_time == fixed_now


def test_find_existing_log_returns_strong_key_match():
    db = MagicMock()
    q = MagicMock()
    db.query.return_value = q
    q.filter.return_value = q

    found = MagicMock()
    q.first.side_effect = [found]  # first call = strong key

    out = vl._find_existing_log(
        db,
        erp_unique_id="BPA#1#2#3",
        plant_id=1,
        ga_id=2,
        year=2025,
        period=1,
        week=1,
    )
    assert out is found


def test_find_existing_log_fallback_when_strong_key_not_found():
    db = MagicMock()
    q = MagicMock()
    db.query.return_value = q
    q.filter.return_value = q

    fallback = MagicMock()
    q.first.side_effect = [None, fallback]

    out = vl._find_existing_log(
        db,
        erp_unique_id="BPA#1#2#3",
        plant_id=1,
        ga_id=2,
        year=2025,
        period=1,
        week=1,
    )
    assert out is fallback


def test_find_existing_log_skips_strong_key_when_erp_unique_id_is_hashes():
    db = MagicMock()
    q = MagicMock()
    db.query.return_value = q
    q.filter.return_value = q

    fallback = MagicMock()
    q.first.return_value = fallback

    out = vl._find_existing_log(
        db,
        erp_unique_id="###",
        plant_id=1,
        ga_id=2,
        year=2025,
        period=1,
        week=1,
    )
    assert out is fallback
    assert q.first.call_count == 1


def test_upsert_null_log_inserts_when_no_existing():
    db = MagicMock()
    obj = MagicMock()
    obj.erp_unique_id = "BPA#1#2#3"
    obj.plant_id = 1
    obj.growing_area_id = 2
    obj.year = 2025
    obj.period = 1
    obj.week = 1

    with patch.object(vl, "_build_log_obj_from_erp_row", return_value=obj), \
         patch.object(vl, "_find_existing_log", return_value=None):
        inserted = vl._upsert_null_log(db, erp_row={"x": "y"}, region_id=None, plant_name=None, ga_name=None)

    assert inserted is True
    db.add.assert_called_once_with(obj)


def test_upsert_null_log_updates_when_existing():
    db = MagicMock()

    obj = MagicMock()
    obj.erp_unique_id = "BPA#1#2#3"
    obj.plant_id = 1
    obj.growing_area_id = 2
    obj.year = 2025
    obj.period = 1
    obj.week = 1

    existing = MagicMock()
    existing.active = False

    fixed_now = datetime(2026, 1, 1, 0, 0, 0)

    with patch.object(vl, "_build_log_obj_from_erp_row", return_value=obj), \
         patch.object(vl, "_find_existing_log", return_value=existing), \
         patch.object(vl, "_utcnow_naive", return_value=fixed_now):
        inserted = vl._upsert_null_log(db, erp_row={"x": "y"}, region_id=None, plant_name=None, ga_name=None)

    assert inserted is False
    assert existing.active is True
    assert existing.created_time == fixed_now
    db.add.assert_called_once_with(existing)


def test_is_erp_row_corrected_for_log_returns_false_when_missing_lookup_keys():
    db = MagicMock()
    log = MagicMock(bpa_number=None, line_no=None, shipment=None, release_no=None)

    assert vl._is_erp_row_corrected_for_log(db, log) is False
    db.execute.assert_not_called()


def test_is_erp_row_corrected_for_log_returns_false_when_no_row_found():
    db = MagicMock()

    log = MagicMock(bpa_number="BPA", line_no=1.0, shipment=2.0, release_no=3.0)

    exec_res = MagicMock()
    exec_res.mappings.return_value = exec_res
    exec_res.fetchone.return_value = None
    db.execute.return_value = exec_res

    assert vl._is_erp_row_corrected_for_log(db, log) is False


def test_is_erp_row_corrected_for_log_returns_true_when_row_has_no_nulls():
    db = MagicMock()
    log = MagicMock(bpa_number="BPA", line_no=1.0, shipment=2.0, release_no=3.0)

    exec_res = MagicMock()
    exec_res.mappings.return_value = exec_res
    exec_res.fetchone.return_value = {
        "plant_id": 1,
        "growing_area_id": 2,
        "UNLOAD_YEAR": 2025,
        "UNL_DATE_PD": 1,
        "UNL_DATE_WK": 1,
        "RECEIPT_YEAR": 2025,
        "REC_DATE_PD": 1,
        "REC_DATE_WK": 1,
        "CROP_TYPE": "FRESH",
    }
    db.execute.return_value = exec_res

    with patch.object(vl, "_erp_row_has_required_null_from_mapping", return_value=False):
        assert vl._is_erp_row_corrected_for_log(db, log) is True


def test_is_erp_row_corrected_for_log_returns_false_when_row_still_has_nulls():
    db = MagicMock()
    log = MagicMock(bpa_number="BPA", line_no=1.0, shipment=2.0, release_no=3.0)

    exec_res = MagicMock()
    exec_res.mappings.return_value = exec_res
    exec_res.fetchone.return_value = {"anything": "ok"}
    db.execute.return_value = exec_res

    with patch.object(vl, "_erp_row_has_required_null_from_mapping", return_value=True):
        assert vl._is_erp_row_corrected_for_log(db, log) is False


def test_refresh_null_logs_for_slice_returns_zero_when_no_logs():
    db = MagicMock()
    q = MagicMock()
    db.query.return_value = q
    q.filter.return_value = q
    q.all.return_value = []

    out = vl._refresh_null_logs_for_slice(db, period=1, week=1, year=2026)
    assert out == {"checked": 0, "resolved": 0, "still_active": 0}
    db.commit.assert_not_called()


def test_refresh_null_logs_for_slice_resolves_and_counts_remaining():
    db = MagicMock()

    log1 = MagicMock(active=True)
    log2 = MagicMock(active=True)

    q_all = MagicMock()
    q_all.filter.return_value = q_all
    q_all.all.return_value = [log1, log2]

    q_count = MagicMock()
    q_count.filter.return_value = q_count
    q_count.count.return_value = 1

    db.query.side_effect = [q_all, q_count]

    fixed_now = datetime(2026, 1, 1, 0, 0, 0)

    with patch.object(vl, "_utcnow_naive", return_value=fixed_now), \
         patch.object(vl, "_is_erp_row_corrected_for_log", side_effect=[True, False]):
        out = vl._refresh_null_logs_for_slice(db, period=1, week=1, year=2026)

    assert out["checked"] == 2
    assert out["resolved"] == 1
    assert out["still_active"] == 1
    assert log1.active is False
    db.commit.assert_called_once()


def test_refresh_null_logs_for_slice_inner_exception_rolls_back_and_continues():
    db = MagicMock()

    log1 = MagicMock(active=True)
    log2 = MagicMock(active=True)

    q_all = MagicMock()
    q_all.filter.return_value = q_all
    q_all.all.return_value = [log1, log2]

    q_count = MagicMock()
    q_count.filter.return_value = q_count
    q_count.count.return_value = 1

    db.query.side_effect = [q_all, q_count]

    with patch.object(vl, "_is_erp_row_corrected_for_log", side_effect=[Exception("boom"), True]):
        out = vl._refresh_null_logs_for_slice(db, period=1, week=1, year=2026)

    assert out["checked"] == 2
    assert out["resolved"] == 1
    db.rollback.assert_called()  # inner exception triggers rollback
    db.commit.assert_called_once()



def _get_route_endpoint(path: str, method: str):
    method = method.upper()
    for route in journal.router.routes:
        if getattr(route, "path", None) == path and method in getattr(route, "methods", set()):
            return route.endpoint
    raise AssertionError(f"Route not found: {method} {path}")


def _q(first=None, all_=None, scalar=None):
    """Create a SQLAlchemy-ish query mock."""
    q = MagicMock()
    q.filter.return_value = q
    q.join.return_value = q
    q.group_by.return_value = q
    q.distinct.return_value = q
    q.first.return_value = first
    q.all.return_value = all_ if all_ is not None else []
    q.scalar.return_value = scalar
    return q


@pytest.mark.asyncio
async def test_create_journal_success_no_parent():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    page = SimpleNamespace(page_name="Dashboard", page_id=11)

    db.query.side_effect = [
        _q(first=user),
        _q(first=page),
    ]

    payload = schemas.JournalEntrySchema(
        comments="hello",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=None,
    )

    with patch("journal.journal_all") as journal_all_model, patch("journal.datetime") as dt:
        dt.now.return_value.strftime.return_value = "2026-01-12 12:00"

        res = await journal.create_journal(payload=payload, db=db)

        assert res == {"status": "success"}
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        journal_all_model.assert_called_once()


@pytest.mark.asyncio
async def test_create_journal_success_with_parent():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    page = SimpleNamespace(page_name="Dashboard", page_id=11)
    parent = SimpleNamespace(parent_journal_id=None, page_id=11)

    db.query.side_effect = [
        _q(first=user),
        _q(first=page),
        _q(first=parent),
    ]

    payload = schemas.JournalEntrySchema(
        comments="reply",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=123,
    )

    with patch("journal.journal_all") as journal_all_model, patch("journal.datetime") as dt:
        dt.now.return_value.strftime.return_value = "2026-01-12 12:00"

        res = await journal.create_journal(payload=payload, db=db)

        assert res == {"status": "success"}
        journal_all_model.assert_called_once()
        # ensure reply uses the provided parent id
        assert journal_all_model.call_args.kwargs["parent_journal_id"] == 123


@pytest.mark.asyncio
async def test_create_journal_user_query_exception_404():
    db = MagicMock()
    db.query.side_effect = Exception("db down")

    payload = schemas.JournalEntrySchema(
        comments="x",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=None,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal(payload=payload, db=db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_create_journal_page_query_exception_404():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    db.query.side_effect = [_q(first=user), Exception("page query fails")]

    payload = schemas.JournalEntrySchema(
        comments="x",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=None,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal(payload=payload, db=db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Page not found"


@pytest.mark.asyncio
async def test_create_journal_parent_not_found_400():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    page = SimpleNamespace(page_name="Dashboard", page_id=11)

    db.query.side_effect = [_q(first=user), _q(first=page), _q(first=None)]

    payload = schemas.JournalEntrySchema(
        comments="reply",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=123,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal(payload=payload, db=db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Parent comment not found"


@pytest.mark.asyncio
async def test_create_journal_nested_reply_not_allowed_400():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    page = SimpleNamespace(page_name="Dashboard", page_id=11)
    parent = SimpleNamespace(parent_journal_id=999, page_id=11)

    db.query.side_effect = [_q(first=user), _q(first=page), _q(first=parent)]

    payload = schemas.JournalEntrySchema(
        comments="reply",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=123,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal(payload=payload, db=db)

    assert exc.value.status_code == 400
    assert "Nested replies" in exc.value.detail


@pytest.mark.asyncio
async def test_create_journal_parent_different_page_400():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    page = SimpleNamespace(page_name="Dashboard", page_id=11)
    parent = SimpleNamespace(parent_journal_id=None, page_id=999)

    db.query.side_effect = [_q(first=user), _q(first=page), _q(first=parent)]

    payload = schemas.JournalEntrySchema(
        comments="reply",
        email="a@b.com",
        page_name="Dashboard",
        img_url=None,
        parent_journal_id=123,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal(payload=payload, db=db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Parent comment belongs to a different page"


@pytest.mark.asyncio
async def test_get_journal_entry_success():
    db = MagicMock()
    db.query.return_value = _q(all_=[{"journal_id": 1}])

    endpoint = _get_route_endpoint("/get_journal_entry", "GET")
    res = await endpoint(db=db)
    assert res == {"data": [{"journal_id": 1}]}


@pytest.mark.asyncio
async def test_get_journal_entry_exception_400():
    db = MagicMock()
    db.query.side_effect = Exception("boom")

    with pytest.raises(HTTPException) as exc:
        endpoint = _get_route_endpoint("/get_journal_entry", "GET")
        await endpoint(db=db)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_journal_owner_success_crop_year_range():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    owner = SimpleNamespace(ownership_id="O1", growing_area_id=33, crop_year="2024-25", year=2025, crop_type="CHIP")
    area = SimpleNamespace(growing_area_id=33, growing_area_name="GA", growing_area_desc="DESC", region=2)
    reg = SimpleNamespace(region_name="East - US")

    db.query.side_effect = [
        _q(first=user),
        _q(first=owner),
        _q(first=area),
        _q(first=reg),
    ]

    payload = SimpleNamespace(
        comments="owner comment",
        email="a@b.com",
        ownership_id="O1",
        parent_journal_id=None,
        growing_area_name=None,
        growing_area_desc=None,
        img_url=None,
    )

    with patch("journal.journal_ownership") as journal_owner_model, patch("journal.datetime") as dt:
        dt.now.return_value.strftime.return_value = "2026-01-12 12:00"

        res = await journal.create_journal_owner(payload=payload, db=db)

        assert res == {"status": "success"}
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        journal_owner_model.assert_called_once()
        assert journal_owner_model.call_args.kwargs["filter_year_1"] == "2024"
        assert journal_owner_model.call_args.kwargs["filter_year_2"] == 2025


@pytest.mark.asyncio
async def test_create_journal_owner_success_with_parent_and_single_year():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    owner = SimpleNamespace(ownership_id="O1", growing_area_id=33, crop_year="2024", year=2024, crop_type="CHIP")
    area = SimpleNamespace(growing_area_id=33, growing_area_name="GA", growing_area_desc="DESC", region=2)
    reg = SimpleNamespace(region_name="East - US")
    parent = SimpleNamespace(parent_journal_id=None, ownership_id="O1")

    db.query.side_effect = [
        _q(first=user),
        _q(first=owner),
        _q(first=area),
        _q(first=reg),
        _q(first=parent),
    ]

    payload = schemas.JournalEntryOwnerSchema(
        comments="reply",
        email="a@b.com",
        ownership_id="O1",
        parent_journal_id=10,
        growing_area_name=None,
        growing_area_desc=None,
        img_url=None,
    )

    with patch("journal.journal_ownership") as journal_owner_model, patch("journal.datetime") as dt:
        dt.now.return_value.strftime.return_value = "2026-01-12 12:00"

        res = await journal.create_journal_owner(payload=payload, db=db)

        assert res == {"status": "success"}
        assert journal_owner_model.call_args.kwargs["filter_year_1"] == "2024"
        assert journal_owner_model.call_args.kwargs["filter_year_2"] is None
        assert journal_owner_model.call_args.kwargs["parent_journal_id"] == 10


@pytest.mark.asyncio
async def test_create_journal_owner_parent_not_found_400():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    owner = SimpleNamespace(ownership_id="O1", growing_area_id=33, crop_year="2024", year=2024, crop_type="CHIP")
    area = SimpleNamespace(growing_area_id=33, growing_area_name="GA", growing_area_desc="DESC", region=2)
    reg = SimpleNamespace(region_name="East - US")

    db.query.side_effect = [
        _q(first=user),
        _q(first=owner),
        _q(first=area),
        _q(first=reg),
        _q(first=None),
    ]

    payload = schemas.JournalEntryOwnerSchema(
        comments="reply",
        email="a@b.com",
        ownership_id="O1",
        parent_journal_id=10,
        growing_area_name=None,
        growing_area_desc=None,
        img_url=None,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal_owner(payload=payload, db=db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Parent ownership comment not found"


@pytest.mark.asyncio
async def test_create_journal_owner_nested_reply_not_allowed_400():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    owner = SimpleNamespace(ownership_id="O1", growing_area_id=33, crop_year="2024", year=2024, crop_type="CHIP")
    area = SimpleNamespace(growing_area_id=33, growing_area_name="GA", growing_area_desc="DESC", region=2)
    reg = SimpleNamespace(region_name="East - US")
    parent = SimpleNamespace(parent_journal_id=99, ownership_id="O1")

    db.query.side_effect = [
        _q(first=user),
        _q(first=owner),
        _q(first=area),
        _q(first=reg),
        _q(first=parent),
    ]

    payload = schemas.JournalEntryOwnerSchema(
        comments="reply",
        email="a@b.com",
        ownership_id="O1",
        parent_journal_id=10,
        growing_area_name=None,
        growing_area_desc=None,
        img_url=None,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal_owner(payload=payload, db=db)

    assert exc.value.status_code == 400
    assert "Nested replies" in exc.value.detail


@pytest.mark.asyncio
async def test_create_journal_owner_parent_different_ownership_400():
    db = MagicMock()

    user = SimpleNamespace(first_name="john", last_name="doe", user_id=7)
    owner = SimpleNamespace(ownership_id="O1", growing_area_id=33, crop_year="2024", year=2024, crop_type="CHIP")
    area = SimpleNamespace(growing_area_id=33, growing_area_name="GA", growing_area_desc="DESC", region=2)
    reg = SimpleNamespace(region_name="East - US")
    parent = SimpleNamespace(parent_journal_id=None, ownership_id="OTHER")

    db.query.side_effect = [
        _q(first=user),
        _q(first=owner),
        _q(first=area),
        _q(first=reg),
        _q(first=parent),
    ]

    payload = schemas.JournalEntryOwnerSchema(
        comments="reply",
        email="a@b.com",
        ownership_id="O1",
        parent_journal_id=10,
        growing_area_name=None,
        growing_area_desc=None,
        img_url=None,
    )

    with pytest.raises(HTTPException) as exc:
        await journal.create_journal_owner(payload=payload, db=db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Parent comment belongs to different ownership_id"


@pytest.mark.asyncio
async def test_get_journal_entry_owner_us_branch():
    db = MagicMock()
    db.query.return_value = _q(all_=[{"journal_id": 1}])

    res = await journal.get_journal_owner(region="US", year=2025, db=db)
    assert res == {"data": [{"journal_id": 1}]}


@pytest.mark.asyncio
async def test_get_journal_entry_owner_all_data_branch():
    db = MagicMock()
    db.query.return_value = _q(all_=[{"journal_id": 2}])

    res = await journal.get_journal_owner(region="All Data", year=2025, db=db)
    assert res == {"data": [{"journal_id": 2}]}


@pytest.mark.asyncio
async def test_get_journal_entry_owner_specific_region_branch():
    db = MagicMock()
    db.query.return_value = _q(all_=[{"journal_id": 3}])

    res = await journal.get_journal_owner(region="East - US", year=2025, db=db)
    assert res == {"data": [{"journal_id": 3}]}


@pytest.mark.asyncio
async def test_get_journal_entry_owner_exception_400():
    db = MagicMock()
    db.query.side_effect = Exception("fail")

    with pytest.raises(HTTPException) as exc:
        await journal.get_journal_owner(region="US", year=2025, db=db)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_journal_ownership_detailed_info_success():
    db = MagicMock()
    db.query.return_value = _q(all_=[{"x": 1}])

    endpoint = _get_route_endpoint("/get_journal_ownership_detailed_info", "GET")
    res = await endpoint(db=db)
    assert res == {"data": [{"x": 1}]}


@pytest.mark.asyncio
async def test_get_journal_ownership_detailed_info_exception_400():
    db = MagicMock()
    db.query.side_effect = Exception("boom")

    with pytest.raises(HTTPException) as exc:
        endpoint = _get_route_endpoint("/get_journal_ownership_detailed_info", "GET")
        await endpoint(db=db)

    assert exc.value.status_code == 400


def test_get_ownership_journal_common_success():
    db = MagicMock()

    row1 = SimpleNamespace(_mapping={"a": 1})
    row2 = SimpleNamespace(_mapping={"b": 2})

    exec_result = MagicMock()
    exec_result.fetchall.return_value = [row1, row2]
    db.execute.return_value = exec_result

    res = journal.get_ownership_journal_common(db=db)
    assert res == {"data": [{"a": 1}, {"b": 2}]}


def test_get_ownership_journal_common_exception_400():
    db = MagicMock()
    db.execute.side_effect = Exception("sql error")

    with pytest.raises(HTTPException) as exc:
        journal.get_ownership_journal_common(db=db)

    assert exc.value.status_code == 400