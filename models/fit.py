import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union


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


class DataTypes(StrEnum):
    STEP_COUNT_DELTA = 'com.google.step_count.delta'
    SLEEP_SEGMENT = 'com.google.sleep.segment'
    HEART_MINUTES = 'com.google.heart_minutes'
    HEART_RATE_BPM = 'com.google.heart_rate.bpm'
    BODY_FAT_PERCENTAGE = 'com.google.body.fat.percentage'


class Mode(StrEnum):
    STEPS = 'steps'
    SLEEP = 'sleep'
    MET = 'met'
    RHR = 'rhr'
    BODY_FAT = 'body_fat'

    @classmethod
    def get_data_type(cls, mode):
        mode_data_type_map = {
            cls.STEPS: DataTypes.STEP_COUNT_DELTA,
            cls.SLEEP: DataTypes.SLEEP_SEGMENT,
            cls.MET: DataTypes.HEART_MINUTES,
            cls.RHR: DataTypes.HEART_RATE_BPM,
            cls.BODY_FAT: DataTypes.BODY_FAT_PERCENTAGE,
        }
        return mode_data_type_map[mode]


class MetricRes(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    value: Optional[Union[int, float]] = Field(default=None)
