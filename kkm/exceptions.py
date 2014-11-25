# -*- coding: utf-8 -*-
"""
Copyright (c) 2005,2007
@author: Marat Khayrullin <xmm.dev@gmail.com>
"""

kkmCommonError = 1
kkmUnknownError = 2
kkmUnknownModelError = 3
kkmNotImplementedError = 4
kkmUnknownAnswerError = 5
kkmConnectionError = 6
kkmNoAnswerError = 7
kkmPrinterConnectionError = 8
kkmOutOfPaperError = 9
kkmWrongPasswordError = 10
kkmIncorrectPasswordError = 11
kkmWrongMoneyError = 12
kkmWrongQuantityError = 13
kkmMultiplyOverflowError = 14
kkmWrongDateError = 15
kkmWrongTimeError = 16
kkmLowPaymentError = 17
kkmFiscalMemoryOverflowError = 18
kkmIncorectModeError = 19
kkmReportError = 20
kkmNeedZReportError = 21
kkmDoubleZReportError = 22


class KKMException(Exception):
    """"""
    _stdMsg = ''
    _stdCode = 0
    _drvMsg = ''
    _drvCode = 0
    _msg = ''

    def __init__(self, msg=''):
        if self.__class__ is KKMException:
            raise RuntimeError('KKMException should not be instantiated directly')
        self._msg = msg

    def __str__(self):
        if self._msg != '':
            return self._msg
        elif self._drvMsg != '':
            return self._drvMsg
        else:
            return self._stdMsg


class KKMCommonErr(KKMException):
    _stdMsg = 'KKM ERROR'
    _stdCode = kkmCommonError


class KKMUnknownErr(KKMException):
    """
    Неизвестная ошибка
    """
    _stdMsg = 'Unknown error'
    _stdCode = kkmUnknownError


class KKMUnknownModelErr(KKMException):
    """
    Неизвестная модель ККМ
    """
    _stdMsg = 'Unknown KKM model'
    _stdCode = kkmUnknownModelError


class KKMNotImplementedErr(KKMException):
    """
    Не реализованная функция
    """
    _stdMsg = 'Not implemented'
    _stdCode = kkmNotImplementedError


class KKMUnknownAnswerErr(KKMException):
    """
    Неверный формат ответа от ККМ
    """
    _stdMsg = 'Wrong response'
    _stdCode = kkmUnknownAnswerError


class KKMConnectionErr(KKMException):
    """
    Нет связи с ККМ
    """
    _stdMsg = 'KKM connection error'
    _stdCode = kkmConnectionError


class KKMNoAnswerErr(KKMException):
    """
    Нет ответа от ККМ
    """
    _stdMsg = 'No response from KKM'
    _stdCode = kkmNoAnswerError


class KKMPrinterConnectionErr(KKMException):
    """
    Нет связи с принтером
    """
    _stdMsg = 'Not reposne from printer'
    _stdCode = kkmPrinterConnectionError


class KKMOutOfPaperErr(KKMException):
    """
    Нет бумаги
    """
    _stdMsg = 'No paper'
    _stdCode = kkmOutOfPaperError


class KKMWrongPasswordErr(KKMException):
    """
    Недопустимый пароль
    """
    _stdMsg = 'Wrong password (1)'
    _stdCode = kkmWrongPasswordError


class KKMIncorrectPasswordErr(KKMException):
    """
    Недопустимый пароль
    """
    _stdMsg = 'Wrong password (2)'
    _stdCode = kkmIncorrectPasswordError


class KKMWrongMoneyErr(KKMException):
    """"""
    _stdMsg = 'Неверная цена (сумма)'
    _stdCode = kkmWrongMoneyError


class KKMWrongQuantityErr(KKMException):
    """
    Неверное количество
    """
    _stdMsg = 'Wrong quantity'
    _stdCode = kkmWrongQuantityError


class KKMMultiplyOverflowErr(KKMException):
    """
    Переполнение при умножении
    """
    _stdMsg = 'KKM overflow error on multilpy'
    _stdCode = kkmMultiplyOverflowError


class KKMWrongDateErr(KKMException):
    """
    Неверная дата
    """
    _stdMsg = 'Wrong date'
    _stdCode = kkmWrongDateError


class KKMWrongTimeErr(KKMException):
    """
    Неверное время
    """
    _stdMsg = 'Wrond time'
    _stdCode = kkmWrongTimeError


class KKMLowPaymentErr(KKMException):
    """
    Вносимая клиентом сумма меньше суммы чека
    """
    _stdMsg = 'Low payment'
    _stdCode = kkmLowPaymentError


class KKMFiscalMemoryOverflowErr(KKMException):
    """
    Фискальная память переполнена
    """
    _stdMsg = 'Fiscal memory overflow'
    _stdCode = kkmFiscalMemoryOverflowError


class KKMIncorectModeErr(KKMException):
    """
    Необходима смена режима для выполнения команды
    """
    _stdMsg = 'Incorrect mode'
    _stdCode = kkmIncorectModeError


class KKMNoDeviceErr(KKMException):
    """
    Устройство ККМ не найдено
    """
    _stdMsg = 'KKM device not found'
    _stdCode = kkmConnectionError


class KKMReportErr(KKMException):
    """
    Снятие отчета прервалось
    """
    _stdMsg = 'Report interrupted'
    _stdCode = kkmReportError


class KKMNeedZReportErr(KKMException):
    """
    Смена превысила 24 часа
    """
    _stdMsg = '24 hours exceded'
    _stdCode = kkmNeedZReportError


class KKMDoubleZReportErr(KKMException):
    """
    Обнуленная касса (повторное гашение не возможно)
    """
    _stdMsg = 'Session already closed'
    _stdCode = kkmDoubleZReportError
