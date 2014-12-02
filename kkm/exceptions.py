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


class KKMCommonErr(KKMException):
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


class KKMOutOfPaperErr(KKMException):
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


class KKMWrongMoneyErr(KKMException):
    """
    Неверная цена (сумма)
    """
    _defaultMessage = 'Wrong amount'
    _defaultCode = 12


class KKMWrongQuantityErr(KKMException):
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


class KKMLowPaymentErr(KKMException):
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


class KKMIncorectModeErr(KKMException):
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


class KKMNeedZReportErr(KKMException):
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
    1: KKMCommonErr(1, 'Контрольная лента обработана без ошибок.'),
    8: KKMWrongMoneyErr(8),
    10: KKMWrongQuantityErr(10),
    15: KKMCommonErr(15, 'Повторная скидка на операцию не возможна'),
    20: KKMCommonErr(20, 'Неверная длина'),
    26: KKMCommonErr(26, 'Отчет с гашением прерван. Вход в режим заблокирован'),
    30: KKMCommonErr(30, 'Вход в режим заблокирован'),
    102: KKMIncorectModeErr(102),
    103: KKMOutOfPaperErr(103),
    106: KKMCommonErr(106, 'Неверный тип чека'),
    114: KKMCommonErr(114, 'Сумма платежей меньше суммы чека'),
    117: KKMCommonErr(117, 'Переполнение суммы платежей'),
    122: KKMCommonErr(122, 'Данная модель ККМ не может выполнить команду'),
    123: KKMCommonErr(123, 'Неверная величина скидки / надбавки'),
    127: KKMCommonErr(127, 'Переполнение при умножении'),
    134: KKMLowPaymentErr(134),
    136: KKMNeedZReportErr(136),
    140: KKMCommonErr(140, 'Неверный пароль'),
    143: DoubleZReportError(143),
    151: KKMCommonErr(151, 'Подсчет суммы сдачи не возможен'),
    154: KKMCommonErr(154, 'Чек закрыт - операция невозможна'),
    155: KKMCommonErr(155, 'Чек открыт - операция невозможна'),
    156: SessionAlreadyOpenedError(),
    190: KKMCommonErr(190, 'Необходимо провести профилактические работы'),
    201: KKMCommonErr(201, 'Нет связи с внешним устройством'),
    209: KKMCommonErr(209, 'Перегрев головки принтера'),
    210: KKMCommonErr(210, 'Ошибка обмена с ЭКЛЗ на уровне интерфейса I2O')
}


def get_exception_by_error_code(code):
    return exception_table.get(code)
