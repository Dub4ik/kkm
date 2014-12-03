# -*- coding: utf-8 -*-
"""
 Copyright (c) 2005, 2012
 @author: Marat Khayrullin <xmm.dev@gmail.com>
"""
import atexit
import os
import logging

from .common import TaxArea, DiscountValueType, DiscountSign
from .. import exceptions as err


log = logging.getLogger('kkm')

# Возможные значения переменной checkType в методе OpenCheck
kkm_sell_check = 0
kkm_StornoSell_check = 1
kkm_return_check = 2
kkm_StornoReturn_check = 3
kkm_Buy_check = 4
kkm_StornoBuy_check = 5
kkm_annulate_check = 6

# Report Types
kkm_clearing_report = 1
kkm_z_report = 2
kkm_x_report = 3
kkm_department_report = 4
kkm_cashier_report = 5
kkm_goods_report = 6
kkm_hour_report = 7
kkm_quantity_report = 8


class KkmMeta(type):
    __registry = {}

    def __init__(cls, name, base, dict):
        super().__init__(name, base, dict)
        if name != 'KKM':
            cls.__registry[name] = cls
            log.debug('Registered kkm module {}'.format(name))

    @classmethod
    def auto_create(mcs, port_params=None, password=0):
        if not port_params:
            if os.name == 'posix':
                port_params = {'port': '/dev/kkm', 'baudrate': 9600}
            elif os.name == 'nt':
                port_params = {'port': 2, 'baudrate': 9600}
            else:
                log.critical('Не поддерживаемая платформа')
                raise err.CommonError('Не поддерживаемая платформа')
        for kkm in list(mcs.__registry.values()):
            try:
                log.debug('KkmMeta.autoCreate type={} device={}'.format(kkm, port_params))
                return kkm(port_params, password)
            except err.KKMException:
                pass
        log.critical('Нет связи с ККМ или неизвестная модель ККМ')
        raise err.CommonError('Нет связи с ККМ или неизвестная модель ККМ')


class KKMDriver(metaclass=KkmMeta):
    """
    Абстактный базовый класс поддержки Контрольно-Кассовых Машин.
    """
    # Значения специфичные для конкретных моделей ККМ
    _passwordLen = 4  # Длина пароля
    _moneyWidth = 10  # Кол-во разрядов
    _quantityWidth = 10  # Кол-во разрядов
    _stringMax = 20  # Максимальное значение
    _displayMax = 20  # Максимальная длина строки для вывода на дисплей пользователя
    _moneyMax = 9999999999  # Максимальное значение (учитывая _moneyPrecision)
    _quantityMax = 9999999999  # Максимальное значение (учитывая _quantityPrecision)

    def __init__(self, params):
        self._device = None
        self._params = params
        self._str_max = 0
        self._klishe_max = 0
        self._klishe_len = 0
        self._test_only = 0
        self._check_cash = 1
        # Флаг выполнения команд в режиме регистрации с предварительной проверкой исполнимости
        self._pre_test = 1

    def open_device(self):
        atexit.register(self.close_device)

    def close_device(self):
        try:
            self._device.close()
            self._device = None
        except:
            log.critical('Can\'t close KKM device.')
            raise err.CommonError('Can\'t close KKM device.')

    def is_opened(self):
        return self._device is not None

    def is_registration_mode(self):
        pass

    def is_x_report_mode(self):
        pass

    def is_z_report_mode(self):
        pass

    def is_programming_mode(self):
        pass

    def is_inspector_mode(self):
        pass

    def is_check_open(self):
        pass

    def set_registration_mode(self, password):
        pass

    def set_x_report_mode(self, password):
        pass

    def set_z_report_mode(self, password):
        pass

    def set_programming_mode(self, password):
        pass

    def set_inspector_mode(self, password):
        pass

    def is_test_only_mode(self):
        return self._test_only

    def is_pre_test_mode(self):
        return self._pre_test

    def is_check_cash_mode(self):
        return self._check_cash

    def set_test_only_mode(self, enabled):
        self._test_only = enabled

    def set_pre_test_mode(self, enabled):
        self._pre_test = enabled

    def set_check_cash_mode(self, enabled):
        self._check_cash = enabled

    # gettypekkm
    # state

    def get_kkm_id(self):
        pass

    def get_password_len(self):
        return self._passwordLen

    def get_money_width(self):
        return self._moneyWidth

    def get_quantity_width(self):
        return self._quantityWidth

    def get_string_max(self):
        return self._str_max

    def get_display_string_max(self):
        return self._displayMax

    def get_klishe_len(self):
        return self._klishe_len

    def get_clishe_max_len(self):
        return self._klishe_max

    def open_check(self, check_type):
        pass

    def sell(self, name, price, quantity, department):
        pass

    def buy_return(self, name, price, quantity):
        pass

    def annulate(self):
        pass

    def storno(self):
        pass

    def payment(self, sum, pay_type=None):
        pass

    def discount(self, count, area=TaxArea.WHOLE_CHECK, discount_type=DiscountValueType.PERCENT,
                 sign=DiscountSign.DISCOUNT):
        pass

    def close_check(self):
        pass

    def cash_income(self, sum):
        pass

    def cash_outcome(self, sum):
        pass

    def report(self, type):
        pass

    def get_last_summary(self):
        pass

    def get_check_num(self):
        pass

    def get_check_sum(self):
        pass

    def print_string(self, msg):
        pass

    def print_to_display(self, msg):
        pass

    def open_cash_box(self):
        pass

    def set_check_header(self):
        pass

    def set_check_footer(self):
        pass

    def cash_pay_type(self):
        pass

    def credit_pay_type(self):
        pass

    def tara_pay_type(self):
        pass

    def card_pay_type(self):
        pass

    def programming(self, **args):
        """
        Args <1>стр.74:
        kkmNumber [1-99] - Номер ККМ в магазине
        multiDepart ['multi','single'] - Одна или несколько секций
          payTypes (credit,tara,card)
          useArea ['trade'|'service'|'restrant'|'oil']
          checkFont [0/1] normal/condenced
          ctrltapeFont [0/1] normal/condenced
        taxType ['deny'|'all'|'sell'] запрещено, на весь чек, на каждую продажу
        departName [0|1] deny/allow print
        printNotClearedSum [0|1|2] deny/allow/с момента регистрации
        makeIncasation [0|1]
          printBrightness [0..3] min/средняя/норма/высокая
        Args <1>стр.78:
        """
        pass

    def set_cashier_password(self, cashier, password):
        pass

    def set_admin_password(self, password):
        pass

    def set_sys_admin_password(self, password):
        pass

    def set_klishe(self, klishe):
        pass

    def set_depart_name(self, depart, name):
        pass

    def set_tax_rate(self, tax, value):
        pass