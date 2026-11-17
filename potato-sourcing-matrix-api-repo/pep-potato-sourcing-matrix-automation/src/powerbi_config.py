import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import PowerBIConfigJSON, powerbi_refresh_log
from schemas import PowerBIConfigIn, PowerBiRefreshLog

router = APIRouter()

@router.post('/create_refresh_logs')
def create_refresh_logs(payload: PowerBiRefreshLog, db: Session = Depends(get_db)):
    try:
        new_log = powerbi_refresh_log(**payload.dict())
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return {"status": "success","log_id": new_log.log_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{config_name}")
def get_config(config_name: str, db: Session = Depends(get_db)):
    """
    Fetch a JSON configuration by name, with optional Power BI schema validation.

    Args:
        config_name (str): Name of the configuration key.
        db (Session): Database session.

    Returns:
        dict | PowerBIConfigIn: Parsed JSON config. For 'powerbi_report_urls',
            returns a Pydantic-validated PowerBIConfigIn object.

    Raises:
        HTTPException:
            - 404: If config_name is not found.
            - 500: If stored JSON is invalid.
    """
    try:
        row = (
            db.query(PowerBIConfigJSON)
            .filter(PowerBIConfigJSON.config_name == config_name)
            .first()
        )
        if not row: # pragma: no cover
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config '{config_name}' not found",
            )
        try:
            payload = json.loads(row.config_json)
        except json.JSONDecodeError: # pragma: no cover
            raise HTTPException(
                status_code=500,
                detail="Invalid JSON stored in database",
            )
        # If it is Power BI config → validate using schema
        if config_name == "powerbi_report_urls":
            return PowerBIConfigIn(**payload)
        return payload # pragma: no cover
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.post("/{config_name}")
def upsert_config(config_name: str,config: PowerBIConfigIn ,db: Session = Depends(get_db)):
    """
    Create or update a JSON configuration by name, with optional schema validation.

    Args:
        config_name (str): Name of the configuration key.
        config (dict): Configuration payload to store.
        db (Session): Database session.

    Returns:
        dict: Status message and config_name.

    Raises:
        HTTPException:
            - 400: If Power BI config JSON fails schema validation.
    """
    # Validate using schema ONLY when needed
    try:
        if config_name == "powerbi_report_urls":
            try:
                validated = PowerBIConfigIn(**config)
                json_str = json.dumps(validated.dict())
            except Exception as e: # pragma: no cover
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid Power BI JSON format: {str(e)}"
                )
        else:
            json_str = json.dumps(config)
        # Fetch existing row
        row = (
            db.query(PowerBIConfigJSON)
            .filter(PowerBIConfigJSON.config_name == config_name)
            .first()
        )
        if row:
            row.config_json = json_str
        else: # pragma: no cover
            row = PowerBIConfigJSON(
                config_name=config_name,
                config_json=json_str,
            )
            db.add(row)
        db.commit()
        db.refresh(row)
        return {"status": "Success", "config_name": config_name}
    except Exception as e: # pragma: no cover
            raise HTTPException(status_code=400, detail=str(e))