import logging

from dateutil.parser import parse
from fastapi import HTTPException, APIRouter
from typing import Optional

from models.fit import ResponseModel, Mode
from services.fit import FitClient

router = APIRouter()
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


@router.get('/data/{marker}', response_model=Optional[ResponseModel])
async def get_marker_data(marker: Mode, start_date: str, end_date: str):
    """
    Retrieve biomarker data for the specified time range [start_date, end_date].
    The data is aggregated daily and represented by the start date, especially in cases of cross-day data like sleep.

    Args:

        marker: Marker.
        start_date: start date (inclusive).
        end_date: end date (inclusive)

    Returns: ResponseModel.

        x: List[str] // dates
        y: List[Any] // values
    """
    try:
        start_date = parse(start_date)
        end_date = parse(end_date)
        logger.info(f'Fetching {marker} data from {start_date} to {end_date}...')
        fit_client = FitClient()
        if marker == Mode.SLEEP:
            res = fit_client.get_sleep(start_date=start_date, end_date=end_date)
        elif marker == Mode.STEPS:
            res = fit_client.get_steps(start_date=start_date, end_date=end_date)
        elif marker == Mode.MET:
            res = fit_client.get_met_hours(start_date=start_date, end_date=end_date)
        elif marker == Mode.RHR:
            res = fit_client.get_rhr(start_date=start_date, end_date=end_date)
        elif marker == Mode.BODY_FAT:
            res = fit_client.get_body_fat(start_date=start_date, end_date=end_date)
        else:
            raise KeyError(f'Marker "{marker}" is unsupported.')
        return res
    except Exception as exc:
        logger.exception('Failed to fetch marker data.', exc_info=exc)
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(exc)}')
