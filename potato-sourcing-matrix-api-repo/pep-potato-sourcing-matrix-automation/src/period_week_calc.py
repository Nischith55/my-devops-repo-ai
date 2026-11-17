"""Period and week calculation API"""
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException

router = APIRouter()

var_format_dm = "%d/%m"
var_format_dmb = "%d/%b"


def calculate_period_and_week(year, specified_date: date, start_day=6, periods=13):
    """Determine the period and week for a given date within a fiscal/calendar year.

    The function computes the start and end dates for sequential periods (typically 13
    periods per year where the first 12 have 4 weeks and the 13th may have 4 or 5 weeks),
    then finds which period and which week within that period the provided date falls into.

    Args:
        year (int): The calendar year used as the basis for period calculation.
        specified_date (date): The date to locate within the period/week structure.
        start_day (int, optional): Weekday that marks the start of weeks where Monday=0,
            Sunday=6. Defaults to 6.
        periods (int, optional): Number of periods to divide the year into (usually 13).

    Returns:
        dict: A dictionary containing at least the following keys:
            - 'Period' (int): The period number (1..periods).
            - 'week' (int): The week number inside the period (1..4/5).
            - 'year' (int): The year the specified date belongs to.
            - 'Period_with_week' (str): A combined string like 'P3W2'.
            - 'Start_Date' (date): The start date of the period.
            - 'End_Date' (date): The end date of the period.

    Notes:
        If the specified_date falls outside the constructed periods for the supplied
        year, the function attempts to handle boundary conditions that may belong to
        the previous/next year. The function preserves existing behavior for edge cases.
    """
    try:
        start_date = date(year, 1, 1)
        start_day_of_week = start_date.weekday()
        offset = (start_day - start_day_of_week) % 7

        if offset != 0:
            start_date -= timedelta(days=(start_day_of_week + 1))

        period = 1

        for i in range(periods):
            end_date = start_date + timedelta(days=(4 * 7) - 1)
            if period == 13:
                next_year_start_date = date(year + 1, 1, 1)
                num_weeks_period_13 = (next_year_start_date - start_date).days // 7
                end_date += timedelta(days=(num_weeks_period_13 * 7) - (4 * 7))
            if start_date <= specified_date <= end_date:
                week = min(((specified_date - start_date).days // 7) + 1, 5)
                return {
                    'Period': period,
                    'week': week,
                    'year': specified_date.year,
                    'Period_with_week': f'P{period}W{week}',
                    'Start_Date': start_date,
                    'End_Date': end_date,
                }

            start_date = end_date + timedelta(days=1)
            period += 1
        last_week_start_date = date(year - 1, 12, 31) - timedelta(days=start_day_of_week)
        last_week_end_date = last_week_start_date + timedelta(days=(4 * 7) - 1)

        if last_week_start_date <= specified_date <= last_week_end_date:
            next_year_start_date = date(year, 1, 1)
            first_week_end_date = next_year_start_date + timedelta(days=(4 * 7) - 1)

            if next_year_start_date <= specified_date <= first_week_end_date: # pragma: no cover
                return {
                    'Period': 1,
                    'week': 1,
                    'year': specified_date.year,
                    'Period_with_week': 'P1W1',
                    'Start_Date': next_year_start_date,
                    'End_Date': first_week_end_date,
                }
        return {'Period': 1, 'week': 1, 'year': specified_date.year+1}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_period_dates(year, start_day=6, periods=13):
    """
    Build a list of period definitions (start/end dates and weeks) for a year.

    Each period normally has 4 weeks, and period 13 may have 4 or 5 weeks,
    depending on where the year boundary falls.
    """
    try:
        start_date = date(year, 1, 1)
        start_day_of_week = start_date.weekday()
        offset = (start_day - start_day_of_week) % 7

        if offset != 0:
            # align to the first week-start before/at the fiscal year
            start_date -= timedelta(days=(start_day_of_week + 1))

        period = 1
        period_dates = []

        for _ in range(periods):
            # default: 4 weeks (28 days inclusive)
            end_date = start_date + timedelta(days=(4 * 7) - 1)

            # period 13 stretches until the last week that touches next year's start
            if period == 13:
                next_year_start_date = date(year + 1, 1, 1)
                end_date = next_year_start_date - timedelta(days=1)

            # number of full weeks in this period (inclusive)
            num_weeks = (end_date - start_date).days // 7 + 1

            period_entry = {
                "Period": period,
                "Start_Date": start_date.strftime("%Y-%m-%d"),
                "End_Date": end_date.strftime("%Y-%m-%d"),
                "Weeks": [],
            }

            current_date = start_date
            week = 1

            # include all weeks fully covering the period range
            while current_date <= end_date and week <= num_weeks:
                period_entry["Weeks"].append({
                    "Week": week,
                    "Start_Date": current_date.strftime("%Y-%m-%d"),
                    "End_Date": (current_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                })
                current_date += timedelta(days=7)
                week += 1

            period_dates.append(period_entry)

            # next period starts the day after this period's end
            start_date = end_date + timedelta(days=1)
            period += 1

        return period_dates
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



def get_period_week_dates(year: int, period: int, week: int, start_day=6, periods=13):
    """Return the start and end date for a specific year, period and week.

    Args:
        year (int): Calendar year to calculate periods for.
        period (int): Period number to look up (1..periods).
        week (int): Week number within the period to look up.
        start_day (int, optional): Weekday used as the start of the week (Monday=0).
            Defaults to 6 (Sunday).
        periods (int, optional): Number of periods in the year (default 13).

    Returns:
        dict or None: A dictionary with keys 'Period', 'Week', 'Period_with_week',
            'Start_Date', 'End_Date' when found; otherwise `None` if no match.
    """
    try:
        all_data = calculate_period_dates(year, start_day, periods)  
        for p in all_data:
            if p["Period"] == period:
                for w in p["Weeks"]:
                    if w["Week"] == week:
                        return {
                            "Period": period,
                            "Week": week,
                            "Period_with_week": f"P{period}W{week}",
                            "Start_Date": w["Start_Date"],
                            "End_Date": w["End_Date"]
                        }
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_period_week_dates(year, start_day=6, periods=13):
    """Generate a compact list of period/week date ranges for display or selection.

    The returned structure uses short date formats (e.g., '01/Jan') for the
    `Start_Date` and `End_Date` fields and contains one entry per week across all
    periods. Each entry includes a combined `'Date'` range string.

    Args:
        year (int): Calendar year for which to build the period/week listing.
        start_day (int, optional): Weekday index that marks week start (Monday=0).
            Defaults to 6 (Sunday).
        periods (int, optional): Number of periods to consider (default 13).

    Returns:
        dict: A dictionary with a single key 'period_and_week' mapping to a list of
            weekly entries. Each entry includes 'Period', 'Week', 'Start_Date',
            'End_Date', and a 'Date' field combining start and end strings.
    """
    try:
        start_date = date(year, 1, 1)
        while start_date.weekday() != start_day:
            start_date -= timedelta(days=1)

        next_year_start = date(year + 1, 1, 1)
        while next_year_start.weekday() != start_day:
            next_year_start -= timedelta(days=1)

        total_days = (next_year_start - start_date).days
        total_weeks = total_days // 7

        weeks_per_period = [4] * periods
        if total_weeks > 52:
            weeks_per_period[-1] = 5
        else:
            weeks_per_period[-1] = 4

        result = []
        current_date = start_date
        for period in range(1, periods + 1):
            num_weeks = weeks_per_period[period - 1]

            for week in range(1, num_weeks + 1):
                start_str = current_date.strftime(var_format_dmb)
                end_str = (current_date + timedelta(days=6)).strftime(var_format_dmb)
                if current_date.year > year and period == 13:# pragma: no cover
                    break

                result.append({
                    "Period": period,
                    "Week": week,
                    "Period_with_week": f"P{period}W{week}",
                    "Start_Date": start_str,
                    "End_Date": end_str,
                    "Date": f"{start_str}-{end_str}"
                })
                current_date += timedelta(days=7)

        return {"period_and_week": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def calculate_period_week_start_end_date(year, start_day=6, periods=13):
    """Function to get year, period, and week level start & end dates in dd/mm - dd/mm format.

    This function calculates the start and end dates for each week within each period of a given year.
    Dates are formatted as day/month (e.g., 02/12 for December 2) and concatenated in the 'Date' field.

    Args:
        year (int): The year for which to calculate periods and weeks.
        start_day (int, optional): The weekday to start the year on (0=Monday, 6=Sunday). Defaults to 6 (Sunday).
        periods (int, optional): Number of periods in the year. Defaults to 13.

    Returns:
        dict: A dictionary with key 'period_and_week' containing a list of dictionaries, each representing a week.
              Each week dict includes 'Period', 'Week', 'Period_with_week', 'Start_Date', 'End_Date', and 'Date'.
    """
    try:
        start_date = date(year, 1, 1)
        while start_date.weekday() != start_day:
            start_date -= timedelta(days=1)

        next_year_start = date(year + 1, 1, 1)
        while next_year_start.weekday() != start_day:
            next_year_start -= timedelta(days=1)

        total_days = (next_year_start - start_date).days
        total_weeks = total_days // 7

        weeks_per_period = [4] * periods
        if total_weeks > 52:
            weeks_per_period[-1] = 5
        else:
            weeks_per_period[-1] = 4

        result = []
        current_date = start_date
        for period in range(1, periods + 1):
            num_weeks = weeks_per_period[period - 1]

            for week in range(1, num_weeks + 1):
                start_str = current_date.strftime(var_format_dm)
                end_str = (current_date + timedelta(days=6)).strftime(var_format_dm)
                if current_date.year > year and period == 13: # pragma: no cover
                    break

                result.append({
                    "Period": period,
                    "Week": week,
                    "Period_with_week": f"P{period}W{week}",
                    "Start_Date": start_str,
                    "End_Date": end_str,
                    "Date": f"{start_str} - {end_str}"
                })
                current_date += timedelta(days=7)

        return {"period_and_week": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def calculate_period_start_end_dates_fixed(year, start_day=6, periods=13):
    """Function to get start and end dates for all periods in a year, each with a fixed 28-day duration.

    This function calculates the start and end dates for each of the 13 periods in the given year.
    Each period is exactly 28 days long, starting from the adjusted start date based on the start_day.
    Dates are formatted as day/month (e.g., 29/12 for December 29) and concatenated in the 'Date' field.

    Args:
        year (int): The year for which to calculate periods.
        start_day (int, optional): The weekday to start the year on (0=Monday, 6=Sunday). Defaults to 6 (Sunday).
        periods (int, optional): Number of periods in the year. Defaults to 13.

    Returns:
        dict: A dictionary with key 'periods' containing a list of dictionaries, each representing a period.
              Each period dict includes 'Period', 'Start_Date', 'End_Date', and 'Date' (formatted as 'dd/mm - dd/mm').
    """
    try:
        start_date = date(year, 1, 1)
        while start_date.weekday() != start_day:
            start_date -= timedelta(days=1)

        result = []
        for period in range(1, periods + 1):
            end_date = start_date + timedelta(days=27)  # 28 days - 1 for inclusive
            start_str = start_date.strftime(var_format_dm)
            end_str = end_date.strftime(var_format_dm)
            result.append({
                "Period": period,
                "Start_Date": start_str,
                "End_Date": end_str,
                "Date": f"{start_str} - {end_str}"
            })
            start_date = end_date + timedelta(days=1)

        return {"periods": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/get_period_and_week")
async def get_period_and_week(year: int, date_input: date):
    """API endpoint: return period and week for a given date.

    Query parameters:
        year (int): Calendar year to use for period calculation.
        date_input (date): The date to locate.

    Returns:
        dict: JSON payload with key 'period_and_week' whose value is the output
        of `calculate_period_and_week`.
    """
    result = calculate_period_and_week(year, date_input)
    return {"period_and_week": result}


@router.get("/get_all_periods")
async def get_all_periods(year: int):
    """API endpoint: list all period start/end dates and their weeks for a year.

    Args:
        year (int): Calendar year to compute periods for.

    Returns:
        dict: JSON payload with key 'period_and_week' containing the list produced
        by `calculate_period_dates`.
    """
    period_dates = calculate_period_dates(year)
    return {"period_and_week": period_dates}

@router.get("/get_all_periodweek_start_end_dates")
async def get_pw_start_end_dates(year: int):
    """API endpoint: return compact period/week start and end dates for display.

    Args:
        year (int): Calendar year to compute the listing for.

    Returns:
        dict: JSON payload with key 'period_and_week' containing the result of
        `calculate_period_week_dates`.
    """
    period_dates = calculate_period_week_dates(year)
    return {"period_and_week": period_dates}

@router.get("/get_period_week_start_end_date")
async def get_pw_start_end_date(year: int,period:int,week:int):
    """API endpoint: return start/end date for a specific period-week.

    Args:
        year (int): Calendar year.
        period (int): Period number.
        week (int): Week number within the period.

    Returns:
        dict: JSON payload with key 'period_and_week' mapping to the result from
        `get_period_week_dates` (or `None` if not found).
    """
    period_week_dates = get_period_week_dates(year,period,week)
    return {"period_and_week": period_week_dates}

@router.get("/get_period_start_end_dates_fixed")
async def get_period_start_end_dates_fixed(year: int):
    """API endpoint: return start and end dates for all periods with fixed 28-day duration.

    This endpoint provides the start and end dates for each of the 13 periods in the specified year,
    where each period is exactly 28 days long. Dates are formatted as day/month (e.g., '29/12')
    and a combined 'Date' range string.

    Args:
        year (int): Calendar year to compute the period dates for.

    Returns:
        dict: JSON payload with key 'periods' containing a list of period dictionaries,
              each with 'Period', 'Start_Date', 'End_Date', and 'Date' (formatted as 'dd/mm - dd/mm').
    """
    period_dates = calculate_period_start_end_dates_fixed(year)
    return period_dates

@router.get("/get_period_week_start_end_dates")
async def pw_start_end_dates(year: int): 
    """API endpoint: return period/week start and end dates in dd/mm format.

    This endpoint provides a list of all weeks across all periods for the specified year,
    with dates formatted as day/month (e.g., '02/12') and a combined 'Date' range string.

    Args:
        year (int): Calendar year to compute the period/week dates for.

    Returns:
        dict: JSON payload with key 'period_and_week' containing the result of
        `calculate_period_week_start_end_date`.
    """
    period_dates = calculate_period_week_start_end_date(year)
    return {"period_and_week": period_dates}

@router.get("/has_five_weeks")
def calculate_week_num(year: int, period: int):
    """Determine whether the specified period contains five weeks.

    This helper computes the period boundaries for the provided year and returns
    whether the requested period is a five-week period. The function is typically
    used as a lightweight API handler at `/has_five_weeks`.

    Args:
        year (int): Calendar year to evaluate.
        period (int): Period number (1..13).

    Returns:
        bool or None: `True` if the given period contains five weeks, `False` if it
        contains four weeks, or `None` if the period cannot be determined.
    """
    try:
        start_date = date(year, 1, 1)
        start_day = 6
        start_day_of_week = start_date.weekday()
        offset = (start_day_of_week - start_day + 1) % 7
        if offset != 0:
            start_date += timedelta(days=7 - offset)
        period_dates = []
        for i in range(1, 14):
            end_date = start_date + timedelta(days=(4 * 7) - 1)
            if i == 13:
                next_year_start_date = date(year + 1, 1, 1)
                end_date = next_year_start_date - timedelta(days=1)
                num_weeks = (end_date - start_date).days // 7 + 1
            else:
                num_weeks = 4

            period_dates.append({
                'Period': i,
                'Start_Date': start_date.strftime("%Y-%m-%d"),
                'End_Date': end_date.strftime("%Y-%m-%d"),
                'Weeks': num_weeks,
                'Has_Five_Weeks': i == 13 and num_weeks == 5
            })

            start_date = end_date + timedelta(days=1)
        has_five_weeks = next((p['Has_Five_Weeks']
                               for p in period_dates if p['Period'] == period), None)
        return has_five_weeks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))