import os
import random

from fastapi import HTTPException, APIRouter

from models.strugglebus import Event

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
    GPC       Consume Alpha-GPC
    LTH       Consume L-Theanine
    RSV       Consume Resveratrol
    OG3       Consume Omega-3 fish oil (EPA+DHA)
    DAY       Skip dinner (once a week)
    MON       Fast entire day (once a month)
    TRI       Fast 3 consecutive days (once a quarter)

    Args:
        event: Event

    Returns: bool, indicating the event outcome.
    """
    try:
        probability = float(os.getenv(event))
        return random.random() < probability
    except KeyError:
        raise HTTPException(status_code=400, detail=f"The event '{event}' is not supported. Please choose from the following supported events: {[str(e) for e in Event]}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")

