import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union, List, Any


class StrEnum(str, Enum):
    def __repr__(self):
        return self.value


class Scopes(StrEnum):
    SLEEP = 'https://www.googleapis.com/auth/fitness.sleep.read'
    ACTIVITY = 'https://www.googleapis.com/auth/fitness.activity.read'
    BLOOD_GLUCOSE = 'https://www.googleapis.com/auth/fitness.blood_glucose.read'
    BLOOD_PRESSURE = 'https://www.googleapis.com/auth/fitness.blood_pressure.read'
    BODY = 'https://www.googleapis.com/auth/fitness.body.read'
    BODY_TEMPERATURE = 'https://www.googleapis.com/auth/fitness.body_temperature.read'
    LOCATION = 'https://www.googleapis.com/auth/fitness.location.read'
    NUTRITION = 'https://www.googleapis.com/auth/fitness.nutrition.read'
    OXYGEN_SATURATION = 'https://www.googleapis.com/auth/fitness.oxygen_saturation.read'
    REPRODUCTIVE_HEALTH = 'https://www.googleapis.com/auth/fitness.reproductive_health.read'
    HEART_RATE = 'https://www.googleapis.com/auth/fitness.heart_rate.read'


class ModeURI(StrEnum):
    STEP_COUNT_DELTA = 'com.google.step_count.delta'
    SLEEP_SEGMENT = 'com.google.sleep.segment'
    HEART_MINUTES = 'com.google.heart_minutes'
    HEART_RATE_BPM = 'com.google.heart_rate.bpm'
    BODY_FAT_PERCENTAGE = 'com.google.body.fat.percentage'


class DTypes(StrEnum):
    INT = 'int'
    FLOAT = 'float'


class SleepTypes(StrEnum):
    UNSPECIFIED = "unspecified"
    AWAKE = "awake"
    GENERIC = "generic"
    OUT_OF_BED = "out_of_bed"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"


class Mode(StrEnum):
    STEPS = 'steps'
    SLEEP = 'sleep'
    MET = 'met'
    RHR = 'rhr'
    BODY_FAT = 'body_fat'

    @classmethod
    def get_sleep_types(cls, core=True) -> dict:
        sleep_type_dict = {
            0: SleepTypes.UNSPECIFIED,
            1: SleepTypes.AWAKE,
            2: SleepTypes.GENERIC,
            3: SleepTypes.OUT_OF_BED,
            4: SleepTypes.LIGHT,
            5: SleepTypes.DEEP,
            6: SleepTypes.REM,
        }
        if core:
            return {k: v for k, v in sleep_type_dict.items() if k in [2, 4, 5, 6]}
        return sleep_type_dict

    @classmethod
    def get_mode_uri(cls, mode):
        mode_uri_map = {
            cls.STEPS: ModeURI.STEP_COUNT_DELTA,
            cls.SLEEP: ModeURI.SLEEP_SEGMENT,
            cls.MET: ModeURI.HEART_MINUTES,
            cls.RHR: ModeURI.HEART_RATE_BPM,
            cls.BODY_FAT: ModeURI.BODY_FAT_PERCENTAGE,
        }
        return mode_uri_map[mode]

    @classmethod
    def get_dtype(cls, mode):
        mode_dtype_map = {
            cls.STEPS: DTypes.INT,
            cls.SLEEP: DTypes.INT,
            cls.MET: DTypes.FLOAT,
            cls.RHR: DTypes.FLOAT,
            cls.BODY_FAT: DTypes.FLOAT,
        }
        return mode_dtype_map[mode]


class MetricRes(BaseModel):
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    value: Optional[Union[int, float]] = Field(default=None)


class ResponseModel(BaseModel):
    x: List[str]
    y: List[Any]
