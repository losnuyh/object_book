# No detailed implementation.
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta, time


class Money:
    @classmethod
    @property
    def ZERO(cls) -> Money:
        return cls.wons(0)

    @staticmethod
    def wons(amount: float) -> Money:
        return Money(amount)

    def __init__(self, amount: float):
        self.amount = amount

    def __add__(self, amount: Money) -> Money:
        return Money(self.amount + amount.amount)

    def __sub__(self, amount: Money) -> Money:
        return Money(self.amount - amount.amount)

    def __mul__(self, percent: float) -> Money:
        return Money(self.amount * percent)

    def __lt__(self, other) -> bool:
        return self.amount < other.amount

    def __le__(self, other) -> bool:
        return self.amount <= other.amount

    def __gt__(self, other) -> bool:
        return self.amount > other.amount

    def __ge__(self, other) -> bool:
        return self.amount >= other.amount

    def __eq__(self, other) -> bool:
        return self.amount == other.amount

    def __str__(self) -> str:
        return '{} won'.format(self.amount)


class Customer:
    pass


class Screening:
    def __init__(self, movie, sequence: int, whenScreened: datetime):
        self._movie = movie
        self._sequence = sequence
        self._whenScreened = whenScreened

    @property
    def whenScreened(self) -> datetime:
        return self._whenScreened

    def isSequence(self, sequence: int) -> bool:
        return self._sequence == sequence

    def getMovieFee(self) -> Money:
        return self._movie.fee;

    def reserve(self, customer, audienceCount: int) -> Reservation:
        return Reservation(customer, self, self.calculateFee(audienceCount), audienceCount)

    def calculateFee(self, audienceCount: int) -> Money:
        return self._movie.calculateMovieFee(self).times(audienceCount)


class Reservation:
    def __init__(self, customer: Customer, screening: Screening, fee: Money, audienceCount: int):
        self._customer = customer
        self._screening = screening
        self._fee = fee
        self._audienceCount = audienceCount


class Movie:
    def __init__(self, title: str, runningTime: timedelta, fee: Money, discountPolicy: DiscountPolicy):
        self._title = title
        self._runningTime = runningTime
        self._fee = fee
        self._discountPolicy = discountPolicy

    @property
    def fee(self) -> Money:
        return self._fee

    def calculateMovieFee(self, screening: Screening) -> Money:
        return self.fee - self._discountPolicy.calculateDiscountAmount(screening)

    def changeDiscountPolicy(self, discountPolicy: DiscountPolicy):
        self._discountPolicy = discountPolicy


class DiscountPolicy(metaclass=ABCMeta):
    def __init__(self, *conditions: DiscountCondition):
        self._conditions = conditions

    def calculateDiscountAmount(self, screening: Screening):
        for condition in self._conditions:
            if condition.isSatisfiedBy(screening):
                return self.getDiscountAmount(screening)
        return Money.ZERO

    @abstractmethod
    def getDiscountAmount(self, screening: Screening) -> Money:
        pass


class AmountDiscountPolicy(DiscountPolicy):
    def __init__(self, discountAmount: Money, *conditions: DiscountCondition):
        super().__init__(*conditions)
        self._discountAmount = discountAmount

    def getDiscountAmount(self, screening: Screening) -> Money:
        return self._discountAmount


class PercentDiscountPolicy(DiscountPolicy):
    def __init__(self, percent: float, *conditions: DiscountCondition):
        super().__init__(*conditions)
        self._percent = percent

    def getDiscountAmount(self, screening: Screening) -> Money:
        return screening.getMovieFee() * self._percent


class NoneDiscountPolicy(DiscountPolicy):
    def getDiscountAmount(self, screening: Screening) -> Money:
        return Money.ZERO # type: ignore


class DiscountCondition(metaclass=ABCMeta):
    @abstractmethod
    def isSatisfiedBy(self, screening: Screening) -> bool:
        pass


class SequenceCondition(DiscountCondition):
    def __init__(self, sequence: int):
        self._sequence = sequence

    def isSatisfiedBy(self, screening: Screening) -> bool:
        return screening.isSequence(self._sequence)


class PeriodCondition(DiscountCondition):
    def __init__(self, dayOfWeek: int, startTime: time, endTime: time):
        self._dayOfWeek = dayOfWeek
        self._startTime = startTime
        self._endTime = endTime

    def isSatisfiedBy(self, screening: Screening) -> bool:
        return (screening.whenScreened.weekday() == self._dayOfWeek and
                self._startTime <= screening.whenScreened.time() and
                self._endTime >= screening.whenScreened.time())



if __name__ == '__main__':
    avatar = Movie("아바타",
                   timedelta(minutes=120),
                   Money.wons(10_000),
                   AmountDiscountPolicy(
                       Money.wons(800),
                       SequenceCondition(1),
                       SequenceCondition(10),
                       PeriodCondition(
                           0,
                           time(hour=10, minute=0),
                           time(hour=11, minute=59),
                       ),
                       PeriodCondition(
                           3,
                           time(hour=10, minute=0),
                           time(hour=20, minute=59),
                       ),
                   )
    )

    titanic = Movie("타이타닉",
                    timedelta(minutes=180),
                    Money.wons(11_000),
                    PercentDiscountPolicy(
                        0.1,
                        PeriodCondition(
                            1,
                            time(hour=14),
                            time(hour=16, minute=59),
                        ),
                        SequenceCondition(2),
                        PeriodCondition(
                            3,
                            time(hour=10),
                            time(hour=13, minute=59),
                        ),
                    )
    )

    starWars = Movie("스타워즈",
                     timedelta(minutes=21),
                     Money.wons(10_000),
                     NoneDiscountPolicy())
