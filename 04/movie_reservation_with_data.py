from enum import Enum, auto
from datetime import timedelta


class Movie:
    title: str
    runningTime: timedelta
    fee: Money
    discountConditions: list[DiscountCondition]
    _movieType: MovieType
    _discountAmount: Money
    _discountPercent: float


class MovieType(Enum):
    AMOUNT_DISCOUNT = auto()
    PERCENT_DISCOUNT = auto()
    NONE_DISCOUNT = auto()
                                             
