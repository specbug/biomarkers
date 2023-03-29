from enum import Enum


class StrEnum(str, Enum):
    def __repr__(self):
        return self.value


class Event(StrEnum):
    GPC = "GPC"
    LTH = "LTH"
    RSV = "RSV"
    OG3 = "OG3"
    DAY = "DAY"
    MON = "MON"
    TRI = "TRI"
