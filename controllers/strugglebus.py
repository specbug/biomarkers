import os
import random

from fastapi import HTTPException, APIRouter

from models.strugglebus import Event
from services.strugglebus import get_random_action_state

router = APIRouter()


@router.get("/do/{event}", response_model=bool)
def get_event_action_state(event: Event):
    """
    The fn uses a random number generator to simulate the challenging conditions that our ancestors faced during
    the hunter-gatherer era. The configuration assigns a daily probability to several events as shown in the table
    below. Based on the assigned probability, the fn returns a binary outcome that determines whether to proceed with
    the corresponding event on the measurement day.

    Event     Description
    ----------------------------------------------
    GPC       Consume Alpha-GPC \n
    LTH       Consume L-Theanine \n
    RSV       Consume Resveratrol \n
    OG3       Consume Omega-3 fish oil (EPA+DHA) \n
    DAY       Skip dinner (once a week) \n
    MON       Fast entire day (once a month) \n
    TRI       Fast 3 consecutive days (once a quarter) \n

    Args:
        event: Event

    Returns: bool, indicating the event outcome.
    """
    try:
        return get_random_action_state(event=event)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"The event '{event}' is not supported. Please choose from the following supported events: {[str(e) for e in Event]}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")

