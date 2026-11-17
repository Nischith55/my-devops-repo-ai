from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from database import get_db

router = APIRouter()


@router.get('/')
def filtered_market(db: Session = Depends(get_db)):
    """
    Fetch all active market–flex mappings.

    Args:
        db (Session): Database session dependency.

    Returns:
        dict: Active MarketFlexMapping records under key `MarketFlexMapping`.

    Raises:
        HTTPException:
            - 200: If no records are present for any year.
            - 400: On query execution failure.
    """
    filtered_market = db.query(models.MarketFlexMapping).filter(
            models.MarketFlexMapping.status == "ACTIVE").all()
    if not filtered_market:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="No market flex value is present for this year.")
    return {"status": "success", "MarketFlexMapping": filtered_market}



@router.get('/year/{year}')
def filtered_market_year(year: int, db: Session = Depends(get_db)):
    """
    Fetch active market–flex mappings filtered by ownership year.

    Args:
        year (int): Target ownership year (current or previous).
        db (Session): Database session dependency.

    Returns:
        dict: Filtered MarketFlexMapping records under key `MarketFlexMapping`.

    Raises:
        HTTPException:
            - 200: If no records are present for the given year.
            - 400: On query execution failure.
    """
    
    filtered_market = db.query(models.MarketFlexMapping) \
        .join(models.Ownership,
            models.Ownership.ownership_id == models.MarketFlexMapping.ownership_id) \
        .filter(models.MarketFlexMapping.status == "ACTIVE",
                or_(models.Ownership.year == year, models.Ownership.year == year - 1)) \
        .all()
    if not filtered_market:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No market flex value is present for this year.")
    return {"status": "success", "MarketFlexMapping": filtered_market}



def total_ship_calculation(ownership_id: str, db: Session = Depends(get_db)):
    """
    Recalculate and update total_ship for a given ownership record.

    Formula:
        total_ship = to_ship + market_and_flex

    Args:
        ownership_id (str): Ownership identifier.
        db (Session): Database session dependency.

    Raises:
        HTTPException:
            - 400: On query or update failure.
    """
    try:
        ownership_record = db.query(models.Ownership) \
            .filter(models.Ownership.ownership_id == ownership_id).first()

        ownership_record.total_ship = ownership_record.to_ship + ownership_record.market_and_flex
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post('/market_flex')
def update_market_flex(payload: schemas.MarketFlexPayload,
                       db: Session = Depends(get_db)):
    """
    Create or update market–flex mappings and refresh ownership totals.

    Behavior:
        - For each row_id in the payload:
            * Update existing MarketFlexMapping or insert a new one.
            * Set status to ACTIVE/INACTIVE based on market_flex_value.
        - Aggregate market_flex_value per ownership and update
          Ownership.market_and_flex.
        - Recalculate Ownership.total_ship using total_ship_calculation.

    Args:
        payload (MarketFlexPayload): List of market–flex updates.
        db (Session): Database session dependency.

    Returns:
        dict: Status message indicating success.

    Raises:
        HTTPException:
            - 400: On insert/update/aggregation failure.
    """
    update_market_flex = payload.Payload_MarketFlex
    try:
        for item in update_market_flex:
            record = db.query(models.MarketFlexMapping).filter(
                models.MarketFlexMapping.row_id == item.row_id,
                models.MarketFlexMapping.row_id.in_(
                    [item.row_id for item in update_market_flex])).first()

            if record is not None:
                if item.market_flex_value == 0:
                    db.query(models.MarketFlexMapping).filter(
                        models.MarketFlexMapping.row_id == item.row_id).update(
                        {models.MarketFlexMapping.market_flex_value: item.market_flex_value,
                         models.MarketFlexMapping.status: "INACTIVE"}, synchronize_session='fetch')
                else:
                    db.query(models.MarketFlexMapping).filter(
                        models.MarketFlexMapping.row_id == item.row_id).update(
                        {models.MarketFlexMapping.market_flex_value: item.market_flex_value,
                         models.MarketFlexMapping.status: "ACTIVE"}, synchronize_session='fetch')
            else:
                if item.market_flex_value == 0:  # pragma: no cover
                    payload = {
                        "row_id": item.row_id,
                        "growing_area_id": item.growing_area_id,
                        "grower_id": item.grower_id,
                        "ownership_id": item.ownership_id,
                        "status": "INACTIVE",
                        "market_flex_value": item.market_flex_value}
                    new_record = models.MarketFlexMapping(**payload)
                    db.add(new_record)
                else:  # pragma: no cover
                    payload = {
                        "row_id": item.row_id,
                        "growing_area_id": item.growing_area_id,
                        "grower_id": item.grower_id,
                        "ownership_id": item.ownership_id,
                        "status": "ACTIVE",
                        "market_flex_value": item.market_flex_value}
                    new_record = models.MarketFlexMapping(**payload)
                    db.add(new_record)
            db.commit()

            market_value = db.query(models.MarketFlexMapping.ownership_id,
                                    func.sum(models.MarketFlexMapping.market_flex_value).label('total_sum')) \
                .filter(models.MarketFlexMapping.growing_area_id == item.growing_area_id) \
                .group_by(models.MarketFlexMapping.ownership_id).all()

            # Updating the extension column in Ownership table
            for value in market_value: # pragma: no cover
                db.query(models.Ownership).filter(
                    models.Ownership.ownership_id == value.ownership_id).update(
                    {models.Ownership.market_and_flex: value.total_sum},
                    synchronize_session=False)
                # print(agg_value)
            db.commit()
            total_ship_calculation(item.ownership_id, db)

        return {"status": "success"}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))