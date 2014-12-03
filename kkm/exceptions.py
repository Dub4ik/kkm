# -*- coding: utf-8 -*-
"""
Copyright (c) 2005,2007
@author: Marat Khayrullin <xmm.dev@gmail.com>
"""


class KKMException(Exception):
    def __init__(self, code=0, message=''):
        if self.__class__ is KKMException:
            raise RuntimeError('KKMException should not be instantiated directly')
        super().__init__(code, message)

    def __str__(self):
        return '{}: {}'.format(*self.args)


class CommonError(KKMException):
    pass


class UnknownError(KKMException):
    def __init__(self):
        super().__init__(2, 'Unknown error')


class UnknownModelError(KKMException):
    def __init__(self):
        super().__init__(3, 'Unknown KKM model')


class FunctionNotImplementedError(KKMException):
    """
    Не реализованная функция
    """

    def __init__(self):
        super().__init__(4, 'Not implemented')


class WrongResponseError(KKMException):
    """
    Неверный формат ответа от ККМ
    """

    def __init__(self):
        super().__init__(5, 'Wrong response')


class KKMConnectionErr(KKMException):
    """
    Нет связи с ККМ
    """

    def __init__(self):
        super().__init__(6, 'KKM connection error')


class KKMNoAnswerErr(KKMException):
    """
    Нет ответа от ККМ
    """

    def __init__(self):
        super().__init__(7, 'No response from KKM')


class KKMPrinterConnectionErr(KKMException):
    """
    Нет связи с принтером
    """
    _defaultMessage = 'Not reposne from printer'
    _defaultCode = 8


class OutOfPaperError(KKMException):
    """
    Нет бумаги
    """

    def __init__(self):
        super().__init__(103, 'No paper or paper jammed')


class WrongPasswordError(KKMException):
    """
    Недопустимый пароль
    """

    def __init__(self):
        super().__init__(10, 'Wrong password (1)')


class WrongPassword2Error(KKMException):
    """
    Недопустимый пароль
    """

    def __init__(self):
        super().__init__(11, 'Wrong password (1)')


class InvalidAmountError(KKMException):
    """
    Неверная цена (сумма)
    """

    def __init__(self):
        super().__init__(8, 'Invalid amount')


class InvalidQuantityError(KKMException):
    """
    Неверное количество
    """

    def __init__(self):
        super().__init__(10, 'Invalid quantity')


class MultiplyOverflowErr(KKMException):
    """
    Переполнение при умножении
    """

    def __init__(self):
        super().__init__(14, 'KKM overflow error on multilpy')


class InvalidDateError(KKMException):
    """
    Неверная дата
    """

    def __init__(self):
        super().__init__(15, 'Invalid date')


class InvalidTimeError(KKMException):
    """
    Неверное время
    """

    def __init__(self):
        super().__init__(16, 'Invalid time')


class LowPaymentError(KKMException):
    """
    Вносимая клиентом сумма меньше суммы чека
    """

    def __init__(self):
        super().__init__(134, 'Low payment')


class FiscalMemoryOverflowError(KKMException):
    """
    Фискальная память переполнена
    """

    def __init__(self):
        super().__init__(18, 'Fiscal memory overflow')


class InvalidModeForOperationError(KKMException):
    """
    Необходима смена режима для выполнения команды
    """

    def __init__(self):
        super().__init__(102, 'Invalid mode for requested operation')


class DeviceNotFoundError(KKMException):
    """
    Устройство ККМ не найдено
    """

    def __init__(self):
        super().__init__(20, 'KKM device not found')


class ReportInterruptedError(KKMException):
    """
    Снятие отчета прервалось
    """

    def __init__(self):
        super().__init__(21, 'Report interrupted')


class ZReportRequiredError(KKMException):
    """
    Смена превысила 24 часа
    """

    def __init__(self):
        super().__init__(136, '24 hours exceded')


class DoubleZReportError(KKMException):
    """
    Обнуленная касса (повторное гашение не возможно)
    """

    def __init__(self):
        super().__init__(143, 'Session already closed')


class SessionAlreadyOpenedError(KKMException):
    """
    Смена открыта - операция невозможна
    """

    def __init__(self):
        super().__init__(156, 'Session already opened.')


exception_table = {
    1: CommonError(1, 'Контрольная лента обработана без ошибок.'),
    8: InvalidAmountError(),
    10: InvalidQuantityError(),
    15: CommonError(15, 'Повторная скидка на операцию не возможна'),
    20: CommonError(20, 'Неверная длина'),
    26: CommonError(26, 'Отчет с гашением прерван. Вход в режим заблокирован'),
    30: CommonError(30, 'Вход в режим заблокирован'),
    102: InvalidModeForOperationError(),
    103: OutOfPaperError(),
    106: CommonError(106, 'Неверный тип чека'),
    114: CommonError(114, 'Сумма платежей меньше суммы чека'),
    117: CommonError(117, 'Переполнение суммы платежей'),
    122: CommonError(122, 'Данная модель ККМ не может выполнить команду'),
    123: CommonError(123, 'Неверная величина скидки / надбавки'),
    127: CommonError(127, 'Переполнение при умножении'),
    134: LowPaymentError(),
    136: ZReportRequiredError(),
    140: CommonError(140, 'Неверный пароль'),
    143: DoubleZReportError(),
    151: CommonError(151, 'Подсчет суммы сдачи не возможен'),
    154: CommonError(154, 'Чек закрыт - операция невозможна'),
    155: CommonError(155, 'Чек открыт - операция невозможна'),
    156: SessionAlreadyOpenedError(),
    190: CommonError(190, 'Необходимо провести профилактические работы'),
    201: CommonError(201, 'Нет связи с внешним устройством'),
    209: CommonError(209, 'Перегрев головки принтера'),
    210: CommonError(210, 'Ошибка обмена с ЭКЛЗ на уровне интерфейса I2O')
}


def get_exception_by_error_code(code):
    return exception_table.get(code)
