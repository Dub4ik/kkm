# -*- coding: utf-8 -*-
'''
Copyright (c) 2005,2007
@author: Marat Khayrullin <xmm.dev@gmail.com>
'''

kkmCommonError            = 1
kkmUnknownError           = 2
kkmUnknownModelError      = 3
kkmNotImplementedError    = 4
kkmUnknownAnswerError     = 5
kkmConnectionError        = 6
kkmNoAnswerError          = 7
kkmPrinterConnectionError = 8
kkmOutOfPaperError        = 9
kkmWrongPasswordError     = 10
kkmIncorrectPasswordError = 11
kkmWrongMoneyError        = 12
kkmWrongQuantityError     = 13
kkmMultiplyOverflowError  = 14
kkmWrongDateError         = 15
kkmWrongTimeError         = 16
kkmLowPaymentError        = 17
kkmFiscalMemoryOverflowError = 18
kkmIncorectModeError      = 19
kkmReportError            = 20
kkmNeedZReportError       = 21
kkmDoubleZReportError     = 22


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
        if (self._msg != ''):
            return self._msg
        elif (self._drvMsg != ''):
            return self._drvMsg
        else:
            return self._stdMsg

#class xxx(WrongQuantity):
#    _drvMsg = 'XXX_msg'
#    _drvCode = 2


class KKMCommonErr(KKMException):
    """"""
    _stdMsg = ''
    _stdCode = kkmCommonError


class KKMUnknownErr(KKMException):
    """"""
    _stdMsg = 'Неизвестная ошибка'
    _stdCode = kkmUnknownError


class KKMUnknownModelErr(KKMException):
    """"""
    _stdMsg = 'Неизвестная модель ККМ'
    _stdCode = kkmUnknownModelError


class KKMNotImplementedErr(KKMException):
    """"""
    _stdMsg = 'Не реализованная функция'
    _stdCode = kkmNotImplementedError


class KKMUnknownAnswerErr(KKMException):
    """"""
    _stdMsg = 'Неверный формат ответа от ККМ'
    _stdCode = kkmUnknownAnswerError


class KKMConnectionErr(KKMException):
    _stdMsg = 'Нет связи с ККМ'
    _stdCode = kkmConnectionError


class KKMNoAnswerErr(KKMException):
    """"""
    _stdMsg = 'Нет ответа от ККМ'
    _stdCode = kkmNoAnswerError


class KKMPrinterConnectionErr(KKMException):
    """"""
    _stdMsg = 'Нет связи с принтером'
    _stdCode = kkmPrinterConnectionError


class KKMOutOfPaperErr(KKMException):
    """"""
    _stdMsg = 'Нет бумаги'
    _stdCode = kkmOutOfPaperError


class KKMWrongPasswordErr(KKMException):
    """"""
    _stdMsg = 'Недопустимый пароль'
    _stdCode = kkmWrongPasswordError


class KKMIncorrectPasswordErr(KKMException):
    """"""
    _stdMsg = 'Недопустимый пароль'
    _stdCode = kkmIncorrectPasswordError


class KKMWrongMoneyErr(KKMException):
    """"""
    _stdMsg = 'Неверная цена (сумма)'
    _stdCode = kkmWrongMoneyError


class KKMWrongQuantityErr(KKMException):
    _stdMsg = 'Неверное количество'
    _stdCode = kkmWrongQuantityError


class KKMMultiplyOverflowErr(KKMException):
    """"""
    _stdMsg = 'Переполнение при умножении'
    _stdCode = kkmMultiplyOverflowError


class KKMWrongDateErr(KKMException):
    """"""
    _stdMsg = 'Неверная дата'
    _stdCode = kkmWrongDateError


class KKMWrongTimeErr(KKMException):
    """"""
    _stdMsg = 'Неверное время'
    _stdCode = kkmWrongTimeError


class KKMLowPaymentErr(KKMException):
    """"""
    _stdMsg = 'Вносимая клиентом сумма меньше суммы чека'
    _stdCode = kkmLowPaymentError


class KKMFiscalMemoryOverflowErr(KKMException):
    """"""
    _stdMsg = 'Фискальная память переполнена'
    _stdCode = kkmFiscalMemoryOverflowError


class KKMIncorectModeErr(KKMException):
    """"""
    _stdMsg = 'Необходима смена режима для выполнения команды'
    _stdCode = kkmIncorectModeError


class KKMNoDeviceErr(KKMException):
    _stdMsg = 'Устройство ККМ не найдено'
    _stdCode = kkmConnectionError


class KKMReportErr(KKMException):
    _stdMsg = 'Снятие отчета прервалось'
    _stdCode = kkmReportError


class KKMNeedZReportErr(KKMException):
    _stdMsg = 'Смена превысила 24 часа'
    _stdCode = kkmNeedZReportError


class KKMDoubleZReportErr(KKMException):
    _stdMsg = 'Обнуленная касса (повторное гашение не возможно)'
    _stdCode = kkmDoubleZReportError
