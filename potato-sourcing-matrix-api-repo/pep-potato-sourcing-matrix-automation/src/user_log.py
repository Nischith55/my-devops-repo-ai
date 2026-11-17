import csv
import io
import models
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
import schemas
from database import get_db

router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED)
def user_log(payload: schemas.UserlogSchema, db: Session = Depends(get_db)):
    """
    Insert a new record into user_log table.

    Args:
        payload (UserlogSchema): User activity log details.
        db (Session): Database session dependency.

    Returns:
        dict: Success message on inserting log.

    Raises:
        HTTPException:
            - 400: Insert failure.
    """
    try:
        new_user_log = models.user_log(**payload.dict())
        db.add(new_user_log)
        db.commit()
        return {"status": "success", "result": "User log added Successfully !"}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/get_last_30_days_log')
def get_user_log(db: Session = Depends(get_db)):
    """
    Fetch user logs created within the last 30 days.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict:
            - data list of records if found
            - message stating no logs found if empty

    Raises:
        HTTPException:
            - 400: Query execution failure.
    """
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)

        records = db.query(models.user_log) \
            .filter(models.user_log.date >= thirty_days_ago.date()).all()
        if not records: # pragma: no cover
            return {"status": "success", "user_log": "no user log present"}
        return {"status": "success", "user_log": records}
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/export_last_30_days')
def export_last_30_days(db: Session = Depends(get_db)):
    """
    Export last 30 days of user logs as a downloadable CSV file.

    Args:
        db (Session): Database session dependency.

    Returns:
        StreamingResponse: CSV file download of log data.

    Raises:
        HTTPException:
            - 400: Data fetch or file generation failure.
    """
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)

        records = db.query(models.user_log) \
            .filter(models.user_log.date >= thirty_days_ago.date()).all()

        # Prepare CSV data
        csv_data = []
        for record in records:
            csv_data.append([record.id, record.email, record.date_time, record.date])

        # Generate CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'email', 'login-ddate-time', 'date'])
        writer.writerows(csv_data)

        # Create a streaming response for downloading the CSV file
        output.seek(0)
        csv_bytes = output.getvalue().encode('utf-8')
        return StreamingResponse(iter([csv_bytes]), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=last_30_days_records.csv"})
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))
