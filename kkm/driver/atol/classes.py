# -*- coding: utf-8 -*-
"""
 Copyright (c) 2005, 2012
 @author: Marat Khayrullin <xmm.dev@gmail.com>
 Использованные документы:
 <1>: Атол технологии
       Руководство программиста: Протокол работы ККМ v2.4
 <2>: Атол технологии
       Руководство программиста: Общий драйвер ККМ v.5.1
       (версия док-ции: 1.7 от 15.05.2002)
 <3>: Курское ОАО "Счетмаш"
       Инструкция по программированию РЮИБ.466453.528 И15
       Машина электронная контрольно-кассовая Феликс-Р Ф
<4>: Атол технологии
       Приложение к протоколу работы ККМ (2009)
"""
import codecs
import logging
import sys
import serial
import time
from datetime import datetime

import ipark_lib.hardware.codecs.common as ipark_codecs
from .. import base
from ...exceptions import *
from kkm.driver.atol import control_symbols as symbol, constants as const, commands as cmd, modes


try:
    codecs.lookup('cp437-vkp80')
except LookupError:
    codecs.register(ipark_codecs.search_function)

log = logging.getLogger('kkm')

# Битовые значения переменной flags (<1>стр.34)
_atol_TestOnly_flag = 0x01
_atol_CheckCash_flag = 0x02

# Коды режима отчетов без гашения
_atol_X_report = 1
_atol_Department_report = 2
_atol_Cashier_report = 3
_atol_Goods_report = 4
_atol_Hour_report = 5
_atol_Quantity_report = 7

# Тип закрытия чека (<1>стр.38)
_atol_cash_payment = 1  # наличными
_atol_type2_payment = 2  # кредитом
_atol_type3_payment = 3  # тарой
_atol_type4_payment = 4  # пл. картой

# Параметры ККМ различных моделей
# type.model: (name, type, model, majorver, minorver, build, maxstring, klishelen, klishemax)
_models_table = {
    '1.14': ('Феликс-Р Ф', 1, 14, 2, 3, 2185, 20, 20, 8),
    '1.24': ('Феликс-Р К', 1, 24, 2, 4, 3700, 38, 38, 8),
    '1.41': ('PayVKP-80K', 1, 24, 2, 4, 3700, 42, 42, 8),
}
MODEL_PAYVKP_80K = '1.41'
_atol_StringMax_idx = 6
_atol_KlisheLen_idx = 7
_atol_KlisheMax_idx = 8

exception_table = {
    1: KKMCommonErr('Контрольная лента обработана без ошибок.'),
    8: KKMWrongMoneyErr(),
    10: KKMWrongQuantityErr(),
    15: KKMCommonErr('Повторная скидка на операцию не возможна'),
    20: KKMCommonErr('Неверная длина'),
    26: KKMCommonErr('Отчет с гашением прерван. Вход в режим заблокирован'),
    30: KKMCommonErr('Вход в режим заблокирован'),
    102: KKMIncorectModeErr(),
    103: KKMOutOfPaperErr(),
    106: KKMCommonErr('Неверный тип чека'),
    114: KKMCommonErr('Сумма платежей меньше суммы чека'),
    117: KKMCommonErr('Переполнение суммы платежей'),
    122: KKMCommonErr('Данная модель ККМ не может выполнить команду'),
    123: KKMCommonErr('Неверная величина скидки / надбавки'),
    127: KKMCommonErr('Переполнение при умножении'),
    134: KKMLowPaymentErr(),
    136: KKMNeedZReportErr(),
    140: KKMCommonErr('Неверный пароль'),
    143: KKMDoubleZReportErr(),
    151: KKMCommonErr('Подсчет суммы сдачи не возможен'),
    154: KKMCommonErr('Чек закрыт - операция невозможна'),
    155: KKMCommonErr('Чек открыт - операция невозможна'),
    156: KKMCommonErr('Смена открыта - операция невозможна'),
    190: KKMCommonErr('Необходимо провести профилактические работы'),
    201: KKMCommonErr('Нет связи с внешним устройством'),
    209: KKMCommonErr('Перегрев головки принтера'),
    210: KKMCommonErr('Ошибка обмена с ЭКЛЗ на уровне интерфейса I2O')
}

_check_types = {
    base.kkm_sell_check: 1,
    base.kkm_return_check: 2,
    base.kkm_annulate_check: 3
}


def check_exception(response):
    try:
        if response[0] != ord('U'):
            log.error('Wrong response {}'.format(response))
            raise KKMUnknownAnswerErr()
        else:
            code = response[1]
            if code > 0:
                raise_exception(code)
            return response
    except IndexError:
        log.error(str(KKMUnknownAnswerErr))
        raise KKMUnknownAnswerErr


def raise_exception(code):
    if code != 0:
        ex = exception_table.get(code)
        if ex:
            log.error('Device returned error {}: {}'.format(code, ex))
            raise exception_table[code]
        else:
            log.error('Device returned error {}.'.format(code))
            raise KKMUnknownErr()


def _escape(data):
    return data.replace(symbol.DLE, symbol.DLE + symbol.DLE) \
        .replace(symbol.ETX, symbol.DLE + symbol.ETX)


def _unescape(data):
    return data.replace(symbol.DLE + symbol.ETX, symbol.ETX) \
        .replace(symbol.DLE + symbol.DLE, symbol.DLE)


def _calc_crc(data):
    crc = 0
    for i in range(len(data)):
        crc ^= data[i]
    return crc


def str2atol(txt, length):
    """
    Преобразование строки в формат ккм.
    C локализацией и дополнением пробелами до значения length.
    """
    txt = txt.encode('cp866')
    ctrl_num = 0
    for c in txt:
        if c < ord(' '):
            ctrl_num += 1
    length += ctrl_num
    if len(txt) < length:
        txt = txt.ljust(length)
    return txt[:length]


def atol2str(txt):
    """
    Преобразование строки из формата ккм (локализация).
    """
    return txt.decode('cp866')


def number2atol(number, width=2):
    """
    Преобразование числа в формат ккм.
    Если width > длины number - дополнить слева нулями,
    иначе срезать конец.
    Ширина в знаках, а не в байтах!!!
    <1>стр.17 Запихать по 2 цифры в один байт.
    """
    number = str(number)
    if (width % 2) != 0:
        width += 1
    if len(number) >= width:
        number = number[:width]
    else:
        number = number.zfill(width)
    result = []
    for i in range(0, len(number), 2):
        result += [int(number[i]) << 4 | int(number[i + 1])]
    return bytes(result)


def atol2number(number):
    """
    Преобразование числа из формата ккм.
    <1>стр.17
    """
    val = b''
    for i in range(len(number)):
        dec = number[i]
        if dec < 10:
            zero = b'0'
        else:
            zero = b''
        val = val + zero + hex(int(dec)).encode('ascii')[2:]
    return int(val)


def date2atol(date_):
    return date_


def atol_datetime_to_native_datetime(data):
    year = atol2number(data[0:1])
    month = atol2number(data[1:2])
    day = atol2number(data[2:3])
    hour = atol2number(data[3:4])
    minute = atol2number(data[4:5])
    second = atol2number(data[5:6])
    return datetime(year, month, day, hour, minute, second)


class Driver(base.KKMDriver):
    """
    Драйвер к ККМ с протоколом обмена компании 'Атол технологии'(версии. 2.4)
    """

    def __init__(self, params, password=0):
        super().__init__(params)
        self.__flags = _atol_CheckCash_flag  # Флаги режима регистрации
        self._kkm_password = number2atol(password, 4)
        self._str_max = 0
        self._klishe_max = 0
        self._klishe_len = 0

    def _money2atol(self, money, width=None):
        """
        Преобразование денежной суммы в формат ккм (МДЕ).
        ширина в знаках, а не в байтах!!!
        <1>стр.17
        """
        if width is None:
            width = self._moneyWidth
        elif width > self._moneyWidth:
            log.error(str(
                KKMWrongMoneyErr('Затребована ширина превышающая максимально допустимое значение')))
            raise KKMWrongMoneyErr('Затребована ширина превышающая максимально допустимое значение')
        if money > self._moneyMax:
            log.error(str(
                KKMWrongMoneyErr('Число типа "money" превышает максимально допустимое значение')))
            raise KKMWrongMoneyErr('Число типа "money" превышает максимально допустимое значение')
        return number2atol(int(money), width)

    @staticmethod
    def _atol2money(money):
        """
        Преобразование из формата ккм (МДЕ) в денежную сумму.
        <1>стр.17
        """
        return atol2number(money)

    def _quantity2atol(self, quantity, width=None):
        """
        Преобразование количества в формат ккм.
        ширина в знаках, а не в байтах!!!
        <1>стр.17
        """
        if width is None:
            width = self._quantityWidth
        elif width > self._quantityWidth:
            log.error('Required quantity number length greater than max allowed.')
            raise KKMWrongQuantityErr()
        if quantity > self._quantityMax:
            log.error('Quantoty value greater than max allowed.')
            raise KKMWrongQuantityErr(
                'Число типа "quantity" превышает максимально допустимое значение.')
        quantity = str(quantity).encode('ascii')
        return number2atol(int(quantity), width)

    @staticmethod
    def _atol2quantity(quantity):
        """
        Преобразование из формата ккм (МДЕ) в количество.
        <1>стр.17
        """
        return atol2number(quantity)

    def set_device_model(self, model=None):
        if model is None:
            device_type = self.get_device_info()
            log.debug('Device type info: {}'.format(device_type))
            model_id = str(device_type['type']) + '.' + str(device_type['model'])
        model_info = _models_table.get(model)
        if not model_info:
            log.error('Unknow device {}'.format(model_id))
            raise KKMUnknownModelErr()
        self._str_max = model_info[_atol_StringMax_idx]
        self._klishe_max = model_info[_atol_KlisheMax_idx]
        self._klishe_len = model_info[_atol_KlisheLen_idx]

    def open_device(self):
        """
        Проверить наличие блокировки устройства
        Заблокировать или вывалиться с ошибкой
        """
        log.debug('=== Open device ===')
        try:
            self._device = serial.Serial(**self._params)
            super().open_device()
        except:
            raise KKMCommonErr('System error at opening KKM device')
        if not self._device:
            raise KKMCommonErr('Unknown error at opening KKM device')

    def _set_readtimeout(self, timeout):
        log.debug('Set read timeout {}.'.format(timeout))
        self._device.setTimeout(timeout)

    def _atol_send_data_sequence(self, data):
        device = self._device
        command = data[self._passwordLen // 2]
        log.debug('Command: {}, Data: {}.'.format(command, data))
        data = _escape(data) + symbol.ETX
        crc = bytes((_calc_crc(data),))
        data = symbol.STX + data + crc
        try:
            # Активный передатчик
            for conection_attempt in range(const.CON_ATTEMPTS):
                is_answered = False
                for enq_attempt in range(const.ENQ_ATTEMPTS):
                    log.debug('Sending ENQ #{}.'.format(enq_attempt + 1))
                    device.write(symbol.ENQ)
                    self._set_readtimeout(const.T1_TIMEOUT)
                    response = device.read(1)
                    log.debug('Recieved: {}.'.format(symbol.get_symbol_name(response)))
                    if len(response) < 1:
                        log.debug('No data.')
                        continue
                    if response == symbol.ACK:
                        return self._retrieve_data(command, data)
                    elif response == symbol.NAK:
                        log.debug('Sleep {}'.format(const.T1_TIMEOUT))
                        time.sleep(const.T1_TIMEOUT)
                        continue
                    elif response == symbol.ENQ:
                        log.debug('Sleep {}'.format(const.T7_TIMEOUT))
                        time.sleep(const.T7_TIMEOUT)
                        break
                    else:
                        log.debug('Garbage detected, ignored.')
                if not is_answered:
                    device.write(symbol.EOT)
                    log.error('Failed {} attempts of sending ENQ.'.format(const.ENQ_ATTEMPTS))
                    raise KKMConnectionErr
            device.write(symbol.EOT)
        except OSError as e:  # for Linux
            exc = sys.exc_info()
            if exc[1].errno == 19:
                log.error(KKMNoDeviceErr())
                raise KKMNoDeviceErr()
            else:
                log.error(e)
                raise KKMConnectionErr()
        except Exception as e:  # win32file raise common exception, not OSError as Linux
            log.error(e)
            raise KKMConnectionErr()
        log.error(KKMConnectionErr())
        raise KKMConnectionErr()

    def _retrieve_data(self, command, data):
        device = self._device
        for ack_attempt in range(const.ACK_ATTEMPTS):
            log.debug('Sending data #{}: {}.'.format(ack_attempt + 1, data))
            device.write(data)
            self._set_readtimeout(const.T3_TIMEOUT)
            response = device.read(1)
            log.debug('Recieved: {}.'.format(symbol.get_symbol_name(response)))
            if len(response) == 0:
                log.debug('No data.')
                continue
            if response == symbol.ENQ and ack_attempt == 0:
                log.debug('ENQ recieved at first place, ignored.')
                continue
            elif response == symbol.ACK or response == symbol.ENQ:
                if response == symbol.ACK:
                    device.write(symbol.EOT)
                    # Активный приемник
                    for con_attempt in range(const.CON_ATTEMPTS):
                        log.debug('Sending CON #{}.'.format(con_attempt + 1))
                        self._set_readtimeout(const.get_t5_timeout_for(command))
                        response = device.read(1)
                        log.debug('Recieved: {}.'.format(symbol.get_symbol_name(response)))
                        if len(response) == 0:
                            log.error('KKM no answer.')
                            raise KKMNoAnswerErr()
                        if response == symbol.ENQ:
                            break
                for ack_attempt_2 in range(const.ACK_ATTEMPTS):
                    log.debug('Sending ACK #{}.'.format(ack_attempt_2 + 1))
                    device.write(symbol.ACK)
                    self._set_readtimeout(const.T2_TIMEOUT)
                    for stx_attempt in range(const.STX_ATTEMPTS):
                        log.debug('STX waiting #{}.'.format(stx_attempt + 1))
                        response = device.read(1)
                        log.debug('Recieved: {}.'.format(symbol.get_symbol_name(response)))
                        if len(response) == 0:
                            log.error('No data.')
                            raise KKMNoAnswerErr
                        elif response == symbol.ENQ:
                            break
                        elif response != symbol.STX:
                            continue
                        else:  # (ch == symbol.STX):
                            log.debug('Reading until ETX.')
                            full_response = b''
                            prev_symbol = b''
                            no_data_retry_num = 0
                            self._set_readtimeout(const.T6_TIMEOUT)
                            while True:
                                response = device.read(1)
                                if len(response) == 0:
                                    if no_data_retry_num >= const.NO_DATA_RETRY_COUNT:
                                        log.error('No answer.')
                                        raise KKMNoAnswerErr()
                                    else:
                                        log.debug('No data, retry.')
                                        no_data_retry_num += 1
                                    continue
                                else:
                                    if response == symbol.ETX and prev_symbol != symbol.DLE:
                                        log.debug('[ETX detected]')
                                        break
                                    full_response += response
                                    prev_symbol = response
                            log.debug('Recieved data: {}.'.format(symbol.humanize(full_response)))
                            response = device.read(1)  # Ждем CRC
                            log.debug('CRC data: {}.'.format(symbol.get_symbol_name(response)))
                            if len(response) == 0:
                                log.debug('No data.')
                                break
                            calculated_crc = _calc_crc(full_response + symbol.ETX)
                            recieved_crc = ord(response)
                            log.debug('Calculated/recieved CRC: {}/{}'
                                      .format(calculated_crc, recieved_crc))
                            if calculated_crc != recieved_crc:
                                log.error('CRC does not match, sending NAK.')
                                device.write(symbol.NAK)
                                break
                            else:
                                self._set_readtimeout(const.T4_TIMEOUT)
                                log.debug('ACK sending.')
                                device.write(symbol.ACK)
                                log.debug('ACK sent')
                                response = device.read(1)
                                log.debug('Recieved: {}.'
                                          .format(symbol.get_symbol_name(response)))
                                if response == symbol.EOT or len(response) == 0:
                                    log.debug('[EOT detected]')
                                    return _unescape(full_response)
                                elif response == symbol.STX:
                                    continue
                                else:
                                    self._set_readtimeout(2)  # _atol_T???_timeout
                                    response = device.read(1)
                                    if len(response) == 0:
                                        return _unescape(full_response)
                                    else:
                                        break
                    if stx_attempt >= const.STX_ATTEMPTS - 1:
                        log.error('KKM no answer.')
                        raise KKMNoAnswerErr()
                device.write(symbol.EOT)
                log.error('Failed {} attempts of sending ACK.'.format(const.ACK_ATTEMPTS))
                raise KKMNoAnswerErr
        device.write(symbol.EOT)
        log.error('Failed {} attempts of sending data.'.format(const.ACK_ATTEMPTS))
        raise KKMConnectionErr

    # Запросы

    def get_last_summary(self):
        """Запрос последнего сменного итога.
        <1>стр.28
        """
        try:
            data = self._kkm_password + cmd.GET_LAST_SUMMARY
            return self._atol2money(check_exception(self._atol_send_data_sequence(data))[2:])
        except IndexError:
            raise KKMUnknownAnswerErr

    def get_status(self):
        log.info('=== get_status:BEGIN ===')
        response = self._atol_send_data_sequence(self._kkm_password + cmd.GET_STATUS)
        try:
            if response[0] != ord('D'):
                raise KKMUnknownAnswerErr()
            cashier = atol2number(response[1:2])
            site = atol2number(response[2:3])
            kkm_datetime = atol_datetime_to_native_datetime(response[3:9])
            flags = response[9]
            mashine = atol2number(response[10:14])
            model = response[14]
            version = str(response[15]) + '.' + str(response[16])
            mode = response[17] & 0x0F
            submode = (response[17] & 0xF0) >> 4
            check = atol2number(response[18:20])
            smena = atol2number(response[20:22])
            check_state = response[22]
            check_sum = atol2number(response[23:28])
            dot = response[28]
            port = response[29]
            result = {'cashier': cashier, 'site': site, 'datetime': kkm_datetime, 'flags': flags,
                      'mashine': mashine, 'model': model, 'version': version, 'mode': mode,
                      'submode': submode, 'check': check, 'smena': smena,
                      'check_state': check_state, 'check_sum': check_sum, 'dot': dot, 'port': port}
            log.info('Device status: {}'.format(result))
            log.info('=== get_status:END ===')
            return result
        except IndexError:
            raise KKMUnknownAnswerErr()

    def get_kkm_id(self):
        """Запрос уникального идентификатора ККМ.
        """
        return self.get_status()[5]

    def get_check_num(self):
        """Запрос текущего номера чека.
        """
        return self.get_status()[10]

    def get_check_sum(self):
        """Запрос суммы текущего чека.
        """
        return self.get_status()[12]

    def get_current_state(self):
        """Запрос кода состояния (режима) ККМ.

        Result: mode, submode, printer, paper
        <1>стр.28
        """
        ans = self._atol_send_data_sequence(self._kkm_password + cmd.GET_CURRENT_STATE)
        try:
            mode = ans[1] & 0x0F
            submode = (ans[1] & 0xF0) >> 4
            printer = (ans[2] & 0x02) == 1
            paper = (ans[2] & 0x01) == 1
        except IndexError:
            raise KKMUnknownAnswerErr
        return mode, submode, printer, paper

    def get_current_mode(self):
        """Запрос режима ККМ
        """
        return self.get_current_state()[0]

    def get_device_info(self):
        """
        Получение типа устройства.
        Result: error, protocol, type, model, mode,
        majorver, minorver, codepage, build, name
        <1>стр.28,63
        """
        log.info('=== get_device_info:BEGIN ===')
        response = self._atol_send_data_sequence(self._kkm_password + cmd.GET_DEVICE_TYPE)
        try:
            if response[0] != 0:
                raise_exception(response[0])
            error = response[0]
            protocol = response[1]
            type_ = response[2]
            model = response[3]
            mode = (response[4] << 8) | response[5]
            majorver = response[6]
            minorver = response[7]
            codepage = response[8]
            build = atol2number(response[9:11])
            name = response[11:]
        except IndexError:
            raise KKMUnknownAnswerErr
        result = {'error': error, 'protocol': protocol, 'type': type_, 'model': model, 'mode': mode,
                  'majorver': majorver, 'minorver': minorver, 'codepage': codepage, 'build': build,
                  'name': name.decode('cp866')}
        log.info('Device info: {}'.format(result))
        log.info('=== get_device_info:END ===')
        return result

    def reset_mode(self):
        """
        Выход из текущего режима.
        """
        check_exception(self._atol_send_data_sequence(self._kkm_password + cmd.RESET_MODE))

    def set_mode(self, mode, password):
        """
        Установить режим.
        <1>стр.19
        """
        log.debug('=== Set mode {}/{} ==='.format(mode, password))
        current_mode = self.get_current_mode()
        if mode != current_mode:
            if current_mode != modes.SELECT:
                self.reset_mode()
            check_exception(self._atol_send_data_sequence(self._kkm_password +
                                                          cmd.SET_MODE +
                                                          number2atol(mode) +
                                                          number2atol(password, 8)))

    def is_registration_mode(self):
        return self.get_current_mode() == modes.REGISTRATION

    def is_x_report_mode(self):
        return self.get_current_mode() == modes.X_REPORT

    def is_z_report_mode(self):
        return self.get_current_mode() == modes.Z_REPORT

    def is_programming_mode(self):
        return self.get_current_mode() == modes.PROGRAMMING

    def is_inspector_mode(self):
        return self.get_current_mode() == modes.INSPECTOR

    def is_check_open(self):
        return self.get_status()[12] != 0

    def set_registration_mode(self, password):
        self.set_mode(modes.REGISTRATION, password)

    def set_x_report_mode(self, password):
        self.set_mode(modes.X_REPORT, password)

    def set_z_report_mode(self, password):
        self.set_mode(modes.Z_REPORT, password)

    def set_programming_mode(self, password):
        self.set_mode(modes.PROGRAMMING, password)

    def set_inspector_mode(self, password):
        # self.SetMode(_atol_Inspector_mode, password)
        raise KKMNotImplementedErr

    # Общие команды

    def print_string(self, txt, wrap=False):
        """
        Печать строки на кассовой ленте
        """
        log.debug('=== Pring string: \'{}\', wrap={} ==='.format(txt, wrap))
        idx = 0
        slen = len(txt)
        smax = self.get_string_max()
        while idx <= slen:
            data = b''.join((self._kkm_password, cmd.PRINT_STRING,
                             str2atol(txt[idx:idx + smax], smax)))
            check_exception(self._atol_send_data_sequence(data))
            idx += smax
            if not wrap:
                break

    def print_to_display(self, txt):
        """
        Вывод сообщения на дисплей покупателя
        """
        data = ''.join((self._kkm_password, cmd.PRINT_TO_DISPLAY, number2atol(1),
                        str2atol(txt, self.get_display_string_max())))
        check_exception(self._atol_send_data_sequence(data))


    def open_cash_box(self):
        data = self._kkm_password + cmd.OPEN_CASH_BOX
        check_exception(self._atol_send_data_sequence(data))


    # Команды режима регистрации <1>стр.34

    def get_reg_flags(self):
        flags = 0
        if self.is_test_only_mode():
            flags |= _atol_TestOnly_flag
        if self.is_check_cash_mode():
            flags |= _atol_CheckCash_flag
        return flags

    def cash_pay_type(self):
        return _atol_cash_payment

    def credit_pay_type(self):
        return _atol_type2_payment

    def tara_pay_type(self):
        return _atol_type3_payment

    def card_pay_type(self):
        return _atol_type4_payment

    def cash_income(self, sum):
        """Внесение денег."""
        data = ''.join((self._kkm_password,
                        cmd.CASH_INCOME,
                        number2atol(self.get_reg_flags()),
                        self._money2atol(sum)))
        check_exception(self._atol_send_data_sequence(data))

    def cash_outcome(self, sum):
        """
        Выплата денег (инкасация).
        """
        data = ''.join((self._kkm_password,
                        cmd.CASH_OUTCOME,
                        number2atol(self.get_reg_flags()),
                        self._money2atol(sum)))
        check_exception(self._atol_send_data_sequence(data))

    def open_check(self, check_type=base.kkm_sell_check):
        """
        Открыть Чек.
        <2>стр.44,<3>стр.37
        """
        log.debug('=== Open check {} ==='.format(check_type))
        data = b''.join((self._kkm_password,
                         cmd.OPEN_CHECK,
                         number2atol(self.get_reg_flags()),
                         number2atol(_check_types[check_type])))
        check_exception(self._atol_send_data_sequence(data))

    def sell(self, name, price, quantity, department):
        """
        Продажа.
        Если режим TestOnly включен - выполнить только проверку возможности исполнения.
        Если режим PreTestMode включен - выполнить с проверкой возможности исполнения.
        <1>стр.35
        """
        log.info('=== Sell \'{}\', price: {}, quantity: {}, department: {} ==='
                 .format(name, price, quantity, department))
        if self.is_pre_test_mode() or self.is_test_only_mode():
            data = b''.join((self._kkm_password, cmd.SELL,
                             number2atol(self.get_reg_flags() | _atol_TestOnly_flag),
                             self._money2atol(price), self._quantity2atol(quantity),
                             number2atol(department)))
            check_exception(self._atol_send_data_sequence(data))
        if self.is_test_only_mode():
            return
        self.print_string(name)
        data = b''.join((self._kkm_password, cmd.SELL, number2atol(self.get_reg_flags()),
                         self._money2atol(price), self._quantity2atol(quantity),
                         number2atol(department)))
        check_exception(self._atol_send_data_sequence(data))

    def buy_return(self, name, price, quantity):
        """
        Возврат.
        Если режим TestOnly включен - выполнить только проверку возможности исполнения.
        Если режим PreTestMode включен - выполнить с проверкой возможности исполнения.
        <1>стр.37
        """
        if self.is_pre_test_mode() or self.is_test_only_mode():
            check_exception(
                self._atol_send_data_sequence(self._kkm_password + cmd.RETURN_ + \
                                              number2atol(
                                                  self.get_reg_flags() | _atol_TestOnly_flag) + \
                                              self._money2atol(price) + self.quantity2atol(
                    quantity))
            )
        if self.is_test_only_mode():
            return
        self.print_string(name)
        check_exception(
            self._atol_send_data_sequence(self._kkm_password + cmd.RETURN_ + \
                                          number2atol(self.get_reg_flags()) + self._money2atol(
                price) + \
                                          self.quantity2atol(quantity))
        )


    def discount(self, count, area=base.kkm_Sell_dis,
                 type_=base.kkm_Sum_dis, sign=base.kkm_Discount_dis):
        """Начисление скидки/надбавки.

        <1>стр.37
        """
        log.info('Discount : ' + str(count) + '\t' + number2atol(count))
        if area == base.kkm_Sell_dis:
            area = 1
        else:
            area = 0
        if type_ == base.kkm_Procent_dis:
            type_ = 0
            count = number2atol(count * 100, 5)  # 100.00%
        else:
            type_ = 1
            count = self._money2atol(count)
        if sign == base.kkm_Discount_dis:
            sign = 0
        else:
            sign = 1
        check_exception(
            self._atol_send_data_sequence(self._kkm_password + _atol_Discount_cmd + \
                                          number2atol(self.get_reg_flags()) + \
                                          number2atol(area) + \
                                          number2atol(type) + \
                                          number2atol(sign) + \
                                          count)
        )


    def annulate(self):
        check_exception(self._atol_send_data_sequence(self._kkm_password + cmd.ANNULATE))


    def payment(self, sum, pay_type=None):
        """
        Оплата чека с подсчетом суммы сдачи.
        <1>стр.38
        """
        atol_sum = self._money2atol(sum)
        log.info('=== Payment: {} ({}) ==='.format(sum, atol_sum))
        if pay_type is None:
            pay_type = self.cash_pay_type()
        data = b''.join((self._kkm_password,
                         cmd.CLOSE_CHECK,
                         number2atol(self.get_reg_flags()),
                         number2atol(pay_type),
                         atol_sum))
        check_exception(self._atol_send_data_sequence(data))

        # Команды режима отчетов без гашения


    def report_wo_clearing(self, report_type):
        data = self._kkm_password + cmd.X_REPORT + number2atol(report_type)
        check_exception(self._atol_send_data_sequence(data))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 2 and submode == 2:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
            if mode == 2 and submode == 0:
                if printer:
                    raise KKMPrinterConnectionErr
                if paper:
                    raise KKMOutOfPaperErr
                else:
                    return


    # Команды режима отчетов c гашением

    def clearing_report(self):
        check_exception(self._atol_send_data_sequence(self._kkm_password + cmd.CLEARING_REPORT))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 3 and submode == 2:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
            if mode == 3 and submode == 0:
                if printer:
                    raise KKMPrinterConnectionErr
                if paper:
                    raise KKMOutOfPaperErr
                else:
                    return
            else:
                raise KKMReportErr


    def z_report_hold(self):
        """
        Включить режим формирования отложенных Z отчётов.
        Result: кол-во свободных полей для записи Z-отчётов
        <4>стр.9
        """
        data = self._kkm_password + cmd.Z_REPORT_TO_MEM
        response = check_exception(self._atol_send_data_sequence(data))
        try:
            return response[2]
        except IndexError:
            raise KKMUnknownAnswerErr


    def z_report_unhold(self):
        """
        Распечатать отложенные Z-отчёты и отключить режим отложенных Z отчётов.
        """
        check_exception(self._atol_send_data_sequence(self._kkm_password + cmd.Z_REPORT_FROM_MEM))


    def z_report(self):
        check_exception(self._atol_send_data_sequence(self._kkm_password + cmd.Z_REPORT))
        mode, submode, printer, paper = self.get_current_state()
        log.debug(str(('00', mode, submode, printer, paper)))
        while mode == 3 and submode == 2:
            log.debug(str('32-0'))
            time.sleep(const.REPORT_TIMEOUT)
            log.debug(str('32-1'))
            mode, submode, printer, paper = self.get_current_state()
            log.debug(str(('32-2', mode, submode, printer, paper)))
        if mode == 7 and submode == 1:
            log.debug(str('71-0'))
            while mode == 7 and submode == 1:
                log.debug(str('71-1'))
                time.sleep(const.REPORT_TIMEOUT)
                log.debug(str('71-2'))
                mode, submode, printer, paper = self.get_current_state()
                log.debug(str(('71-3', mode, submode, printer, paper)))
            return
        else:
            log.debug(str(('??', mode, submode, printer, paper)))
            if mode == 3 and submode == 0:
                # ZReport finished but an exception will raise
                raise KKMFiscalMemoryOverflowErr
            if printer:
                raise KKMPrinterConnectionErr
            if paper:
                raise KKMOutOfPaperErr
            else:
                raise KKMReportErr


    def common_clearing(self):
        check_exception(self._atol_send_data_sequence(self._kkm_password + cmd.COMMON_CLEAR))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 3 and submode == 6:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
            if mode == 3 and submode == 0:
                if printer:
                    raise KKMPrinterConnectionErr
                if paper:
                    raise KKMOutOfPaperErr
                else:
                    return
            else:
                raise KKMReportErr


    def report(self, report_type):
        report_table = {
            base.kkm_Clearing_report: (self.clearing_report, None),
            base.kkm_Z_report: (self.z_report, None),
            base.kkm_X_report: (self.report_wo_clearing, 1),
            base.kkm_Department_report: (self.report_wo_clearing, 2),
            base.kkm_Cashier_report: (self.report_wo_clearing, 3),
            base.kkm_Goods_report: (self.report_wo_clearing, 4),
            base.kkm_Hour_report: (self.report_wo_clearing, 5),
            base.kkm_Quantity_report: (self.report_wo_clearing, 7)
        }
        report = report_table.get(report_type)
        if not report:
            raise KKMReportErr('Unknown report type.')
        if report[1] is not None:
            report[0](self, report[1])
        else:
            report[0](self)


    # Команды режима программирования
    # <1>стр.44

    def read_table(self, table, row, field):
        data = ''.join((self._kkm_password, cmd.READ_TABLE, number2atol(table), number2atol(row, 4),
                        number2atol(field)))
        try:
            return check_exception(self._atol_send_data_sequence(data))[2:]
        except IndexError:
            raise KKMUnknownAnswerErr


    def write_table(self, table, row, field, value):
        data = ''.join(
            (self._kkm_password, cmd.PROGRAMMING, number2atol(table), number2atol(row, 4),
             number2atol(field), value))
        return check_exception(self._atol_send_data_sequence(data))


    def programming(self, args):
        """
        Программирование ККМ.
        args в виде {'параметр': значение,}
        """
        # (table,row,field,bitmask,type,length,{None|dict|func})
        ptable = {
            'kkmNumber': (2, 1, 1, None, 'int', 1, None),
            'multiDepart': (2, 1, 2, None, 'int', 1, {'multi': 0, 'single': 1}),
            'taxType': (2, 1, 11, None, 'int', 1, {'deny': 0, 'all': 1, 'sell': 2}),
            'departName': (2, 1, 15, None, 'int', 1, {0: 0, 1: 1}),
            'printNotClearedSum': (2, 1, 18, 0b00000011, 'bin', 1,
                                   {False: 0, 'deny': 0, 'all': 0b00000001,
                                    'last': 0b00000011, True: 0b11}),
            'makeIncasation': (
                2, 1, 18, 0b00000100, 'bin', 1, {False: 0, True: 0b00000100}),
            'extendedZreport': (
                2, 1, 18, 0b00001000, 'bin', 1, {False: 0, True: 0b00001000}),
            'pushLength': (2, 1, 22, 0b00000111, 'bin', 1, None),  # 0..15
            'onCutCheck': (2, 1, 22, 0b00110000, 'bin', 1,
                           {'save': 0, 'push': 0b010000, 'drop': 0b110000}),
            'prevCheck': (2, 1, 22, 0b01000000, 'bin', 1, {'save': 0, 'drop': 0b1000000}),
            'startCheck': (2, 1, 22, 0b10000000, 'bin', 1, {'loop': 0, 'push': 0b10000000}),
            'kkmPassword': (2, 1, 23, None, 'int', 2, None),
            'cutDocument': (2, 1, 24, None, 'int', 1, {False: 0, True: 1}),
            'setPayCreditName': (12, 1, 1, None, 'string', 10, None),
            'setPayTaraName': (12, 2, 1, None, 'string', 10, None),
            'setPayCardName': (12, 3, 1, None, 'string', 10, None)
        }
        try:
            for k in list(args.keys()):
                table, row, field, bitmask, rtype, length, trans = ptable[k]
                if trans is None:
                    value = args[k]
                elif isinstance(trans, dict):  # Dict
                    value = trans[args[k]]
                elif callable(trans):
                    value = trans(args[k])
                else:
                    raise KKMNotImplementedErr
                if bitmask is not None:
                    old_value = ord(self.read_table(table, row, field))
                    log.debug(str(('P0 %s %s' % (old_value, bin(old_value)))))
                    log.debug(str(('P1 %s | (%s & ~%s), %s' % (
                        bin(value), bin(old_value), bin(bitmask), bin(old_value & ~bitmask)))))
                    value |= (old_value & ~bitmask)
                    log.debug(str(('P2', bin(value), chr(value), 'AA')))
                    value = chr(value)
                    # value = number2atol(value, length * 2)
                elif rtype == 'string':
                    value = str2atol(value, length)
                elif rtype == 'int':
                    value = number2atol(value, length * 2)  # по 2 знака на байт!
                else:
                    raise KKMNotImplementedErr
                self.write_table(table, row, field, value)
        except KeyError:
            raise KKMNotImplementedErr


    def set_kkm_password(self, password):
        self._kkm_password = number2atol(password, 4)
        data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(2), number2atol(1, 4),
                        number2atol(23), self._kkm_password))
        check_exception(self._atol_send_data_sequence(data))


    def set_cashier_password(self, cashier, password):
        data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(3),
                        number2atol(cashier, 4), number2atol(1), number2atol(password, 8)))
        check_exception(self._atol_send_data_sequence(data))


    def set_admin_password(self, password):
        data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(3), number2atol(29, 4),
                        number2atol(1), number2atol(password, 8)))
        check_exception(self._atol_send_data_sequence(data))


    def set_sys_admin_password(self, password):
        data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(3), number2atol(30, 4),
                        number2atol(1), number2atol(password, 8)))
        check_exception(self._atol_send_data_sequence(data))


    def set_klishe(self, klishe):
        """
        Установить клише/рекламу в чеке.
        параметр klishe - список строк.
        <1>стр.78
        """
        i = 1
        for s in klishe:
            data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(6), number2atol(i, 4),
                            number2atol(1), str2atol(s, self.get_klishe_len())))
            check_exception(self._atol_send_data_sequence(data))
            i += 1
            for j in range(i, self.get_clishe_max_len()):
                data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(6),
                                number2atol(j, 4), number2atol(1),
                                str2atol(s, self.get_klishe_len())))
                check_exception(self._atol_send_data_sequence(data))


    def set_depart_name(self, depart, name):
        data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(7), number2atol(depart, 4),
                        number2atol(1), str2atol(name, 20)))
        check_exception(self._atol_send_data_sequence(data))


    def set_tax_rate(self, tax, value):
        data = ''.join((self._kkm_password, cmd.PROGRAMMING, number2atol(8), number2atol(tax, 4),
                        number2atol(1), number2atol(value, 4)))
        check_exception(self._atol_send_data_sequence(data))
