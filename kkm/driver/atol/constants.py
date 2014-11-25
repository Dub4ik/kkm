# -*- coding: utf8 -*-
from . import commands


CON_ATTEMPTS = 100  # Ожидание первого ACK
ANS_ATTEMPTS = 100  # Ожидание STX
STX_ATTEMPTS = 100  # Кол-во попыток прочитать STX байт
ENQ_ATTEMPTS = 10  # Кол-во проверок готовности ККМ (по стандарту - 5)
ACK_ATTEMPTS = 10

T1_TIMEOUT = 0.5  # ?Стандартное время ожидания получения 1го байта
T2_TIMEOUT = 20  # Время ожидания состояния "Идет передача ответа"
T3_TIMEOUT = 0.5
T4_TIMEOUT = 0.5
T5_TIMEOUT = 10  # Время ожидания состояния "Готов к передаче ответа"
T6_TIMEOUT = 0.5
T7_TIMEOUT = 0.5
T8_TIMEOUT = 1

T5_TIMEOUT_MAP = {
    commands.CLOSE_CHECK: 20,
    commands.Z_REPORT: 40,
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

NO_DATA_RETRY_COUNT = 10  # Hack for some cases if not data recieved during response reading


def get_t5_timeout_for(command):
    return T5_TIMEOUT_MAP.get(command, T5_TIMEOUT)


REPORT_TIMEOUT = 0.5

PASSWORD_MAX_LEN = 4  # Длина пароля
RESPONSE_MAX_LEN = 10240  # Max длина ответа от ККМ

_atol_mode1_offline = b'\x8000'
_atol_mode1_online = b'\x4000'
_atol_mode1_passive = b'\x2000'
_atol_mode1_fiscreg = b'\x1000'
_atol_mode1_fiscard = b'\x0800'
