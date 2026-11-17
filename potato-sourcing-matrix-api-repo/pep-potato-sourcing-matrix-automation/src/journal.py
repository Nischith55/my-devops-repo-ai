from schemas import JournalEntrySchema, JournalEntryOwnerSchema
from models import journal_all,user_information,page_information,journal_ownership,growing_area,Ownership, region, View_ownership_journal_info
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database import get_db
from datetime import datetime
import pytz
from sqlalchemy import or_,text



router = APIRouter()

# General Journal

@router.post('/post_journal_entry', status_code=status.HTTP_201_CREATED)
async def create_journal(payload: JournalEntrySchema, db: Session = Depends(get_db)):
    """
    Create a journal entry (comment or one-level reply).

    Args:
        payload (JournalEntrySchema): Journal data including comment, user email, page, and optional parent id.
        db (Session): Database session.

    Returns:
        dict: API success status.

    Raises:
        HTTPException:
            - 404: If user/page not found.
            - 400: If parent comment invalid or nested reply attempted.
    """
    #Fetching user info
    try:
        user = db.query(user_information).filter(user_information.email == payload.email).first()
    except Exception:
        raise HTTPException(status_code = 404, detail = "User not found")
    #Fetching page info
    try:
        page = db.query(page_information).filter(page_information.page_name == payload.page_name).first()
    except Exception:
        raise HTTPException(status_code = 404, detail = "Page not found")
    #Parent comment checks
    parent_id = payload.parent_journal_id
    if parent_id is not None:
        parent = (
            db.query(journal_all)
            .filter(journal_all.journal_id == parent_id)
            .first()
        )
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="Parent comment not found"
            )
        if parent.parent_journal_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Nested replies are not allowed. You can only reply to main comments."
            )
        if parent.page_id != page.page_id:
            raise HTTPException(
                status_code=400,
                detail="Parent comment belongs to a different page"
            )
    #Timezone
    cst = pytz.timezone("US/Central")
    cst_time = datetime.now(cst).strftime("%Y-%m-%d %H:%M")
    new_journal_entry = journal_all(
                        comments = payload.comments,
                        page_name = page.page_name,
                        page_id = page.page_id,
                        user_first_name = str.title(user.first_name),
                        user_last_name = str.title(user.last_name),
                        email = payload.email,
                        user_id = user.user_id,
                        img_url = payload.img_url,
                        created_time = cst_time,
                        parent_journal_id=parent_id
    )
    db.add(new_journal_entry)
    db.commit()
    db.refresh(new_journal_entry)
    return {"status":"success"}

@router.get('/get_journal_entry')
async def get_journal_all(db: Session = Depends(get_db)): 
    """
    Fetch all general journal entries.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of journal records under 'data'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        records = db.query(journal_all).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
# Ownership Journal

@router.post('/post_journal_entry_owner', status_code=status.HTTP_201_CREATED)
async def create_journal_owner(payload: JournalEntryOwnerSchema, db: Session = Depends(get_db)):
    """
    Create an ownership journal entry (comment or one-level reply).

    Args:
        payload (JournalEntryOwnerSchema): Ownership comment data containing ownership and GA info.
        db (Session): Database session.

    Returns:
        dict: API success status.

    Raises:
        HTTPException:
            - 404: If user, ownership, GA, or region not found.
            - 400: If parent comment invalid or belongs to different ownership_id.
    """
    #Fetching user info
    try:
        user = db.query(user_information).filter(user_information.email == payload.email).first()
    except Exception:# pragma: no cover
        raise HTTPException(status_code = 404, detail = "User not found")
    #Fetching Ownership info
    try:
        owner = db.query(Ownership).filter(Ownership.ownership_id == payload.ownership_id).first()
    except Exception:# pragma: no cover
        raise HTTPException(status_code = 404, detail = "Ownership data not found")
    #Fetching area info
    try:
        if payload.growing_area_desc == None or payload.growing_area_name == None:
            area = db.query(growing_area).filter(growing_area.growing_area_id == owner.growing_area_id).first()
    except Exception:# pragma: no cover
        raise HTTPException(status_code = 404, detail = "GA not found")
    #Fetching Region
    try:
        reg = db.query(region).filter(region.region_id==area.region).first()
    except Exception:# pragma: no cover
        raise HTTPException(status_code = 404, detail = "Region not found")
    #Parent comment checks
    parent_id = payload.parent_journal_id
    if parent_id is not None:
        parent = (
            db.query(journal_ownership)
            .filter(journal_ownership.journal_id == parent_id)
            .first()
        )
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="Parent ownership comment not found"
            )
        if parent.parent_journal_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Nested replies are not allowed. You can only reply to main comments."
            )
        if parent.ownership_id != payload.ownership_id:
            raise HTTPException(
                status_code=400,
                detail="Parent comment belongs to different ownership_id"
            )
    #Timezone
    cst = pytz.timezone("US/Central")
    cst_time = datetime.now(cst).strftime("%Y-%m-%d %H:%M")
    #Filter_year
    crop_year = owner.crop_year
    years = crop_year.split("-")
    if len(crop_year)>4:
        filter_year_1 = years[0]
        filter_year_2 = int("20"+years[1])
    else:
        filter_year_1 = years[0]
        filter_year_2 = None
    new_journal_entry_owner = journal_ownership(
                                        comments = payload.comments,
                                        user_first_name =str.title(user.first_name),
                                        user_last_name = str.title(user.last_name),
                                        email = payload.email,
                                        user_id = user.user_id,
                                        ownership_id = payload.ownership_id,
                                        growing_area_name = area.growing_area_name,
                                        growing_area_desc = area.growing_area_desc,
                                        img_url = payload.img_url,
                                        region = reg.region_name,
                                        year = owner.year,
                                        crop_type = owner.crop_type,
                                        crop_year = owner.crop_year,
                                        created_time = cst_time,
                                        filter_year_1 = filter_year_1,
                                        filter_year_2 = filter_year_2,
                                        parent_journal_id=parent_id
    )
    db.add(new_journal_entry_owner)
    db.commit()
    db.refresh(new_journal_entry_owner)
    return {"status":"success"}

@router.get('/get_journal_entry_owner/{region}/{year}')
async def get_journal_owner(region:str,year:int ,db: Session = Depends(get_db)): 
    """
    Fetch ownership journal entries filtered by region and year.

    Args:
        region (str): Region filter (US, All Data, or specific region).
        year (int): Year filter.
        db (Session): Database session.

    Returns:
        dict: List of entries under 'data'.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        if region =="US":
            records = db.query(journal_ownership).filter(journal_ownership.region.in_(['East - US','Central - US','West - US']),
                                            or_(journal_ownership.filter_year_1 == year, journal_ownership.filter_year_2 == year)).all()
            return {"data": records}
        elif region == "All Data":
            records = db.query(journal_ownership).filter(or_(journal_ownership.filter_year_1 == year, journal_ownership.filter_year_2 == year)).all()
            return {"data":records}
        else:
            records = db.query(journal_ownership).filter(journal_ownership.region==region,
                                                     or_(journal_ownership.filter_year_1 == year, journal_ownership.filter_year_2 == year)).all()
            return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

# Jounal Ownership detailed info

@router.get('/get_journal_ownership_detailed_info')
async def get_journal_all(db: Session = Depends(get_db)): 
    """
    Fetch detailed ownership journal view records.

    Args:
        db (Session): Database session.

    Returns:
        dict: List of detailed journal entries.

    Raises:
        HTTPException: If query fails.
    """
    try:
        records = db.query(View_ownership_journal_info).all()
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
@router.get("/get_ownership_journal_common")
def get_ownership_journal_common(db: Session = Depends(get_db)):  
    """
    Fetch ownership journal data using TVF [dbo].[get_ownership_journal_data].

    Args:
        db (Session): Database session.

    Returns:
        dict: List of ownership records under 'data'.

    Raises:
        HTTPException: If SQL execution fails.
    """
    try:
        query = text("""SELECT * FROM [dbo].[get_ownership_journal_data]()""")
        results = db.execute(query).fetchall()
        data = [dict(row._mapping) for row in results]
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error querying TVF: {str(e)}") from e
    

