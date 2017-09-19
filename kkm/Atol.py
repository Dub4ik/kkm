# -*- coding: utf-8 -*-
'''
 Copyright (c) 2017
 @extended code author: Evgeny Kaltashkin <zhecka@gmail.com>

 Copyright (c) 2005, 2012
 @original code author: Marat Khayrullin <xmm.dev@gmail.com>
'''

'''
 Использованные документы:
 <1>: Атол технологии
       Руководство программиста: Протокол работы ККМ v2.4 версия 6.00 (26.12.2012)
 <2>: Атол технологии
       Руководство программиста: Общий драйвер ККМ v.5.1
       (версия док-ции: 1.7 от 15.05.2002)
 <3>: Курское ОАО "Счетмаш"
       Инструкция по программированию РЮИБ.466453.528 И15
       Машина электронная контрольно-кассовая Феликс-Р Ф
<4>: Атол технологии
       Приложение к протоколу работы ККМ (2009)
'''

import kkm
import Table2Params
from Exceptions import *

from decimal import Decimal
import string,struct
import time
import datetime
import logging

FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('kkm')
logger.setLevel(logging.DEBUG)

_atol_STX = '\x02'  # ^B Начало текста
_atol_ETX = '\x03'  # ^C Конец текста
_atol_EOT = '\x04'  # ^D Конец передачи
_atol_ENQ = '\x05'  # ^E Запрос
_atol_ACK = '\x06'  # ^F Подтверждение
_atol_DLE = '\x10'  # ^Q Экранирование управ. символов
_atol_NAK = '\x15'  # ^U Отрицание
_atol_FS  = '\x1C'  # ^] Разделитель полей

_atol_CON_attempt  = 100  # Ожидание первого ACK
_atol_ANS_attempt  = 100  # Ожидание STX
_atol_STX_attempt  = 100  # Кол-во попыток прочитать STX байт
_atol_ENQ_attempt  = 40   # Кол-во проверок готовности ККМ # по стандарту - 5, но ZReport подает на PayVKP-80K
_atol_ACK_attempt  = 10
_atol_T1_timeout   = 0.5  # ?Стандартное время ожидания получения 1го байта
_atol_T2_timeout   = 20   # Время ожидания состояния "Идет передача ответа"
_atol_T3_timeout   = 0.5
_atol_T4_timeout   = 0.5
_atol_T5_timeout   = 20   # Время ожидания состояния "Готов к передаче ответа"
_atol_T6_timeout   = 0.5
_atol_T7_timeout   = 0.5
_atol_T8_timeout   = 1

_atol_PASSWD_len   = 4      # Длина пароля
_atol_ANSWER_len   = 10240  # Max длина ответа от ККМ

# Коды комманд
_atol_GetLastSummary_cmd  = 'X'
_atol_GetStatus_cmd       = '?'
_atol_GetCurrentState_cmd = 'E'
_atol_GetTypeDevice_cmd   = '\xA5'
_atol_SetMode_cmd         = 'V'
_atol_ResetMode_cmd       = 'H'
_atol_PrintString_cmd     = 'L'
_atol_PrintCustom_cmd     = '\x87'
_atol_PrintToDisplay_cmd  = '\x8F'
_atol_OpenCashBox_cmd     = '\x80'
_atol_CashIncom_cmd       = 'I'
_atol_CashOutcom_cmd      = 'O'
_atol_OpenCheck_cmd       = '\x92'
_atol_Sell_cmd            = 'R'
_atol_Return_cmd          = 'W'
_atol_Discount_cmd        = 'C'
_atol_Annulate_cmd        = 'Y'
_atol_AnnulateSumm_Cmd	  = 'A'
_atol_Payment_cmd         = 'J'
_atol_Calculate_cmd       = '\x99'
_atol_GetCashSummary_cmd  = 'M'
_atol_XReport_cmd         = 'g'
_atol_ClearingReport_cmd  = 'T'
_atol_ZReport_cmd         = 'Z'
_atol_CommonClear_cmd     = 'w'
_atol_ReadTable_cmd       = 'F'
_atol_Programming_cmd     = 'P'
_atol_ZReportToMem_cmd    = '\xB4'
_atol_ZReportFromMem_cmd  = '\xB5'
_atol_CutCheck_cmd	  = '\x75'
_atol_ByPass_cmd	  = '\x8F\x8F'
_atol_SecCode_cmd 	  = 'm'


# <1>стр 13-14
_atol_T5_timeout_exception = {
    _atol_Payment_cmd: 20,
    _atol_ZReport_cmd: 40,
    _atol_SecCode_cmd: 5,
    0x62: 50,
    0x6b: 10,
    0x8d: 20,
    0x8e: 20,
    0x91: 45,
    0xa8: 120,
    0xa9: 120,
    0xa6: 50,
    0xa7: 20,
    0xaa: 120,
    0xab: 120,
    0xac: 120,
    0xad: 120,
}


def _get_T5_timeout(cmd):
    return _atol_T5_timeout_exception.get(cmd, _atol_T5_timeout)


_atol_Select_mode         = 0
_atol_Registration_mode   = 1
_atol_XReport_mode        = 2
_atol_ZReport_mode        = 3
_atol_Programming_mode    = 4
_atol_Inspector_mode      = 5

# Битовые значения переменной flags (<1>стр.34)
_atol_TestOnly_flag      = 0x01
_atol_CheckCash_flag     = 0x02

### Коды режима отчетов без гашения
_atol_X_report          = 1
_atol_Department_report = 2
_atol_Cashier_report    = 3
_atol_Goods_report      = 4
_atol_Hour_report       = 5
_atol_Quantity_report   = 7

_atol_Report_timeout    = 0.5

# Тип закрытия чека (<1>стр.38)
_atol_cash_payment  = 1  # наличными
_atol_type2_payment = 2  # кредитом
_atol_type3_payment = 3  # тарой
_atol_type4_payment = 4  # пл. картой

# Возможные значения переменной checkType в методе OpenCheck
kkm_Sell_check          = 0
kkm_StornoSell_check    = 1
kkm_Return_check        = 2
kkm_StornoReturn_check  = 3
kkm_Buy_check           = 4
kkm_StornoBuy_check     = 5
kkm_Annulate_check      = 6

# Discount options
kkm_Check_dis    = 0 # Скидка на чек
kkm_Sell_dis     = 1 # Скидка на позицию
kkm_Procent_dis  = 0 # Процентная скидка
kkm_Sum_dis      = 1 # Скидка суммой
kkm_Discount_dis = 0 # Скидка
kkm_Increase_dis = 1 # Надбавка

# Параметры ККМ различных моделей
# type.model: (name, type, model, majorver, minorver, build,
#              maxstring, klishelen, klishemax, tablemaxlength)
_modelTable = {
    '1.13': (u'Триум-Ф', 1, 14, 2, 3, 2185, 20, 20, 8, 40),
    '1.14': (u'Феликс-Р Ф', 1, 14, 2, 3, 2185, 20, 20, 8, 20),
    '1.15': (u'Феликс-02К', 1, 14, 2, 3, 2185, 20, 20, 8, 20),
    '1.16': (u'Меркурий-140Ф АТОЛ', 1, 14, 2, 3, 2185, 20, 20, 8, 24),
    '1.20': (u'Торнадо', 1, 14, 2, 3, 2185, 20, 20, 8, 48),
    '1.23': (u'Меркурий MS-K', 1, 14, 2, 3, 2185, 20, 20, 8, 39),
    '1.24': (u'Феликс-Р К', 1, 24, 2, 4, 3700, 38, 38, 8, 38),
    '1.27': (u'Феликс-3СК', 1, 24, 2, 4, 3700, 38, 38, 8, 38),
    '1.30': (u'FPrint-02K', 1, 24, 2, 4, 3700, 38, 38, 8, 56),
    '1.31': (u'FPrint-03K', 1, 24, 2, 4, 3700, 38, 38, 8, 32),
    '1.32': (u'FPrint-88K', 1, 24, 2, 4, 3700, 38, 38, 8, 56),
    '1.35': (u'FPrint-5200K', 1, 24, 2, 4, 3700, 38, 38, 8, 36),
    '1.41': (u'PayVKP-80K', 1, 24, 2, 4, 3700, 42, 42, 8, 56),
    '1.45': (u'PayPPU-700K', 1, 24, 2, 4, 3700, 42, 42, 8, 56),
    '1.46': (u'PayCTS-2000K', 1, 24, 2, 4, 3700, 42, 42, 8, 72),
    '1.47': (u'FPrint-55K', 1, 24, 2, 4, 3700, 42, 42, 8, 36),
    '1.51': (u'FPrint-11ПТК', 1, 24, 2, 4, 3700, 42, 42, 8, 32),
    '1.52': (u'FPrint-22K', 1, 24, 2, 4, 3700, 42, 42, 8, 48),
    }

_typesTable = {
    '0': (u'Тип не определен'),
    '1': (u'ККТ'),
    '2': (u'Весы'),
    '3': (u'Блок Memo Plus(TM)'),
    '4': (u'Принтер этикеток'),
    '5': (u'Терминал сбора данных'),
    '6': (u'Дисплей покупателя'),
    '7': (u'Сканер штрихкода, PIN-клавиатура, ресторанная клавиатура'),
    '8': (u''),
    }
    
_atol_StringMax_idx = 6
_atol_KlisheLen_idx = 7
_atol_KlisheMax_idx = 8

kkmtocp866="\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\
\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\
\x20\x21\x22\x23\xfc\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\
\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\
\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\
\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\
\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\
\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\
\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\
\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\
\x24\xf2\x2d\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20"
        
cp866tokkm="\x20\x20\x20\x20\x20\x20\x20\x20\x20\x09\x0a\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x21\x22\x23\xfc\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\
\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\
\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\
\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\
\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\
\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\
\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\
\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\
\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\xfa\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x24\x20\x20\x20"

oldcp866tokkm="\x20\x20\x20\x20\x20\x20\x20\x20\x20\xfe\xfd\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x21\x22\x23\xfc\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\
\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\
\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\
\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\
\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\
\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\
\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\
\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\
\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\xfa\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\
\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x24\x20\x20\x20"

exceptionTable = {
	0: KKMCommonErr(u'Ошибок нет'),
	1: KKMCommonErr(u'Контрольная лента обработана без ошибок'),
	8: KKMWrongMoneyErr,
	10: KKMWrongQuantityErr,
	11: KKMCommonErr(u'Переполнение счетчика наличности'),
	12: KKMCommonErr(u'Невозможно сторно последней операции'),
	13: KKMCommonErr(u'Сторно по коду невозможно (в чеке зарегистрировано меньшее количество товаров с указанным кодом)'),
	14: KKMCommonErr(u'Невозможен повтор последней операции'),
	15: KKMCommonErr(u'Повторная скидка на операцию невозможна'),
	16: KKMCommonErr(u'Скидка/надбавка на предыдущую операцию невозможна'),
	17: KKMCommonErr(u'Неверный код товара'),
	18: KKMCommonErr(u'Неверный штрихкод товара'),
	19: KKMCommonErr(u'Неверный формат'),
	20: KKMCommonErr(u'Неверная длина'),
	21: KKMCommonErr(u'ККТ заблокирована в режиме ввода даты'),
	22: KKMCommonErr(u'Требуется подтверждение ввода даты'),
	24: KKMCommonErr(u'Нет больше данных для передачи ПО ККТ'),
	25: KKMCommonErr(u'Нет подтверждения или отмены продажи'),
	26: KKMCommonErr(u'Отчет с гашением прерван. Вход в режим невозможен.'),
	27: KKMCommonErr(u'Отключение контроля наличности невозможно (не настроены необходимые типы оплаты).'),
	30: KKMCommonErr(u'Вход в режим заблокирован'),
	31: KKMCommonErr(u'Проверьте дату и время'),
	32: KKMCommonErr(u'Дата и время в ККТменьше чем в ЭКЛЗ/ФП'),
	33: KKMCommonErr(u'Невозможно закрыть архив'),
	61: KKMCommonErr(u'Товар не найден'),
	62: KKMCommonErr(u'Весовой штрихкод с количеством <>1.000'),
	63: KKMCommonErr(u'Переполнение буфера чека'),
	64: KKMCommonErr(u'Недостаточное количество товара'),
	65: KKMCommonErr(u'Сторнируемое количество больше проданного'),
	66: KKMCommonErr(u'Заблокированный товар не найден в буфере чека'),
	67: KKMCommonErr(u'Данный товар не продавался в чеке, сторно невозможно'),
	68: KKMCommonErr(u'Memo PlusTM 3TM заблокировано с ПК'),
	69: KKMCommonErr(u'Ошибка контрольной суммы таблицы настроек Memo PlusTM 3TM'),
	70: KKMCommonErr(u'Неверная команда от ККТ'),
	102: KKMIncorectModeErr,
	103: KKMOutOfPaperErr,
	104: KKMCommonErr(u'Нет связи с принтером чеков'),
	105: KKMCommonErr(u'Механическая ошибка печатающего устройства'),
	106: KKMCommonErr(u'Неверный тип чека'),
	107: KKMCommonErr(u'Нет больше строк картинки'),
	108: KKMCommonErr(u'Неверный номер регистра'),
	109: KKMCommonErr(u'Недопустимое целевое устройство'),
	110: KKMCommonErr(u'Нет места в массиве картинок'),
	111: KKMCommonErr(u'Неверный номер картинки / картинка отсутствует'),
	112: KKMCommonErr(u'Сумма сторно больше, чем было получено данным типом оплаты'),
	113: KKMCommonErr(u'Сумма не наличных платежей превышает сумму чека'),
	114: KKMCommonErr(u'Сумма платежей меньше суммы чека'),
	115: KKMCommonErr(u'Накопление меньше суммы возврата илианнулирования'),
	117: KKMCommonErr(u'Переполнение суммы платежей'),
	118: KKMCommonErr(u'(зарезервировано)'),
	122: KKMCommonErr(u'Данная модель ККТ не может выполнить команду'),
	123: KKMCommonErr(u'Неверная величина скидки / надбавки'),
	124: KKMCommonErr(u'Операция после скидки / надбавки невозможна'),
	125: KKMCommonErr(u'Неверная секция'),
	126: KKMCommonErr(u'Неверный вид оплаты'),
	127: KKMCommonErr(u'Переполнение при умножении'),
	128: KKMCommonErr(u'Операция запрещена в таблице настроек'),
	129: KKMCommonErr(u'Переполнение итога чека'),
	130: KKMCommonErr(u'Открыт чек аннулирования –операция невозможна'),
	132: KKMCommonErr(u'Переполнение буфера контрольной ленты'),
	134: KKMLowPaymentErr,
	135: KKMCommonErr(u'Открыт чек возврата –операция невозможна'),
	136: KKMNeedZReportErr,
	137: KKMCommonErr(u'Открыт чек продажи –операция невозможна'),
	138: KKMCommonErr(u'Переполнение ФП'),
	140: KKMCommonErr(u'Неверный пароль'),
	141: KKMCommonErr(u'Буфер контрольной ленты не переполнен'),
	142: KKMCommonErr(u'Идет обработка контрольной ленты'),
	143: KKMDoubleZReportErr,
	145: KKMCommonErr(u'Неверный номер таблицы'),
	146: KKMCommonErr(u'Неверный номер ряда'),
	147: KKMCommonErr(u'Неверный номер поля'),
	148: KKMCommonErr(u'Неверная дата'),
	149: KKMCommonErr(u'Неверное время'),
	150: KKMCommonErr(u'Сумма чека по секции меньше суммы сторно'),
	151: KKMCommonErr(u'Подсчет суммы сдачи невозможен'),
	152: KKMCommonErr(u'В ККТ нет денег для выплаты'),
	154: KKMCommonErr(u'Чек закрыт – операция невозможна'),
	155: KKMCommonErr(u'Чек открыт – операция невозможна'),
	156: KKMCommonErr(u'Смена открыта, операция невозможна'),
	157: KKMCommonErr(u'ККТ заблокирована, ждет ввода пароля доступа к ФП'),
	158: KKMCommonErr(u'Заводской номер уже задан'),
	159: KKMCommonErr(u'Исчерпан лимит перерегистраций'),
	160: KKMCommonErr(u'Ошибка ФП'),
	162: KKMCommonErr(u'Неверный номер смены'),
	163: KKMCommonErr(u'Неверный тип отчета'),
	164: KKMCommonErr(u'Недопустимый пароль'),
	165: KKMCommonErr(u'Недопустимый заводской номер ККТ'),
	166: KKMCommonErr(u'Недопустимый РНМ'),
	167: KKMCommonErr(u'Недопустимый ИНН'),
	168: KKMCommonErr(u'ККТ не фискализирована'),
	169: KKMCommonErr(u'Не задан заводской номер'),
	170: KKMCommonErr(u'Нет отчетов'),
	171: KKMCommonErr(u'Режим не активизирован'),
	172: KKMCommonErr(u'Нет указанного чека в КЛ'),
	173: KKMCommonErr(u'Нет больше записей КЛ'),
	174: KKMCommonErr(u'Некорректный код или номер кода защиты ККТ'),
	176: KKMCommonErr(u'Требуется выполнение общего гашения'),
	177: KKMCommonErr(u'Команда не разрешена введенными кодами защиты ККТ'),
	178: KKMCommonErr(u'Невозможна отмена скидки/надбавки'),
	179: KKMCommonErr(u'Невозможно закрыть чек данным типом оплаты (в чеке присутствуют операции без контроля наличных)'),
	180: KKMCommonErr(u'Неверный номер маршрута'),
	181: KKMCommonErr(u'Неверный номер начальной зоны'),
	182: KKMCommonErr(u'Неверный номер конечной зоны'),
	183: KKMCommonErr(u'Неверный тип тарифа'),
	184: KKMCommonErr(u'Неверный тариф'),
	186: KKMCommonErr(u'Ошибка обмена с фискальным модулем'),
	190: KKMCommonErr(u'Необходимо провести профилактические работы'),
	191: KKMCommonErr(u'Неверные номера смен в ККТи ЭКЛЗ'),
	200: KKMCommonErr(u'Нет устройства, обрабатывающего данную команду'),
	201: KKMCommonErr(u'Нет связи с внешним устройством'),
	202: KKMCommonErr(u'Ошибочное состояние ТРК'),
	203: KKMCommonErr(u'Больше одной регистрации в чеке'),
	204: KKMCommonErr(u'Ошибочный номер ТРК'),
	205: KKMCommonErr(u'Неверный делитель'),
	207: KKMCommonErr(u'Исчерпан лимитактивизаций'),
	208: KKMCommonErr(u'Активизация данной ЭКЛЗ в составе данной ККТ невозможна'),
	209: KKMCommonErr(u'Перегрев головки принтера'),
	210: KKMCommonErr(u'Ошибка обмена с ЭКЛЗ на уровне интерфейса I2C'),
	211: KKMCommonErr(u'Ошибка формата передачи ЭКЛЗ'),
	212: KKMCommonErr(u'Неверное состояние ЭКЛЗ'),
	213: KKMCommonErr(u'Неисправимая ошибка ЭКЛЗ'),
	214: KKMCommonErr(u'Авария крипто-процессора ЭКЛЗ'),
	215: KKMCommonErr(u'Исчерпан временной ресурс ЭКЛЗ'),
	216: KKMCommonErr(u'ЭКЛЗ переполнена'),
	217: KKMCommonErr(u'В ЭКЛЗ переданы неверная датаили время'),
	218: KKMCommonErr(u'В ЭКЛЗ нет запрошенных данных'),
	219: KKMCommonErr(u'Переполнение ЭКЛЗ (итог чека)'),
	220: KKMCommonErr(u'Буфер переполнен'),
	221: KKMCommonErr(u'Невозможно напечатать вторую фискальную копию'),
	222: KKMCommonErr(u'Требуется гашение ЭЖ'),
	223: KKMCommonErr(u'Сумма налога больше суммы регистраций по чеку и/или итога или больше суммы регистрации'),
	224: KKMCommonErr(u'Начисление налога на последнюю операцию невозможно'),
	225: KKMCommonErr(u'Неверный номер ЭКЛЗ'),
	228: KKMCommonErr(u'Сумма сторно налога больше суммы зарегистрированного налога данного типа'),
	229: KKMCommonErr(u'Ошибка SD'),
	230: KKMCommonErr(u'Операция невозможна, недостаточно питания')
}


def checkException(ans):
    try:
        if (ans[0] != 'U'):
            logger.error(unicode(KKMUnknownAnswerErr),repr(ans))
            raise KKMUnknownAnswerErr
        else:
            raiseException(ord(ans[1]))
            return ans
    except IndexError:
        logger.error(unicode(KKMUnknownAnswerErr),repr(ans))
        raise KKMUnknownAnswerErr


def raiseException(code):
    if (code != 0):
        try:
            logger.error(unicode("ErrorCode: %s Error: %s"%(code,exceptionTable[code])))
            raise exceptionTable[code]
        except KeyError:
            logger.error(unicode(KKMUnknownErr(u'Неизвестный код ошибки: %d' % code)))
            raise KKMUnknownErr(u'Неизвестный код ошибки: %d' % code)


def _escaping(data):
    replace = string. replace
    escaped = replace(data, _atol_DLE, _atol_DLE + _atol_DLE)
    return replace(escaped, _atol_ETX, _atol_DLE + _atol_ETX)


def _unescaping(data):
    replace = string.replace
    unescaped = replace(data, _atol_DLE + _atol_ETX, _atol_ETX)
    unescaped = replace(unescaped, _atol_DLE + _atol_DLE, _atol_DLE)
    return unescaped


def _calc_crc(data):
    #from binascii import crc32
    #return crc32(data)
    crc = 0
    for i in range(len(data)):
        crc ^= ord(data[i])
    return crc

#def createAtol( device, speed, password ):
#    return AtolKKM( device, speed, password )


class AtolKKM(kkm.KKM):
    """Драйвер к ККМ с протоколом обмена компании 'Атол технологии'(версии. 2.4)
    """

    def __init__(self, device, password=0):
        _passwordLen       = 4           # Длина пароля
        _moneyWidth        = 10          # Кол-во разрядов
        _quantityWidth     = 10          # Кол-во разрядов
        _stringMax         = 20          # Максимальное значение
        _displayMax        = 20          # Максимальная длина строки для вывода на дисплей пользователя
        _moneyMax          = 9999999999  # Максимальное значение
        _quantityMax       = 9999999999  # Максимальное значение
        _moneyPrecision    = 100         # Точность денежной единицы после десят. точки (в виде множителя)
        _quantityPrecision = 1000        # Точность единицы измерения веса после десят. точки (в виде множителя)

        self.__flags       = _atol_CheckCash_flag  # Флаги режима регистрации
        self._kkmPassword = self.number2atol(password, 4)
        kkm.KKM.__init__(self, device, self._kkmPassword)
        logger.debug('Device inited OK')
        print self.GetStatus()
        self.typeDev = self.GetTypeDevice()
        self.modelTable = _modelTable
        self.typesTable = _typesTable
        self.kkmModelParams = Table2Params.kkmModelParams
        self.model = model = str(ord(self.typeDev['type'])) + '.' + str(ord(self.typeDev['model']))
        if model not in _modelTable:
            raise KKMUnknownModelErr
        self.initStringMax()
        self.initKlisheMax()
        self.initKlisheLen()
#        self.BuildTransTable()

    def OpenDevice(self):
        import serial
        # Проверить наличие блокировки устройства
        # Заблокировать или вывалиться с ошибкой
        try:
            self._kkm = serial.Serial(**self._device)
        except:
            raise KKMCommonErr(u'System error at opening KKM device')
        if (not self._kkm):
            raise KKMCommonErr(u'Unknown error at opening KKM device')

    def _set_readtimeout(self, timeout):
        self._kkm.setTimeout(timeout)

    def _atol_send_data(self, data):
        kkm = self._kkm

        cmd = data[self._passwordLen / 2]
        logger.debug('cmd: 0x%02x(%s) data: %s len: %d', ord(cmd), repr(cmd), repr(data), len(data))
        data = _escaping(data) + _atol_ETX
        crc = _calc_crc(data)
        data = _atol_STX + data + chr(crc)
        logger.debug('escaped data: %s len: %d crc: %d', repr(data), len(data), crc)

        try:
            ### Активный передатчик #######################
            for unused in range(_atol_CON_attempt):
                is_answered = False
                for unused in range(_atol_ENQ_attempt):
                    kkm.write(_atol_ENQ)
                    self._set_readtimeout(_atol_T1_timeout)
                    ch = kkm.read(1)
                    if ch == '':
                        logger.debug('No data')
                        continue
                    is_answered = True
                    if (ch == _atol_NAK):
                        logger.debug('NAK')
                        time.sleep(_atol_T1_timeout)
                    elif (ch == _atol_ENQ):
                        logger.debug('ENQ')
                        time.sleep(_atol_T7_timeout)
                        break
                    elif (ch != _atol_ACK):
                        logger.debug('received garbage')
                        break
                    else:  # (ch == _atol_ACK):
                        for k in range(_atol_ACK_attempt):
                            kkm.write(data)
                            self._set_readtimeout(_atol_T3_timeout)
                            ch = kkm.read(1)
                            #print "2[%s]" %(ch)
                            if (ch == ''):
                                #time.sleep(0.5)
                                continue
                            elif (ch != _atol_ACK or (ch == _atol_ENQ and k == 1)):
                                logger.debug('(ch != _atol_ACK(%s) or (ch == _atol_ENQ and k == 1(%d)))', k, ch != _atol_ACK)
                                continue
                            elif (ch == _atol_ACK or (ch == _atol_ENQ and k > 1)):
                                logger.debug('(ch == _atol_ACK(%s) or (ch == _atol_ENQ and k > 1(%d)))', k, ch == _atol_ACK)
                                if (ch == _atol_ACK):
                                    kkm.write(_atol_EOT)
############################### Активный приемник #######################
                                    for unused in range(_atol_CON_attempt):
                                        logger.debug('cmd 0x%02x(%s), T5 timeout %d', ord(cmd), cmd, _get_T5_timeout(cmd))
                                        self._set_readtimeout(_get_T5_timeout(cmd))
                                        ch = kkm.read(1)
                                        #print "3[%s]" %(ch)
                                        if (ch == ''):
                                            logger.error('%s: Failed %s attempts of receiving ENQ', unicode(KKMNoAnswerErr), _atol_CON_attempt)
                                            raise KKMNoAnswerErr
                                        elif (ch == _atol_ENQ):
                                            break
                                ch = ''
                                for unused in range(_atol_ACK_attempt):
                                    kkm.write(_atol_ACK)
                                    for wait_stx in range(_atol_STX_attempt):
                                        self._set_readtimeout(_atol_T2_timeout)
                                        ch = kkm.read(1)
                                        if (ch == ''):
                                            logger.error('%s: No data received on ACK', unicode(KKMNoAnswerErr))
                                            raise KKMNoAnswerErr
                                        elif (ch == _atol_ENQ):
                                            break
                                        elif (ch != _atol_STX):
                                            continue
                                        else:  # (ch == _atol_STX):
                                            answer = ''
                                            DLE_Flag = 0
                                            while (1 == 1):  # Длину буфера проверять не надо
                                                self._set_readtimeout(_atol_T6_timeout)
                                                ch = kkm.read(1)
                                                #print "5[%s]" %(ch)
                                                if (ch == ''):
                                                    break
                                                else:
                                                    if (DLE_Flag == 1):
                                                        #print "DLE off"
                                                        DLE_Flag = 0
                                                    else:
                                                        if (ch == _atol_ETX):  # Не экранир-ый ETX
                                                            #print "ETX"
                                                            break
                                                        elif (ch == _atol_DLE):
                                                            #print "DLE on"
                                                            DLE_Flag = 1
                                                answer = answer + ch
                                            # self._set_readtimeout(kkm, _atol_T6_timeout) # Уже установлен
                                            ch = kkm.read(1)  # Ждем CRC
                                            #print "6[%s]" %(ch)
                                            if (ch == ''):
                                                break
                                            #print "len=%d" %(len(answer))
                                            #for v in range(len(answer)):
                                            #    print ":%d" %(ord(answer[v]))
                                            crc = _calc_crc(answer + _atol_ETX)
                                            #print "ans:[%s] crc:[%d] ?= [%d]" %(answer + _atol_ETX,crc,ord(ch))
                                            if (crc != ord(ch)):
                                                #print "CRC err"
                                                kkm.write(_atol_NAK)
                                                break
                                            else:
                                                kkm.write(_atol_ACK)
                                                self._set_readtimeout(_atol_T4_timeout)
                                                ch = kkm.read(1)
                                                #print "7[%s]" %(ch)
                                                if (ch == _atol_EOT or ch == ''):
                                                    #print "answer1:" + answer
                                                    return _unescaping(answer)
                                                elif (ch == _atol_STX):
                                                    continue
                                                else:
                                                    self._set_readtimeout(2)  # _atol_T???_timeout
                                                    ch = kkm.read(1)
                                                    #print "8[%s]" %(ch)
                                                    if (ch == ''):
                                                        #print "answer2:" + answer
                                                        return _unescaping(answer)
                                                    else:
                                                        break
                                    if wait_stx >= _atol_STX_attempt - 1:
                                        raise KKMNoAnswerErr ####
                                kkm.write(_atol_EOT)
                                logger.error('%s: Failed %s attempts of sending ACK' % (unicode(KKMNoAnswerErr), _atol_ACK_attempt))
                                raise KKMNoAnswerErr
                        kkm.write(_atol_EOT)
                        logger.error('%s: Failed %s attempts of sending data' % (unicode(KKMNoAnswerErr), _atol_ACK_attempt))
                        raise KKMConnectionErr
                if not is_answered:
                    kkm.write(_atol_EOT)
                    logger.error('%s: Failed %s attempts of sending ENQ' % (unicode(KKMNoAnswerErr), _atol_ENQ_attempt))
                    raise KKMConnectionErr
                    break
            kkm.write(_atol_EOT)
        except OSError as e:  # for Linux
            import sys
            exc = sys.exc_info()
            if exc[1].errno == 19:
                logger.error('(1) %s' % unicode(KKMNoDeviceErr))
                raise KKMNoDeviceErr
            else:
                logger.error('(2) %s' % unicode(e))
                raise KKMConnectionErr
        except Exception as e:  # win32file raise common exception, not OSError as Linux
            logger.error('(2) %s' % unicode(e))
            raise KKMConnectionErr
        logger.error('(3) %s' % unicode(KKMConnectionErr))
        raise KKMConnectionErr

    def str2atol(self, txt, length):
        """Преобразование строки в формат ккм.

        C локализацией и дополнением пробелами до значения length.
        """
#        txt = unicode(txt).encode('cp866')
        txt = unicode(txt.decode('utf8')).encode('cp866')
        ctrlNum = 0
        for c in txt:
            if c < ' ':
                ctrlNum += 1
        length += ctrlNum
        if (len(txt) < length):
            txt = string.ljust(txt, length)
        return txt[:length]

    def strany2atol(self, txt, calign=0):
        """Преобразование строки в формат ккм.
        C локализацией
        """
        txt = unicode(txt.decode('utf8')).encode('cp866')
        if calign == 1:
            txt=txt.center(self.getStringMax())
        return txt[:self.getStringMax()]

    def atol2str(self, txt):
        """Преобразование строки из формата ккм (локализация)."""
        return txt.decode('cp866')

    def word2atol(self,number):
        number = int(number)
        val = struct.pack('>h', number)
        logger.debug('%s'%repr(val))
        return val

    def int2atol(self,number):
        number = int(number)
        return struct.pack('B', number)

    def number2atol(self, number, width=2):
        """Преобразование числа в формат ккм.

        Если width > длины number - дополнить слева нулями,
        иначе срезать конец.
        Ширина в знаках, а не в байтах!!!
        <1>стр.17 Запихать по 2 цифры в один байт."""
        number = str(number)
        if ((width % 2) != 0):
            width += 1
        if (len(number) >= width):
            number = number[:width]
        else:
            number = string.zfill(str(number), width)
        val = ''
        i = 0
        while (i < len(number)):
            val = val + chr(int(number[i]) << 4 | int(number[i + 1]))
            i += 2
        return val

    def bcd2int(self,number):
        """ Fast BCD to Integer Bytearray Convert """
        intarray = []
        for i in range(len(number)):
            bcd = ord(number[i])
            intarray.append((bcd & 0x0f) + ((int(bcd) & 0xf0) >> 4)*10)
        return intarray

    def atol2number(self, number):
        """Преобразование числа из формата ккм.

        <1>стр.17"""
        val = ''
        i = 0
        for i in range(len(number)):
            dec = ord(number[i])
            if (dec < 10):
                zero = '0'
            else:
                zero = ''
            val = val + zero + hex(dec)[2:]
        return long(val)

    def money2atol(self, money, width=None):
        """Преобразование денежной суммы (decimal) в формат ккм (МДЕ).

        ширина в знаках, а не в байтах!!!
        <1>стр.17"""
        if (width == None):
            width = self._moneyWidth
        elif (width > self._moneyWidth):
            logger.error(unicode(KKMWrongMoneyErr(u'Затребована ширина превышающая максимально допустимое значение')))
            raise KKMWrongMoneyErr(u'Затребована ширина превышающая максимально допустимое значение')
        money = round(money * self._moneyPrecision)
#        money = float(money * self._moneyPrecision)
        if (money > self._moneyMax):
            logger.error(unicode(KKMWrongMoneyErr(u'Число типа "money" превышает максимально допустимое значение')))
            raise KKMWrongMoneyErr(u'Число типа "money" превышает максимально допустимое значение')
        return self.number2atol(long(money), width)

    def atol2money(self, money):
        """Преобразование из формата ккм (МДЕ) в денежную сумму (decimal).

        <1>стр.17"""
        return Decimal(self.atol2number(money)) / self._moneyPrecision

    def quantity2atol(self, quantity, width=None):
        """Преобразование количества в формат ккм.

        ширина в знаках, а не в байтах!!!
        <1>стр.17"""
        if (width == None):
            width = self._quantityWidth
        elif (width > self._quantityWidth):
            logger.error(unicode(KKMWrongQuantityErr(u'Затребована ширина превышающая максимально допустимое значение')))
            raise KKMWrongQuantityErr(u'Затребована ширина превышающая максимально допустимое значение')
        quantity = round(quantity * self._quantityPrecision)  # Марсель! Округлять или срезать ???
        if (quantity > self._quantityMax):
            logger.error(unicode(KKMWrongQuantityErr(u'Число типа "quantity" превышает максимально допустимое значение')))
            raise KKMWrongQuantityErr(u'Число типа "quantity" превышает максимально допустимое значение')
        quantity = str(quantity)
        dot = string.find(quantity, '.')
        if (dot > 0):
            quantity = quantity[0:dot]
        else:
            logger.critical(str(RuntimeError(u'Невозможное значение')))
            raise RuntimeError(u'Невозможное значение')
        # Для скорости можно сдублировать, иначе - лишнее двойное преобразование
        return self.number2atol(long(quantity), width)

    def atol2quantity(self, quantity):
        """Преобразование из формата ккм (МДЕ) в количество.

        <1>стр.17"""
        return self.atol2number(quantity) / self._quantityPrecision

    def date2atol(self, bdate):
        return bdate

    def atol2date(self, bdate):
        darr = self.bcd2int(bdate)
        darr[0] = darr[0]+2000
        d = datetime.date(darr[0],darr[1],darr[2])
        return d

    def time2atol(self, btime):
        return btime

    def atol2time(self, btime):
        tarr = self.bcd2int(btime)
        t = datetime.time(tarr[0],tarr[1],tarr[2])
        return t

    ### Запросы

    def GetLastSummary(self):
        """Запрос последнего сменного итога.
        <1>стр.28
        """
        try:
            return self.atol2money(
                checkException(
                self._atol_send_data(self._kkmPassword + _atol_GetLastSummary_cmd)
                )[2:]
                )
        except IndexError:
            raise KKMUnknownAnswerErr

    def GetCashSummary(self):
        ans = self._atol_send_data(self._kkmPassword + _atol_GetCashSummary_cmd)
        try:
            if (ans[0] == 'M'):
                logger.info('CashInKKM %d'%self.atol2money(ans[2:]))
                return self.atol2money(ans[2:])
            else:
                return 0
        except IndexError:
            raise KKMUnknownAnswerErr


    def GetStatus(self):
        ans = self._atol_send_data(self._kkmPassword + _atol_GetStatus_cmd)
        try:
            if (ans[0] != 'D'):
                raise KKMUnknownAnswerErr
            cashier = self.atol2number(ans[1])
            site = self.atol2number(ans[2])
            date = self.atol2date(ans[3:6])
            time = self.atol2time(ans[6:9])
            flags = ord(ans[9])
            mashine = self.atol2number(ans[10:14])
            model = ord(ans[14])
            version = ans[15] + '.' + ans[16]
            mode = ord(ans[17]) & 0x0F
            submode = (ord(ans[17]) & 0xF0) >> 4
            check = self.atol2number(ans[18:20])
            smena = self.atol2number(ans[20:22])
            checkState = ord(ans[22])
            checkSum = self.atol2number(ans[23:28])
            dot = ord(ans[28])
            port = ord(ans[29])
        except IndexError:
            raise KKMUnknownAnswerErr
        return (cashier, site, date, time, flags, \
                mashine, model, version, mode, submode, \
                check, smena, checkState, checkSum, dot, port)

    def getKKMId(self):
        """Запрос уникального идентификатора ККМ.
        """
        return self.GetStatus()[5]

    def GetCheckNum(self):
        """Запрос текущего номера чека.
        """
        return self.GetStatus()[10]

    def GetCheckSum(self):
        """Запрос суммы текущего чека.
        """
        return self.GetStatus()[12]

    def GetCurrentState(self):
        """Запрос кода состояния (режима) ККМ.

        Result: mode, submode, printer, paper
        <1>стр.28
        """
        ans = self._atol_send_data(self._kkmPassword + _atol_GetCurrentState_cmd)
        try:
            mode = ord(ans[1]) & 0x0F
            submode = (ord(ans[1]) & 0xF0) >> 4
            printer = (ord(ans[2]) & 0x02) == 1
            paper = (ord(ans[2]) & 0x01) == 1
        except IndexError:
            raise KKMUnknownAnswerErr
        return (mode, submode, printer, paper)

    def GetCurrentMode(self):
        """Запрос режима ККМ
        """
        return self.GetCurrentState()[0]

    _atol_mode1_offline = '\x8000'
    _atol_mode1_online  = '\x4000'
    _atol_mode1_passive = '\x2000'
    _atol_mode1_fiscreg = '\x1000'
    _atol_mode1_fiscard = '\x0800'

    def GetTypeDevice(self):
        """Получение типа устройства.

        Result: error, protocol, type, model, mode,
        majorver, minorver, codepage, build, name
        <1>стр.28,63
        """

        ans = self._atol_send_data(self._kkmPassword + _atol_GetTypeDevice_cmd)
        try:
            if (ord(ans[0]) != 0):
                raiseException(ord(ans[0]))
            error = ans[0]
            protocol = ans[1]
            type_ = ans[2]
            model = ans[3]
            mode = (ord(ans[4]) << 8) | ord(ans[5])
            majorver = ord(ans[6])
            minorver = ord(ans[7])
            codepage = ord(ans[8])
            build = self.atol2number(ans[9:11])
            name = ans[11:]
        except IndexError:
            raise KKMUnknownAnswerErr
        #print 'XMM 5 GetTypeDev', {'error': error, 'protocol': protocol, 'type': type, 'model': model,
        #        'mode': mode, 'majorver': majorver, 'minorver': minorver,
        #        'codepage': codepage, 'build': build, 'name': name}
        return {'error': error, 'protocol': protocol, 'type': type_, 'model': model,
                'mode': mode, 'majorver': majorver, 'minorver': minorver,
                'codepage': codepage, 'build': build, 'name': name}

    def ResetMode(self):
        """Выход из текущего режима.
        """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_ResetMode_cmd)
            )

    def SetMode(self, mode, modePassword):
        """Установить режим.

        <1>стр.19
        """
        curMode = self.GetCurrentMode()
        if (mode != curMode):
            if (curMode != _atol_Select_mode):
                self.ResetMode()
            checkException(
                self._atol_send_data(self._kkmPassword + _atol_SetMode_cmd + \
                                     self.number2atol(mode) + self.number2atol(modePassword, 8))
                )

    def isRegistrationMode(self):
        return self.GetCurrentMode() == _atol_Registration_mode

    def isXReportMode(self):
        return self.GetCurrentMode() == _atol_XReport_mode

    def isZReportMode(self):
        return self.GetCurrentMode() == _atol_ZReport_mode

    def isProgrammingMode(self):
        return self.GetCurrentMode() == _atol_Programming_mode

    def isInspectorMode(self):
        return self.GetCurrentMode() == _atol_Inspector_mode

    def isCheckOpen(self):
        return self.GetStatus()[12] != 0

    def setRegistrationMode(self, password):
        self.SetMode(_atol_Registration_mode, password)

    def setXReportMode(self, password):
        self.SetMode(_atol_XReport_mode, password)

    def setZReportMode(self, password):
        self.SetMode(_atol_ZReport_mode, password)

    def setProgrammingMode(self, password):
        self.SetMode(_atol_Programming_mode, password)

    def setInspectorMode(self, password):
        raise KKMNotImplementedErr
        self.SetMode(_atol_Inspector_mode, password)

    def SetSecCode(self,code):
        logger.debug('Code %s: Atol Code: %s'%(code,self.atol2number(self.number2atol(code,16))))
        checkException(
            self._atol_send_data('\x6d\x04'+self.number2atol(code,16))
            )

    def initStringMax(self):
        try:
            self._strMax = _modelTable[self.model][_atol_StringMax_idx]
        except KeyError:
            raise KKMUnknownModelErr

    def initKlisheMax(self):
        try:
            self._klisheMax = _modelTable[self.model][_atol_KlisheMax_idx]
        except KeyError:
            raise KKMUnknownModelErr

    def initKlisheLen(self):
        try:
            self._klisheLen = _modelTable[self.model][_atol_KlisheLen_idx]
        except KeyError:
            raise KKMUnknownModelErr

    ### Общие команды

    def PrintString(self, txt, wrap=False):
        """Печать строки на кассовой ленте"""
        idx = 0
        slen = len(txt)
        smax = self.getStringMax()
        logger.info("SMAX: %d, SLEN: %d, TXT: '%s'"%(slen,smax,txt))
        while idx <= slen:
            checkException(
                self._atol_send_data(self._kkmPassword + _atol_PrintString_cmd + \
                                     self.str2atol(txt, smax))
                )
#            checkException(
#                self._atol_send_data(self._kkmPassword + _atol_PrintString_cmd + \
#                                     self.str2atol(txt[idx:idx + smax], smax))
#                )
            idx += smax
            if not wrap:
                break


    def PrintCustom(self, txt, printer=1, font=0, magnify=0, spacing=5, bright=0, cl=1, kl=1, fmt=0, center=0):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_PrintCustom_cmd + \
                                 self.number2atol(self.getRegFlags()) + self.number2atol(printer) + self.number2atol(font) + self.number2atol(magnify) + self.number2atol(spacing) + \
                                 self.number2atol(bright) + self.number2atol(cl) + self.number2atol(kl) + self.number2atol(fmt) + '\x00\x00' + \
                                 self.strany2atol(txt,calign=center))
            )

    def ByPassKKM(self,txt):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_ByPass_cmd + txt)
            )
            
    def BarCodePrint(self,barcode):
        """ Barcode Print """
        barcodeinit = [ '\x1ba\x01', '\x1dh\x80', '\x1dw\x02', '\x1dH\x01' ]
#        barcodeinit = [ '\x1ba\x01', '\x1dh\xa2', '\x1dw\x02', '\x1dH\x01' ]
        barcodeinit.append('\x1dk\x04' + barcode + '\x00')
        for bytecode in barcodeinit:
            checkException(
                self._atol_send_data(self._kkmPassword + _atol_ByPass_cmd + bytecode)
                )

    def OpenCashBox(self):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_OpenCashBox_cmd)
            )
            
    def CutCheck(self,flag=0):
        """ Обрезка чека """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_CutCheck_cmd + self.number2atol(flag))
            )

    ### Команды режима регистрации
    # <1>стр.34

    def getRegFlags(self):
        flags = 0
        if (self.isTestOnlyMode()):
            flags |= _atol_TestOnly_flag
        if (self.isCheckCashMode()):
            flags |= _atol_CheckCash_flag
        return flags

    def cashPayType( self ):   return _atol_cash_payment
    def creditPayType( self ): return _atol_type2_payment
    def taraPayType( self ):   return _atol_type3_payment
    def cardPayType( self ):   return _atol_type4_payment

    def CashIncome(self, sum_):
        """Внесение денег."""
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_CashIncom_cmd + \
                            self.number2atol(self.getRegFlags()) + self.money2atol(sum_))
            )

    def CashOutcome(self, sum_):
        """Выплата денег (инкасация)."""
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_CashOutcom_cmd + \
                            self.number2atol(self.getRegFlags()) + self.money2atol(float(sum_)))
            )

    _checkTypeDict = {
        kkm.kkm_Sell_check     : 1,
        kkm.kkm_Return_check   : 2,
        kkm.kkm_Annulate_check : 3
        }

    def OpenCheck(self, checkType=kkm.kkm_Sell_check):
        """Открыть Чек.

        <2>стр.63,<3>стр.37"""
        print 'kkmPassword',self._kkmPassword
        checkException(
            self._atol_send_data(self._kkmPassword + \
                                 _atol_OpenCheck_cmd + self.number2atol(self.getRegFlags()) + self.number2atol(self._checkTypeDict[checkType]))
            )

    def Sell(self, name, price, quantity, department):
        """Продажа.

        Если режим TestOnly включен - выполнить только проверку возможности исполнения.
        Если режим PreTestMode включен - выполнить с проверкой возможности исполнения.
        <1>стр.35
        """
        logger.info('Sell %s, price: %s, quantity: %s, department: %s' % (
                    name, price, quantity, department))
        if (self.isPreTestMode() or self.isTestOnlyMode()):
            checkException(
                self._atol_send_data(self._kkmPassword + _atol_Sell_cmd + \
                                self.number2atol(self.getRegFlags() | _atol_TestOnly_flag) + \
                                self.money2atol(price) + self.quantity2atol(quantity) + \
                                self.number2atol(department))
                )
        if (self.isTestOnlyMode()):
            return
        self.PrintString(name)
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Sell_cmd + \
                                 self.number2atol(self.getRegFlags()) + self.money2atol(price) + \
                                 self.quantity2atol(quantity) + self.number2atol(department))
            )

    def BuyReturn(self, name, price, quantity):
        """Возврат.

        Если режим TestOnly включен - выполнить только проверку возможности исполнения.
        Если режим PreTestMode включен - выполнить с проверкой возможности исполнения.
        <1>стр.37
        """
        if (self.isPreTestMode() or self.isTestOnlyMode()):
            checkException(
                self._atol_send_data(self._kkmPassword + _atol_Return_cmd + \
                                self.number2atol(self.getRegFlags() | _atol_TestOnly_flag) + \
                                self.money2atol(price) + self.quantity2atol(quantity))
                )
        if (self.isTestOnlyMode()):
            return
        self.PrintString(name)
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Return_cmd + \
                                 self.number2atol(self.getRegFlags()) + self.money2atol(price) + \
                                 self.quantity2atol(quantity))
            )

    def Discount(self, count, area=kkm.kkm_Sell_dis, \
                  type_=kkm.kkm_Sum_dis, sign_=kkm.kkm_Discount_dis):
        """Начисление скидки/надбавки.

        <1>стр.37
        """
        if (area == kkm.kkm_Sell_dis):
            area = 1
        else:
            area = 0
        if (type_ == kkm.kkm_Procent_dis):
            type_ = 0
            count = self.number2atol(count * 100, 5)  # 100.00%
        else:
            type_ = 1
            count = self.money2atol(count)
        if (sign_ == kkm.kkm_Discount_dis):
            sign_ = 0
        else:
            sign_ = 1

        logger.info('Discount : ' + repr(count) + '\t' + str(self.atol2money(count)))

        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Discount_cmd + \
                                 self.number2atol(self.getRegFlags()) + \
                                 self.number2atol(area) + \
                                 self.number2atol(type_) + \
                                 self.number2atol(sign_) + \
                                 count)
            )

    def Annulate(self):
        """ Аннулирование всего чека """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Annulate_cmd)
            )


    def AnnulateSumm(self, sum_, count_):
        """Аннулирование чека с указанием суммы

        <1>стр.38
        """
        logger.info('AnnulateSumm : ' + str(sum_) + '\t' + self.money2atol(sum_))
#        if (payType == None):
#            payType = self.cashPayType()
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_AnnulateSumm_Cmd + \
                                 self.number2atol(self.getRegFlags()) + \
                                 self.money2atol(sum_) + self.quantity2atol(count_))
            )

    def Payment(self, sum_, payType=None):
        """Оплата чека с подсчетом суммы сдачи.

        <1>стр.38
        """
        logger.info('Payment : ' + str(sum_) + '\t' + self.money2atol(sum_))
        if (payType == None):
            payType = self.cashPayType()
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Payment_cmd + \
                                 self.number2atol(self.getRegFlags()) + \
                                 self.number2atol(payType) + self.money2atol(sum_))
            )

    def Calculate(self, sum_, payType=None):
        """Проверка чека с подсчетом суммы сдачи.

        <1>стр.71
        """
        logger.info('Calculate : ' + str(sum_) + '\t' + self.money2atol(sum_))
        if (payType == None):
            payType = self.cashPayType()
        res=checkException(
            self._atol_send_data(self._kkmPassword + _atol_Calculate_cmd + \
                                 self.number2atol(self.getRegFlags()) + \
                                 self.number2atol(payType) + self.money2atol(sum_))
            )
        if res[1] == '\x00':
           print "Ostatok: %d, Sdacha: %d"%(self.atol2money(res[2:7]),self.atol2money(res[8:13]))

    ### Команды режима отчетов без гашения

    def ReportWOClearing(self, reportType):
        """
        """
        import time
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_XReport_cmd + \
                                 self.number2atol(reportType))
            )
        mode, submode, printer, paper = self.GetCurrentState()
        while (mode == 2 and submode == 2):
            time.sleep(_atol_Report_timeout)
            mode, submode, printer, paper = self.GetCurrentState()
            if (mode == 2 and submode == 0):
                if (printer):
                    raise KKMPrinterConnectionErr
                if (paper):
                    raise KKMOutOfPaperErr
                else:
                    return

    ### Команды режима отчетов c гашением

    def ClearingReport(self):
        """
        """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_ClearingReport_cmd)
            )
        mode, submode, printer, paper = self.GetCurrentState()
        while (mode == 3 and submode == 2):
            time.sleep(_atol_Report_timeout)
            mode, submode, printer, paper = self.GetCurrentState()
            if (mode == 3 and submode == 0):
                if (printer):
                    raise KKMPrinterConnectionErr
                if (paper):
                    raise KKMOutOfPaperErr
                else:
                    return
            else:
                raise KKMReportErr

    def ZReportHold(self):
        """Включить режим формирования отложенных Z отчётов.

        Result: кол-во свободных полей для записи Z-отчётов
        <4>стр.9
        """
        try:
            return ord(checkException(
                self._atol_send_data(self._kkmPassword + _atol_ZReportToMem_cmd)
                )[2])
        except IndexError:
            raise KKMUnknownAnswerErr

    def ZReportUnHold(self):
        """Распечатать отложенные Z-отчёты и отключить режим отложенных Z отчётов.
        """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_ZReportFromMem_cmd)
            )

    def ZReport(self):
        """
        """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_ZReport_cmd)
            )
        mode, submode, printer, paper = self.GetCurrentState()
        logger.debug(str(('00', mode, submode, printer, paper)))
        while (mode == 3 and submode == 2):
            logger.debug(str(('32-0')))
            time.sleep(_atol_Report_timeout)
            logger.debug(str(('32-1')))
            mode, submode, printer, paper = self.GetCurrentState()
            logger.debug(str(('32-2', mode, submode, printer, paper)))
        if (mode == 7 and submode == 1):
            logger.debug(str(('71-0')))
            while (mode == 7 and submode == 1):
                logger.debug(str(('71-1')))
                time.sleep(_atol_Report_timeout)
                logger.debug(str(('71-2')))
                mode, submode, printer, paper = self.GetCurrentState()
                logger.debug(str(('71-3', mode, submode, printer, paper)))
            return
        else:
            logger.debug(str(('??', mode, submode, printer, paper)))
            if (mode == 3 and submode == 0):
                # ZReport finished but an exception will raise
                logger.info('ZReport printed. Command waiting')
                return
            if (printer):
                raise KKMPrinterConnectionErr
            if (paper):
                raise KKMOutOfPaperErr
            else:
                raise KKMReportErr

    def CommonClearing(self):
        """
        """
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_CommonClear_cmd)
            )
        mode, submode, printer, paper = self.GetCurrentState()
        while (mode == 3 and submode == 6):
            time.sleep(_atol_Report_timeout)
            mode, submode, printer, paper = self.GetCurrentState()
            if (mode == 3 and submode == 0):
                if (printer):
                    raise KKMPrinterConnectionErr
                if (paper):
                    raise KKMOutOfPaperErr
                else:
                    return
            else:
                raise KKMReportErr

    _reportTable = {
        kkm.kkm_Clearing_report: (ClearingReport, None),
        kkm.kkm_Z_report: (ZReport, None),
        kkm.kkm_X_report: (ReportWOClearing, 1),
        kkm.kkm_Department_report: (ReportWOClearing, 2),
        kkm.kkm_Cashier_report: (ReportWOClearing, 3),
        kkm.kkm_Goods_report: (ReportWOClearing, 4),
        kkm.kkm_Hour_report: (ReportWOClearing, 5),
        kkm.kkm_Quantity_report: (ReportWOClearing, 7)
        }

    def Report(self, type_):
        """
        """
        try:
            if (self._reportTable[type_][1] != None):
                self._reportTable[type_][0](self, self._reportTable[type_][1])
            else:
                self._reportTable[type_][0](self)
        except KeyError:
            raise KKMReportErr(u'Неизвестный тип отчета')

    ### Команды режима программирования
    # <1>стр.44

    def readTable(self, table, row, field):
        logger.debug('Read Table')
        try:
            return checkException(
                self._atol_send_data(self._kkmPassword + _atol_ReadTable_cmd + \
                                     self.number2atol(table) + self.number2atol(row) + \
                                     self.number2atol(field))
                )[2:]
#        try:
#            return checkException(
#                self._atol_send_data(self._kkmPassword + _atol_ReadTable_cmd + \
#                                     self.number2atol(table) + self.number2atol(row, 4) + \
#                                     self.number2atol(field))
#                )[2:]
        except IndexError:
            raise KKMUnknownAnswerErr

    def AltReadTable(self, table, row, field):
        logger.debug('Alternate Read Table')
        try:
            return checkException(
                self._atol_send_data(self._kkmPassword + _atol_ReadTable_cmd + \
                                     self.int2atol(table) + self.word2atol(row) + \
                                     self.int2atol(field))
                )[2:]
#        try:
#            return checkException(
#                self._atol_send_data(self._kkmPassword + _atol_ReadTable_cmd + \
#                                     self.number2atol(table) + self.number2atol(row, 4) + \
#                                     self.number2atol(field))
#                )[2:]
        except IndexError:
            raise KKMUnknownAnswerErr

    def _writeTable(self, table, row, field, value):
        logger.debug('Write table')
        return checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(table) + self.number2atol(row, 4) + \
                                 self.number2atol(field) + value)
            )

    def writeTable(self, table, row, field, value):
        logger.debug('Custom Write table')
        return checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(table) + self.number2atol(row, 4) + \
                                 self.number2atol(field) + value)
            )

    _progTable = {  # (table,row,field,bitmask,type,length,{None|dict|func})
        'kkmNumber':          (2,1,1,None,'int',1,None),
        'multiDepart':        (2,1,2,None,'int',1,{'multi':0,'single':1}),
        'taxType':            (2,1,11,None,'int',1,{'deny':0,'all':1,'sell':2}),
        'departName':         (2,1,15,None,'int',1,{0:0,1:1}),
        'printNotClearedSum': (2,1,18,0b00000011,'bin',1,{False:0,'deny':0,'all':0b00000001,'last':0b00000011,True:0b11}),
        'makeIncasation':     (2,1,18,0b00000100,'bin',1,{False:0,True:0b00000100}),
        'extendedZreport':    (2,1,18,0b00001000,'bin',1,{False:0,True:0b00001000}),
        'pushLength':         (2,1,22,0b00000111,'bin',1,None),  # 0..15
        'onCutCheck':         (2,1,22,0b00110000,'bin',1,{'save':0,'push':0b010000,'drop':0b110000}),
        'prevCheck':          (2,1,22,0b01000000,'bin',1,{'save':0,'drop':0b1000000}),
        'startCheck':         (2,1,22,0b10000000,'bin',1,{'loop':0,'push':0b10000000}),
        'kkmPassword':        (2,1,23,None,'int',2,None),
        'cutDocument':        (2,1,24,None,'int',1,{False:0,True:1}),
        'setPayCreditName':   (12,1,1,None,'string',10,None),
        'setPayTaraName':     (12,2,1,None,'string',10,None),
        'setPayCardName':     (12,3,1,None,'string',10,None)
        }

    def Programming(self, args):
        """Программирование ККМ.

        args в виде {'параметр': значение,}
        """
        try:
            for k in args.keys():
                table, row, field, bitmask, rtype, length, trans = self._progTable[k]
                if (trans == None):
                    value = args[k]
                elif (type(trans) == type({})):  # Dict
                    value = trans[args[k]]
                    print('dict value %s'%bin(value))
                elif (str(type(trans)) == str(type(lambda x: x))):  # function
                    value = trans(args[k])
                    print('lambda value %s'%bin(value))
                else:
                    raise KKMNotImplementedErr
                if (bitmask != None):
                    oldValue = ord(self.readTable(table, row, field))
                    logger.debug(str(('P0 old %s oldbin %s' % (oldValue, bin(oldValue)))))
                    #oldValue = self.atol2number(oldValue)
                    logger.debug(str(('P1 bin %s | (oldbin %s & ~%s), binold %s' % (bin(value), bin(oldValue), bin(bitmask), bin(oldValue & ~bitmask)))))
                    value |= (oldValue & ~bitmask)
                    logger.debug(str(('P2', bin(value), chr(value), 'AA')))
                    value = chr(value)
                    #value = self.number2atol(value, length * 2)
                elif (rtype == 'string'):
                    value = self.str2atol(value, length)
                elif (rtype == 'int'):
                    value = self.number2atol(value, length * 2)  # по 2 знака на байт!
                else:
                    raise KKMNotImplementedErr
                print('dict newvalue %s'%bin(ord(value)))
                self._writeTable(table, row, field, value)
        except KeyError:
            raise KKMNotImplementedErr

    def setKKMPassword(self, password):
        self._kkmPassword = self.number2atol(password, 4)
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(2) + self.number2atol(1, 4) + \
                                 self.number2atol(23) + self._kkmPassword)
            )

    def setCashierPassword(self, cashier, password):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(3) + self.number2atol(cashier, 4) + \
                                 self.number2atol(1) + self.number2atol(password, 8))
            )

    def setAdminPassword(self, password):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(3) + self.number2atol(29, 4) + \
                                 self.number2atol(1) + self.number2atol(password, 8))
            )

    def setSysAdminPassword(self, password):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(3) + self.number2atol(30, 4) + \
                                 self.number2atol(1) + self.number2atol(password, 8))
            )


    def cp866toatol(self,text,calign=0):
         encoded = unicode(text.decode('utf-8')).encode('cp866')
         txt = "".join(encoded)
         if calign == 1:
            txt=txt.center(self.getStringMax(),' ')
         txt = '{:<56}'.format(txt)
         return txt
        
    def setKlishe(self, klishe):
        """Установить клише/рекламу в чеке.

        параметр klishe - список строк.
        <1>стр.78
        """
        i = 1
        for s in klishe:
            checkException(
                self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                     self.number2atol(6) + self.number2atol(i, 4) + \
                                     self.number2atol(1) + self.cp866toatol(s, calign=1))
#                                     self.number2atol(1) + self.strany2atol(s, self.getKlisheLen()))
            )
            i += 1
#        for j in range(i, self.getKlisheMax()):
#            checkException(
#                self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
#                                     self.number2atol(6) + self.number2atol(j, 4) + \
#                                     self.number2atol(1) + self.str2atol(s, self.getKlisheLen()))
#            )

    def setDepartName(self, depart, name):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(7) + self.number2atol(depart, 4) + \
                                 self.number2atol(1) + self.str2atol(name, 20))
            )

    def setTaxRate(self, tax, value):
        checkException(
            self._atol_send_data(self._kkmPassword + _atol_Programming_cmd + \
                                 self.number2atol(8) + self.number2atol(tax, 4) + \
                                 self.number2atol(1) + self.number2atol(value, 4))
            )

    def BuildTransTable(self):
        self.transtable = []
        self.backtranstable = [ '\x20' for i in range(256) ]
        for i in xrange(128,160):
          self.transtable.append(chr(i))
        for i in xrange(32,128):
          self.transtable.append(chr(i))
#        self.transtable.append(' ')
        for i in xrange(160,176):
          self.transtable.append(chr(i))
        for i in xrange(224,240):
          self.transtable.append(chr(i))
        self.transtable[36]='\xfc'
        self.transtable.append('\x24')
        self.transtable.append('\xf2')
        self.transtable.append('-')
        for i in xrange(163,256):
          self.transtable.append('\x20')
        transtable = ['%s'%chr(i) for i in range(256) ]
	backtranstable = [ '\x20' for i in range(256) ]
	index=0
	for i in xrange(128,160):
	    transtable[i] = chr(index)
	    index+=1
	#for i in xrange(32,128):
	#    transtable.append(chr(i))
	#self.transtable.append(' ')
	index=128
	for i in xrange(0,32):
	    transtable[i] = '\x20'
	for i in xrange(160,176):
	    transtable[i] = chr(index)
	    index+=1
	for i in xrange(176,224):
	    transtable[i] = '\x20'
	for i in xrange(224,240):
	    transtable[i] = chr(index)
	    index+=1
	for i in xrange(240,256):
	    transtable[i] = '\x20'
	transtable[36]='\xfc'  # \x24
	transtable[252]='\x24' # \xfc
	transtable[9]='\xfe'   # \x09
	transtable[10]='\xfd'  # \x0a
	transtable[196]='\xfa' # \xc4


    def print_table(self, lines, separate_head=True):
      """Prints a formatted table given a 2 dimensional array"""
      #Count the column width
      widths = []
      for line in lines:
          for i,size in enumerate([len(x) for x in line]):
              while i >= len(widths):
                  widths.append(0)
              if size > widths[i]:
                  widths[i] = size

      #Generate the format string to pad the columns
      print_string = ""
      for i,width in enumerate(widths):
          print_string += "{" + str(i) + ":" + str(width) + "} | "
      if (len(print_string) == 0):
          return
      print_string = print_string[:-3]

      #Print the actual data
      for i,line in enumerate(lines):
          print(print_string.format(*line))
          if (i == 0 and separate_head):
              print("-"*(sum(widths)+3*(len(widths)-1)))

            
#    def PrintToDisplay(self, txt):
#        """Вывод сообщения на дисплей покупателя"""
#        checkException(
#            self._atol_send_data(self._kkmPassword + _atol_PrintToDisplay_cmd + \
#                                 self.number2atol(1) + \
#                                 self.str2atol(txt, self.getDisplayStringMax()))
#            )
#
#    def DirectPrint(self, txt):
#        """Вывод сообщения на дисплей покупателя"""
#        checkException(
#            self._atol_send_data(self._kkmPassword + _atol_PrintToDisplay_cmd + \
#                                 self.number2atol(0) + \
#                                 self.str2atol(txt, self.getDisplayStringMax()))
#            )
