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
import logging
import sys
import serial
import time
from datetime import datetime
from . import control_symbols as symbol, \
    constants as const, commands as cmd, modes
from .. import base
from ..common import TaxArea, DiscountValueType, DiscountSign
from ...exceptions import *


log = logging.getLogger(__name__)

# Битовые значения переменной flags (<1>стр.34)
_atol_test_only_flag = 0x01
_atol_check_cash_flag = 0x02

# Коды режима отчетов без гашения
_atol_x_report = 1
_atol_department_report = 2
_atol_cashier_report = 3
_atol_goods_report = 4
_atol_hour_report = 5
_atol_quantity_report = 7

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

_check_types = {
    base.kkm_sell_check: 1,
    base.kkm_return_check: 2,
    base.kkm_annulate_check: 3
}


def check_exception(response):
    if len(response) < 2 or response[0] != ord('U'):
        log.error('Wrong response {}'.format(response))
        raise WrongResponseError()
    code = response[1]
    if code > 0:
        raise get_exception_by_error_code(code)
    return response


def atol_escape(data):
    return data.replace(symbol.DLE, symbol.DLE + symbol.DLE) \
        .replace(symbol.ETX, symbol.DLE + symbol.ETX)


def atol_unescape(data):
    return data.replace(symbol.DLE + symbol.ETX, symbol.ETX) \
        .replace(symbol.DLE + symbol.DLE, symbol.DLE)


def atol_calc_crc(data):
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

    def __init__(self, port, baudrate, password=0):
        super().__init__({'port': port, 'baudrate': baudrate})
        self.__flags = _atol_check_cash_flag
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
            log.error(str(InvalidAmountError()))
            raise InvalidAmountError()
        if money > self._moneyMax:
            log.error(str(InvalidAmountError()))
            raise InvalidAmountError()
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
            raise InvalidQuantityError()
        if quantity > self._quantityMax:
            log.error('Quantity value greater than max allowed.')
            raise InvalidQuantityError()
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
            model = str(device_type['type']) + '.' + str(device_type['model'])
        model_info = _models_table.get(model)
        if not model_info:
            log.error('Unknow device {}'.format(model))
            raise UnknownModelError()
        self._str_max = model_info[_atol_StringMax_idx]
        self._klishe_max = model_info[_atol_KlisheMax_idx]
        self._klishe_len = model_info[_atol_KlisheLen_idx]

    def open_device(self):
        """
        Проверить наличие блокировки устройства
        Заблокировать или вывалиться с ошибкой
        """
        log.info('> Open device.')
        try:
            self._device = serial.Serial(**self._params)
            super().open_device()
        except:
            raise CommonError('System error at opening KKM device')
        if not self._device:
            raise CommonError('Unknown error at opening KKM device')
        log.debug('> Open device completed.')

    def _set_read_timeout(self, timeout):
        log.debug('Set read timeout {}.'.format(timeout))
        self._device.timeout=timeout

    def _atol_send_data_sequence(self, data):
        device = self._device
        command = data[self._passwordLen // 2]
        data = atol_escape(data) + symbol.ETX
        crc = bytes((atol_calc_crc(data),))
        data = symbol.STX + data + crc
        try:
            # Активный передатчик
            for conection_attempt in range(const.CON_ATTEMPTS):
                is_answered = False
                no_data_retry_num = const.NO_DATA_RETRY_COUNT
                self._set_read_timeout(const.T1_TIMEOUT)
                for enq_attempt in range(const.ENQ_ATTEMPTS):
                    if no_data_retry_num >= const.NO_DATA_RETRY_COUNT:
                        log.debug('Sending ENQ #{}.'.format(enq_attempt + 1))
                        no_data_retry_num = 0
                        device.write(symbol.ENQ)
                    no_data_retry_num += 1
                    response = device.read(1)
                    if len(response) < 1:
                        log.debug('No data #{}.'.format(no_data_retry_num))
                        continue
                    log.debug('Recieved: {}.'.format(
                        symbol.get_symbol_name(response)))
                    if response == symbol.ACK:
                        result = self._retrieve_data(command, data)
                        log.debug('Response: [{}].'.format(result))
                        return result
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
                    log.error('Failed {} attempts of sending ENQ.'.format(
                        const.ENQ_ATTEMPTS))
                    raise KKMConnectionErr
            device.write(symbol.EOT)
        except OSError as e:  # for Linux
            exc = sys.exc_info()
            if exc[1].errno == 19:
                log.error(DeviceNotFoundError())
                raise DeviceNotFoundError()
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
        no_data_retry_num = const.NO_DATA_RETRY_COUNT
        self._set_read_timeout(const.T3_TIMEOUT)
        for ack_attempt in range(const.ACK_ATTEMPTS):
            if no_data_retry_num >= const.NO_DATA_RETRY_COUNT:
                log.debug('Sending data #{}: {}.'.format(
                    ack_attempt + 1, data))
                no_data_retry_num = 0
                device.write(data)
            no_data_retry_num += 1
            response = device.read(1)
            if len(response) == 0:
                log.debug('No data #{}.'.format(no_data_retry_num))
                continue
            log.debug('Recieved: {}.'.format(symbol.get_symbol_name(response)))
            if response == symbol.ENQ and ack_attempt == 0:
                log.debug('ENQ recieved at first place, ignored.')
                continue
            elif response == symbol.ACK or response == symbol.ENQ:
                if response == symbol.ACK:
                    device.write(symbol.EOT)
                    self._set_read_timeout(const.get_t5_timeout_for(command))
                    for con_attempt in range(const.CON_ATTEMPTS):
                        log.debug('Sending CON #{}.'.format(con_attempt + 1))
                        response = device.read(1)
                        log.debug('Recieved: {}.'.format(
                            symbol.get_symbol_name(response)))
                        if len(response) == 0:
                            log.error('KKM no answer.')
                            raise KKMNoAnswerErr()
                        if response == symbol.ENQ:
                            break
                for ack_attempt_2 in range(const.ACK_ATTEMPTS):
                    log.debug('Sending ACK #{}.'.format(ack_attempt_2 + 1))
                    device.write(symbol.ACK)
                    self._set_read_timeout(const.T2_TIMEOUT)
                    for stx_attempt in range(const.STX_ATTEMPTS):
                        log.debug('STX waiting #{}.'.format(stx_attempt + 1))
                        response = device.read(1)
                        log.debug('Recieved: {}.'.format(
                            symbol.get_symbol_name(response)))
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
                            dle_detected = False
                            no_data_retry_num = 0
                            self._set_read_timeout(const.T6_TIMEOUT)
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
                                    if response == symbol.ETX and not dle_detected:
                                        log.debug('[ETX detected]')
                                        break
                                    full_response += response
                                    dle_detected = response == symbol.DLE and not dle_detected
                            log.debug('Raw response: [{}].'.format(
                                symbol.humanize(full_response)))
                            response = device.read(1)  # Ждем CRC
                            if len(response) < 1:
                                log.debug('No CRC data.')
                                break
                            log.debug('CRC data: [{}].'.format(response[0]))
                            calculated_crc = atol_calc_crc(
                                full_response + symbol.ETX)
                            recieved_crc = ord(response)
                            log.debug('Calculated/recieved CRC: {}/{}'
                                      .format(calculated_crc, recieved_crc))
                            if calculated_crc != recieved_crc:
                                log.error('CRC does not match, sending NAK.')
                                device.write(symbol.NAK)
                                break
                            else:
                                self._set_read_timeout(const.T4_TIMEOUT)
                                log.debug('ACK sending.')
                                device.write(symbol.ACK)
                                log.debug('ACK sent')
                                response = device.read(1)
                                log.debug('Recieved: {}.'
                                          .format(symbol.get_symbol_name(response)))
                                if response == symbol.EOT or len(response) == 0:
                                    log.debug('[EOT detected]')
                                    return atol_unescape(full_response)
                                elif response == symbol.STX:
                                    continue
                                else:
                                    # _atol_T???_timeout
                                    self._set_read_timeout(2)
                                    response = device.read(1)
                                    if len(response) == 0:
                                        return atol_unescape(full_response)
                                    else:
                                        break
                    if stx_attempt >= const.STX_ATTEMPTS - 1:
                        log.error('KKM no answer.')
                        raise KKMNoAnswerErr()
                device.write(symbol.EOT)
                log.error('Failed {} attempts of sending ACK.'.format(
                    const.ACK_ATTEMPTS))
                raise KKMNoAnswerErr
        device.write(symbol.EOT)
        log.error('Failed {} attempts of sending data.'.format(
            const.ACK_ATTEMPTS))
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
            raise WrongResponseError

    def get_status(self):
        log.debug('> Get status.')
        response = self._atol_send_data_sequence(
            self._kkm_password + cmd.GET_STATUS)
        try:
            if response[0] != ord('D'):
                raise WrongResponseError()
            cashier = atol2number(response[1:2])
            site = atol2number(response[2:3])
            kkm_datetime = atol_datetime_to_native_datetime(response[3:9])
            flags = response[9]
            mask = 1 << 1
            is_session_opened = (flags & mask) == mask
            mashine = atol2number(response[10:14])
            model = response[14]
            version = str(response[15]) + '.' + str(response[16])
            mode = response[17] & 0x0F
            submode = (response[17] & 0xF0) >> 4
            check = atol2number(response[18:20])
            session_num = atol2number(response[20:22])
            check_state = response[22]
            check_sum = atol2number(response[23:28])
            dot_position = response[28]
            port = response[29]
            result = {'cashier': cashier, 'site': site, 'datetime': kkm_datetime, 'flags': flags,
                      'mashine': mashine, 'model': model, 'version': version, 'mode': mode,
                      'submode': submode, 'check': check, 'is_session_opened': is_session_opened,
                      'session_num': session_num, 'check_state': check_state,
                      'check_sum': check_sum, 'dot_position': dot_position, 'port': port}
            log.debug('Device status: {}.'.format(result))
            log.debug('> Get status completed.')
            return result
        except IndexError:
            raise WrongResponseError()

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
        """
        Запрос кода состояния (режима) ККМ.
        Result: mode, submode, printer, paper
        <1>стр.28
        """
        log.info('> Get current state.')
        response = self._atol_send_data_sequence(
            self._kkm_password + cmd.GET_CURRENT_STATE)
        try:
            mode = response[1] & 0b1111
            submode = response[1] >> 4
            flags = response[2] >> 4
            paper_fail = (flags & 0b0001) == 0b0001
            printer_fail = (flags & 0b0010) == 0b0010
            result = (mode, submode, printer_fail, paper_fail,)
            log.debug('state={}.{}, paper_fail={}, printer_fail={} (flags:[{}]>>[{}])'
                      .format(mode, submode, paper_fail, printer_fail,
                              bin(response[2]), bin(flags)))
            log.debug('> Get current state completed.')
            return result
        except IndexError:
            raise WrongResponseError()

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
        log.info('> Get device info.')
        response = self._atol_send_data_sequence(
            self._kkm_password + cmd.GET_DEVICE_TYPE)
        try:
            if response[0] != 0:
                raise get_exception_by_error_code(response[0])
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
            raise WrongResponseError
        result = {'error': error, 'protocol': protocol, 'type': type_, 'model': model, 'mode': mode,
                  'majorver': majorver, 'minorver': minorver, 'codepage': codepage, 'build': build,
                  'name': name.decode('cp866')}
        log.debug('Device info: {}.'.format(result))
        log.debug('> Get device info completd.')
        return result

    def reset_mode(self):
        """
        Выход из текущего режима.
        """
        check_exception(self._atol_send_data_sequence(
            self._kkm_password + cmd.RESET_MODE))

    def set_mode(self, mode, password):
        """
        Установить режим.
        <1>стр.19
        """
        log.info('> Set mode: {}, password: {}'.format(mode, password))
        current_mode = self.get_current_mode()
        if mode != current_mode:
            if current_mode != modes.SELECT:
                self.reset_mode()
            data = b''.join((self._kkm_password, cmd.SET_MODE, number2atol(mode),
                             number2atol(password, 8),))
            check_exception(self._atol_send_data_sequence(data))
            log.debug('> Set mode completed.'.format(mode, password))

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
        return self.get_status()['check_state'] != 0

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
        raise FunctionNotImplementedError

    # Общие команды

    def print_string(self, txt, wrap=False):
        """
        Печать строки на кассовой ленте
        """
        log.info('> Print string: \'{}\', wrap={}.'.format(txt, wrap))
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
        log.debug('> Print string: \'{}\' completed.'.format(txt, wrap))

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

    def get_reg_flags(self):
        flags = 0
        if self.is_test_only_mode():
            flags |= _atol_test_only_flag
        if self.is_check_cash_mode():
            flags |= _atol_check_cash_flag
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
        log.info('=== cash_income({}) ==='.format(sum))
        data = b''.join((self._kkm_password,
                         cmd.CASH_INCOME,
                         number2atol(self.get_reg_flags()),
                         self._money2atol(sum)))
        check_exception(self._atol_send_data_sequence(data))
        log.debug('=== cash_income({}) finished ==='.format(sum))

    def cash_outcome(self, sum):
        """
        Выплата денег (инкасация).
        """
        log.info('=== cash_outcome({}) ==='.format(sum))
        data = b''.join((self._kkm_password,
                         cmd.CASH_OUTCOME,
                         number2atol(self.get_reg_flags()),
                         self._money2atol(sum)))
        check_exception(self._atol_send_data_sequence(data))
        log.debug('=== cash_outcome({}) finished ==='.format(sum))

    def open_check(self, check_type=base.kkm_sell_check):
        """
        Открыть Чек.
        <2>стр.44,<3>стр.37
        """
        log.info('> Open check: {}.'.format(check_type))
        data = b''.join((self._kkm_password, cmd.OPEN_CHECK, number2atol(self.get_reg_flags()),
                         number2atol(_check_types[check_type])))
        check_exception(self._atol_send_data_sequence(data))
        log.debug('> Open check completed.')

    def sell(self, name, price, quantity=1000, department=0):
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
                             number2atol(self.get_reg_flags() |
                                         _atol_test_only_flag),
                             self._money2atol(
                                 price), self._quantity2atol(quantity),
                             number2atol(department)))
            check_exception(self._atol_send_data_sequence(data))
        if self.is_test_only_mode():
            return
        self.print_string(name)
        data = b''.join((self._kkm_password, cmd.SELL, number2atol(self.get_reg_flags()),
                         self._money2atol(
                             price), self._quantity2atol(quantity),
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
            data = b''.join((self._kkm_password, cmd.RETURN_,
                             number2atol(self.get_reg_flags() |
                                         _atol_test_only_flag),
                             self._money2atol(price), self._quantity2atol(quantity)))
            check_exception(self._atol_send_data_sequence(data))
        if self.is_test_only_mode():
            return
        self.print_string(name)
        data = b''.join((self._kkm_password, cmd.RETURN_, number2atol(self.get_reg_flags()),
                         self._money2atol(price), self._quantity2atol(quantity)))
        check_exception(self._atol_send_data_sequence(data))

    def discount(self, count, area=TaxArea.WHOLE_CHECK, discount_type=DiscountValueType.PERCENT,
                 sign=DiscountSign.DISCOUNT):
        """
        Начисление скидки/надбавки.
        """
        log.info('=== discount() ===')
        area = 1 if area == TaxArea.BY_POSITION else 0
        if discount_type == DiscountValueType.PERCENT:
            discount_type = 0
            count = number2atol(count * 100, 5)  # 100.00%
        else:
            discount_type = 1
            count = self._money2atol(count)
        sign = 0 if sign == DiscountSign.DISCOUNT else 1
        # ---
        data = b''.join((self._kkm_password, cmd.DISCOUNT, number2atol(self.get_reg_flags()),
                         number2atol(area), number2atol(discount_type), number2atol(sign), count,))
        check_exception(self._atol_send_data_sequence(data))
        log.debug('=== discount() finished ===')

    def annulate(self):
        log.info('> Annulate check')
        check_exception(self._atol_send_data_sequence(
            self._kkm_password + cmd.ANNULATE))
        log.debug('> Annulate completd.')

    def payment(self, sum, pay_type=None):
        """
        Оплата чека с подсчетом суммы сдачи.
        <1>стр.38
        """
        atol_sum = self._money2atol(sum)
        log.info('=== payment({}, pay_type={}) ==='.format(sum, atol_sum))
        if pay_type is None:
            pay_type = self.cash_pay_type()
        data = b''.join((self._kkm_password,
                         cmd.CLOSE_CHECK,
                         number2atol(self.get_reg_flags()),
                         number2atol(pay_type),
                         atol_sum))
        check_exception(self._atol_send_data_sequence(data))
        log.debug('=== payment({}, pay_type={}) finished ==='.format(sum, atol_sum))

    def x_report(self, report_type=1):
        data = b''.join((self._kkm_password, cmd.X_REPORT,
                         number2atol(report_type),))
        check_exception(self._atol_send_data_sequence(data))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 2 and submode == 2:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
            if mode == 2 and submode == 0:
                if printer:
                    raise KKMPrinterConnectionErr()
                if paper:
                    raise OutOfPaperError()
                else:
                    return

    def clearing_report(self):
        check_exception(self._atol_send_data_sequence(
            self._kkm_password + cmd.CLEARING_REPORT))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 3 and submode == 2:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
            if mode == 3 and submode == 0:
                if printer:
                    raise KKMPrinterConnectionErr()
                if paper:
                    raise OutOfPaperError()
                else:
                    return
            else:
                raise ReportInterruptedError()

    def open_session(self, text=''):
        log.info('> Open session: \'{}\'.'.format(text))
        data = b''.join((self._kkm_password, cmd.OPEN_SESSION,
                         b'\x00', str2atol(text, len(text))))
        check_exception(self._atol_send_data_sequence(data))
        log.debug('> Session opened.')

    def z_report(self):
        log.info('> Z-Rreport')
        check_exception(self._atol_send_data_sequence(
            self._kkm_password + cmd.Z_REPORT))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 3 and submode == 2:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
        if mode == 7 and submode == 1:
            while mode == 7 and submode == 1:
                time.sleep(const.REPORT_TIMEOUT)
                mode, submode, printer, paper = self.get_current_state()
        else:
            if mode == 3 and submode == 0:
                raise FiscalMemoryOverflowError()
            if printer:
                raise KKMPrinterConnectionErr()
            if paper:
                raise OutOfPaperError()
            else:
                raise ReportInterruptedError()
        log.debug('> Z-Report comleted.')

    def z_report_to_memory(self):
        """
        Включить режим формирования отложенных Z отчётов.
        Result: кол-во свободных полей для записи Z-отчётов
        <4>стр.9
        """
        log.info('> Z-Report to memory mode enable.')
        data = self._kkm_password + cmd.Z_REPORT_TO_MEM
        response = check_exception(self._atol_send_data_sequence(data))[2]
        log.info(
            '> Z-Report to memory mode enabled. {} free memoryots reported.'.format(response))
        try:
            log.debug('=== z_report_to_memory() finished ===')
            return response
        except IndexError:
            raise WrongResponseError

    def z_report_from_memory(self):
        """
        Распечатать отложенные Z-отчёты и отключить режим отложенных Z отчётов.
        """
        log.info('> Z-Report from memory.')
        data = self._kkm_password + cmd.Z_REPORT_FROM_MEM
        check_exception(self._atol_send_data_sequence(data))
        log.debug('> Z-Report from memory completed.')

    def common_clearing(self):
        check_exception(self._atol_send_data_sequence(
            self._kkm_password + cmd.COMMON_CLEAR))
        mode, submode, printer, paper = self.get_current_state()
        while mode == 3 and submode == 6:
            time.sleep(const.REPORT_TIMEOUT)
            mode, submode, printer, paper = self.get_current_state()
            if mode == 3 and submode == 0:
                if printer:
                    raise KKMPrinterConnectionErr
                if paper:
                    raise OutOfPaperError
                else:
                    return
            else:
                raise ReportInterruptedError

    def report(self, report_type):
        report_table = {
            base.kkm_clearing_report: (self.clearing_report, None),
            base.kkm_z_report: (self.z_report, None),
            base.kkm_x_report: (self.x_report, 1),
            base.kkm_department_report: (self.x_report, 2),
            base.kkm_cashier_report: (self.x_report, 3),
            base.kkm_goods_report: (self.x_report, 4),
            base.kkm_hour_report: (self.x_report, 5),
            base.kkm_quantity_report: (self.x_report, 7)
        }
        report = report_table.get(report_type)
        if not report:
            raise ReportInterruptedError()
        if report[1] is not None:
            report[0](self, report[1])
        else:
            report[0](self)

    def _read_table(self, table, row, field):
        log.info('=== read_table(table={}, row={}, field={}) ==='.format(
            table, row, field))
        mask = 255
        data = b''.join((self._kkm_password, cmd.READ_TABLE, number2atol(table),
                         bytes((row & (mask << 8), row & mask)), bytes((field,))))
        try:
            result = check_exception(self._atol_send_data_sequence(data))[2:]
            log.debug('Field data: {}'.format(result))
            log.debug('=== read_table({}, {}, {}) finished ==='.format(
                table, row, field))
            return result
        except IndexError:
            raise WrongResponseError

    def _write_table(self, table, row, field, value):
        log.info('=== write_table(table={}, row={}, field={}, val={}) ==='
                 .format(table, row, field, value))
        mask = 255
        data = b''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(table),
                         bytes((row & (mask << 8), row & mask)), bytes((field,)), value))
        result = check_exception(self._atol_send_data_sequence(data))
        log.debug('=== write_table({}, {}, {}, {}) finished ==='
                  .format(table, row, field, value))
        return result

    def programming(self, **kwargs):
        """
        Программирование ККМ.
        args в виде {'параметр': значение,}
        """
        # (table,row,field,bitmask,type,length,{None|dict|func})
        log.info('=== programming({})'.format(kwargs))
        ptable = {
            'kkmNumber': (2, 1, 1, None, 'int', 1, None),
            'multiDepart': (2, 1, 2, None, 'int', 1, {'multi': 0, 'single': 1}),
            'taxType': (2, 1, 11, None, 'int', 1, {'deny': 0, 'all': 1, 'sell': 2}),
            'departName': (2, 1, 15, None, 'int', 1, {0: 0, 1: 1}),
            'print_protected_sum': (2, 1, 18, 0b00000011, 'bin', 1,
                                    {False: 0, 'deny': 0, 'all': 0b00000001,
                                     'last': 0b00000011, True: 0b11}),
            'allow_encashment': (2, 1, 18, 0b00000100, 'bin', 1, {False: 0, True: 0b00000100}),
            'extended_z_report': (2, 1, 18, 0b00001000, 'bin', 1, {False: 0, True: 0b00001000}),
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
            for k, v in kwargs.items():
                table, row, field, bitmask, rtype, length, trans = ptable[k]
                if trans is None:
                    value = v
                elif isinstance(trans, dict):  # Dict
                    value = trans[v]
                elif callable(trans):
                    value = trans(v)
                else:
                    raise FunctionNotImplementedError()
                if bitmask is not None:
                    old_value = self._read_table(table, row, field)[0]
                    value |= (old_value & ~bitmask)
                    log.debug('Old/new: [{}]/[{}]'.format(old_value, value))
                    value = bytes((value,))
                    # value = number2atol(value, length * 2)
                elif rtype == 'string':
                    value = str2atol(value, length)
                elif rtype == 'int':
                    # по 2 знака на байт!
                    value = number2atol(value, length * 2)
                else:
                    raise FunctionNotImplementedError
                self._write_table(table, row, field, value)
            log.info('=== programming({}) finished'.format(kwargs))
        except KeyError:
            raise FunctionNotImplementedError()

    def set_kkm_password(self, password):
        self._kkm_password = number2atol(password, 4)
        data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(2), number2atol(1, 4),
                        number2atol(23), self._kkm_password))
        check_exception(self._atol_send_data_sequence(data))

    def set_cashier_password(self, cashier, password):
        data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(3),
                        number2atol(cashier, 4), number2atol(1), number2atol(password, 8)))
        check_exception(self._atol_send_data_sequence(data))

    def set_admin_password(self, password):
        data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(3), number2atol(29, 4),
                        number2atol(1), number2atol(password, 8)))
        check_exception(self._atol_send_data_sequence(data))

    def set_sys_admin_password(self, password):
        data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(3), number2atol(30, 4),
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
            data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(6), number2atol(i, 4),
                            number2atol(1), str2atol(s, self.get_klishe_len())))
            check_exception(self._atol_send_data_sequence(data))
            i += 1
            for j in range(i, self.get_clishe_max_len()):
                data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(6),
                                number2atol(j, 4), number2atol(1),
                                str2atol(s, self.get_klishe_len())))
                check_exception(self._atol_send_data_sequence(data))

    def set_depart_name(self, depart, name):
        data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(7), number2atol(depart, 4),
                        number2atol(1), str2atol(name, 20)))
        check_exception(self._atol_send_data_sequence(data))

    def set_tax_rate(self, tax, value):
        data = ''.join((self._kkm_password, cmd.WRITE_TABLE, number2atol(8), number2atol(tax, 4),
                        number2atol(1), number2atol(value, 4)))
        check_exception(self._atol_send_data_sequence(data))
