from enum import Enum


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
