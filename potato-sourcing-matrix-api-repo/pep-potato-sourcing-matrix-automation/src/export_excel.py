from fastapi import APIRouter
from database import SessionLocal
from fastapi.responses import StreamingResponse
from datetime import datetime
import pandas as pd
import schemas
import io
from io import BytesIO
import csv
from sqlalchemy import text
from typing import List, Union, Dict
from openpyxl.styles import (Font, PatternFill, Border, Side, Alignment)
from openpyxl.utils import get_column_letter
import zipfile


router = APIRouter()
media_type_str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
var_plant_name = "Plant Name"
var_east_us = "East - US"
var_central_us = "Central - US"
var_west_us = "West - US"
var_canada = "Canada"
var_tp_mcwt = "total-Plan-$/MCWT"
var_tp_total = "total-Plan-Total$"
var_ta_mcwt = "total-Actual-$/MCWT"
var_ta_total = "total-Actual-Total$"
var_gr_area = "G.Area"
var_gr = "Growing Area"

def generate_excel_response(
    data: Union[List[Dict], pd.DataFrame], 
    filename_prefix: str, 
    sheet_name: str = "Sheet1"
) -> StreamingResponse: # pragma: no cover
    """
    Generates a StreamingResponse for downloading an Excel file.
    
    Args:
        data: List of dictionaries or a Pandas DataFrame.
        filename_prefix: The name of the file (without extension or timestamp).
        sheet_name: Optional name for the Excel sheet.
    """
    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    file_name = f"{filename_prefix}_{str_date}.xlsx"

    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        for cell in ws[1]:
            cell.alignment = cell.alignment.copy(wrap_text=True)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type=media_type_str,
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )

def generate_stacked_excel_response(
    top_data: Union[List[Dict], pd.DataFrame],
    bottom_data: Union[List[Dict], pd.DataFrame],
    filename_prefix: str,
    sheet_name: str = "Sheet1",
    gap: int = 2
) -> StreamingResponse:  # pragma: no cover
    """
    Generates an Excel file with two tables, one stacked below the other.
    
    Args:
        top_data: The first dataset (starts at row 0).
        bottom_data: The second dataset (starts after top_data + gap).
        filename_prefix: Name of the file.
        gap: Number of rows to skip between the first and second table (default 2).
    """

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    file_name = f"{filename_prefix}_{str_date}.xlsx"

    df1 = top_data if isinstance(top_data, pd.DataFrame) else pd.DataFrame(top_data)
    df2 = bottom_data if isinstance(bottom_data, pd.DataFrame) else pd.DataFrame(bottom_data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name=sheet_name, startrow=0, header=True)
        start_row_2 = len(df1) + 1 + gap if not df1.empty else 0
        df2.to_excel(writer, index=False, sheet_name=sheet_name, startrow=start_row_2, header=True)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=media_type_str,
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )

def _safe_rate(numerator: float, denominator: float) -> float: # pragma: no cover
    """
    Safely compute division result as a rounded rate.
    When the denominator is zero or falsy, return 0.0 to avoid a ZeroDivisionError.

    Args:
        numerator: The numerator for the rate.
        denominator: The denominator for the rate.
    Returns:
        The rounded result to two decimal places if denominator is valid, otherwise 0.0.
    """
    return round(numerator / denominator, 2) if denominator and denominator != 0 else 0.0

@router.post('/export_test')
def dynamic_period_schema_creator(periods:List[str]): # pragma: no cover
    """
    Expand a list of period strings into a detailed list of period-week entries.
    For each period string (e.g., "1"), this function will create entries for 4 weeks
    and return a list of dicts containing keys: `dynamic_period_with_P` (e.g., 'P1|W1'),
    `dynamic_period`, and `dynamic_week`.

    Args:
        periods: List of period identifiers as strings.

    Returns:
        A list of dictionaries with expanded period-week information.
    """
    dynamic_period_list=[]
    for items in sorted(periods,key=int):
        for weeks in range(1,5):
            dynamic_period_with_p = f"P{items}|W{weeks}"
            dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_p,"dynamic_period":items,"dynamic_week":weeks}
            dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

def dynamic_period_only_schema_creator(periods:List[str]): # pragma: no cover
    """
    Convert a list of period strings into a list of period label dictionaries.
    Each input period 'n' will be transformed into {'dynamic_period_with_P': 'Pn', 'dynamic_period': 'n'}.

    Args:
        periods: List of period identifiers as strings.

    Returns:
        A list of dictionaries with `dynamic_period_with_P` and `dynamic_period` keys.
    """
    dynamic_period_list=[]
    for items in periods:
        dynamic_period_with_p = f"P{items}"
        dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_p,"dynamic_period":items}
        dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

def dynamic_period_schema_creator_forecast(periods:List[str]): # pragma: no cover
    """
    Create dynamic label entries for forecast spreadsheets that include Plan/Act/Diff tags.
    For each period string, creates labels like 'P1-Plan', 'P1-Act', and 'P1-Diff'.

    Args:
        periods: List of period identifiers as strings.

    Returns:
        A list of dictionaries with `dynamic_period_with_P` and `dynamic_period` fields.
    """
    list_placeholder=["Plan","Act","Diff"]
    dynamic_period_list=[]
    for item in periods:
        for lp in list_placeholder:
            dynamic_period_with_p = f"P{item}-{lp}"
            dynamic_period_object = {"dynamic_period_with_P":dynamic_period_with_p,"dynamic_period":item}
            dynamic_period_list.append(dynamic_period_object)
    return dynamic_period_list

@router.post('/export_plant_matrix_allocation')
def export_plant_matrix_allocation(
    periods: List[str],
    payload: schemas.ExportExcelPlantMatrixAllocationList
):  # pragma: no cover
    """
    Export plant matrix allocation into an Excel file per plant.
    Aggregates growing area allocations for each plant across specified periods and weeks, producing
    an Excel file containing formatted allocation strings by period/week along with totals and averages.
    """
    unique_plants = sorted({entry.plant_name for entry in payload.data})
    period_list = dynamic_period_schema_creator(periods)
    date_map = {}
    for item in payload.data:
        key = (str(item.period), str(item.week))
        if key not in date_map:
            date_map[key] = getattr(item, "Export_date", "") or ""
    output_export_json = []
    for up in unique_plants:
        export_object = {"plant_name": up}
        total_value = 0
        filtered_payload = [item for item in payload.data if item.plant_name == up]
        for pl in period_list:
            p = str(pl["dynamic_period"])
            w = str(pl["dynamic_week"])
            filtered_payload_period = [
                item for item in filtered_payload
                if str(item.period) == p and str(item.week) == w
            ]
            allocation_placeholder = ""
            for fpp in filtered_payload_period:
                allocation_placeholder = allocation_placeholder + fpp.growing_area_name + "-" + str(round(fpp.value)) + " "
                total_value += fpp.value
            export_date = date_map.get((p, w), "")
            if export_date:
                export_object[f'{pl["dynamic_period_with_P"]}\n{export_date}'] = allocation_placeholder
            else:
                export_object[pl["dynamic_period_with_P"]] = allocation_placeholder

        export_object["Total"] = round(total_value)
        output_export_json.append(export_object)
        weekly_average = 0
        for fp in filtered_payload:
            weekly_average += round(fp.value)
        export_object["Annual Weekly Avg."] = round(weekly_average / 52)
    return generate_excel_response(
        data=output_export_json,
        filename_prefix="plant_matrix_allocation",
        sheet_name="Sheet1"
    )


@router.post('/export_excel_ownership')
def export_excel_ownership(payload:schemas.ExportExcelOwnershipList): # pragma: no cover
    """
    Export ownership rows to an Excel file with a fixed column order.\
    Reorders each payload item to strictly follow `key_order` and returns a downloadable Excel file.

    Args:
        payload: `ExportExcelOwnershipList` payload containing ownership items.

    Returns:
        StreamingResponse with an Excel file named "ownership_<timestamp>.xlsx".
    """
    key_order =["Growing_Area","Contract","Shrinkage","To_Ship","Market","Flex","A2S","Extension","Demand","Position"]
    reordered_payload = [{key: item.dict().get(key) for key in key_order} for item in payload.data]

    return generate_excel_response(data=reordered_payload, filename_prefix="ownership", sheet_name="Sheet1")


@router.post('/export_plant_matrix_region_week')
def export_plant_matrix_region_week(
    periods: List[str],
    payload: schemas.ExportExcelplantmatrixregionweekList
): # pragma: no cover
    period_list = dynamic_period_schema_creator(periods)
    
    # 1. Map data for O(1) lookup
    data_map = {(item.region_name, str(item.period), str(item.week)): item.totalValue_regionWise for item in payload.data}
    date_map = {(str(item.period), str(item.week)): (getattr(item, "Export_date", "") or "") for item in payload.data}

    # 2. Define our region rows (without Totals yet to control order)
    regions = [var_east_us, var_west_us, var_central_us, var_canada]
    # We use a nested dict to keep row data organized
    row_data = {name: {"Region": name} for name in regions}
    flus_row = {"Region": "FLUS Total"}
    flna_row = {"Region": "FLNA Total"}
    
    # Track grand totals per row
    running_totals = dict.fromkeys(regions, 0)
    running_flus = 0
    running_flna = 0

    # 3. Populate Period Columns
    for pl in period_list:
        p, w = str(pl["dynamic_period"]), str(pl["dynamic_week"])
        dt = date_map.get((p, w), "")
        hdr = f'{pl["dynamic_period_with_P"]}\n{dt}' if dt else pl["dynamic_period_with_P"]
        
        # Get values
        v_e = round(data_map.get((var_east_us, p, w), 0))
        v_w = round(data_map.get((var_west_us, p, w), 0))
        v_c = round(data_map.get((var_central_us, p, w), 0))
        v_can = round(data_map.get((var_canada, p, w), 0))

        # Assign values to columns
        row_data[var_east_us][hdr] = v_e
        row_data[var_west_us][hdr] = v_w
        row_data[var_central_us][hdr] = v_c
        row_data[var_canada][hdr] = v_can
        
        f_us = v_e + v_w + v_c
        f_na = f_us + v_can
        
        flus_row[hdr] = f_us
        flna_row[hdr] = f_na

        # Increment totals
        running_totals[var_east_us] += v_e
        running_totals[var_west_us] += v_w
        running_totals[var_central_us] += v_c
        running_totals[var_canada] += v_can
        running_flus += f_us
        running_flna += f_na

    # 4. NOW add the Total column (guarantees it is the last key added)
    for name in regions:
        row_data[name]["Total"] = running_totals[name]
    flus_row["Total"] = running_flus
    flna_row["Total"] = running_flna

    # 5. Assemble in the specific order you requested
    output_export_json = [
        row_data[var_east_us],
        row_data[var_west_us],
        row_data[var_central_us],
        flus_row,
        row_data[var_canada],
        flna_row
    ]

    return generate_excel_response(
        data=output_export_json,
        filename_prefix="plant_matrix_region_week",
        sheet_name="Sheet1"
    )


@router.post('/export_plant_matrix_region_period')
def export_plant_matrix_region_period(
    periods: List[str],
    payload: schemas.ExportExcelplantmatrixregionweekList
):  # pragma: no cover
    period_list = dynamic_period_only_schema_creator(periods)
    
    data_map = {}
    date_map = {}
    for item in payload.data:
        p_str = str(item.period)
        data_map[(item.region_name, p_str)] = item.totalValue_regionWise
        if p_str not in date_map:
            date_map[p_str] = getattr(item, "Export_date", "") or ""

    regions = [var_east_us, var_central_us, var_west_us, var_canada]
    row_data = {name: {"Region": name} for name in regions}
    flus_row = {"Region": "FLUS Total"}
    flna_row = {"Region": "FLNA Total"}
    
    running_totals = dict.fromkeys(regions, 0)
    running_flus = 0
    running_flna = 0

    for pl in period_list:
        p_str = str(pl["dynamic_period"])
        dt = date_map.get(p_str, "")
        hdr = f'{pl["dynamic_period_with_P"]}\n{dt}' if dt else pl["dynamic_period_with_P"]
        
        v_e = round(data_map.get((var_east_us, p_str), 0))
        v_c = round(data_map.get((var_central_us, p_str), 0))
        v_w = round(data_map.get((var_west_us, p_str), 0))
        v_can = round(data_map.get((var_canada, p_str), 0))

        row_data[var_east_us][hdr] = v_e
        row_data[var_central_us][hdr] = v_c
        row_data[var_west_us][hdr] = v_w
        row_data[var_canada][hdr] = v_can
        
        f_us = v_e + v_c + v_w
        f_na = f_us + v_can
        
        flus_row[hdr] = f_us
        flna_row[hdr] = f_na

        running_totals[var_east_us] += v_e
        running_totals[var_central_us] += v_c
        running_totals[var_west_us] += v_w
        running_totals[var_canada] += v_can
        running_flus += f_us
        running_flna += f_na

    for name in regions:
        row_data[name]["Total"] = running_totals[name]
    flus_row["Total"] = running_flus
    flna_row["Total"] = running_flna

    output_export_json = [
        row_data[var_east_us],
        row_data[var_central_us],
        row_data[var_west_us],
        flus_row,
        row_data[var_canada],
        flna_row
    ]

    return generate_excel_response(
        data=output_export_json,
        filename_prefix="plant_matrix_region_period",
        sheet_name="Sheet1"
    )

@router.post('/export_plant_matrix_grower_week')
def export_plant_matrix_grower_week(
    periods: List[str],
    crop_type_gw: str,
    crop_year_gw: str,
    payload: schemas.ExportExcelplantmatrixgrowerweekList
):  # pragma: no cover
    """
    Export plant matrix aggregated by grower per week.
    """
    period_list = dynamic_period_schema_creator(periods)
    data_map = {}
    unique_growers = set()
    target_type = crop_type_gw.lower() if crop_type_gw else ""
    date_map = {}
    for item in payload.data:
        key_pw = (str(item.period), str(item.week))
        if key_pw not in date_map:
            date_map[key_pw] = getattr(item, "Export_date", "") or ""
        unique_growers.add(item.growing_area_name)
        if target_type == "all" or (item.crop_type.lower() == target_type and item.crop_year == crop_year_gw):
            key = (item.growing_area_name, str(item.period), str(item.week))
            data_map[key] = data_map.get(key, 0) + item.total_value
    def week_header(pl):
        p = str(pl["dynamic_period"])
        w = str(pl["dynamic_week"])
        export_date = date_map.get((p, w), "")
        if export_date:
            return f'{pl["dynamic_period_with_P"]}\n{export_date}'
        return pl["dynamic_period_with_P"]
    output_export_json = []
    for ug in sorted(unique_growers):
        export_object = {"Growing_Area": ug}
        total_row_sum = 0
        for pl in period_list:
            p_val = str(pl["dynamic_period"])
            w_val = str(pl["dynamic_week"])
            raw_val = data_map.get((ug, p_val, w_val), 0)
            rounded_val = round(raw_val)
            export_object[week_header(pl)] = rounded_val
            total_row_sum += rounded_val
        export_object["Total"] = total_row_sum
        output_export_json.append(export_object)
    return generate_excel_response(
        data=output_export_json,
        filename_prefix="plant_matrix_grower_week",
        sheet_name="Sheet1"
    )

@router.post('/export_plant_matrix_grower_period')
def export_plant_matrix_grower_period(
    periods: List[str],
    crop_type_gp: str,
    crop_year_gp: str,
    payload: schemas.ExportExcelplantmatrixgrowerweekList
):  # pragma: no cover
    """
    Export plant matrix aggregated by grower per period (no weekly detail).
    """
    period_list = dynamic_period_only_schema_creator(periods)
    data_map = {}
    unique_growers = set()
    target_type = crop_type_gp.lower() if crop_type_gp else ""
    date_map = {}
    for item in payload.data:
        p_key = str(item.period)
        if p_key not in date_map:
            date_map[p_key] = getattr(item, "Export_date", "") or ""
        unique_growers.add(item.growing_area_name)
        if target_type == "all" or (item.crop_type.lower() == target_type and item.crop_year == crop_year_gp):
            key = (item.growing_area_name, str(item.period))
            data_map[key] = data_map.get(key, 0) + item.total_value
    def period_header(pl):
        p = str(pl["dynamic_period"])
        export_date = date_map.get(p, "")
        if export_date:
            return f'{pl["dynamic_period_with_P"]}\n{export_date}'
        return pl["dynamic_period_with_P"]
    output_export_json = []
    for ug in sorted(unique_growers):
        export_object = {"Growing_Area": ug}
        total_row_sum = 0
        for pl in period_list:
            p_val = str(pl["dynamic_period"])
            raw_val = data_map.get((ug, p_val), 0)
            rounded_val = round(raw_val)
            export_object[period_header(pl)] = rounded_val
            total_row_sum += rounded_val
        export_object["Total"] = total_row_sum
        output_export_json.append(export_object)
    return generate_excel_response(
        data=output_export_json,
        filename_prefix="plant_matrix_grower_period",
        sheet_name="Sheet1"
    )

@router.post('/export_forecast')
def export_forecast(periods:List[str],payload:schemas.ExportExcelForecastList): # pragma: no cover
    """
    Export forecast (period-level) Plan/Actual/Diff for all plants into an Excel file.
    Aggregates forecast and actual values per plant across periods (no weekly detail) and writes totals.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelForecastList` payload with forecast and actual per plant/period.

    Returns:
        StreamingResponse with Excel file named "forecast_<timestamp>.xlsx" including Plan/Act/Diff per period.
    """
    unique_plants =  sorted({entry.plant_name for entry in payload.data})
    period_list =dynamic_period_only_schema_creator(periods)
    output_export_json = []
    for up in unique_plants:
        export_object={"plant_name":up}
        filtered_payload = [item for item in payload.data if item.plant_name==up]
        total_act =0
        total_fore=0
        total_delta=0
        for pl in period_list:
            filtered_payload_period = [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) 
            ]
            
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload_period[0].total_forecast_value)
            total_act+=round(filtered_payload_period[0].total_actual_value)
            export_object[f"{pl['dynamic_period_with_P']}-Act"]=round(filtered_payload_period[0].total_actual_value)
            total_fore+=round(filtered_payload_period[0].total_forecast_value)
            export_object[f"{pl['dynamic_period_with_P']}-Diff"]=round(filtered_payload_period[0].total_forecast_value)-round(filtered_payload_period[0].total_actual_value)
            total_delta+=round(filtered_payload_period[0].total_forecast_value)-round(filtered_payload_period[0].total_actual_value)
            
        export_object["Total_plan"]=total_fore
        export_object["Total_Act"]=total_act
        export_object["Total_Delta"]=total_delta
        output_export_json.append(export_object)
    
    return generate_excel_response(data=output_export_json, filename_prefix="forecast", sheet_name="Sheet1")

@router.post('/export_inflation_deflation')
def export_inflation_deflation(payload:schemas.ExportExcelInflationDeflationList): # pragma: no cover
    """
    Export inflation and deflation metrics across several categories into an Excel file.
    This endpoint accepts a list of period metrics and outputs rows such as 'Material CY', 'Freight CY', 'Total',
    'Prior Year' entries, and other performance indicators with period columns and a computed Total.

    Args:
        payload: `ExportExcelInflationDeflationList` payload containing metrics per period.

    Returns:
        StreamingResponse with an Excel file that lists the various inflation/deflation metrics per period.
    """
    output_export_json =[]
    var_perf_yag = "Performance vs YAG"
    export_object = {var_perf_yag:"Material CY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].material,2)
        total+=round(filtered_payload[0].material,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Freight CY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].freight,2)
        total+=round(filtered_payload[0].freight,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Total"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total,2)
        total+=round(filtered_payload[0].total,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Material PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].material_prev,2)
        total+=round(filtered_payload[0].material_prev,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Freight PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].freight_prev,2)
        total+=round(filtered_payload[0].freight_prev,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Total PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total_prior,2)
        total+=round(filtered_payload[0].total_prior,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"(B)/W vs PY MAT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].bw_than_py_matl,2)
        total+=round(filtered_payload[0].bw_than_py_matl,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"(B)/W vs. PY FRT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].bw_than_py_frt,2)
        total+=round(filtered_payload[0].bw_than_py_frt,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"(B)/W vs. PY TOT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].bw_than_py_total,2)
        total+=round(filtered_payload[0].bw_than_py_total,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"$ Impact vs PY"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].impact_bw_vs_prior_year,0)
        total+=round(filtered_payload[0].impact_bw_vs_prior_year,0)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Index (%) -MAT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].index_mat,1)
        total+=round(filtered_payload[0].index_mat,1)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Index (%) -FRT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].index_frt,2)
        total+=round(filtered_payload[0].index_frt,2)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    export_object = {var_perf_yag:"Index (%) -TOT"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].index,1)
        total+=round(filtered_payload[0].index,1)
    export_object["Total"]=round(total/13,2)
    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json, filename_prefix="inflation_deflation", sheet_name="Sheet1")


@router.post('/export_performance_vs_plan')
def export_performance_vs_plan(payload1:schemas.ExportExcelPvpList,payload2:schemas.ExportExcelPvpPvList): # pragma: no cover
    """
    Export a Performance vs Plan report as an Excel file.
    Compares actuals (payload1) and plan values (payload2) across multiple performance metrics
    (Material, Freight, Total) and computes per-period and overall totals with safe averaging.

    Args:
        payload1: `ExportExcelPvpList` containing actuals and BW/per-unit metrics.
        payload2: `ExportExcelPvpPvList` containing plan values for price variance tasks.

    Returns:
        StreamingResponse with the resulting Excel file summarizing the PVP metrics per period.
    """
    output_export_json =[]
    var_perf_plan = "Performance vs Plan"
    export_object = {var_perf_plan:"Actual($/u)-Material"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total_material_actual,2)
        total+=round(filtered_payload[0].total_material_actual,2)
        if round(filtered_payload[0].total_material_actual,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Actual($/u)-Freight"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].total_freight_cost_actual,2)
        total+=round(filtered_payload[0].total_freight_cost_actual,2)
        if round(filtered_payload[0].total_freight_cost_actual,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)


    export_object = {var_perf_plan:"Actual($/u)-Total"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round((filtered_payload[0].total_freight_cost_actual+filtered_payload[0].total_material_actual),2)
        total+=round((filtered_payload[0].total_freight_cost_actual+filtered_payload[0].total_material_actual),2)
        if round((filtered_payload[0].total_freight_cost_actual+filtered_payload[0].total_material_actual),2)!= 0:
          count+=1  
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Plan($/u)-Material"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==1]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
        if round(filtered_payload[0].value,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Plan($/u)-Freight"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
        if round(filtered_payload[0].value,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Plan($/u)-Raw Material"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==3]
        export_object[f"P{pr}"]=round(filtered_payload[0].value,2)
        total+=round(filtered_payload[0].value,2)
        if round(filtered_payload[0].value,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Plan($/u)-total"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload_1 = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==1]
        filtered_payload_2 = [item for item in payload2.data if item.period==pr and item.price_variance_task_id==2]
        export_object[f"P{pr}"]=round(filtered_payload_1[0].value+filtered_payload_2[0].value,2)
        total+=round(filtered_payload_1[0].value+filtered_payload_2[0].value,2)
        if round(filtered_payload_1[0].value+filtered_payload_2[0].value,2)!= 0:
          count+=1  
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"PV($/u)-Material-B/(W)"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].MATERIAL_BW_per_unit,2)
        total+=round(filtered_payload[0].MATERIAL_BW_per_unit,2)
        if round(filtered_payload[0].MATERIAL_BW_per_unit,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"PV($/u)-Freight-B/(W)"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].FREIGHT_BW_per_unit,2)
        total+=round(filtered_payload[0].FREIGHT_BW_per_unit,2)
        if round(filtered_payload[0].FREIGHT_BW_per_unit,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Total"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].FREIGHT_BW_per_unit+filtered_payload[0].MATERIAL_BW_per_unit,2)
        total+=round(filtered_payload[0].FREIGHT_BW_per_unit+filtered_payload[0].MATERIAL_BW_per_unit,2)
        if round(filtered_payload[0].FREIGHT_BW_per_unit+filtered_payload[0].MATERIAL_BW_per_unit,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"IMP B/(W) Vs Plan ($)"}
    total=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].IMPACT_BW_vs_Plan,0)
        total+=round(filtered_payload[0].IMPACT_BW_vs_Plan,2)
    export_object["Total"]=round(total,2)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Index (%) -MAT"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].Index_percent_MAT,2)
        total+=round(filtered_payload[0].Index_percent_MAT,2)
        if round(filtered_payload[0].Index_percent_MAT,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Index (%) -FRT"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].Index_percent_FRT,2)
        total+=round(filtered_payload[0].Index_percent_FRT,2)
        if round(filtered_payload[0].Index_percent_FRT,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {var_perf_plan:"Index (%) -TOT"}
    total=0
    count=0
    for pr in range(1,14):
        filtered_payload = [item for item in payload1.data if item.period==pr]
        export_object[f"P{pr}"]=round(filtered_payload[0].Index_percent,2)
        total+=round(filtered_payload[0].Index_percent,2)
        if round(filtered_payload[0].Index_percent_FRT,2)!= 0:
            count+=1
    export_object["Total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json, filename_prefix=var_perf_plan, sheet_name="Sheet1")


@router.post('/export_offcontract')
def export_offcontract(payload:schemas.ExportOffContractList, payload_plan:schemas.ExportOffContractList): # pragma: no cover
    """
    Export Off-Contract adjustments (Actual and Plan) in a stacked Excel file.
    The function computes per-task off-contract adjustments for each period and stacks the Actual table
    and the Plan table in a single Excel file with a delta line for comparisons.

    Args:
        payload: Actuals (`ExportOffContractList`) per period.
        payload_plan: Plans (`ExportOffContractList`) per period.

    Returns:
        StreamingResponse containing a two-table Excel file (actual and plan) with totals and delta.
    """
    act_cats = [(9, "Misc Bills"), (7, "Price ADJ"), (8, "Project"), (10, "Standards Adjustement"), 
                (1, "JE (+)"), (6, "JE (-)"), (3, "Stoarage research"), (2, "End year ADJ"), (13, "Others")]
    plan_cats = [(1, "Misc Bills"), (2, "Price ADJ"), (3, "Project"), (4, "Standards Adjustement"), 
                 (5, "JE (+)"), (6, "JE (-)"), (7, "Stoarage research"), (8, "End year ADJ"), (9, "Others")]

    var_off_contract_adj_act = "Off Contract Adj-Act"
    var_off_contract_adj_plan = "Off Contract Adj-Plan"

    act_lookup = {(item.off_contract_task_id, item.period): item.value for item in payload.data}
    plan_lookup = {(item.off_contract_plan_task_id, item.period): item.value for item in payload_plan.data}

    output_act = []
    for tid, name in act_cats:
        row = {var_off_contract_adj_act: name}
        total = 0
        for pr in range(1, 14):
            val = round(act_lookup.get((tid, pr), 0), 0)
            row[f"P{pr}"] = val
            total += val
        row["Total"] = round(total, 2)
        output_act.append(row)

    act_total_row = {var_off_contract_adj_act: "Total Off Contract Adj"}
    for pr in range(1, 14):
        act_total_row[f"P{pr}"] = sum(r[f"P{pr}"] for r in output_act)
    act_total_row["Total"] = round(sum(act_total_row[f"P{pr}"] for pr in range(1, 14)), 0)
    output_act.append(act_total_row)

    output_plan = []
    for tid, name in plan_cats:
        row = {var_off_contract_adj_plan: name}
        total = 0
        for pr in range(1, 14):
            val = round(plan_lookup.get((tid, pr), 0), 0)
            row[f"P{pr}"] = val
            total += val
        row["Total"] = round(total, 2)
        output_plan.append(row)

    plan_total_row = {var_off_contract_adj_plan: "Total Off Contract plan"}
    for pr in range(1, 14):
        plan_total_row[f"P{pr}"] = sum(r[f"P{pr}"] for r in output_plan)
    plan_total_row["Total"] = round(sum(plan_total_row[f"P{pr}"] for pr in range(1, 14)), 0)
    output_plan.append(plan_total_row)

    delta_row = {var_off_contract_adj_plan: "Delta Off Contract"}
    for pr in range(1, 14):
        delta_row[f"P{pr}"] = act_total_row[f"P{pr}"] - plan_total_row[f"P{pr}"]
    delta_row["Total"] = round(sum(delta_row[f"P{pr}"] for pr in range(1, 14)), 0)
    output_plan.append(delta_row)

    return generate_stacked_excel_response(top_data=output_act, bottom_data=output_plan, filename_prefix="Off_contract")


@router.post('/export_Adjustments_freight')
def export_adjustments_freight(payload:schemas.ExportExcelAdjustmentsFreightList, payload_plan:schemas.ExportExcelAdjustmentsFreightList): # pragma: no cover
    """
    Export Freight Adjustments for both Actual (top) and Plan (bottom) datasets to a stacked Excel workbook.
    The function computes categories and totals across 13 periods for both datasets and appends a delta row
    showing the difference between actual and plan values per period.

    Args:
        payload: `ExportExcelAdjustmentsFreightList` for actual adjustments per period.
        payload_plan: `ExportExcelAdjustmentsFreightList` for plan adjustments per period.

    Returns:
        StreamingResponse that contains a stacked Excel workbook with Actual and Plan tables.
    """
    cats = [(1, "Adjustments"), (2, "Sourcing"), (3, "Rail Lease Expense"), (4, "Productivity"), 
            (5, "Auto=pay-fuel"), (6, "Fuel Surcharge"), (7, "Accesorial"), (8, "Others")]
    
    var_freight_adj_act = "Freight Adjustments-Act"
    var_freight_adj_plan = "Freight Adjustments-Plan"

    act_lookup = {(item.freight_task_id, item.period): item.value for item in payload.data}
    plan_lookup = {(item.freight_task_plan_id, item.period): item.value for item in payload_plan.data}

    output_act = []
    for tid, name in cats:
        row = {var_freight_adj_act: name}
        t = sum(round(act_lookup.get((tid, p), 0), 0) for p in range(1, 14))
        for p in range(1, 14): row[f"P{p}"] = round(act_lookup.get((tid, p), 0), 0)
        row["Total"] = round(t, 2)
        output_act.append(row)

    act_total_row = {var_freight_adj_act: "Total Freight Adjustment"}
    for p in range(1, 14): act_total_row[f"P{p}"] = sum(r[f"P{p}"] for r in output_act)
    act_total_row["Total"] = round(sum(act_total_row[f"P{p}"] for p in range(1, 14)), 0)
    output_act.append(act_total_row)

    output_plan = []
    for tid, name in cats:
        row = {var_freight_adj_plan: name}
        t = sum(round(plan_lookup.get((tid, p), 0), 0) for p in range(1, 14))
        for p in range(1, 14): row[f"P{p}"] = round(plan_lookup.get((tid, p), 0), 0)
        row["Total"] = round(t, 2)
        output_plan.append(row)

    plan_total_row = {var_freight_adj_plan: "Total Freight Adjustment"}
    for p in range(1, 14): plan_total_row[f"P{p}"] = sum(r[f"P{p}"] for r in output_plan)
    plan_total_row["Total"] = round(sum(plan_total_row[f"P{p}"] for p in range(1, 14)), 0)
    output_plan.append(plan_total_row)

    delta_row = {var_freight_adj_plan: "Delta Freight Adjustments"}
    for p in range(1, 14): delta_row[f"P{p}"] = act_total_row[f"P{p}"] - plan_total_row[f"P{p}"]
    delta_row["Total"] = round(sum(delta_row[f"P{p}"] for p in range(1, 14)), 0)
    output_plan.append(delta_row)

    conv_row = {var_freight_adj_plan: "Conv CWT-Trip"}
    for p in range(1, 14): conv_row[f"P{p}"] = round(plan_lookup.get((9, p), 0), 2)
    conv_row["Total"] = round(sum(conv_row[f"P{p}"] for p in range(1, 14)) / 13, 2)
    output_plan.append(conv_row)

    return generate_stacked_excel_response(top_data=output_act, bottom_data=output_plan, filename_prefix="Freight")


@router.post('/export_adjustments_P4P')
def export_adjustments_p4p(payload: schemas.ExportExcelAdjustmentsP4PList): # pragma: no cover
    """
    Export P4P (Plan for Plan) adjustments as an Excel workbook.
    Outputs several rows showing solids/defects plan, actual/forecast, diffs, and totals across 13 periods.

    Args:
        payload: `ExportExcelAdjustmentsP4PList` payload with P4P data per period.

    Returns:
        StreamingResponse with an Excel containing P4P adjustments per period.
    """
    var_p4p_adj = "P4P Adjustments"
    # Create lookup map for O(1) access
    lookup = {item.periods: item for item in payload.data}
    output_export_json = []

    field_mappings = [
        ("Solids-Plan", "solid_plan"),
        ("Solids-Actual/Fcst", "solid_actual"),
        ("Diff(Solids)", "diff_solid"),
        ("Defects-Plan", "defects_plan"),
        ("Defects-Actual/Fcst", "defects_actual"),
        ("Diff(Defects)", "diff_Defects"),
        ("Total-Actual ", "ptdActualP4P"),
        ("Total-DIFF", "p4pDiff"),
    ]

    for label, attr in field_mappings:
        row = {var_p4p_adj: label}
        row_total = 0
        for pr in range(1, 14):
            val = round(getattr(lookup.get(pr), attr, 0), 0)
            row[f"P{pr}"] = val
            row_total += val
        row["Total"] = round(row_total, 0)
        output_export_json.append(row)

    total_plan_row = {var_p4p_adj: "Total-Plan"}
    tp_grand_total = 0
    for pr in range(1, 14):
        item = lookup.get(pr)
        val = round(item.solid_plan or 0, 0) + round(item.defects_plan or 0, 0) if item else 0
        total_plan_row[f"P{pr}"] = val
        tp_grand_total += val
    total_plan_row["Total"] = round(tp_grand_total, 0)
    
    output_export_json.insert(6, total_plan_row)

    return generate_excel_response(data=output_export_json, filename_prefix="Adjustments_P4P", sheet_name="Sheet1")


@router.post('/export_excel_adjustments_GA')
def export_excel_adjustments_ga(payload1: schemas.ExportExcelAdjustmentsGAList, payload2: schemas.ExportExcelAdjustmentsGAplanList): # pragma: no cover
    """
    Export General & Administrative (G&A) adjustments into a stacked Excel workbook.
    The function processes actual G&A adjustments (payload1) and plan G&A adjustments (payload2) for each period,
    aggregates per line and produces a stacked Excel with totals and a delta output row.

    Args:
        payload1: `ExportExcelAdjustmentsGAList` for actual G&A adjustments.
        payload2: `ExportExcelAdjustmentsGAplanList` for plan G&A adjustments.

    Returns:
        StreamingResponse with a stacked Excel containing G&A adjustments for each period.
    """
    def process_ga_block(data, label_key, id_attr, categories):
        lookup = {(getattr(item, id_attr), item.period): item.value for item in data}
        rows = []
        for cat_id, cat_name in categories:
            row = {label_key: cat_name}
            row_total = sum(round(lookup.get((cat_id, pr), 0), 0) for pr in range(1, 14))
            for pr in range(1, 14):
                row[f"P{pr}"] = round(lookup.get((cat_id, pr), 0), 0)
            row["Total"] = round(row_total, 0) / 1000
            rows.append(row)

        total_row = {label_key: "Total"}
        grand_sum = 0
        for pr in range(1, 14):
            p_sum = sum(r[f"P{pr}"] for r in rows)
            total_row[f"P{pr}"] = p_sum / 1000
            grand_sum += p_sum
        total_row["Total"] = round(grand_sum, 0) / 1000
        rows.append(total_row)
        return rows

    ga_cats = [
        (1, "HeadQuarters30510-2000100226"), (2, "Rhinelander30541-2798100200"),
        (3, "Research30548-2798100201"), (4, "Seed30516-2000100228"), (5, "Others")
    ]
    ga_plan_cats = [(i+1, name) for i, name in ga_cats] 

    act_rows = process_ga_block(payload1.data, "G&A Adj - Act", "general_administrative_id", ga_cats)
    plan_rows = process_ga_block(payload2.data, "G&A Adj - Plan", "general_administrative_plan_id", ga_plan_cats)

    delta_row = {"G&A Adj - Plan": "Delta Total- G&A expense"}
    d_total = 0
    for pr in range(1, 14):
        diff = act_rows[-1][f"P{pr}"] - plan_rows[-1][f"P{pr}"]
        delta_row[f"P{pr}"] = diff
        d_total += diff
    delta_row["Total"] = round(d_total, 0)
    plan_rows.append(delta_row)

    return generate_stacked_excel_response(top_data=act_rows, bottom_data=plan_rows, filename_prefix="Adjustments_GA")


@router.post('/export_excel_adjustments_BTL')
def export_excel_adjustments_btl(
    payload1: schemas.ExportExcelAdjustmentsBTLList, 
    payload2: schemas.ExportExcelAdjustmentsBTLplanList
): # pragma: no cover
    """
    Export BTL (Below The Line) adjustments for Actual and Plan in a combined Excel workbook.
    This endpoint computes list rows for BTL tasks and returns a stacked Excel file with actuals and plan values and delta.

    Args:
        payload1: `ExportExcelAdjustmentsBTLList` containing actual BTL adjustments.
        payload2: `ExportExcelAdjustmentsBTLplanList` containing plan BTL adjustments.

    Returns:
        StreamingResponse with a stacked Excel for BTL adjustments per period.
    """
    def process_btl_data(data, label_key, task_id_attr, total_label):
        """Helper to transform raw payload into structured rows for Excel."""
        lookup = {(getattr(item, task_id_attr), item.period): item.value for item in data}
        
        rows = []
        categories = [(1, "BTL(+)"), (2, "BTL(-)"), (3, "Others")]
        
        for task_id, task_name in categories:
            row = {label_key: task_name}
            row_total = 0
            for pr in range(1, 14):
                val = round(lookup.get((task_id, pr), 0), 0)
                row[f"P{pr}"] = val
                row_total += val
            row["Total"] = round(row_total, 2)
            rows.append(row)
            
        total_row = {label_key: total_label}
        grand_total = 0
        for pr in range(1, 14):
            period_sum = sum(r[f"P{pr}"] for r in rows)
            total_row[f"P{pr}"] = period_sum
            grand_total += period_sum
        total_row["Total"] = round(grand_total, 0)
        rows.append(total_row)
        
        return rows

    act_rows = process_btl_data(payload1.data, "BTL - Act", "btl_task_id", "Total BTL")
    plan_rows = process_btl_data(payload2.data, "BTL - Plan", "btl_plan_task_id", "Total BTL- Plan")

    delta_row = {"BTL - Plan": "Delta Total- BTL"}
    delta_total = 0
    act_total_row = act_rows[-1]
    plan_total_row = plan_rows[-1]

    for pr in range(1, 14):
        p_key = f"P{pr}"
        diff = act_total_row[p_key] - plan_total_row[p_key]
        delta_row[p_key] = diff
        delta_total += diff
    
    delta_row["Total"] = round(delta_total, 0)
    plan_rows.append(delta_row)

    return generate_stacked_excel_response(
        top_data=act_rows, 
        bottom_data=plan_rows, 
        filename_prefix="Adjustments_BTL"
    )


@router.post('/export_excel_adjustments_Productivity')
def export_excel_adjustments_productivity(
    payload1: schemas.ExportExcelAdjustmentsProductivityList,
    payload2: schemas.ExportExcelAdjustmentsProductivityPlanList
): # pragma: no cover
    """
    Export Productivity adjustments (Actual and Plan) in a stacked Excel workbook.
    This function computes rows for productivity tasks, gross, net, others and totals, and stacks actuals and plan
    sections into a single workbook with delta analysis.

    Args:
        payload1: `ExportExcelAdjustmentsProductivityList` for actual productivity adjustments.
        payload2: `ExportExcelAdjustmentsProductivityPlanList` for plan productivity adjustments.

    Returns:
        StreamingResponse with a stacked Excel workbook for productivity adjustments per period.
    """

    var_act_key, var_plan_key = "Productivity - Act", "Productivity-Plan"
    categories = [
        (1, "Productivity - Task"),
        (2, "Productivity Gross"),
        (3, "Productivity-net"),
        (4, "Others")
    ]

    map_act = {(item.productivity_task_id, item.period): item.value for item in payload1.data}
    map_plan = {(item.productivity_plan_task_id, item.period): item.value for item in payload2.data}

    output_act = []
    for tid, name in categories:
        row = {var_act_key: name}
        row_sum = 0
        for pr in range(1, 14):
            val = round(map_act.get((tid, pr), 0), 0)
            row[f"P{pr}"] = val
            row_sum += val
        row["Total"] = round(row_sum, 2)
        output_act.append(row)

    total_act_row = {var_act_key: "Total Productivity"}
    grand_total_act = 0
    for pr in range(1, 14):
        p_sum = sum(r[f"P{pr}"] for r in output_act)
        total_act_row[f"P{pr}"] = p_sum
        grand_total_act += p_sum
    total_act_row["Total"] = round(grand_total_act, 0)
    output_act.append(total_act_row)

    output_plan = []
    for tid, name in categories:
        row = {var_plan_key: name}
        row_sum = 0
        for pr in range(1, 14):
            val = round(map_plan.get((tid, pr), 0), 0)
            row[f"P{pr}"] = val
            row_sum += val
        row["Total"] = round(row_sum, 2)
        output_plan.append(row)

    total_plan_row = {var_plan_key: "Total productivity-Plan"}
    grand_total_plan = 0
    for pr in range(1, 14):
        p_sum = sum(r[f"P{pr}"] for r in output_plan)
        total_plan_row[f"P{pr}"] = p_sum
        grand_total_plan += p_sum
    total_plan_row["Total"] = round(grand_total_plan, 0)
    output_plan.append(total_plan_row)

    delta_row = {var_plan_key: "Delta Total Productivity"}
    delta_total = 0
    for pr in range(1, 14):
        diff = total_act_row[f"P{pr}"] - total_plan_row[f"P{pr}"]
        delta_row[f"P{pr}"] = diff
        delta_total += diff
    delta_row["Total"] = round(delta_total, 0)
    output_plan.append(delta_row)

    return generate_stacked_excel_response(
        top_data=output_act, 
        bottom_data=output_plan, 
        filename_prefix="Adjustments_Productivity"
    )


@router.post('/export_Freight_Rates_vendor_site')
def export_freight_rates_vendor_site(periods:List[str],payload:schemas.ExportExcelAFreightRateVendorSiteCodeList): # pragma: no cover
    """
    Export freight rates per vendor site and plant for the requested periods.
    Produces a spreadsheet listing each unique vendor-site and plant combo with per-period rate, round-trip, and fuel conversion factor columns.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelAFreightRateVendorSiteCodeList` payload containing vendor-site rate records.

    Returns:
        StreamingResponse containing an Excel file with freight rates per vendor-site and plant.
    """
    output_export_json =[]
    unique_od_combinations = sorted([
    {"business_unit": item[0], "vendor_site_code": item[1], "plant_name": item[2]}
    for item in {(item.business_unit, item.vendor_site_code, item.plant_name) for item in payload.data}
],key=lambda x: x["vendor_site_code"])

    period_list = dynamic_period_only_schema_creator(periods)
    for pld in unique_od_combinations:
        export_object ={
            "Business Unit":pld["business_unit"],
            "Vendor Code":pld["vendor_site_code"],
                        "Plants":pld["plant_name"]
                        }
        filtered_payload=[item for item in payload.data if
                 item.business_unit==pld["business_unit"] and item.vendor_site_code==pld["vendor_site_code"] and item.plant_name==pld["plant_name"]
            ]
        for pl in period_list:
            filtered_payload_period = [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) 
            ]
            export_object[var_gr_area]=filtered_payload_period[0].growing_area
            export_object["Miles"]=filtered_payload_period[0].miles
            export_object[f"{pl['dynamic_period_with_P']}-Rate"]=filtered_payload_period[0].rate
            export_object[f"{pl['dynamic_period_with_P']}-RT"]=filtered_payload_period[0].round_trip
            export_object[f"{pl['dynamic_period_with_P']}-Fuel_CF"]=filtered_payload_period[0].fuel_cf
        output_export_json.append(export_object)
    
    return generate_excel_response(data=output_export_json, filename_prefix="Freight_rates_vendor_site_code", sheet_name="Sheet1")


@router.post('/export_freight_rate_period')
def export_freight_rate_period(periods:List[str],payload:schemas.ExportExcelFreightRateperiodList): # pragma: no cover
    """
    Export freight rate summary for plants aggregated at the period level.
    The function returns per-plant values for Plan and Actual $/MCWT and total dollar spends, and computes per-plant totals and grand totals.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelFreightRateperiodList` payload with plant and period-level freight data.

    Returns:
        StreamingResponse containing the FreightRate period Excel file.
    """
    unique_plant =  sorted({entry.plant_name for entry in payload.data})
    period_list = dynamic_period_only_schema_creator(periods)
    output_export_json = []
    for uga in unique_plant:
        total_forecast_volume_frp=0
        total_forecast_spend_week_frp=0
        total_actual_vol_frp=0
        total_dollar_spend_week_frp =0
        export_object={var_plant_name:uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(filtered_payload[0].forecast_dollar_bymcwt,2)
                total_forecast_volume_frp+=round(filtered_payload[0].forecast_volume,2)
                total_forecast_spend_week_frp+=round(filtered_payload[0].forecast_total_dollar_spend,2)
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecast_total_dollar_spend,0)
                
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_dollar_bymcwt,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].actual_total_dollar_spend
                total_dollar_spend_week_frp+=round(filtered_payload[0].actual_total_dollar_spend,2)
                total_actual_vol_frp+=round(filtered_payload[0].actual_volume,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0
        if total_forecast_volume_frp>0:
            export_object[var_tp_mcwt]=round(total_forecast_spend_week_frp/total_forecast_volume_frp,2)
        else:
            export_object[var_tp_mcwt]=0
        export_object[var_tp_total]=total_forecast_spend_week_frp
        if total_actual_vol_frp>0:
            export_object[var_ta_mcwt]=round(total_dollar_spend_week_frp/total_actual_vol_frp,2)
        else:
            export_object[var_ta_mcwt]=0
        export_object[var_ta_total]=total_dollar_spend_week_frp
        output_export_json.append(export_object)

    export_object={var_plant_name:"Total"}
    grand_total_forecast_volume_total_frp=0
    grand_total_forecast_total_dollar_spend_total_frp=0
    grand_total_actual_total_dollar_spend_total_frp=0
    grand_total_actual_vol_total_frp=0
    for pl in period_list:
        total_forecast_volume_total_frp=0
        total_forecast_total_dollar_spend_total_frp=0
        total_actual_total_dollar_spend_total_frp=0
        total_actual_vol_total_frp=0
        filtered_payload_total = [item for item in payload.data if str(item.period)==str(pl["dynamic_period"])]
        for fpt in filtered_payload_total:
            total_forecast_volume_total_frp+=round(fpt.forecast_volume,2)
            total_forecast_total_dollar_spend_total_frp+=round(fpt.forecast_total_dollar_spend,2)
            total_actual_total_dollar_spend_total_frp+=round(fpt.actual_total_dollar_spend,2)
            total_actual_vol_total_frp+=round(fpt.actual_volume,2)
        if total_forecast_volume_total_frp>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(total_forecast_total_dollar_spend_total_frp/total_forecast_volume_total_frp,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Total$"]=total_forecast_total_dollar_spend_total_frp
        if total_actual_vol_total_frp>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(total_actual_total_dollar_spend_total_frp/total_actual_vol_total_frp,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=total_actual_total_dollar_spend_total_frp
        grand_total_forecast_volume_total_frp+=total_forecast_volume_total_frp
        grand_total_forecast_total_dollar_spend_total_frp+=total_forecast_total_dollar_spend_total_frp
        grand_total_actual_total_dollar_spend_total_frp+=total_actual_total_dollar_spend_total_frp
        grand_total_actual_vol_total_frp+=total_actual_vol_total_frp
    export_object[var_tp_mcwt]=_safe_rate(grand_total_forecast_total_dollar_spend_total_frp,grand_total_forecast_volume_total_frp)
    export_object[var_tp_total]=grand_total_forecast_total_dollar_spend_total_frp
    export_object[var_ta_mcwt]=_safe_rate(grand_total_actual_total_dollar_spend_total_frp,grand_total_actual_vol_total_frp)
    export_object[var_ta_total]=grand_total_actual_total_dollar_spend_total_frp

    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json, filename_prefix="PotatoRates_FreightRate_period", sheet_name="Sheet1")

@router.post('/export_freight_rate_week')
def export_freight_rate_week(periods:List[str],payload:schemas.ExportExcelFreightRateweekList): # pragma: no cover
    """
    Export freight rate summary for plants aggregated at the weekly level.
    Produces per-plant weekly Plan and Actual $/MCWT and total dollar values, with computed totals and grand totals.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelFreightRateweekList` payload with weekly freight data.

    Returns:
        StreamingResponse containing the FreightRate weekly Excel file.
    """
    unique_plant =  sorted({entry.plant_name for entry in payload.data})
    period_list_frw = dynamic_period_schema_creator(periods)
    output_export_json = []
    for uga in unique_plant:
        total_forecast_volume_frw=0
        total_forecast_spend_week_frw=0
        total_actual_vol_frw=0
        total_dollar_spend_week_frw =0
        export_object_frw={var_plant_name:uga}
        for pl in period_list_frw:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"]) and  str(item.week_no) == str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
                export_object_frw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(filtered_payload[0].forecast_dollor_cwt,2)
                total_forecast_volume_frw+=round(filtered_payload[0].forecast_volume,2)
                total_forecast_spend_week_frw+=round(filtered_payload[0].forecast_spend_week,2)
                export_object_frw[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecast_spend_week,0)
                
                export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_dollor_MCWT_week,2)
                export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].Total_dollor_spend_week
                total_dollar_spend_week_frw+=round(filtered_payload[0].Total_dollor_spend_week,2)
                total_actual_vol_frw+=round(filtered_payload[0].actual_volume,2)
            else:
                export_object_frw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object_frw[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0
        if total_forecast_volume_frw>0:
            export_object_frw[var_tp_mcwt]=round(total_forecast_spend_week_frw/total_forecast_volume_frw,2)
        else:
            export_object_frw[var_tp_mcwt]=0
        export_object_frw[var_tp_total]=total_forecast_spend_week_frw
        if total_actual_vol_frw>0:
            export_object_frw[var_ta_mcwt]=round(total_dollar_spend_week_frw/total_actual_vol_frw,2)
        else:
            export_object_frw[var_ta_mcwt]=0
        export_object_frw[var_ta_total]=total_dollar_spend_week_frw
        output_export_json.append(export_object_frw)

    export_object_frw={var_plant_name:"Total"}
    grand_total_forecast_volume_total_frw=0
    grand_total_forecast_total_dollar_spend_total_frw=0
    grand_total_actual_total_dollar_spend_total_frw=0
    grand_total_actual_vol_total_frw=0
    for pl in period_list_frw:
        total_forecast_volume_total_frw=0
        total_forecast_total_dollar_spend_total_frw=0
        total_actual_total_dollar_spend_total_frw=0
        total_actual_vol_total_frw=0
        filtered_payload_total = [item for item in payload.data if str(item.period)==str(pl["dynamic_period"]) and  str(item.week_no) == str(pl["dynamic_week"]) ]
        for fpt in filtered_payload_total:
            total_forecast_volume_total_frw+=round(fpt.forecast_volume,2)
            total_forecast_total_dollar_spend_total_frw+=round(fpt.forecast_spend_week,2)
            total_actual_total_dollar_spend_total_frw+=round(fpt.Total_dollor_spend_week,2)
            total_actual_vol_total_frw+=round(fpt.actual_volume,2)
        if total_forecast_volume_total_frw>0:
            export_object_frw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(total_forecast_total_dollar_spend_total_frw/total_forecast_volume_total_frw,2)
        else:
            export_object_frw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
        export_object_frw[f"{pl['dynamic_period_with_P']}-Total$"]=total_forecast_total_dollar_spend_total_frw
        if total_actual_vol_total_frw>0:
            export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(total_actual_total_dollar_spend_total_frw/total_actual_vol_total_frw,2)
        else:
            export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
        export_object_frw[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=total_actual_total_dollar_spend_total_frw
        grand_total_forecast_volume_total_frw+=total_forecast_volume_total_frw
        grand_total_forecast_total_dollar_spend_total_frw+=total_forecast_total_dollar_spend_total_frw
        grand_total_actual_total_dollar_spend_total_frw+=total_actual_total_dollar_spend_total_frw
        grand_total_actual_vol_total_frw+=total_actual_vol_total_frw
    export_object_frw[var_tp_mcwt]=_safe_rate(grand_total_forecast_total_dollar_spend_total_frw,grand_total_forecast_volume_total_frw)
    export_object_frw[var_tp_total]=grand_total_forecast_total_dollar_spend_total_frw
    export_object_frw[var_ta_mcwt]=_safe_rate(grand_total_actual_total_dollar_spend_total_frw,grand_total_actual_vol_total_frw)
    export_object_frw[var_ta_total]=grand_total_actual_total_dollar_spend_total_frw

    output_export_json.append(export_object_frw)

    return generate_excel_response(data=output_export_json, filename_prefix="PotatoRates_FreightRate_weekly", sheet_name="Sheet1")

@router.post('/export_freight_growing_area')
def export_freight_growing_area(payload:schemas.ExportExcelFreightRateGrowingAreaList): # pragma: no cover
    """
    Export freight rates for each Growing Area -> Plant pairing into an Excel file.
    Produces a sheet with Origin (growing area) and Destination (plant) and, for each period
    P1..P13, a Plan and an Actual rate column

    Args:
        payload: `ExportExcelFreightRateGrowingAreaList` containing per-growing-area/plants rates

    Returns:
        StreamingResponse containing an Excel file with Plan and Actual rate columns for each period.
    """
    unique_od_combinations = sorted([
    {"growing_area_name": item[0], "plant_name": item[1]}
    for item in {(item.growing_area_name, item.plant_name) for item in payload.data}
],key=lambda x: x["growing_area_name"])
    output_export_json = []
    for uga in unique_od_combinations:
        export_object={"Origin":uga["growing_area_name"],"Destination":uga["plant_name"]}
        filtered_payload = [item for item in payload.data if item.plant_name==uga["plant_name"] and item.growing_area_name==uga["growing_area_name"]]
        for pl in range(1,14):
            filtered_payload_period = [item for item in filtered_payload if item.period==pl]
            if len(filtered_payload)>0:
                 
                 export_object[f"P{pl}|Plan"]=filtered_payload_period[0].rate_plan
                 export_object[f"P{pl}|Actual"]=filtered_payload_period[0].rate_actual
        output_export_json.append(export_object)
    
    return generate_excel_response(data=output_export_json,filename_prefix="Freight_Rates_GrowingArea",sheet_name="Sheet1")

@router.post('/Export_Excel_PotatoRates_GrowingArea_period')
def export_excel_potatorates_growingarea_period(periods:List[str],payload:schemas.ExportExcelPotatoRatesGrowingAreaPeriodList): # pragma: no cover
    """
    Export potato rates per Growing Area aggregated at the period level.
    Builds a per-growing-area row for each specified period with Plan ($/MCWT), Total$ and Actual $/MCWT and Total$ values.

    Args:
        periods: list of period ids (strings)
        payload: `ExportExcelPotatoRatesGrowingAreaPeriodList` containing rate and volume values per growing area and period

    Returns:
        StreamingResponse containing an Excel file with one row per Growing Area and period columns.
    """
    unique_growing_area =  sorted({entry.growing_area_name for entry in payload.data})
    period_list = dynamic_period_only_schema_creator(periods)
    output_export_json = []
    for uga in unique_growing_area:
        total_forecast_volume=0
        total_forecast_total_dollar_spend=0
        total_actual_total_dollar_spend=0
        total_actual_vol=0
        export_object={var_gr:uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.growing_area_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(filtered_payload[0].fcst_rate,2)
                total_forecast_volume+=round(filtered_payload[0].forecast_volume,2)
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].fcst_total_dollor,0)
                total_forecast_total_dollar_spend+=round(filtered_payload[0].fcst_total_dollor,2)
                if filtered_payload[0].actual_volume==0:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                else:
                    export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_total_dollor/filtered_payload[0].actual_volume,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].actual_total_dollor
                total_actual_total_dollar_spend+=round(filtered_payload[0].actual_total_dollor,2)
                total_actual_vol+=round(filtered_payload[0].actual_volume,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0
        if total_forecast_volume>0:
            export_object[var_tp_mcwt]=round(total_forecast_total_dollar_spend/total_forecast_volume,2)
        else:
            export_object[var_tp_mcwt]=0
        export_object[var_tp_total]=total_forecast_total_dollar_spend
        if total_actual_vol>0:
            export_object[var_ta_mcwt]=round(total_actual_total_dollar_spend/total_actual_vol,2)
        else:
            export_object[var_ta_mcwt]=0
        export_object[var_ta_total]=total_actual_total_dollar_spend
        output_export_json.append(export_object)

    export_object={var_gr:"Total"}
    grand_total_forecast_volume_total=0
    grand_total_forecast_total_dollar_spend_total=0
    grand_total_actual_total_dollar_spend_total=0
    grand_total_actual_vol_total=0
    for pl in period_list:
        total_forecast_volume_total=0
        total_forecast_total_dollar_spend_total=0
        total_actual_total_dollar_spend_total=0
        total_actual_vol_total=0
        filtered_payload_total = [item for item in payload.data if str(item.period)==str(pl["dynamic_period"])]
        for fpt in filtered_payload_total:
            total_forecast_volume_total+=round(fpt.forecast_volume,2)
            total_forecast_total_dollar_spend_total+=round(fpt.fcst_total_dollor,2)
            total_actual_total_dollar_spend_total+=round(fpt.actual_total_dollor,2)
            total_actual_vol_total+=round(fpt.actual_volume,2)
        if total_forecast_volume_total>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(total_forecast_total_dollar_spend_total/total_forecast_volume_total,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Total$"]=total_forecast_total_dollar_spend_total
        if total_actual_vol_total>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(total_actual_total_dollar_spend_total/total_actual_vol_total,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=total_actual_total_dollar_spend_total
        grand_total_forecast_volume_total+=total_forecast_volume_total
        grand_total_forecast_total_dollar_spend_total+=total_forecast_total_dollar_spend_total
        grand_total_actual_total_dollar_spend_total+=total_actual_total_dollar_spend_total
        grand_total_actual_vol_total+=total_actual_vol_total
    export_object[var_tp_mcwt]=_safe_rate(grand_total_forecast_total_dollar_spend_total,grand_total_forecast_volume_total)
    export_object[var_tp_total]=grand_total_forecast_total_dollar_spend_total
    export_object[var_ta_mcwt]=_safe_rate(grand_total_actual_total_dollar_spend_total,grand_total_actual_vol_total)
    export_object[var_ta_total]=grand_total_actual_total_dollar_spend_total

    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json,filename_prefix="PotatoRates_GrowingArea_period",sheet_name="Sheet1")

@router.post('/Export_Excel_PotatoRates_GrowingArea_week') 
def export_excel_potatorates_growingarea_week(periods: List[str],
                                              payload: schemas.ExportExcelPotatoRatesGrowingAreaWeekList):  # pragma: no cover
    """
    Export potato rates per Growing Area at a weekly granularity.
    For each growing area and each week within the requested period list, writes Plan $/MCWT, Total$, Actual $/MCWT and Actual Total$.
    The function also computes total values and per-row weighted rates where applicable.

    Args:
        periods: list of period ids (strings)
        payload: `ExportExcelPotatoRatesGrowingAreaWeekList` with weekly values per growing area

    Returns:
        StreamingResponse containing an Excel workbook with weekly Plan/Actual columns per growing area.
    """
    unique_growing_area_gaw = sorted({entry.growing_area_name for entry in payload.data})
    period_list = dynamic_period_schema_creator(periods)
    output_export_json = []

    for uga in unique_growing_area_gaw:
        total_forecast_total_dollar_spend_gaw = 0.0
        total_actual_total_dollar_spend_gaw = 0.0
        total_actual_vol_gaw = 0.0
        nz_plan_rate_sum = 0.0
        nz_plan_rate_cnt = 0
        export_object_gaw = {var_gr: uga}
        for pl in period_list:
            filtered_payload = [
                item for item in payload.data
                if item.growing_area_name == uga
                and str(item.period) == str(pl["dynamic_period"])
                and str(item.week) == str(pl["dynamic_week"])
            ]
            if filtered_payload:
                row = filtered_payload[0]
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"] = round(row.rate, 2)
                if round(row.rate, 2) != 0:
                    nz_plan_rate_sum += row.rate
                    nz_plan_rate_cnt += 1
                # Plan dollars for Total$
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Total$"] = round(row.forecaste_total_dollor, 0)
                total_forecast_total_dollar_spend_gaw += float(row.forecaste_total_dollor)
                if row.actual_volume == 0:
                    export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"] = 0
                else:
                    export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"] = round(
                        row.actual_total_dollor / row.actual_volume, 2
                    )
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-Total$"] = row.actual_total_dollor
                total_actual_total_dollar_spend_gaw += float(row.actual_total_dollor)
                total_actual_vol_gaw += float(row.actual_volume)
            else:
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"] = 0
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Total$"] = 0
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"] = 0
                export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-Total$"] = 0

        # Plan total rate: average of non-zero per-cell Plan rates 
        export_object_gaw[var_tp_mcwt] = _safe_rate(nz_plan_rate_sum, nz_plan_rate_cnt)
        export_object_gaw[var_tp_total] = round(total_forecast_total_dollar_spend_gaw, 0)
        # Actual total rate: keep volume-weighted logic 
        export_object_gaw[var_ta_mcwt] = _safe_rate(total_actual_total_dollar_spend_gaw, total_actual_vol_gaw)
        export_object_gaw[var_ta_total] = round(total_actual_total_dollar_spend_gaw, 0)
        output_export_json.append(export_object_gaw)
    # ===== Grand Total row =====
    export_object_gaw = {var_gr: "Total"}
    grand_total_actual_total_dollar_spend_total = 0.0
    grand_total_actual_vol_total = 0.0
    grand_total_forecast_total_dollar_spend_total = 0.0
    grand_nz_plan_rate_sum = 0.0
    grand_nz_plan_rate_cnt = 0

    for pl in period_list:
        total_actual_total_dollar_spend_total = 0.0
        total_actual_vol_total = 0.0
        total_forecast_total_dollar_spend_total = 0.0
        filtered_payload_total = [
            item for item in payload.data
            if str(item.period) == str(pl["dynamic_period"])
            and str(item.week) == str(pl["dynamic_week"])
        ]
        for fpt in filtered_payload_total:
            if round(fpt.rate, 2) != 0:
                grand_nz_plan_rate_sum += fpt.rate
                grand_nz_plan_rate_cnt += 1
            total_forecast_total_dollar_spend_total += float(fpt.forecaste_total_dollor)
            total_actual_total_dollar_spend_total += float(fpt.actual_total_dollor)
            total_actual_vol_total += float(fpt.actual_volume)
        # Plan rate for this cell: volume-weighted
        if sum(fp.forecast_volume for fp in filtered_payload_total) > 0:
            pw_plan_rate = _safe_rate(
                total_forecast_total_dollar_spend_total,
                sum(fp.forecast_volume for fp in filtered_payload_total)
            )
        else:
            pw_plan_rate = 0
        export_object_gaw[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"] = round(pw_plan_rate, 2)
        export_object_gaw[f"{pl['dynamic_period_with_P']}-Total$"] = round(total_forecast_total_dollar_spend_total, 0)
        export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"] = _safe_rate(
            total_actual_total_dollar_spend_total, total_actual_vol_total
        )
        export_object_gaw[f"{pl['dynamic_period_with_P']}-Actual-Total$"] = round(total_actual_total_dollar_spend_total, 0)
        grand_total_forecast_total_dollar_spend_total += total_forecast_total_dollar_spend_total
        grand_total_actual_total_dollar_spend_total += total_actual_total_dollar_spend_total
        grand_total_actual_vol_total += total_actual_vol_total
    # Grand totals
    export_object_gaw[var_tp_mcwt] = _safe_rate(grand_nz_plan_rate_sum, grand_nz_plan_rate_cnt)
    export_object_gaw[var_tp_total] = round(grand_total_forecast_total_dollar_spend_total, 0)
    export_object_gaw[var_ta_mcwt] = _safe_rate(
        grand_total_actual_total_dollar_spend_total, grand_total_actual_vol_total
    )
    export_object_gaw[var_ta_total] = round(grand_total_actual_total_dollar_spend_total, 0)
    output_export_json.append(export_object_gaw)

    return generate_excel_response(data=output_export_json,filename_prefix="PotatoRates_GrowingArea_week",sheet_name="Sheet1")

@router.post('/Export_Excel_PotatoRates_plantview_period')
def export_excel_potatorates_plantview_period(periods:List[str],payload:schemas.ExportExcelPotatoRatesPlantViewPeriodList): # pragma: no cover      
    """
    Export potato rates for a Plant View aggregated at the period level.
    Creates one row per plant with Plan $/MCWT, Total$, Actual $/MCWT and Actual Total$ for each requested period,
    and computes totals and grand totals across plants.

    Args:
        periods: list of period ids (strings)
        payload: `ExportExcelPotatoRatesPlantViewPeriodList` with plant-level rates and volume values per period

    Returns:
        StreamingResponse containing an Excel workbook with per-plant period summaries.
    """
    unique_plant =  sorted({entry.plant_name for entry in payload.data})
    period_list = dynamic_period_only_schema_creator(periods)
    output_export_json = []
    for uga in unique_plant:
        total_forecast_volume_pp=0
        total_forecast_spend_week_pp=0
        total_actual_vol_pp=0
        total_dollar_spend_week_pp =0
        export_object={var_plant_name:uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(filtered_payload[0].forecast_dollar_bymcwt,2)
                total_forecast_volume_pp+=round(filtered_payload[0].forecast_volume,2)
                total_forecast_spend_week_pp+=round(filtered_payload[0].forecast_total_dollar_spend,2)
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecast_total_dollar_spend,0)
                
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_dollar_bymcwt,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].actual_total_dollar_spend
                total_dollar_spend_week_pp+=round(filtered_payload[0].actual_total_dollar_spend,2)
                total_actual_vol_pp+=round(filtered_payload[0].actual_volume,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0
        if total_forecast_volume_pp>0:
            export_object[var_tp_mcwt]=round(total_forecast_spend_week_pp/total_forecast_volume_pp,2)
        else:
            export_object[var_tp_mcwt]=0
        export_object[var_tp_total]=total_forecast_spend_week_pp
        if total_actual_vol_pp>0:
            export_object[var_ta_mcwt]=round(total_dollar_spend_week_pp/total_actual_vol_pp,2)
        else:
            export_object[var_ta_mcwt]=0
        export_object[var_ta_total]=total_dollar_spend_week_pp
        output_export_json.append(export_object)

    export_object={var_plant_name:"Total"}
    grand_total_forecast_volume_total_pp=0
    grand_total_forecast_total_dollar_spend_total_pp=0
    grand_total_actual_total_dollar_spend_total_pp=0
    grand_total_actual_vol_total_pp=0
    for pl in period_list:
        total_forecast_volume_total_pp=0
        total_forecast_total_dollar_spend_total_pp=0
        total_actual_total_dollar_spend_total_pp=0
        total_actual_vol_total_pp=0
        filtered_payload_total = [item for item in payload.data if str(item.period)==str(pl["dynamic_period"])]
        for fpt in filtered_payload_total:
            total_forecast_volume_total_pp+=round(fpt.forecast_volume,2)
            total_forecast_total_dollar_spend_total_pp+=round(fpt.forecast_total_dollar_spend,2)
            total_actual_total_dollar_spend_total_pp+=round(fpt.actual_total_dollar_spend,2)
            total_actual_vol_total_pp+=round(fpt.actual_volume,2)
        if total_forecast_volume_total_pp>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(total_forecast_total_dollar_spend_total_pp/total_forecast_volume_total_pp,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Total$"]=total_forecast_total_dollar_spend_total_pp
        if total_actual_vol_total_pp>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(total_actual_total_dollar_spend_total_pp/total_actual_vol_total_pp,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=total_actual_total_dollar_spend_total_pp
        grand_total_forecast_volume_total_pp+=total_forecast_volume_total_pp
        grand_total_forecast_total_dollar_spend_total_pp+=total_forecast_total_dollar_spend_total_pp
        grand_total_actual_total_dollar_spend_total_pp+=total_actual_total_dollar_spend_total_pp
        grand_total_actual_vol_total_pp+=total_actual_vol_total_pp
    export_object[var_tp_mcwt]=_safe_rate(grand_total_forecast_total_dollar_spend_total_pp,grand_total_forecast_volume_total_pp)
    export_object[var_tp_total]=grand_total_forecast_total_dollar_spend_total_pp
    export_object[var_ta_mcwt]=_safe_rate(grand_total_actual_total_dollar_spend_total_pp,grand_total_actual_vol_total_pp)
    export_object[var_ta_total]=grand_total_actual_total_dollar_spend_total_pp

    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json,filename_prefix="PotatoRates_PlantView_period",sheet_name="Sheet1")

@router.post('/Export_Excel_PotatoRates_PlantView_Week')
def export_excel_potatorates_plantview_week(periods:List[str],payload:schemas.ExportExcelPotatoRatesPlantViewWeekList): # pragma: no cover
    """
    Export potato rates for a Plant View at the weekly level.
    Similar to the period-level plant view but provides Plan/Actual $/MCWT and totals per week.

    Args:
        periods: list of period ids (strings)
        payload: `ExportExcelPotatoRatesPlantViewWeekList` containing plant-level weekly values

    Returns:
        StreamingResponse containing an Excel workbook with per-plant weekly summaries.
    """
    unique_plant =  sorted({entry.plant_name for entry in payload.data})
    period_list = dynamic_period_schema_creator(periods)
    output_export_json = []
    for uga in unique_plant:
        total_forecast_volume_pw=0
        total_forecast_spend_week_pw=0
        total_actual_vol_pw=0
        total_dollar_spend_week_pw =0
        export_object={var_plant_name:uga}
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"]) and  str(item.week_no) == str(pl["dynamic_week"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(filtered_payload[0].forecast_dollor_cwt,2)
                total_forecast_volume_pw+=round(filtered_payload[0].forecast_volume,2)
                total_forecast_spend_week_pw+=round(filtered_payload[0].forecast_spend_week,2)
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=round(filtered_payload[0].forecast_spend_week,0)
                
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(filtered_payload[0].actual_dollor_MCWT_week,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=filtered_payload[0].Total_dollor_spend_week
                total_dollar_spend_week_pw+=round(filtered_payload[0].Total_dollor_spend_week,2)
                total_actual_vol_pw+=round(filtered_payload[0].actual_volume,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Total$"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=0
        if total_forecast_volume_pw>0:
            export_object[var_tp_mcwt]=round(total_forecast_spend_week_pw/total_forecast_volume_pw,2)
        else:
            export_object[var_tp_mcwt]=0
        export_object[var_tp_total]=total_forecast_spend_week_pw
        if total_actual_vol_pw>0:
            export_object[var_ta_mcwt]=round(total_dollar_spend_week_pw/total_actual_vol_pw,2)
        else:
            export_object[var_ta_mcwt]=0
        export_object[var_ta_total]=total_dollar_spend_week_pw
        output_export_json.append(export_object)

    export_object={var_plant_name:"Total"}
    grand_total_forecast_volume_total_pw=0
    grand_total_forecast_total_dollar_spend_total_pw=0
    grand_total_actual_total_dollar_spend_total_pw=0
    grand_total_actual_vol_total_pw=0
    for pl in period_list:
        total_forecast_volume_total_pw=0
        total_forecast_total_dollar_spend_total_pw=0
        total_actual_total_dollar_spend_total_pw=0
        total_actual_vol_total_pw=0
        filtered_payload_total = [item for item in payload.data if str(item.period)==str(pl["dynamic_period"]) and str(item.week_no)==str(pl["dynamic_week"])]
        for fpt in filtered_payload_total:
            total_forecast_volume_total_pw+=round(fpt.forecast_volume,2)
            total_forecast_total_dollar_spend_total_pw+=round(fpt.forecast_spend_week,2)
            total_actual_total_dollar_spend_total_pw+=round(fpt.Total_dollor_spend_week,2)
            total_actual_vol_total_pw+=round(fpt.actual_volume,2)
        if total_forecast_volume_total_pw>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=round(total_forecast_total_dollar_spend_total_pw/total_forecast_volume_total_pw,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Total$"]=total_forecast_total_dollar_spend_total_pw
        if total_actual_vol_total_pw>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=round(total_actual_total_dollar_spend_total_pw/total_actual_vol_total_pw,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual-$/MCWT"]=0
        export_object[f"{pl['dynamic_period_with_P']}-Actual-Total$"]=total_actual_total_dollar_spend_total_pw
        grand_total_forecast_volume_total_pw+=total_forecast_volume_total_pw
        grand_total_forecast_total_dollar_spend_total_pw+=total_forecast_total_dollar_spend_total_pw
        grand_total_actual_total_dollar_spend_total_pw+=total_actual_total_dollar_spend_total_pw
        grand_total_actual_vol_total_pw+=total_actual_vol_total_pw
    export_object[var_tp_mcwt]=_safe_rate(grand_total_forecast_total_dollar_spend_total_pw,grand_total_forecast_volume_total_pw)
    export_object[var_tp_total]=grand_total_forecast_total_dollar_spend_total_pw
    export_object[var_ta_mcwt]=_safe_rate(grand_total_actual_total_dollar_spend_total_pw,grand_total_actual_vol_total_pw)
    export_object[var_ta_total]=grand_total_actual_total_dollar_spend_total_pw

    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json,filename_prefix="PotatoRates_PlantView_week",sheet_name="Sheet1")

@router.post('/export_excel_solids_growingarea')
def export_excel_solids_growingarea(periods:List[str],payload:schemas.ExportExcelSolidsGrowingAreaViewList): # pragma: no cover
    """
    Export solids aggregated by growing area per period into an Excel file.
    The report computes Plan and Actual solids per growing area and returns a file containing per-period columns and totals.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelSolidsGrowingAreaViewList` payload containing solids per growing area and period.

    Returns:
        StreamingResponse with an Excel file containing per-growing area solids metrics.
    """
    unique_growing_area =  sorted({entry.growing_area_name for entry in payload.data})
    period_list = dynamic_period_only_schema_creator(periods)
    output_export_json = []
    for uga in unique_growing_area:
        export_object= {var_gr:uga}
        total_plan=0
        total_plan_vol=0
        total_actual=0
        total_actual_vol=0
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.growing_area_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload[0].plan_rate,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=round(filtered_payload[0].actual_rate,2)
                total_actual += round(filtered_payload[0].actual_total_solids,2)
                total_actual_vol+= round(filtered_payload[0].actual_volume,2)
                total_plan += round(filtered_payload[0].plan_total_solids,2)
                total_plan_vol+= round(filtered_payload[0].forecast_volume,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0
        if total_plan_vol>0:
                export_object["Total-plan"]=round(total_plan/total_plan_vol,2)
        else:
                export_object["Total-plan"]=0
        if total_actual_vol>0:
                export_object["Total-actual"]=round(total_actual/total_actual_vol,2)
        else:
                export_object["Total-actual"]=0
        


        output_export_json.append(export_object)
    
    export_object= {var_gr:"Total"}
    total_plan_total=0
    total_plan_vol_total=0
    total_actual_total=0
    total_actual_vol_total=0
    for pl in period_list:
        total_plan=0
        total_plan_vol=0
        total_actual=0
        total_actual_vol=0
        
        filtered_payload_total = [item for item in payload.data if  str(item.period) == str(pl["dynamic_period"])]
        for fpt in filtered_payload_total:
            total_plan+=round(fpt.plan_total_solids,2)
            total_plan_vol+=round(fpt.forecast_volume,2)
            total_actual+=round(fpt.actual_total_solids,2)
            total_actual_vol+=round(fpt.actual_volume,2)
        if total_plan_vol>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(total_plan/total_plan_vol,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
        if total_actual_vol>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual"]=round(total_actual/total_actual_vol,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0
        total_plan_total+=total_plan
        total_plan_vol_total+=total_plan_vol
        total_actual_total+=total_actual
        total_actual_vol_total+=total_actual_vol
    export_object["Total-plan"]=_safe_rate(total_plan_total,total_plan_vol_total)
    export_object["Total-actual"]=_safe_rate(total_actual_total,total_actual_vol_total)
    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json,filename_prefix="Solids_GrowingArea",sheet_name="Sheet1")

@router.post('/export_excel_solids_plant')
def export_excel_solids_plant(periods:List[str],payload:schemas.ExportExcelSolidsPlantViewList): # pragma: no cover
    """
    Export solids per plant across periods into an Excel file.
    Computes Plan and Actual solids per plant with totals and returns the result as a downloadable Excel file.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelSolidsPlantViewList` payload with per-plant solids and volumes.

    Returns:
        StreamingResponse with an Excel file containing per-plant solids data per period.
    """
    unique_growing_area =  sorted({entry.plant_name for entry in payload.data})
    period_list = dynamic_period_only_schema_creator(periods)
    output_export_json = []
    for uga in unique_growing_area:
        export_object= {var_plant_name:uga}
        total_plan_sp=0
        total_plan_vol_sp=0
        total_actual_sp=0
        total_actual_vol_sp=0
        for pl in period_list:
            filtered_payload = [item for item in payload.data if item.plant_name==uga and str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload)>0:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload[0].forecast_solids,2)
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=round(filtered_payload[0].actual_solids,2)
                total_actual_sp += round(filtered_payload[0].actual_total_solids,2)
                total_actual_vol_sp+= round(filtered_payload[0].actual_volume,2)
                total_plan_sp += round(filtered_payload[0].forecast_total_solids,2)
                total_plan_vol_sp+= round(filtered_payload[0].forecast_volume,2)
            else:
                export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
                export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0
        if total_plan_vol_sp>0:
                export_object["Total-plan"]=round(total_plan_sp/total_plan_vol_sp,2)
        else:
                export_object["Total-plan"]=0
        if total_actual_vol_sp>0:
                export_object["Total-actual"]=round(total_actual_sp/total_actual_vol_sp,2)
        else:
                export_object["Total-actual"]=0
        


        output_export_json.append(export_object)
    
    export_object= {var_plant_name:"Total"}
    total_plan_total_sp=0
    total_plan_vol_total_sp=0
    total_actual_total_sp=0
    total_actual_vol_total_sp=0
    for pl in period_list:
        total_plan_sp=0
        total_plan_vol_sp=0
        total_actual_sp=0
        total_actual_vol_sp=0
        
        filtered_payload_total = [item for item in payload.data if  str(item.period) == str(pl["dynamic_period"])]
        for fpt in filtered_payload_total:
            total_plan_sp+=round(fpt.forecast_total_solids,2)
            total_plan_vol_sp+=round(fpt.forecast_volume,2)
            total_actual_sp+=round(fpt.actual_total_solids,2)
            total_actual_vol_sp+=round(fpt.actual_volume,2)
        if total_plan_vol_sp>0:
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(total_plan_sp/total_plan_vol_sp,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=0
        if total_actual_vol_sp>0:
            export_object[f"{pl['dynamic_period_with_P']}-Actual"]=round(total_actual_sp/total_actual_vol_sp,2)
        else:
            export_object[f"{pl['dynamic_period_with_P']}-Actual"]=0
        total_plan_total_sp+=total_plan_sp
        total_plan_vol_total_sp+=total_plan_vol_sp
        total_actual_total_sp+=total_actual_sp
        total_actual_vol_total_sp+=total_actual_vol_sp
    export_object["Total-plan"]=_safe_rate(total_plan_total_sp,total_plan_vol_total_sp)
    export_object["Total-actual"]=_safe_rate(total_actual_total_sp,total_actual_vol_total_sp)
    output_export_json.append(export_object)
    
    return generate_excel_response(data=output_export_json,filename_prefix="Solids_plantView",sheet_name="Sheet1")


@router.post('/export_finance_summary_solids')
def export_finance_summary_solids(payload:schemas.ExportExcelFinanceSummarySolidsList): # pragma: no cover
    """
    Export a financial summary of solids across multiple metrics to an Excel file.
    Produces various rows like Prior, Plan, Fcst/Act, Index, M$ Impact, and conversion factor per period and provides a summary column.

    Args:
        payload: `ExportExcelFinanceSummarySolidsList` payload containing finance-related solids metrics per period.

    Returns:
        StreamingResponse with an Excel file summarizing finance metrics related to solids.
    """
    output_export_json=[]
    export_object = {"Solids":"Prior"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].prior,2)
        total+=round(filtered_payload[0].prior,2)
        if round(filtered_payload[0].prior,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {"Solids":"Plan"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].plan,2)
        total+=round(filtered_payload[0].plan,2)
        if round(filtered_payload[0].plan,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {"Solids":"Fcst/Act"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].forecast,2)
        total+=round(filtered_payload[0].forecast,2)
        if round(filtered_payload[0].forecast,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {"Solids":"Fcst/Act-ERP"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].fcst_act,2)
        total+=round(filtered_payload[0].fcst_act,2)
        if round(filtered_payload[0].fcst_act,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {"Solids":"+/(-) VS Plan"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].fore_plan,2)
        total+=round(filtered_payload[0].fore_plan,2)
        if round(filtered_payload[0].fore_plan,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {"Solids":"Index VS Plan"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].yag_index,2)
        total+=round(filtered_payload[0].yag_index,2)
        if round(filtered_payload[0].yag_index,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    export_object = {"Solids":"M$Imp B/(W) Plan"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].m_dollar_impact_plan,3)
        total+=round(filtered_payload[0].m_dollar_impact_plan,3)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"M$Imp B/(W) Act/Fcst"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].m_dollar_impact,3)
        total+=round(filtered_payload[0].m_dollar_impact,3)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Delta M$ Imp"}
    total=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].delta_m_imp,2)
        total+=round(filtered_payload[0].delta_m_imp,2)
    export_object["total"]=total
    output_export_json.append(export_object)

    export_object = {"Solids":"Conv. Factor"}
    total=0
    count=0
    for pl in range(1,14):
        filtered_payload = [item for item in payload.data if item.period==pl]
        export_object[f"P{pl}"]=round(filtered_payload[0].conversion_factor,2)
        total+=round(filtered_payload[0].conversion_factor,2)
        if round(filtered_payload[0].conversion_factor,2)!=0:
            count+=1
    export_object["total"]=_safe_rate(total,count)
    output_export_json.append(export_object)

    return generate_excel_response(data=output_export_json,filename_prefix="Finance_solids_summary",sheet_name="Sheet1")
    
@router.post('/Export_Home_Pop_Up')
def export_home_pop_up(payload1:schemas.ExportExcelHomePopUpList,payload2:schemas.ExportExcelHomePopUpPlanList,periods:List[str]): # pragma: no cover
    """
    Export Home Pop-Up volumes comparing Actual vs Plan across business units for specified periods.
    Produces two stacked tables (Actual and Plan) showing volumes for BU categories (FLUS, Co-Man, FLC) per period.

    Args:
        payload1: `ExportExcelHomePopUpList` containing actual volumes per period and week.
        payload2: `ExportExcelHomePopUpPlanList` containing plan volumes per period and week.
        periods: List of period ids as strings.

    Returns:
        Stacked Excel Response with Actual top table and Plan bottom table for Home Pop-Up volumes.
    """
    period_list = dynamic_period_schema_creator(periods)
    output_export_json1=[]
    output_export_json2=[]
    export_object ={"BU-Act":"FLUS"}
    total=0
    for pl in period_list:
           filtered_payload = [item for item in payload1.data if item.category_name=="FLUS" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
           if len(filtered_payload)>0:
            export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
            total+=filtered_payload[0].volume
           else:
            export_object[pl['dynamic_period_with_P']]=0
    export_object["Total"] =total     
    output_export_json1.append(export_object)
    export_object ={"BU-Act":"Co-Man"}
    total=0
    for pl in period_list:
           filtered_payload = [item for item in payload1.data if item.category_name=="Co-Man" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
           if len(filtered_payload)>0:
            export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
            total+=filtered_payload[0].volume
           else:
            export_object[pl['dynamic_period_with_P']]=0
    export_object["Total"] =total 
    output_export_json1.append(export_object)
    export_object ={"BU-Act":"FLC"}
    total=0
    for pl in period_list:
           filtered_payload = [item for item in payload1.data if item.category_name=="FLC" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
           if len(filtered_payload)>0:
            export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
            total+=filtered_payload[0].volume
           else:
            export_object[pl['dynamic_period_with_P']]=0
    export_object["Total"] =total 
    output_export_json1.append(export_object)
    export_object ={"BU-Plan":"FLUS"}
    total=0
    for pl in period_list:
           filtered_payload = [item for item in payload2.data if item.category_name=="FLUS" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
           if len(filtered_payload)>0:
            export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
            total+=filtered_payload[0].volume
           else:
            export_object[pl['dynamic_period_with_P']]=0
    export_object["Total"] =total
    output_export_json2.append(export_object)
    export_object ={"BU-Plan":"Co-Man"}
    total=0
    for pl in period_list:
           filtered_payload = [item for item in payload2.data if item.category_name=="Co-Man" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
           if len(filtered_payload)>0:
            export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
            total+=filtered_payload[0].volume
           else:
            export_object[pl['dynamic_period_with_P']]=0
    export_object["Total"] =total
    output_export_json2.append(export_object)
    export_object ={"BU-Plan":"FLC"}
    total=0
    for pl in period_list:
           filtered_payload = [item for item in payload2.data if item.category_name=="FLC" and str(item.period) == str(pl["dynamic_period"]) and str(item.week)==str(pl["dynamic_week"])]
           if len(filtered_payload)>0:
            export_object[pl['dynamic_period_with_P']]=filtered_payload[0].volume
            total+=filtered_payload[0].volume
           else:
            export_object[pl['dynamic_period_with_P']]=0
    export_object["Total"] =total
    output_export_json2.append(export_object)

    return generate_stacked_excel_response(top_data=output_export_json1, bottom_data=output_export_json2, filename_prefix="Homepopup")

@router.post('/Export_active_allocation_index')
def export_active_allocation_index(payload: schemas.ExportExcelActiveAllocationIndexList): # pragma: no cover
    
    """
    Export Active Allocation index and volumes for Business Units.
    Generates a formatted Excel report showing index and volume rows for each Business Unit
    (Co-MAN, FLC, FLUS) across periods and includes an FY aggregate column. The function
    applies coloring/styles to the workbook header and groups in the writer prior to returning.

    Args:
        payload: `ExportExcelActiveAllocationIndexList` payload containing `target_volume` and `value` per period.

    Returns:
        StreamingResponse with an Excel attachment named e.g. "Active_allocation_index_<timestamp>.xlsx".
    """
    output_export_json = []
    categories = ["Co-Man", "FLC", "FLUS"]
    metrics_to_process = [ "target_volume", "value"]

    for category in categories:
        for metric in metrics_to_process:
            
            metric_label = "Index" if metric == "value" else "Volume"
            bu_label = "Co-MAN" if category == "Co-Man" else category 
            
            export_object = {"Business Unit": bu_label, "": metric_label} 
            
            total = 0
            count = 0
            for pl in range(1, 14):
                filtered_payload = [item for item in payload.data 
                                    if item.category_name == category and item.period == pl]
                
                if len(filtered_payload) > 0:
                    item = filtered_payload[0]
                    current_data = getattr(item, metric)
                    export_object[f"P{pl}"] = current_data
                    if current_data is not None:
                        total += current_data
                        count += 1
                else:
                    export_object[f"P{pl}"] = 0 
            
            export_object["FY"] = total / count if count > 0 else 0
            output_export_json.append(export_object)

    dt = datetime.now()
    str_date = dt.strftime("%d%m%y%H%M%S")
    df = pd.DataFrame(output_export_json)
    file_name = f"Active_allocation_index_{str_date}.xlsx"
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Active_Allocation')

        worksheet = writer.sheets['Active_Allocation']

        header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        header_font = Font(bold=True)
        header_align = Alignment(horizontal="center", vertical="center")

        group_fills = {
            "Co-MAN": PatternFill(start_color="E7F0F9", end_color="E7F0F9", fill_type="solid"),
            "FLC":    PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid"),
            "FLUS":   PatternFill(start_color="B9D0E7", end_color="B9D0E7", fill_type="solid")
        }
        
        bu_align = Alignment(horizontal="left", vertical="center")
        
        index_format = "0.00"
        volume_format = "0"

        normal_side = Side(style="thin")

        full_normal_border = Border(
                                    left=normal_side,
                                    right=normal_side,
                                    top=normal_side,
                                    bottom=normal_side
                                )

        center_alignment = Alignment(
                                    horizontal="center",
                                    vertical="center"
                                    )

        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 12
        for col_num in range(3, 17):
             worksheet.column_dimensions[get_column_letter(col_num)].width = 10

        for cell in worksheet["1:1"]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align

        for start_row in range(2, 8, 2):
            end_row = start_row + 1
            
            bu_name = worksheet.cell(row=start_row, column=1).value
            fill = group_fills.get(bu_name)
            
            worksheet.merge_cells(start_row=start_row, start_column=1, end_row=end_row, end_column=1)
            bu_cell = worksheet.cell(row=start_row, column=1)
            bu_cell.alignment = bu_align
            
            for row_num in [start_row, end_row]:
                
                is_index_row = (row_num == start_row)
                num_format = index_format if is_index_row else volume_format

                for col_num in range(1, 17): 
                    cell = worksheet.cell(row=row_num, column=col_num)
                    if fill:
                        cell.fill = fill
                    
                    if col_num >= 3: 
                        cell.number_format = num_format

        for row_num in range(1,8):
            for col_num in range(1, 17):
                worksheet.cell(row=row_num, column=col_num).border = full_normal_border
                worksheet.cell(row=row_num, column=col_num).alignment = center_alignment

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )


@router.post('/export_forecast_week')
def export_forecast_week(periods:List[str],payload:schemas.ExportExcelForecastWeekList): # pragma: no cover
    """
    Export forecast (weekly) Plan/Actual/Diff data per plant to an Excel file.
    Produces per-plant weekly columns with Plan, Act and Diff values and totals across the specified weeks.

    Args:
        periods: List of period ids as strings (e.g., ["1","2"]).
        payload: `ExportExcelForecastWeekList` payload containing weekly forecast rows per plant.

    Returns:
        StreamingResponse with an Excel file named "forecast_<timestamp>.xlsx" containing weekly plan/act/diff.
    """
    unique_plants =  sorted({entry.plant_name for entry in payload.data})
    period_list =dynamic_period_schema_creator(periods)
    output_export_json = []
    for up in unique_plants:
        export_object={"plant_name":up}
        filtered_payload = [item for item in payload.data if item.plant_name==up]
        total_act =0
        total_fore=0
        total_delta=0
        for pl in period_list:
            filtered_payload_period = [
                item for item in filtered_payload
                if str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"]) 
            ]
            
            export_object[f"{pl['dynamic_period_with_P']}-Plan"]=round(filtered_payload_period[0].forecasted_value)
            total_act+=round(filtered_payload_period[0].total_actual_value)
            export_object[f"{pl['dynamic_period_with_P']}-Act"]=round(filtered_payload_period[0].total_actual_value)
            total_fore+=round(filtered_payload_period[0].forecasted_value)
            export_object[f"{pl['dynamic_period_with_P']}-Diff"]=round(filtered_payload_period[0].forecasted_value)-round(filtered_payload_period[0].total_actual_value)
            total_delta+=round(filtered_payload_period[0].forecasted_value)-round(filtered_payload_period[0].total_actual_value)
            
        export_object["Total_plan"]=total_fore
        export_object["Total_Act"]=total_act
        export_object["Total_Delta"]=total_delta
        output_export_json.append(export_object)
    
    return generate_excel_response(data=output_export_json,filename_prefix="forecast",sheet_name="Sheet1")


@router.post('/export_plant_matrix_allocation_croptype')
def export_plant_matrix_allocation_croptype(
    periods: List[str],
    crop_type: str,
    crop_year: str,
    payload: schemas.ExportExcelPlantMatrixAllocationList
):  # pragma: no cover
    """
    Export plant matrix allocation filtered by crop type and crop year.
    Produces per-plant allocation strings by period/week and computes totals and annual weekly averages.
    """
    unique_plants_plac = sorted({entry.plant_name for entry in payload.data})
    period_list_plac = dynamic_period_schema_creator(periods)
    date_map = {}
    for item in payload.data:
        key = (str(item.period), str(item.week))
        if key not in date_map:
            date_map[key] = getattr(item, "Export_date", "") or ""
    output_export_json_plac = []
    for up in unique_plants_plac:
        export_object_plac = {"plant_name": up}
        total_value = 0
        if crop_type == "Fresh":
            filtered_payload = [
                item for item in payload.data
                if item.plant_name == up and (item.crop_type == "Fresh" or item.crop_type == "FRESH")
                and item.crop_year == crop_year
            ]
        if crop_type == "Storage":
            filtered_payload = [
                item for item in payload.data
                if item.plant_name == up and (item.crop_type == "Storage" or item.crop_type == "STORAGE")
                and item.crop_year == crop_year
            ]
        if crop_type == "All":
            filtered_payload = [item for item in payload.data if item.plant_name == up]
        for pl in period_list_plac:
            allocation_placeholder_plac = ""
            if len(filtered_payload) > 0:
                filtered_payload_period = [
                    item for item in filtered_payload
                    if str(item.period) == str(pl["dynamic_period"]) and str(item.week) == str(pl["dynamic_week"])
                ]
                if len(filtered_payload_period) > 0:
                    for fpp in filtered_payload_period:
                        allocation_placeholder_plac = (
                            allocation_placeholder_plac + fpp.growing_area_name + "-" + str(round(fpp.value)) + " "
                        )
                        total_value += fpp.value
            p = str(pl["dynamic_period"])
            w = str(pl["dynamic_week"])
            export_date = date_map.get((p, w), "")
            if export_date:
                header_key = f'{pl["dynamic_period_with_P"]}\n{export_date}'
            else:
                header_key = pl["dynamic_period_with_P"]
            export_object_plac[header_key] = allocation_placeholder_plac
        export_object_plac["Total"] = round(total_value)
        output_export_json_plac.append(export_object_plac)
        weekly_average = 0
        for fp in filtered_payload:
            weekly_average += round(fp.value)
        export_object_plac["Annual Weekly Avg."] = round(weekly_average / 52)
    return generate_excel_response(
        data=output_export_json_plac,
        filename_prefix="Plant_matrix_allocation_croptype",
        sheet_name="Sheet1"
    )

@router.post('/export_freight_rate_fuelcost_growingarea')
def export_freight_rate_fuelcost_growingarea(periods:List[str],payload:schemas.ExportExcelFreightRateFuelCostGrowingAreaList): # pragma: no cover
    """
    Export fuel cost metrics (total miles and total fuel) for growing areas per period.
    Produces an Excel report listing G.Area -> Plant pairs with total miles covered and total fuel per period, plus a grand total row.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelFreightRateFuelCostGrowingAreaList` payload containing per-growing-area fuel cost data.

    Returns:
        StreamingResponse with an Excel file for the fuel cost growing area report.
    """
    output_export_json = []
    period_list_fcga = dynamic_period_only_schema_creator(periods)
    for uga in payload.data:
        export_object_fcga={var_gr_area:uga.growing_area_name,"Plants":uga.plant_name}
        filtered_payload = [item for item in payload.data if item.plant_name==uga.plant_name and item.growing_area_name==uga.growing_area_name]
        for pl in period_list_fcga:
            filtered_payload_period = [item for item in filtered_payload if str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload_period)>0:
                 
                 export_object_fcga[f"{pl['dynamic_period_with_P']}|Total Miles Covered"]=filtered_payload_period[0].total_miles
                 export_object_fcga[f"{pl['dynamic_period_with_P']}|Total Fuel"]=filtered_payload_period[0].total_fuel
            else:
                export_object_fcga[f"{pl['dynamic_period_with_P']}|Total Miles Covered"]=0
                export_object_fcga[f"{pl['dynamic_period_with_P']}|Total Fuel"]=0
            
        output_export_json.append(export_object_fcga)
    export_object_fcga={var_gr_area:"Total","Plants":" "}
    for pl in period_list_fcga:
        filtered_payload_total = [item for item in payload.data if str(item.period) == str(pl["dynamic_period"])]
        total_total_miles_covered =0
        total_total_fuel =0
        for fpt in filtered_payload_total:
            total_total_miles_covered+=fpt.total_miles
            total_total_fuel+=fpt.total_fuel
        export_object_fcga[f"{pl['dynamic_period_with_P']}|Total Miles Covered"]=total_total_miles_covered
        export_object_fcga[f"{pl['dynamic_period_with_P']}|Total Fuel"]=total_total_fuel
    
    output_export_json.append(export_object_fcga)

    return generate_excel_response(data=output_export_json,filename_prefix="Freight_Rates_GrowingArea",sheet_name="Sheet1")


@router.post('/export_freight_rate_fuelcost_plantview')
def export_freight_rate_fuelcost_plantview(periods:List[str],payload:schemas.ExportExcelFreightRateFuelCostPlantViewList): # pragma: no cover
    """
    Export fuel cost metrics per plant view with total miles and total fuel per period.
    Similar to the growing area version but keyed by plant (Plant Name) and includes a summary/Total row for all plants.

    Args:
        periods: List of period ids as strings.
        payload: `ExportExcelFreightRateFuelCostPlantViewList` payload with plant-level fuel metrics.

    Returns:
        StreamingResponse with an Excel file containing total miles and total fuel per plant per period.
    """
    output_export_json = []
    period_list_fcpv = dynamic_period_only_schema_creator(periods)
    for uga in payload.data:
        export_object_fcpv={var_plant_name:uga.plant_name}
        filtered_payload = [item for item in payload.data if item.plant_name==uga.plant_name]
        for pl in period_list_fcpv:
            filtered_payload_period = [item for item in filtered_payload if str(item.period) == str(pl["dynamic_period"])]
            if len(filtered_payload_period)>0:
                 
                 export_object_fcpv[f"{pl['dynamic_period_with_P']}|Total Miles Covered"]=filtered_payload_period[0].total_miles
                 export_object_fcpv[f"{pl['dynamic_period_with_P']}|Total Fuel"]=filtered_payload_period[0].total_fuel
            else:
                export_object_fcpv[f"{pl['dynamic_period_with_P']}|Total Miles Covered"]=0
                export_object_fcpv[f"{pl['dynamic_period_with_P']}|Total Fuel"]=0
            
        output_export_json.append(export_object_fcpv)
    export_object_fcpv={var_plant_name:"Total"}
    for pl in period_list_fcpv:
        filtered_payload_total = [item for item in payload.data if str(item.period) == str(pl["dynamic_period"])]
        total_total_miles_covered_fcpv =0
        total_total_fuel_fcpv =0
        for fpt in filtered_payload_total:
            total_total_miles_covered_fcpv+=fpt.total_miles
            total_total_fuel_fcpv+=fpt.total_fuel
        export_object_fcpv[f"{pl['dynamic_period_with_P']}|Total Miles Covered"]=total_total_miles_covered_fcpv
        export_object_fcpv[f"{pl['dynamic_period_with_P']}|Total Fuel"]=total_total_fuel_fcpv
    
    output_export_json.append(export_object_fcpv)

    return generate_excel_response(data=output_export_json,filename_prefix="Freight_Rates_PlantView",sheet_name="Sheet1")


@router.get("/export_erp_raw_data_zip/{receipt_year}")
def export_erp_raw_data_zip(receipt_year: int): # pragma: no cover
    """
    Export ERP raw data for a given receipt year as a ZIP file containing a CSV (Excel-readable) file.

    - Input: receipt_year (path param, int)
    - Behaviour:
        * Fetch all rows from dbo.erp_raw_data for that receipt year.
        * Replace NULLs with empty string in export.
        * Return ZIP file as HTTP download.
    """
    class StreamableBuffer:
        def __init__(self):
            self.buffer = io.BytesIO()
            self.offset = 0

        def write(self, b):
            self.buffer.write(b)
            self.offset += len(b)
            return len(b)

        def tell(self):
            return self.offset 

        def seekable(self):
            return False 

        def flush(self):
            pass

        def get_and_clear(self):
            self.buffer.seek(0)
            data = self.buffer.read()
            self.buffer.truncate(0)
            self.buffer.seek(0)
            return data

    def iter_zip():
        try:
            db = SessionLocal()
        except NameError:
            yield b"ERROR: SessionLocal not defined."
            return

        stream_buffer = StreamableBuffer()
        zf = zipfile.ZipFile(stream_buffer, mode='w', compression=zipfile.ZIP_DEFLATED)
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        try:
            query = text("SELECT * FROM dbo.erp_raw_data WHERE RECEIPT_YEAR = :year")
            result = db.execute(query, {"year": receipt_year})
            columns = list(result.keys())

            csv_filename = f"ERP_RAW_DATA_{receipt_year}.csv"
            
            with zf.open(csv_filename, mode='w') as csv_file_in_zip:
                
                def write_csv_chunk():
                    csv_buffer.seek(0)
                    bytes_data = csv_buffer.read().encode('utf-8')
                    csv_file_in_zip.write(bytes_data)
                    csv_buffer.truncate(0)
                    csv_buffer.seek(0)

                writer.writerow(columns)
                write_csv_chunk()
                
                yield stream_buffer.get_and_clear()

                while True:
                    chunk = result.fetchmany(5000)
                    if not chunk:
                        break
                    
                    for row in chunk:
                        writer.writerow(["" if v is None else str(v) for v in row])
                    
                    write_csv_chunk()
                    
                    yield stream_buffer.get_and_clear()

            yield stream_buffer.get_and_clear()

        except Exception as e:
            print(f"ZIP ERROR: {e}")
            
        finally:
            zf.close()
            db.close()
            yield stream_buffer.get_and_clear()

    filename = f"ERP_RAW_DATA_{receipt_year}.zip"

    return StreamingResponse(
        iter_zip(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )