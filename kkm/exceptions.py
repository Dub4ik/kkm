# -*- coding: utf-8 -*-
"""
Copyright (c) 2005,2007
@author: Marat Khayrullin <xmm.dev@gmail.com>
"""


class KKMException(Exception):
    """"""
    _defaultMessage = ''
    _defaultCode = 0
    _drvMsg = ''
    _drvCode = 0
    _msg = ''

    def __init__(self, code=0, message=''):
        if self.__class__ is KKMException:
            raise RuntimeError('KKMException should not be instantiated directly')
        super().__init__(code, message)

    def __str__(self):
        return '{}: {}'.format(*self.args)


class CommonError(KKMException):
    _defaultMessage = 'KKM ERROR'
    _defaultCode = 1


class KKMUnknownErr(KKMException):
    """
    Неизвестная ошибка
    """
    _defaultMessage = 'Unknown error'
    _defaultCode = 2


class KKMUnknownModelErr(KKMException):
    """
    Неизвестная модель ККМ
    """
    _defaultMessage = 'Unknown KKM model'
    _defaultCode = 3


class NotImplementedError(KKMException):
    """
    Не реализованная функция
    """
    _defaultMessage = 'Not implemented'
    _defaultCode = 4


class KKMUnknownAnswerErr(KKMException):
    """
    Неверный формат ответа от ККМ
    """
    _defaultMessage = 'Wrong response'
    _defaultCode = 5


class KKMConnectionErr(KKMException):
    """
    Нет связи с ККМ
    """
    _defaultMessage = 'KKM connection error'
    _defaultCode = 6


class KKMNoAnswerErr(KKMException):
    """
    Нет ответа от ККМ
    """
    _defaultMessage = 'No response from KKM'
    _defaultCode = 7


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
    _defaultMessage = 'No paper'
    _defaultCode = 9


class KKMWrongPasswordErr(KKMException):
    """
    Недопустимый пароль
    """
    _defaultMessage = 'Wrong password (1)'
    _defaultCode = 10


class KKMIncorrectPasswordErr(KKMException):
    """
    Недопустимый пароль
    """
    _defaultMessage = 'Wrong password (2)'
    _defaultCode = 11


class WrongMoneyError(KKMException):
    """
    Неверная цена (сумма)
    """
    _defaultMessage = 'Wrong amount'
    _defaultCode = 12


class WrongQuantityError(KKMException):
    """
    Неверное количество
    """
    _defaultMessage = 'Wrong quantity'
    _defaultCode = 13


class KKMMultiplyOverflowErr(KKMException):
    """
    Переполнение при умножении
    """
    _defaultMessage = 'KKM overflow error on multilpy'
    _defaultCode = 14


class KKMWrongDateErr(KKMException):
    """
    Неверная дата
    """
    _defaultMessage = 'Wrong date'
    _defaultCode = 15


class KKMWrongTimeErr(KKMException):
    """
    Неверное время
    """
    _defaultMessage = 'Wrond time'
    _defaultCode = 16


class LowPaymentError(KKMException):
    """
    Вносимая клиентом сумма меньше суммы чека
    """
    _defaultMessage = 'Low payment'
    _defaultCode = 17


class KKMFiscalMemoryOverflowErr(KKMException):
    """
    Фискальная память переполнена
    """
    _defaultMessage = 'Fiscal memory overflow'
    _defaultCode = 18


class InvalidModeForOperationError(KKMException):
    """
    Необходима смена режима для выполнения команды
    """
    _defaultMessage = 'Incorrect mode'
    _defaultCode = 18


class KKMNoDeviceErr(KKMException):
    """
    Устройство ККМ не найдено
    """
    _defaultMessage = 'KKM device not found'
    _defaultCode = 20


class KKMReportErr(KKMException):
    """
    Снятие отчета прервалось
    """
    _defaultMessage = 'Report interrupted'
    _defaultCode = 21


class ZReportRequiredError(KKMException):
    """
    Смена превысила 24 часа
    """
    _defaultMessage = '24 hours exceded'
    _defaultCode = 22


class DoubleZReportError(KKMException):
    """
    Обнуленная касса (повторное гашение не возможно)
    """
    _defaultMessage = 'Session already closed'
    _defaultCode = 23


class SessionAlreadyOpenedError(KKMException):
    """
    Смена открыта - операция невозможна
    """

    def __init__(self):
        super().__init__(156, 'Session already opened.')


exception_table = {
    1: CommonError(1, 'Контрольная лента обработана без ошибок.'),
    8: WrongMoneyError(8),
    10: WrongQuantityError(10),
    15: CommonError(15, 'Повторная скидка на операцию не возможна'),
    20: CommonError(20, 'Неверная длина'),
    26: CommonError(26, 'Отчет с гашением прерван. Вход в режим заблокирован'),
    30: CommonError(30, 'Вход в режим заблокирован'),
    102: InvalidModeForOperationError(102),
    103: OutOfPaperError(103),
    106: CommonError(106, 'Неверный тип чека'),
    114: CommonError(114, 'Сумма платежей меньше суммы чека'),
    117: CommonError(117, 'Переполнение суммы платежей'),
    122: CommonError(122, 'Данная модель ККМ не может выполнить команду'),
    123: CommonError(123, 'Неверная величина скидки / надбавки'),
    127: CommonError(127, 'Переполнение при умножении'),
    134: LowPaymentError(134),
    136: ZReportRequiredError(136),
    140: CommonError(140, 'Неверный пароль'),
    143: DoubleZReportError(143),
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
