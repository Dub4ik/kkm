# -*- coding: utf-8 -*-
STX = b'\x02'  # ^B Начало текста
ETX = b'\x03'  # ^C Конец текста
EOT = b'\x04'  # ^D Конец передачи
ENQ = b'\x05'  # ^E Запрос
ACK = b'\x06'  # ^F Подтверждение
DLE = b'\x10'  # ^Q Экранирование управ. символов
NAK = b'\x15'  # ^U Отрицание
FS = b'\x1c'  # ^] Разделитель полей

symbols_map = {
    STX: '<STX>',
    ETX: '<ETX>',
    EOT: '<EOT>',
    ENQ: '<ENQ>',
    ACK: '<ACK>',
    DLE: '<DLE>',
    NAK: '<NAK>',
    FS: '<FS>',
}


def get_symbol_name(symbol):
    return symbols_map.get(symbol, symbol)


def humanize(data):
    return ' '.join(symbols_map.get(bytes((s,)), '{:02x}'.format(s)) for s in data)
