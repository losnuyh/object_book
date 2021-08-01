# No detailed implementation.
from __future__ import annotations

from abc import ABCMeta, abstractmethod
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


@dataclass # type: ignore
class Movie(metaclass=ABCMeta):
    _title: str
    _runningTime: timedelta
    _fee: Money
    _discountConditions: list[DiscountCondition]

    def calculateMovieFee(self, screening: Screening) -> Money:
        if self._isDiscountable(screening):
            return self._fee - self.calculateDiscountAmount()
        return self._fee

    def _isDiscountable(self, screening: Screening) -> bool:
        for condition in self._discountConditions:
            if condition.isSatisfiedBy(screening):
                return True
        return False

    @abstractmethod
    def calculateDiscountAmount(self):
        pass


@dataclass
class AmountDiscountMovie(Movie):
    _discountAmount: Money

    def calculateDiscountAmount(self):
        return self._discountAmount


@dataclass
class PercentDiscountMovie(Movie):
    _percent: float

    def calculateDiscountAmount(self):
        return self._fee * self._discountPercent


class NoneDiscountMovie(Movie):
    def calculateDiscountAmount(self):
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


class DiscountCondition(metaclass=ABCMeta):
    @abstractmethod
    def isSatisfiedBy(self, screening: Screening) -> bool:
        pass


@dataclass
class PeriodCondition(DiscountCondition):
    _dayOfWeek: int
    _startTime: time
    _endTime: time

    def isSatisfiedBy(self, screening: Screening) -> bool:
        return (self._dayOfWeek == screening.whenScreened.weekday()
                and self._startTime <= screening.whenScreened
                and self._endTime >= screening.whenScreened)


@dataclass
class SequenceCondition(DiscountCondition):
    _sequence: int

    def isSatisfiedBy(self, screening: Screening) -> bool:
        return self._sequence == screening.sequence


@unique
class DiscountConditionType(Enum):
    SEQUENCE = 'SEQUENCE'
    PERIOD = 'PERIOD'
