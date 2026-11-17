from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from fastapi import HTTPException
import math
import models

ERP_TABLE = "dbo.erp_raw_data"

def _utcnow_naive() -> datetime:
    """
    Get current UTC time as a naive datetime (no timezone, no microseconds).

    Returns:
        datetime: Current UTC timestamp without tzinfo and microseconds.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def _fmt_token(x: Union[float, str, None]) -> str:  
    """
    Normalize a value to a compact string token.

    Rules:
        - None      -> ""
        - float .0  -> integer string (e.g. 10.0 -> "10")
        - float     -> trimmed decimal string
        - other     -> stripped string

    Args:
        x (float | str | None): Value to normalize.

    Returns:
        str: Normalized token string.
    """
    try:
        if x is None:
            return ""
        try:
            f = float(x)
            if math.isfinite(f):
                if f.is_integer():
                    return str(int(f))
                return f"{f:.15g}"
        except Exception:
            pass
        return str(x).strip()
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

def _compose_erp_unique_id(
    bpa: Union[str, None],
    rel: Union[float, None],
    shp: Union[float, None],
    line: Union[float, None],
) -> str: 
    """
    Compose a unique ERP identifier string from given components.

    Args:
        bpa (str | None): BPA number.
        rel (float | None): Release number.
        shp (float | None): Shipment number.
        line (float | None): Line number.

    Returns:
        str: Concatenated unique identifier string.
    """
    try:
        return f"{_fmt_token(bpa)}#{_fmt_token(rel)}#{_fmt_token(shp)}#{_fmt_token(line)}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
def _to_float_or_none(v) -> Optional[float]:  
    """
    Safely convert a value to float or return None.

    Args:
        v (Any): Input value.

    Returns:
        float | None: Parsed float value or None if empty/invalid.
    """
    try:
        if v is None:
            return None
        s = str(v).strip()
        if s == "":
            return None
        return float(s)
    except Exception:
        return None

def _derive_crop_year(
    year_value: Optional[int],
    period: Optional[int],
    crop_type: Optional[str],
) -> Optional[str]:  
    """
    Derive crop year string from year, period, and crop type.

    Logic:
        - STORAGE + period <= 8  -> "<year-1>-<year>"
        - STORAGE + period >  8  -> "<year>-<year+1>"
        - FRESH / others         -> "<year>"

    Args:
        year_value (int | None): UNLOAD_YEAR.
        period (int | None): UNL_DATE_PD (period number).
        crop_type (str | None): CROP_TYPE value.

    Returns:
        str | None: Derived crop year (e.g. "2024-25" or "2025") or None.
    """
    try:
        if year_value is None or period is None:
            return None

        ct = (crop_type or "").strip().upper()

        # STORAGE: cross-year logic like in SQL
        if ct == "STORAGE":
            if period <= 8:
                start_year = year_value - 1
                end_year = year_value
            else:
                start_year = year_value
                end_year = year_value + 1
            return f"{start_year}-{str(end_year)[-2:]}"

        # FRESH / any other crop type: same year (e.g. '2025')
        return str(year_value)
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e


def _is_view_row_complete(row) -> bool:   
    """
    Check if a View_plant_matrix_actual row has all required fields non-null.

    Required fields:
        Plant_Id, growing_area_id, region_id, period_num, week_num,
        p_year, crop_type, storage_period, row_id.

    Args:
        row: ORM row from View_plant_matrix_actual.

    Returns:
        bool: True if all required fields are non-null, else False.
    """
    try:
        required_fields = (
            "Plant_Id",
            "growing_area_id",
            "region_id",
            "period_num",
            "week_num",
            "p_year",
            "crop_type",
            "storage_period",
            "row_id",
        )

        return all(
            getattr(row, f, None) is not None
            for f in required_fields
        )
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _fetch_erp_null_rows_for_slice_sql(
    db: Session, *, plant_id: int, ga_id: int, year: int, period: int, week: int
) -> List[Dict[str, Any]]:   
    """
    Fetch ERP rows for a given slice (year, period, week) from ERP table.

    Note:
        Uses UNLOAD_YEAR/UNL_DATE_PD/UNL_DATE_WK as slice keys and also
        pulls receipt fields to check for nulls later.

    Args:
        db (Session): Database session.
        plant_id (int): Plant ID (currently not used in WHERE).
        ga_id (int): Growing area ID (currently not used in WHERE).
        year (int): UNLOAD_YEAR filter.
        period (int): UNL_DATE_PD filter.
        week (int): UNL_DATE_WK filter.

    Returns:
        list[dict[str, Any]]: List of ERP rows as mapping dicts.
    """
    try:
    # Get ERP rows for the same VIEW slice. Slice is based on: UNLOAD_YEAR (→ p_year), UNL_DATE_PD (→ period_num), UNL_DATE_WK (→ week_num). But we ALSO pull RECEIPT_YEAR / REC_DATE_PD / REC_DATE_WK, so if those are NULL they will be flagged as invalid.
        sql = text(f"""
            SELECT
                plant_id,
                growing_area_id,
                UNLOAD_YEAR,
                UNL_DATE_PD,
                UNL_DATE_WK,
                RECEIPT_YEAR,
                REC_DATE_PD,
                REC_DATE_WK,
                CROP_TYPE,
                Quantity_Accepted_MCWT,
                BPA_NUMBER,
                RELEASE_NO,
                SHIPMENT,
                LINE_NO
            FROM {ERP_TABLE}
            WHERE UNLOAD_YEAR = :year
            AND UNL_DATE_PD  = :period
            AND UNL_DATE_WK  = :week
            AND UPPER(ISNULL(ShipToOrg, '')) <> 'US-PL-MEXICALI-TX-FLI';
        """)
        return list(
            db.execute(
                sql,
                {
                    "year": year,
                    "period": period,
                    "week": week,
                },
            )
            .mappings()
            .all()
        )
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _erp_row_has_required_null_from_mapping(row: Dict[str, Any]) -> bool:  
    """
    Check if any required ERP mapping field is NULL.

    Required:
        plant_id, growing_area_id, RECEIPT_YEAR,
        REC_DATE_PD, REC_DATE_WK, CROP_TYPE, crop_year (derived).

    Args:
        row (dict[str, Any]): ERP row as a mapping.

    Returns:
        bool: True if any required field is None, else False.
    """
    try:
        plant_id      = row.get("plant_id")
        ga_id         = row.get("growing_area_id")
        unload_year   = row.get("UNLOAD_YEAR")
        unload_period = row.get("UNL_DATE_PD")
        receipt_year  = row.get("RECEIPT_YEAR")
        rec_period    = row.get("REC_DATE_PD")
        rec_week      = row.get("REC_DATE_WK")
        crop_type     = row.get("CROP_TYPE")
        crop_year = _derive_crop_year(unload_year, unload_period, crop_type)
        required_values = [
            plant_id,
            ga_id,
            receipt_year,
            rec_period,
            rec_week,
            crop_type,
            crop_year,
        ]
        return any(v is None for v in required_values)
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _build_log_obj_from_erp_row(
    erp_row: Dict[str, Any],
    *,
    region_id: Optional[int],
    plant_name: Optional[str],
    ga_name: Optional[str],
) -> models.PlantMtrxNullLog:   
    """
    Build a PlantMtrxNullLog ORM object from an ERP row.

    Args:
        erp_row (dict[str, Any]): ERP row mapping.
        region_id (int | None): Region ID.
        plant_name (str | None): Plant name.
        ga_name (str | None): Growing area name.

    Returns:
        PlantMtrxNullLog: New log object (not yet committed).
    """
    try:
        receipt_year = erp_row.get("RECEIPT_YEAR")
        period = erp_row.get("REC_DATE_PD")
        week = erp_row.get("REC_DATE_WK")
        crop_type = erp_row.get("CROP_TYPE")
        crop_year = _derive_crop_year(receipt_year, period, crop_type)
        bpa_raw = erp_row.get("BPA_NUMBER")
        bpa_str = (
            str(bpa_raw).strip()[:500]
            if bpa_raw not in (None, "")
            else None
        )
        rel = _to_float_or_none(erp_row.get("RELEASE_NO"))
        shp = _to_float_or_none(erp_row.get("SHIPMENT"))
        line = _to_float_or_none(erp_row.get("LINE_NO"))
        return models.PlantMtrxNullLog(
            plant_id=erp_row.get("plant_id"),
            plant_name=plant_name,
            region_id=region_id,
            growing_area_id=erp_row.get("growing_area_id"),
            growing_area_name=ga_name,
            period=period,
            week=week,
            year=receipt_year,
            crop_type=crop_type,
            crop_year=crop_year,
            sumof_rec_potato=_to_float_or_none(
                erp_row.get("Quantity_Accepted_MCWT")
            ),
            bpa_number=bpa_str,
            release_no=rel,
            shipment=shp,
            line_no=line,
            erp_unique_id=_compose_erp_unique_id(bpa_str, rel, shp, line),
            active=True,
            created_time=_utcnow_naive(),
        )
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _find_existing_log(
    db: Session,
    *,
    erp_unique_id: str,
    plant_id: Optional[int],
    ga_id: Optional[int],
    year: Optional[int],
    period: Optional[int],
    week: Optional[int],
) -> Optional[models.PlantMtrxNullLog]:  
    """
    Find an existing null log for an ERP row.

    Logic:
        1. Try strong key: erp_unique_id + (year, period, week).
        2. If no erp_unique_id or not found, fallback to slice (plant, GA, year, period, week).

    Args:
        db (Session): Database session.
        erp_unique_id (str): Combined ERP identifier.
        plant_id (int | None): Plant ID.
        ga_id (int | None): Growing area ID.
        year (int | None): Year.
        period (int | None): Period.
        week (int | None): Week.

    Returns:
        PlantMtrxNullLog | None: Matching log row, if any.
    """
    try:
        q = db.query(models.PlantMtrxNullLog)
        if erp_unique_id and erp_unique_id != "###":
            rec = (
                q.filter(
                    models.PlantMtrxNullLog.erp_unique_id == erp_unique_id,
                    models.PlantMtrxNullLog.year == year,
                    models.PlantMtrxNullLog.period == period,
                    models.PlantMtrxNullLog.week == week,
                )
                .first()
            )
            if rec:
                return rec
        return (
            q.filter(
                models.PlantMtrxNullLog.plant_id == plant_id,
                models.PlantMtrxNullLog.growing_area_id == ga_id,
                models.PlantMtrxNullLog.year == year,
                models.PlantMtrxNullLog.period == period,
                models.PlantMtrxNullLog.week == week,
                models.PlantMtrxNullLog.active.in_([True, False]),
            )
            .first()
        )
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _upsert_null_log(
    db: Session,
    *,
    erp_row: Dict[str, Any],
    region_id: Optional[int],
    plant_name: Optional[str],
    ga_name: Optional[str],
) -> bool: 
    """
    Insert or update a null log for a given ERP row.

    Behavior:
        - If log exists for the ERP row/slice -> set active=True and update created_time.
        - If not exists -> insert new log.

    Args:
        db (Session): Database session.
        erp_row (dict[str, Any]): ERP row mapping.
        region_id (int | None): Region ID.
        plant_name (str | None): Plant name.
        ga_name (str | None): Growing area name.

    Returns:
        bool: True if inserted, False if updated.
    """
    try:
        obj = _build_log_obj_from_erp_row(
            erp_row, region_id=region_id, plant_name=plant_name, ga_name=ga_name
        )
        existing = _find_existing_log(
            db,
            erp_unique_id=(obj.erp_unique_id or ""),
            plant_id=obj.plant_id,
            ga_id=obj.growing_area_id,
            year=obj.year,
            period=obj.period,
            week=obj.week,
        )
        if existing:
            existing.active = True
            existing.created_time = _utcnow_naive()
            db.add(existing)
            return False
        db.add(obj)
        return True
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _is_erp_row_corrected_for_log(
    db: Session, log: models.PlantMtrxNullLog
) -> bool:   
    """
    Check if ERP row for a given log is now corrected (non-null required fields).

    Uses:
        BPA_Number, Line_No, Shipment, Release_No as lookup keys.

    Args:
        db (Session): Database session.
        log (PlantMtrxNullLog): Existing null log entry.

    Returns:
        bool:
            True  -> ERP row exists and all required fields are non-null.
            False -> ERP row missing or still has nulls.
    """
    try:
        if (
            not log.bpa_number
            or log.line_no is None
            or log.shipment is None
            or log.release_no is None
        ):
            return False
        sql = text(
            f"""
            SELECT TOP 1
                plant_id,
                growing_area_id,
                UNLOAD_YEAR,
                UNL_DATE_PD,
                UNL_DATE_WK,
                RECEIPT_YEAR,
                REC_DATE_PD,
                REC_DATE_WK,
                CROP_TYPE
            FROM {ERP_TABLE}
            WHERE BPA_Number = :bpa
            AND Line_No    = :line
            AND Shipment   = :shp
            AND Release_No = :rel;
        """
        )
        row = (
            db.execute(
                sql,
                {
                    "bpa": str(log.bpa_number).strip(),
                    "line": log.line_no,
                    "shp": log.shipment,
                    "rel": log.release_no,
                },
            )
            .mappings()
            .fetchone()
        )
        if not row:
            return False
        has_nulls = _erp_row_has_required_null_from_mapping(row)
        return not has_nulls
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

def _refresh_null_logs_for_slice(
    db: Session, *, period: int, week: int, year: int
) -> Dict[str, int]: 
    """
    Refresh null logs for a specific slice (period, week, year).

    Steps:
        - Get active logs for the slice.
        - For each log, re-check ERP row using BPA/Line/Shipment/Release.
        - Mark log inactive if ERP row is fully fixed; otherwise keep active.

    Args:
        db (Session): Database session.
        period (int): Period number.
        week (int): Week number.
        year (int): Year.

    Returns:
        dict: Summary counts:
            - "checked": logs processed.
            - "resolved": logs marked inactive.
            - "still_active": remaining active logs for the slice.
    """
    try:
        slice_logs: List[models.PlantMtrxNullLog] = (
            db.query(models.PlantMtrxNullLog)
            .filter(
                models.PlantMtrxNullLog.active == True,
                models.PlantMtrxNullLog.period == period,
                models.PlantMtrxNullLog.week == week,
                models.PlantMtrxNullLog.year == year,
            )
            .all()
        )
        if not slice_logs:
            return {"checked": 0, "resolved": 0, "still_active": 0}
        resolved_count = 0
        for row_log in slice_logs:
            try:
                erp_fixed = _is_erp_row_corrected_for_log(db, row_log)
                if erp_fixed:
                    row_log.active = False
                    row_log.created_time = _utcnow_naive()
                    db.add(row_log)
                    resolved_count += 1
                else:
                    row_log.created_time = _utcnow_naive()
                    db.add(row_log)
            except Exception:
                db.rollback()
                continue
        db.commit()
        remaining_active = (
            db.query(models.PlantMtrxNullLog)
            .filter(
                models.PlantMtrxNullLog.active == True,
                models.PlantMtrxNullLog.period == period,
                models.PlantMtrxNullLog.week == week,
                models.PlantMtrxNullLog.year == year,
            )
            .count()
        )
        return {
            "checked": len(slice_logs),
            "resolved": resolved_count,
            "still_active": remaining_active,
        }
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
