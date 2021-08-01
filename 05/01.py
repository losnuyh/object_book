from dataclasses import dataclass, field
from enum import Enum, unique

from typing import Union
from datetime import datetime, time, timedelta



@dataclass
class Screening:
    _movie: Movie
    _sequence: int
    _whenScreened: datetime

    def reserve(self, customer: Customer, audienceCount: int) -> Reservation:
        return Reservation(customer, self, self.calculateFee(audienceCount), audienceCount)

    def calculateFee(self, audienceCount: int) -> Money:
        return self._movie.calculateMovieFee(self) * audienceCount

    @property
    def whenScreened(self):
        return self._whenScreened
    
    @property
    def sequence(self):
        return self._sequence


class Customer:
    pass


@dataclass
class Movie:
    _title: str
    _duration: timedelta
    _fee: Money
    _discountConditions: list[DiscountCondition]
    
    _movieType: MovieType
    _discountAmount: Money
    _discountPercent: float

    def calculateMovieFee(self, screening: Screening) -> Money:
        if self._isDiscountable(screening):
            return self._fee - self._calculateDiscountAmount()
        return self._fee
    
    def _isDiscountable(self, screening: Screening) -> bool:
        for condition in self._discountConditions:
            if condition.isSatisfiedBy(screening):
                return True
        return False

    def _calculateDiscountAmount(self) -> Money:
        if self._movieType == MovieType.AMOUNT_DISCOUNT:
            return self._calculateAmountDiscountAmount()
        elif self._movieType == MovieType.PERCENT_DISCOUNT:
            return self._calculatePercentDiscountAmount()
        elif self._movieType == MovieType.NONE_DISCOUNT:
            return self._calculateNoneDiscountAmount()
        raise TypeError('movie type is wrong: {}'.format(self._movieType))
        
    def _calculateAmountDiscountAmount(self):
        return self._discountAmount

    def _calculatePercentDiscountAmount(self):
        return self._fee * self._discountPercent

    def _calculateNoneDiscountAmount(self):
        return Money.ZERO


@unique
class MovieType(Enum):
    AMOUNT_DISCOUNT = 'AMOUNT_DISCOUNT'
    PERCENT_DISCOUNT = 'PERCENT_DISCOUNT'
    NONE_DISCOUNT = 'NONE_DISCOUNT'


class Reservation:
    def __init__(self, *args, **kwargs):
        pass


@dataclass
class Money:
    _amount: int = field(default=0)

    @classmethod
    @property
    def ZERO(cls) -> Money:
        return cls(0)

    def __mul__(self, another: Union[Money, int]):
        return 1


@dataclass
class DiscountCondition:
    _type: DiscountConditionType
    _sequence: int
    _dayOfWeek: int
    _startTime: time
    _endTime: time

    def isSatisfiedBy(self, screening: Screening) -> bool:
        if self._type == DiscountConditionType.PERIOD:
            return self._isSatisfiedByPeriod(screening)
        elif self._type == DiscountConditionType.SEQUENCE:
            return self._isSatisfiedBySequence(screening)
        raise TypeError('discount condition type is wrong: {}'.format(self._type))
    
    def _isSatisfiedByPeriod(self, screening: Screening):
        return (self._dayOfWeek == screening.whenScreened.weekday()
                and self._startTime <= screening.whenScreened
                and self._endTime >= screening.whenScreened)

    def _isSatisfiedBySequence(self, screening: Screening):
        return self._sequence == screening.sequence


@unique
class DiscountConditionType(Enum):
    SEQUENCE = 'SEQUENCE'
    PERIOD = 'PERIOD'
