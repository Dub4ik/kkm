# -*- coding: utf-8 -*-
from enum import Enum


class TaxArea(Enum):
    WHOLE_CHECK = 0
    BY_POSITION = 1


class DiscountValueType(Enum):
    PERCENT = 0
    SUM = 1


class DiscountSign(Enum):
    DISCOUNT = 0  # Скидка
    INCREASE = 1  # Надбавка
