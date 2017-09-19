#!/usr/bin/env python
# encoding:utf-8
# This file is generated, do not edit it.

from .commands import *
from .base import BaseApi, BaseStateMachine
from .base import *
from collections import OrderedDict
import sys


class Api(BaseApi):
    """Api implementation mixin."""

    CMDMAP={}
    def get_dump(self, code):
        rawdata = b''
        rawdata += bytes([code])
        # send command to device."""
        self._send_command(GET_DUMP, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_dump(answer)

    def _interp_get_dump(self, answer):
        assert bytes([answer.pop(0)]) == GET_DUMP, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "blocks_count": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_dump",rc)

        return rc

    CMDMAP[GET_DUMP]=_interp_get_dump

    def data_dump(self):
        rawdata = b''
        # send command to device."""
        self._send_command(DATA_DUMP, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_data_dump(answer)

    def _interp_data_dump(self, answer):
        assert bytes([answer.pop(0)]) == DATA_DUMP, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "chip_code": answer.pop(0),
            "bolock_number": (answer.pop(0) + answer.pop(0) << 8),
            "data": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("data_dump",rc)

        return rc

    CMDMAP[DATA_DUMP]=_interp_data_dump

    def data_dump_interrupt(self):
        rawdata = b''
        # send command to device."""
        self._send_command(DATA_DUMP_INTERRUPT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_data_dump_interrupt(answer)

    def _interp_data_dump_interrupt(self, answer):
        assert bytes([answer.pop(0)]) == DATA_DUMP_INTERRUPT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("data_dump_interrupt",rc)

        return rc

    CMDMAP[DATA_DUMP_INTERRUPT]=_interp_data_dump_interrupt

    def get_current_state_short(self):
        rawdata = b''
        # send command to device."""
        self._send_command(GET_CURRENT_STATE_SHORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_current_state_short(answer)

    def _interp_get_current_state_short(self, answer):
        assert bytes([answer.pop(0)]) == GET_CURRENT_STATE_SHORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "flags": KKMFlags((answer.pop(0) + answer.pop(0) << 8)),
            "mode": KKMMode(answer.pop(0)),
            "submode": KKMSubMode(answer.pop(0)),
            "count_ops": answer.pop(0) + (answer.pop(4) << 8),
            "battery": answer.pop(0),
            "power_supply": answer.pop(0),
            "fa_error": self._fa_error(answer.pop(0)),
            "ecpt_error": self._ecpt_error(answer.pop(0)),
            "reserved": bytearray() + bytearray([answer.pop(0)]) + bytearray([answer.pop(0)]) + bytearray([answer.pop(0)]),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_current_state_short",rc)

        return rc

    CMDMAP[GET_CURRENT_STATE_SHORT]=_interp_get_current_state_short

    def get_current_state(self):
        rawdata = b''
        # send command to device."""
        self._send_command(GET_CURRENT_STATE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_current_state(answer)

    def _interp_get_current_state(self, answer):
        assert bytes([answer.pop(0)]) == GET_CURRENT_STATE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "kkt_version": b''+bytes([answer.pop(0)])+bytes([answer.pop(0)]),
            "kkt_build": b''+bytes([answer.pop(0)])+bytes([answer.pop(0)]),
            "kkt_date": [answer.pop(0),answer.pop(0),answer.pop(0)],
            "number_in_room": answer.pop(0),
            "document_serial": (answer.pop(0) + answer.pop(0) << 8),
            "flags": KKMFlags((answer.pop(0) + answer.pop(0) << 8)),
            "mode": KKMMode(answer.pop(0)),
            "submode": KKMSubMode(answer.pop(0)),
            "kkt_port": answer.pop(0),
            "fa_version": b''+bytes([answer.pop(0)])+bytes([answer.pop(0)]),
            "fa_build": b''+bytes([answer.pop(0)])+bytes([answer.pop(0)]),
            "fa_date": [answer.pop(0),answer.pop(0),answer.pop(0)],
            "fa_time": [answer.pop(0),answer.pop(0),answer.pop(0)],
            "fa_flags": FaFlags(answer.pop(0) + (answer.pop(16) << 8)),
            "tmp": self._shift(answer, 4),
            "last_closed_session_no": (answer.pop(0) + answer.pop(0) << 8),
            "free_records_number": (answer.pop(0) + answer.pop(0) << 8),
            "reregistration_no": answer.pop(0),
            "rest_reregistrations": answer.pop(0),
            "inn": b''+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)]),
            "fa_mode": answer.pop(0),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_current_state",rc)

        return rc

    CMDMAP[GET_CURRENT_STATE]=_interp_get_current_state

    def print_bold(self, print_flags, message20):
        rawdata = b''
        rawdata += bytes([print_flags])
        _message20 = (message20+'\x00'*20)[:20]
        _message20 = _message20.encode('cp1251')
        rawdata += _message20
        # send command to device."""
        self._send_command(PRINT_BOLD, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_bold(answer)

    def _interp_print_bold(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_BOLD, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_bold",rc)

        return rc

    CMDMAP[PRINT_BOLD]=_interp_print_bold

    def beep(self):
        rawdata = b''
        # send command to device."""
        self._send_command(BEEP, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_beep(answer)

    def _interp_beep(self, answer):
        assert bytes([answer.pop(0)]) == BEEP, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("beep",rc)

        return rc

    CMDMAP[BEEP]=_interp_beep

    def set_connection(self, port, parameter, timeout):
        rawdata = b''
        rawdata += bytes([port])
        rawdata += bytes([parameter])
        rawdata += bytes([timeout])
        # send command to device."""
        self._send_command(SET_CONNECTION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_set_connection(answer)

    def _interp_set_connection(self, answer):
        assert bytes([answer.pop(0)]) == SET_CONNECTION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("set_connection",rc)

        return rc

    CMDMAP[SET_CONNECTION]=_interp_set_connection

    def get_connection(self, port):
        rawdata = b''
        rawdata += bytes([port])
        # send command to device."""
        self._send_command(GET_CONNECTION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_connection(answer)

    def _interp_get_connection(self, answer):
        assert bytes([answer.pop(0)]) == GET_CONNECTION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "parameter": answer.pop(0),
            "timeout": answer.pop(0),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_connection",rc)

        return rc

    CMDMAP[GET_CONNECTION]=_interp_get_connection

    def technological_reset(self):
        rawdata = b''
        # send command to device."""
        self._send_command(TECHNOLOGICAL_RESET, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_technological_reset(answer)

    def _interp_technological_reset(self, answer):
        assert bytes([answer.pop(0)]) == TECHNOLOGICAL_RESET, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("technological_reset",rc)

        return rc

    CMDMAP[TECHNOLOGICAL_RESET]=_interp_technological_reset

    def print(self, print_flags, message40):
        rawdata = b''
        rawdata += bytes([print_flags])
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(PRINT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print(answer)

    def _interp_print(self, answer):
        assert bytes([answer.pop(0)]) == PRINT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print",rc)

        return rc

    CMDMAP[PRINT]=_interp_print

    def print_header(self, name, document_number):
        rawdata = b''
        _name = (name+'\x00'*30)[:30]
        _name = _name.encode('cp1251')
        rawdata += _name
        rawdata += (document_number).to_bytes(2, sys.byteorder)
        # send command to device."""
        self._send_command(PRINT_HEADER, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_header(answer)

    def _interp_print_header(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_HEADER, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "document_serial": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_header",rc)

        return rc

    CMDMAP[PRINT_HEADER]=_interp_print_header

    def test_run(self, period):
        rawdata = b''
        rawdata += bytes([period])
        # send command to device."""
        self._send_command(TEST_RUN, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_test_run(answer)

    def _interp_test_run(self, answer):
        assert bytes([answer.pop(0)]) == TEST_RUN, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("test_run",rc)

        return rc

    CMDMAP[TEST_RUN]=_interp_test_run

    def get_money_register(self, register):
        rawdata = b''
        if register<256: _register = bytes([register])
        else: _register = (register).to_bytes(2, sys.byteorder)
        rawdata += _register
        # send command to device."""
        self._send_command(GET_MONEY_REGISTER, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_money_register(answer)

    def _interp_get_money_register(self, answer):
        assert bytes([answer.pop(0)]) == GET_MONEY_REGISTER, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "value": self._to_money(self._shift(answer, 6)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_money_register",rc)

        return rc

    CMDMAP[GET_MONEY_REGISTER]=_interp_get_money_register

    def get_operational_register(self, register):
        rawdata = b''
        if register<256: _register = bytes([register])
        else: _register = (register).to_bytes(2, sys.byteorder)
        rawdata += _register
        # send command to device."""
        self._send_command(GET_OPERATIONAL_REGISTER, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_operational_register(answer)

    def _interp_get_operational_register(self, answer):
        assert bytes([answer.pop(0)]) == GET_OPERATIONAL_REGISTER, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "value": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_operational_register",rc)

        return rc

    CMDMAP[GET_OPERATIONAL_REGISTER]=_interp_get_operational_register

    def write_table(self, table, row, field, value):
        rawdata = b''
        rawdata += bytes([table])
        rawdata += (row).to_bytes(2, sys.byteorder)
        rawdata += bytes([field])
        _value = (value+'\x00'*40)[:40]
        _value = _value.encode('cp1251')
        rawdata += _value
        # send command to device."""
        self._send_command(WRITE_TABLE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_write_table(answer)

    def _interp_write_table(self, answer):
        assert bytes([answer.pop(0)]) == WRITE_TABLE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("write_table",rc)

        return rc

    CMDMAP[WRITE_TABLE]=_interp_write_table

    def read_table(self, table, row, field):
        rawdata = b''
        rawdata += bytes([table])
        rawdata += (row).to_bytes(2, sys.byteorder)
        rawdata += bytes([field])
        # send command to device."""
        self._send_command(READ_TABLE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_read_table(answer)

    def _interp_read_table(self, answer):
        assert bytes([answer.pop(0)]) == READ_TABLE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "value": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("read_table",rc)

        return rc

    CMDMAP[READ_TABLE]=_interp_read_table

    def flash_time(self, time):
        rawdata = b''
        rawdata += bytes(list(time))
        # send command to device."""
        self._send_command(FLASH_TIME, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_flash_time(answer)

    def _interp_flash_time(self, answer):
        assert bytes([answer.pop(0)]) == FLASH_TIME, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("flash_time",rc)

        return rc

    CMDMAP[FLASH_TIME]=_interp_flash_time

    def flash_date(self, date):
        rawdata = b''
        rawdata += bytes(list(date))
        # send command to device."""
        self._send_command(FLASH_DATE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_flash_date(answer)

    def _interp_flash_date(self, answer):
        assert bytes([answer.pop(0)]) == FLASH_DATE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("flash_date",rc)

        return rc

    CMDMAP[FLASH_DATE]=_interp_flash_date

    def flash_date_confirm(self, date):
        rawdata = b''
        rawdata += bytes(list(date))
        # send command to device."""
        self._send_command(FLASH_DATE_CONFIRM, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_flash_date_confirm(answer)

    def _interp_flash_date_confirm(self, answer):
        assert bytes([answer.pop(0)]) == FLASH_DATE_CONFIRM, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("flash_date_confirm",rc)

        return rc

    CMDMAP[FLASH_DATE_CONFIRM]=_interp_flash_date_confirm

    def init_table(self):
        rawdata = b''
        # send command to device."""
        self._send_command(INIT_TABLE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_init_table(answer)

    def _interp_init_table(self, answer):
        assert bytes([answer.pop(0)]) == INIT_TABLE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("init_table",rc)

        return rc

    CMDMAP[INIT_TABLE]=_interp_init_table

    def cut_check(self, full):
        rawdata = b''
        rawdata += bytes([int(full)])
        # send command to device."""
        self._send_command(CUT_CHECK, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cut_check(answer)

    def _interp_cut_check(self, answer):
        assert bytes([answer.pop(0)]) == CUT_CHECK, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cut_check",rc)

        return rc

    CMDMAP[CUT_CHECK]=_interp_cut_check

    def font_params_read(self, font):
        rawdata = b''
        rawdata += bytes([font])
        # send command to device."""
        self._send_command(FONT_PARAMS_READ, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_font_params_read(answer)

    def _interp_font_params_read(self, answer):
        assert bytes([answer.pop(0)]) == FONT_PARAMS_READ, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "print_width": (answer.pop(0) + answer.pop(0) << 8),
            "width": answer.pop(0),
            "height": answer.pop(0),
            "count_of_fonts": answer.pop(0),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("font_params_read",rc)

        return rc

    CMDMAP[FONT_PARAMS_READ]=_interp_font_params_read

    def total_annulate(self):
        rawdata = b''
        # send command to device."""
        self._send_command(TOTAL_ANNULATE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_total_annulate(answer)

    def _interp_total_annulate(self, answer):
        assert bytes([answer.pop(0)]) == TOTAL_ANNULATE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("total_annulate",rc)

        return rc

    CMDMAP[TOTAL_ANNULATE]=_interp_total_annulate

    def open_money_box(self):
        rawdata = b''
        # send command to device."""
        self._send_command(OPEN_MONEY_BOX, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_open_money_box(answer)

    def _interp_open_money_box(self, answer):
        assert bytes([answer.pop(0)]) == OPEN_MONEY_BOX, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("open_money_box",rc)

        return rc

    CMDMAP[OPEN_MONEY_BOX]=_interp_open_money_box

    def feed(self, band_flags, rows):
        rawdata = b''
        rawdata += bytes([band_flags])
        rawdata += bytes([rows])
        # send command to device."""
        self._send_command(FEED, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_feed(answer)

    def _interp_feed(self, answer):
        assert bytes([answer.pop(0)]) == FEED, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("feed",rc)

        return rc

    CMDMAP[FEED]=_interp_feed

    def cancel_test_run(self):
        rawdata = b''
        # send command to device."""
        self._send_command(CANCEL_TEST_RUN, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cancel_test_run(answer)

    def _interp_cancel_test_run(self, answer):
        assert bytes([answer.pop(0)]) == CANCEL_TEST_RUN, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cancel_test_run",rc)

        return rc

    CMDMAP[CANCEL_TEST_RUN]=_interp_cancel_test_run

    def readout_operational_registers(self):
        rawdata = b''
        # send command to device."""
        self._send_command(READOUT_OPERATIONAL_REGISTERS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_readout_operational_registers(answer)

    def _interp_readout_operational_registers(self, answer):
        assert bytes([answer.pop(0)]) == READOUT_OPERATIONAL_REGISTERS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("readout_operational_registers",rc)

        return rc

    CMDMAP[READOUT_OPERATIONAL_REGISTERS]=_interp_readout_operational_registers

    def query_table_structure(self, table):
        rawdata = b''
        rawdata += bytes([table])
        # send command to device."""
        self._send_command(QUERY_TABLE_STRUCTURE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_table_structure(answer)

    def _interp_query_table_structure(self, answer):
        assert bytes([answer.pop(0)]) == QUERY_TABLE_STRUCTURE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "name": self._to_string(self._shift(answer, 40)),
            "row_count": (answer.pop(0) + answer.pop(0) << 8),
            "field_count": answer.pop(0),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_table_structure",rc)

        return rc

    CMDMAP[QUERY_TABLE_STRUCTURE]=_interp_query_table_structure

    def query_field_structure(self, table, field):
        rawdata = b''
        rawdata += bytes([table])
        rawdata += bytes([field])
        # send command to device."""
        self._send_command(QUERY_FIELD_STRUCTURE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_field_structure(answer)

    def _interp_query_field_structure(self, answer):
        assert bytes([answer.pop(0)]) == QUERY_FIELD_STRUCTURE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "name": self._to_string(self._shift(answer, 40)),
            "type": bool(answer.pop(0)),
            "length": answer.pop(0),
            "field_vals": self._interp_rest_field_structure(answer),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_field_structure",rc)

        return rc

    CMDMAP[QUERY_FIELD_STRUCTURE]=_interp_query_field_structure

    def print_with_font(self, print_flags, font, message40):
        rawdata = b''
        rawdata += bytes([print_flags])
        rawdata += bytes([font])
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(PRINT_WITH_FONT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_with_font(answer)

    def _interp_print_with_font(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_WITH_FONT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_with_font",rc)

        return rc

    CMDMAP[PRINT_WITH_FONT]=_interp_print_with_font

    def daily_report_wo_annulation(self):
        rawdata = b''
        # send command to device."""
        self._send_command(DAILY_REPORT_WO_ANNULATION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_daily_report_wo_annulation(answer)

    def _interp_daily_report_wo_annulation(self, answer):
        assert bytes([answer.pop(0)]) == DAILY_REPORT_WO_ANNULATION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("daily_report_wo_annulation",rc)

        return rc

    CMDMAP[DAILY_REPORT_WO_ANNULATION]=_interp_daily_report_wo_annulation

    def daily_report_with_annulation(self):
        rawdata = b''
        # send command to device."""
        self._send_command(DAILY_REPORT_WITH_ANNULATION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_daily_report_with_annulation(answer)

    def _interp_daily_report_with_annulation(self, answer):
        assert bytes([answer.pop(0)]) == DAILY_REPORT_WITH_ANNULATION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("daily_report_with_annulation",rc)

        return rc

    CMDMAP[DAILY_REPORT_WITH_ANNULATION]=_interp_daily_report_with_annulation

    def section_report(self):
        rawdata = b''
        # send command to device."""
        self._send_command(SECTION_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_section_report(answer)

    def _interp_section_report(self, answer):
        assert bytes([answer.pop(0)]) == SECTION_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("section_report",rc)

        return rc

    CMDMAP[SECTION_REPORT]=_interp_section_report

    def tax_report(self):
        rawdata = b''
        # send command to device."""
        self._send_command(TAX_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_tax_report(answer)

    def _interp_tax_report(self, answer):
        assert bytes([answer.pop(0)]) == TAX_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("tax_report",rc)

        return rc

    CMDMAP[TAX_REPORT]=_interp_tax_report

    def cashier_report(self):
        rawdata = b''
        # send command to device."""
        self._send_command(CASHIER_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cashier_report(answer)

    def _interp_cashier_report(self, answer):
        assert bytes([answer.pop(0)]) == CASHIER_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cashier_report",rc)

        return rc

    CMDMAP[CASHIER_REPORT]=_interp_cashier_report

    def deposit(self, amount):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        # send command to device."""
        self._send_command(DEPOSIT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_deposit(answer)

    def _interp_deposit(self, answer):
        assert bytes([answer.pop(0)]) == DEPOSIT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "document_serial": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("deposit",rc)

        return rc

    CMDMAP[DEPOSIT]=_interp_deposit

    def withdraw(self, amount):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        # send command to device."""
        self._send_command(WITHDRAW, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_withdraw(answer)

    def _interp_withdraw(self, answer):
        assert bytes([answer.pop(0)]) == WITHDRAW, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "document_serial": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("withdraw",rc)

        return rc

    CMDMAP[WITHDRAW]=_interp_withdraw

    def print_cliche(self):
        rawdata = b''
        # send command to device."""
        self._send_command(PRINT_CLICHE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_cliche(answer)

    def _interp_print_cliche(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_CLICHE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_cliche",rc)

        return rc

    CMDMAP[PRINT_CLICHE]=_interp_print_cliche

    def document_finalization(self, advert):
        rawdata = b''
        rawdata += bytes([int(advert)])
        # send command to device."""
        self._send_command(DOCUMENT_FINALIZATION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_document_finalization(answer)

    def _interp_document_finalization(self, answer):
        assert bytes([answer.pop(0)]) == DOCUMENT_FINALIZATION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("document_finalization",rc)

        return rc

    CMDMAP[DOCUMENT_FINALIZATION]=_interp_document_finalization

    def print_advertisement(self):
        rawdata = b''
        # send command to device."""
        self._send_command(PRINT_ADVERTISEMENT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_advertisement(answer)

    def _interp_print_advertisement(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_ADVERTISEMENT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_advertisement",rc)

        return rc

    CMDMAP[PRINT_ADVERTISEMENT]=_interp_print_advertisement

    def flash_serial_number(self, serial):
        rawdata = b''
        rawdata += self._serial_to_bytes(serial)
        # send command to device."""
        self._send_command(FLASH_SERIAL_NUMBER, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_flash_serial_number(answer)

    def _interp_flash_serial_number(self, answer):
        assert bytes([answer.pop(0)]) == FLASH_SERIAL_NUMBER, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("flash_serial_number",rc)

        return rc

    CMDMAP[FLASH_SERIAL_NUMBER]=_interp_flash_serial_number

    def sell(self, count, price, department, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(count, width=5, pos=3)
        rawdata += self._amount_to_bytes(price, width=5, pos=2)
        rawdata += bytes([department])
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(SELL, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_sell(answer)

    def _interp_sell(self, answer):
        assert bytes([answer.pop(0)]) == SELL, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("sell",rc)

        return rc

    CMDMAP[SELL]=_interp_sell

    def buy(self, count, price, department, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(count, width=5, pos=3)
        rawdata += self._amount_to_bytes(price, width=5, pos=2)
        rawdata += bytes([department])
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(BUY, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_buy(answer)

    def _interp_buy(self, answer):
        assert bytes([answer.pop(0)]) == BUY, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("buy",rc)

        return rc

    CMDMAP[BUY]=_interp_buy

    def cancel_sell(self, count, price, department, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(count, width=5, pos=3)
        rawdata += self._amount_to_bytes(price, width=5, pos=2)
        rawdata += bytes([department])
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(CANCEL_SELL, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cancel_sell(answer)

    def _interp_cancel_sell(self, answer):
        assert bytes([answer.pop(0)]) == CANCEL_SELL, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cancel_sell",rc)

        return rc

    CMDMAP[CANCEL_SELL]=_interp_cancel_sell

    def cancel_buy(self, count, price, department, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(count, width=5, pos=3)
        rawdata += self._amount_to_bytes(price, width=5, pos=2)
        rawdata += bytes([department])
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(CANCEL_BUY, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cancel_buy(answer)

    def _interp_cancel_buy(self, answer):
        assert bytes([answer.pop(0)]) == CANCEL_BUY, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cancel_buy",rc)

        return rc

    CMDMAP[CANCEL_BUY]=_interp_cancel_buy

    def cancellation(self, count, price, department, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(count, width=5, pos=3)
        rawdata += self._amount_to_bytes(price, width=5, pos=2)
        rawdata += bytes([department])
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(CANCELLATION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cancellation(answer)

    def _interp_cancellation(self, answer):
        assert bytes([answer.pop(0)]) == CANCELLATION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cancellation",rc)

        return rc

    CMDMAP[CANCELLATION]=_interp_cancellation

    def close_check(self, amounts4, discount, taxes, message40):
        rawdata = b''
        rawdata += b''+self._amount_to_bytes(amounts4[0], width=5, pos=2)+self._amount_to_bytes(amounts4[1], width=5, pos=2)+self._amount_to_bytes(amounts4[2], width=5, pos=2)+self._amount_to_bytes(amounts4[3], width=5, pos=2)
        rawdata += self._amount_to_bytes(discount, width=2, pos=2)
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(CLOSE_CHECK, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_close_check(answer)

    def _interp_close_check(self, answer):
        assert bytes([answer.pop(0)]) == CLOSE_CHECK, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "change": self._to_money(self._shift(answer, 5)),
            "url": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("close_check",rc)

        return rc

    CMDMAP[CLOSE_CHECK]=_interp_close_check

    def discount(self, amount, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(DISCOUNT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_discount(answer)

    def _interp_discount(self, answer):
        assert bytes([answer.pop(0)]) == DISCOUNT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("discount",rc)

        return rc

    CMDMAP[DISCOUNT]=_interp_discount

    def increse(self, amount, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(INCRESE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_increse(answer)

    def _interp_increse(self, answer):
        assert bytes([answer.pop(0)]) == INCRESE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("increse",rc)

        return rc

    CMDMAP[INCRESE]=_interp_increse

    def annulate_check(self):
        rawdata = b''
        # send command to device."""
        self._send_command(ANNULATE_CHECK, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_annulate_check(answer)

    def _interp_annulate_check(self, answer):
        assert bytes([answer.pop(0)]) == ANNULATE_CHECK, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("annulate_check",rc)

        return rc

    CMDMAP[ANNULATE_CHECK]=_interp_annulate_check

    def subtotal(self):
        rawdata = b''
        # send command to device."""
        self._send_command(SUBTOTAL, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_subtotal(answer)

    def _interp_subtotal(self, answer):
        assert bytes([answer.pop(0)]) == SUBTOTAL, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "amount": self._to_money(self._shift(answer, 5)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("subtotal",rc)

        return rc

    CMDMAP[SUBTOTAL]=_interp_subtotal

    def annulate_discount(self, amount, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(ANNULATE_DISCOUNT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_annulate_discount(answer)

    def _interp_annulate_discount(self, answer):
        assert bytes([answer.pop(0)]) == ANNULATE_DISCOUNT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("annulate_discount",rc)

        return rc

    CMDMAP[ANNULATE_DISCOUNT]=_interp_annulate_discount

    def annulate_increase(self, amount, taxes, message40):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(ANNULATE_INCREASE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_annulate_increase(answer)

    def _interp_annulate_increase(self, answer):
        assert bytes([answer.pop(0)]) == ANNULATE_INCREASE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("annulate_increase",rc)

        return rc

    CMDMAP[ANNULATE_INCREASE]=_interp_annulate_increase

    def print_check_copy(self):
        rawdata = b''
        # send command to device."""
        self._send_command(PRINT_CHECK_COPY, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_check_copy(answer)

    def _interp_print_check_copy(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_CHECK_COPY, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_check_copy",rc)

        return rc

    CMDMAP[PRINT_CHECK_COPY]=_interp_print_check_copy

    def open_check(self, checktype):
        rawdata = b''
        rawdata += bytes([checktype])
        # send command to device."""
        self._send_command(OPEN_CHECK, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_open_check(answer)

    def _interp_open_check(self, answer):
        assert bytes([answer.pop(0)]) == OPEN_CHECK, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("open_check",rc)

        return rc

    CMDMAP[OPEN_CHECK]=_interp_open_check

    def close_check_extended(self, amounts16, discount, taxes, message40):
        rawdata = b''
        rawdata += b''+self._amount_to_bytes(amounts16[0], width=5, pos=2)+self._amount_to_bytes(amounts16[1], width=5, pos=2)+self._amount_to_bytes(amounts16[2], width=5, pos=2)+self._amount_to_bytes(amounts16[3], width=5, pos=2)+self._amount_to_bytes(amounts16[4], width=5, pos=2)+self._amount_to_bytes(amounts16[5], width=5, pos=2)+self._amount_to_bytes(amounts16[6], width=5, pos=2)+self._amount_to_bytes(amounts16[7], width=5, pos=2)+self._amount_to_bytes(amounts16[8], width=5, pos=2)+self._amount_to_bytes(amounts16[9], width=5, pos=2)+self._amount_to_bytes(amounts16[10], width=5, pos=2)+self._amount_to_bytes(amounts16[11], width=5, pos=2)+self._amount_to_bytes(amounts16[12], width=5, pos=2)+self._amount_to_bytes(amounts16[13], width=5, pos=2)+self._amount_to_bytes(amounts16[14], width=5, pos=2)+self._amount_to_bytes(amounts16[15], width=5, pos=2)
        rawdata += self._amount_to_bytes(discount, width=2, pos=2)
        rawdata += bytes(taxes)
        _message40 = (message40+'\x00'*40)[:40]
        _message40 = _message40.encode('cp1251')
        rawdata += _message40
        # send command to device."""
        self._send_command(CLOSE_CHECK_EXTENDED, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_close_check_extended(answer)

    def _interp_close_check_extended(self, answer):
        assert bytes([answer.pop(0)]) == CLOSE_CHECK_EXTENDED, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "change": self._to_money(self._shift(answer, 5)),
            "url": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("close_check_extended",rc)

        return rc

    CMDMAP[CLOSE_CHECK_EXTENDED]=_interp_close_check_extended

    def continue_printing(self):
        rawdata = b''
        # send command to device."""
        self._send_command(CONTINUE_PRINTING, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_continue_printing(answer)

    def _interp_continue_printing(self, answer):
        assert bytes([answer.pop(0)]) == CONTINUE_PRINTING, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("continue_printing",rc)

        return rc

    CMDMAP[CONTINUE_PRINTING]=_interp_continue_printing

    def load_graphics(self, line_no, graphics40):
        rawdata = b''
        rawdata += bytes([line_no])
        rawdata += (graphics40)[:40]
        # send command to device."""
        self._send_command(LOAD_GRAPHICS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_load_graphics(answer)

    def _interp_load_graphics(self, answer):
        assert bytes([answer.pop(0)]) == LOAD_GRAPHICS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("load_graphics",rc)

        return rc

    CMDMAP[LOAD_GRAPHICS]=_interp_load_graphics

    def print_graphics(self, start, end):
        rawdata = b''
        rawdata += bytes([start])
        rawdata += bytes([end])
        # send command to device."""
        self._send_command(PRINT_GRAPHICS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_graphics(answer)

    def _interp_print_graphics(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_GRAPHICS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_graphics",rc)

        return rc

    CMDMAP[PRINT_GRAPHICS]=_interp_print_graphics

    def print_ean13(self, barcode):
        rawdata = b''
        rawdata += bytes(barcode)
        # send command to device."""
        self._send_command(PRINT_EAN13, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_ean13(answer)

    def _interp_print_ean13(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_EAN13, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_ean13",rc)

        return rc

    CMDMAP[PRINT_EAN13]=_interp_print_ean13

    def print_graphics_extended(self, start2, end2, graph_flags):
        rawdata = b''
        rawdata += (start2).to_bytes(2, sys.byteorder)
        rawdata += (end2).to_bytes(2, sys.byteorder)
        rawdata += bytes([graph_flags])
        # send command to device."""
        self._send_command(PRINT_GRAPHICS_EXTENDED, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_graphics_extended(answer)

    def _interp_print_graphics_extended(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_GRAPHICS_EXTENDED, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_graphics_extended",rc)

        return rc

    CMDMAP[PRINT_GRAPHICS_EXTENDED]=_interp_print_graphics_extended

    def load_graphics_extended(self, line_no2, data):
        rawdata = b''
        rawdata += (line_no2).to_bytes(2, sys.byteorder)
        rawdata += bytes(data)
        # send command to device."""
        self._send_command(LOAD_GRAPHICS_EXTENDED, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_load_graphics_extended(answer)

    def _interp_load_graphics_extended(self, answer):
        assert bytes([answer.pop(0)]) == LOAD_GRAPHICS_EXTENDED, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("load_graphics_extended",rc)

        return rc

    CMDMAP[LOAD_GRAPHICS_EXTENDED]=_interp_load_graphics_extended

    def print_graphics_line(self, repeat2, graph_flags, data):
        rawdata = b''
        rawdata += (repeat2).to_bytes(2, sys.byteorder)
        rawdata += bytes([graph_flags])
        rawdata += bytes(data)
        # send command to device."""
        self._send_command(PRINT_GRAPHICS_LINE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_graphics_line(answer)

    def _interp_print_graphics_line(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_GRAPHICS_LINE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_graphics_line",rc)

        return rc

    CMDMAP[PRINT_GRAPHICS_LINE]=_interp_print_graphics_line

    def load_data(self, data_type, block_no, data64):
        rawdata = b''
        rawdata += bytes([int(data_type)])
        rawdata += bytes([block_no])
        rawdata += (data64)[:64]
        # send command to device."""
        self._send_command(LOAD_DATA, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_load_data(answer)

    def _interp_load_data(self, answer):
        assert bytes([answer.pop(0)]) == LOAD_DATA, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("load_data",rc)

        return rc

    CMDMAP[LOAD_DATA]=_interp_load_data

    def print_qrcode(self, qr_type, data_length2, start, params, align):
        rawdata = b''
        rawdata += bytes([qr_type])
        rawdata += (data_length2).to_bytes(2, sys.byteorder)
        rawdata += bytes([start])
        rawdata += (params)[:5]
        rawdata += bytes([align])
        # send command to device."""
        self._send_command(PRINT_QRCODE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_print_qrcode(answer)

    def _interp_print_qrcode(self, answer):
        assert bytes([answer.pop(0)]) == PRINT_QRCODE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
            "params": self._shift(answer, 5),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("print_qrcode",rc)

        return rc

    CMDMAP[PRINT_QRCODE]=_interp_print_qrcode

    def open_shift(self):
        rawdata = b''
        # send command to device."""
        self._send_command(OPEN_SHIFT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_open_shift(answer)

    def _interp_open_shift(self, answer):
        assert bytes([answer.pop(0)]) == OPEN_SHIFT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "op_number": self._oper_number(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("open_shift",rc)

        return rc

    CMDMAP[OPEN_SHIFT]=_interp_open_shift

    def get_device_type(self):
        rawdata = b''
        # send command to device."""
        self._send_command(GET_DEVICE_TYPE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_device_type(answer)

    def _interp_get_device_type(self, answer):
        assert bytes([answer.pop(0)]) == GET_DEVICE_TYPE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "dev_type": answer.pop(0),
            "dev_subtype": answer.pop(0),
            "proto_version": answer.pop(0),
            "proto_subversion": answer.pop(0),
            "dev_model": answer.pop(0),
            "dev_lang": answer.pop(0),
            "name": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_device_type",rc)

        return rc

    CMDMAP[GET_DEVICE_TYPE]=_interp_get_device_type

    def query_fa_status(self):
        rawdata = b''
        # send command to device."""
        self._send_command(QUERY_FA_STATUS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fa_status(answer)

    def _interp_query_fa_status(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FA_STATUS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fa_life_status": answer.pop(0),
            "document_type": answer.pop(0),
            "document_data": answer.pop(0),
            "shift_status": (answer.pop(0) + answer.pop(0) << 8),
            "warning_flags": answer.pop(0),
            "fa_datetime": [answer.pop(0),answer.pop(0),answer.pop(0),answer.pop(0),answer.pop(0)],
            "fa_number": self._shift(answer, 16),
            "fd_number": self._shift(answer, 4),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fa_status",rc)

        return rc

    CMDMAP[QUERY_FA_STATUS]=_interp_query_fa_status

    def query_fa_number(self):
        rawdata = b''
        # send command to device."""
        self._send_command(QUERY_FA_NUMBER, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fa_number(answer)

    def _interp_query_fa_number(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FA_NUMBER, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fa_number": self._shift(answer, 16),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fa_number",rc)

        return rc

    CMDMAP[QUERY_FA_NUMBER]=_interp_query_fa_number

    def query_fa_duration(self):
        rawdata = b''
        # send command to device."""
        self._send_command(QUERY_FA_DURATION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fa_duration(answer)

    def _interp_query_fa_duration(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FA_DURATION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "duration": [answer.pop(0),answer.pop(0),answer.pop(0)],
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fa_duration",rc)

        return rc

    CMDMAP[QUERY_FA_DURATION]=_interp_query_fa_duration

    def query_fa_version(self):
        rawdata = b''
        # send command to device."""
        self._send_command(QUERY_FA_VERSION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fa_version(answer)

    def _interp_query_fa_version(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FA_VERSION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fa_version": self._shift(answer, 16),
            "fe_release": bool(answer.pop(0)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fa_version",rc)

        return rc

    CMDMAP[QUERY_FA_VERSION]=_interp_query_fa_version

    def begin_kkt_registration_report(self, reg_report_type):
        rawdata = b''
        rawdata += bytes([reg_report_type])
        # send command to device."""
        self._send_command(BEGIN_KKT_REGISTRATION_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_begin_kkt_registration_report(answer)

    def _interp_begin_kkt_registration_report(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == BEGIN_KKT_REGISTRATION_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("begin_kkt_registration_report",rc)

        return rc

    CMDMAP[BEGIN_KKT_REGISTRATION_REPORT]=_interp_begin_kkt_registration_report

    def make_kkt_registration_report(self, inn, reg_number, tax_code, work_mode):
        rawdata = b''
        _inn = (inn+'\x00'*12)[:12]
        _inn = _inn.encode('cp1251')
        rawdata += _inn
        rawdata += (reg_number)[:20]
        rawdata += bytes([tax_code])
        rawdata += bytes([work_mode])
        # send command to device."""
        self._send_command(MAKE_KKT_REGISTRATION_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_make_kkt_registration_report(answer)

    def _interp_make_kkt_registration_report(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == MAKE_KKT_REGISTRATION_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fd_number": self._shift(answer, 4),
            "fiscal_feature": self._shift(answer, 4),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("make_kkt_registration_report",rc)

        return rc

    CMDMAP[MAKE_KKT_REGISTRATION_REPORT]=_interp_make_kkt_registration_report

    def reset_fa_state(self, query_code):
        rawdata = b''
        rawdata += bytes([query_code])
        # send command to device."""
        self._send_command(RESET_FA_STATE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_reset_fa_state(answer)

    def _interp_reset_fa_state(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == RESET_FA_STATE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("reset_fa_state",rc)

        return rc

    CMDMAP[RESET_FA_STATE]=_interp_reset_fa_state

    def cancel_fa_document(self):
        rawdata = b''
        # send command to device."""
        self._send_command(CANCEL_FA_DOCUMENT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_cancel_fa_document(answer)

    def _interp_cancel_fa_document(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == CANCEL_FA_DOCUMENT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("cancel_fa_document",rc)

        return rc

    CMDMAP[CANCEL_FA_DOCUMENT]=_interp_cancel_fa_document

    def query_fiscal_results(self, reregistration_number):
        rawdata = b''
        rawdata += bytes([reregistration_number])
        # send command to device."""
        self._send_command(QUERY_FISCAL_RESULTS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fiscal_results(answer)

    def _interp_query_fiscal_results(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FISCAL_RESULTS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "datetime": [answer.pop(0),answer.pop(0),answer.pop(0),answer.pop(0),answer.pop(0)],
            "inn": b''+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)])+bytes([answer.pop(0)]),
            "kkt_reg_number": self._shift(answer, 20),
            "tax_code": answer.pop(0),
            "work_mode": answer.pop(0),
            "cause": answer.pop(0),
            "fd_number": self._shift(answer, 4),
            "fiscal_feature": self._shift(answer, 4),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fiscal_results",rc)

        return rc

    CMDMAP[QUERY_FISCAL_RESULTS]=_interp_query_fiscal_results

    def find_fd_by_nuber(self, document_number):
        rawdata = b''
        rawdata += (document_number).to_bytes(2, sys.byteorder)
        # send command to device."""
        self._send_command(FIND_FD_BY_NUBER, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_find_fd_by_nuber(answer)

    def _interp_find_fd_by_nuber(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == FIND_FD_BY_NUBER, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "document_type": answer.pop(0),
            "ofd_receipt": bool(answer.pop(0)),
            "data": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("find_fd_by_nuber",rc)

        return rc

    CMDMAP[FIND_FD_BY_NUBER]=_interp_find_fd_by_nuber

    def send_TLV_struct(self, data):
        rawdata = b''
        rawdata += bytes(data)
        # send command to device."""
        self._send_command(SEND_TLV_STRUCT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_send_TLV_struct(answer)

    def _interp_send_TLV_struct(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == SEND_TLV_STRUCT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("send_TLV_struct",rc)

        return rc

    CMDMAP[SEND_TLV_STRUCT]=_interp_send_TLV_struct

    def discount_increase_operation(self, oper_type, amount, price, discount_amount, increase_amount, department, taxes, barcode, messagez):
        rawdata = b''
        rawdata += bytes([oper_type])
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        rawdata += self._amount_to_bytes(price, width=5, pos=2)
        rawdata += self._amount_to_bytes(discount_amount, width=5, pos=2)
        rawdata += self._amount_to_bytes(increase_amount, width=5, pos=2)
        rawdata += bytes([department])
        rawdata += bytes(taxes)
        rawdata += bytes(barcode)
        _messagez = (messagez)[:]
        _messagez = _messagez.encode('cp1251')+b'\x00'
        rawdata += _messagez
        # send command to device."""
        self._send_command(DISCOUNT_INCREASE_OPERATION, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_discount_increase_operation(answer)

    def _interp_discount_increase_operation(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == DISCOUNT_INCREASE_OPERATION, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("discount_increase_operation",rc)

        return rc

    CMDMAP[DISCOUNT_INCREASE_OPERATION]=_interp_discount_increase_operation

    def make_reregistration_report(self, reregistration_cause):
        rawdata = b''
        rawdata += bytes([reregistration_cause])
        # send command to device."""
        self._send_command(MAKE_REREGISTRATION_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_make_reregistration_report(answer)

    def _interp_make_reregistration_report(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == MAKE_REREGISTRATION_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fd_number": self._shift(answer, 4),
            "fiscal_feature": self._shift(answer, 4),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("make_reregistration_report",rc)

        return rc

    CMDMAP[MAKE_REREGISTRATION_REPORT]=_interp_make_reregistration_report

    def begin_correction_check(self):
        rawdata = b''
        # send command to device."""
        self._send_command(BEGIN_CORRECTION_CHECK, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_begin_correction_check(answer)

    def _interp_begin_correction_check(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == BEGIN_CORRECTION_CHECK, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("begin_correction_check",rc)

        return rc

    CMDMAP[BEGIN_CORRECTION_CHECK]=_interp_begin_correction_check

    def make_correction_check(self, amount, oper_type):
        rawdata = b''
        rawdata += self._amount_to_bytes(amount, width=5, pos=2)
        rawdata += bytes([oper_type])
        # send command to device."""
        self._send_command(MAKE_CORRECTION_CHECK, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_make_correction_check(answer)

    def _interp_make_correction_check(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == MAKE_CORRECTION_CHECK, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "check_number": (answer.pop(0) + answer.pop(0) << 8),
            "fd_number": self._shift(answer, 4),
            "fiscal_feature": self._shift(answer, 4),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("make_correction_check",rc)

        return rc

    CMDMAP[MAKE_CORRECTION_CHECK]=_interp_make_correction_check

    def begin_calculation_report(self):
        rawdata = b''
        # send command to device."""
        self._send_command(BEGIN_CALCULATION_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_begin_calculation_report(answer)

    def _interp_begin_calculation_report(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == BEGIN_CALCULATION_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("begin_calculation_report",rc)

        return rc

    CMDMAP[BEGIN_CALCULATION_REPORT]=_interp_begin_calculation_report

    def make_calculation_report(self):
        rawdata = b''
        # send command to device."""
        self._send_command(MAKE_CALCULATION_REPORT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_make_calculation_report(answer)

    def _interp_make_calculation_report(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == MAKE_CALCULATION_REPORT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fd_number": self._shift(answer, 4),
            "fiscal_feature": self._shift(answer, 4),
            "unconfirmed_count": self._shift(answer, 4),
            "first_unconfirmed": [answer.pop(0),answer.pop(0),answer.pop(0)],
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("make_calculation_report",rc)

        return rc

    CMDMAP[MAKE_CALCULATION_REPORT]=_interp_make_calculation_report

    def get_info_exchange_status(self):
        rawdata = b''
        # send command to device."""
        self._send_command(GET_INFO_EXCHANGE_STATUS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_get_info_exchange_status(answer)

    def _interp_get_info_exchange_status(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == GET_INFO_EXCHANGE_STATUS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "status": bool(answer.pop(0)),
            "connection": answer.pop(0),
            "reading": bool(answer.pop(0)),
            "message_count": (answer.pop(0) + answer.pop(0) << 8),
            "document_number": self._shift(answer, 4),
            "first_document": [answer.pop(0),answer.pop(0),answer.pop(0),answer.pop(0),answer.pop(0)],
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("get_info_exchange_status",rc)

        return rc

    CMDMAP[GET_INFO_EXCHANGE_STATUS]=_interp_get_info_exchange_status

    def query_fiscal_document_TLV(self, fiscal_document_number):
        rawdata = b''
        rawdata += (fiscal_document_number)[:4]
        # send command to device."""
        self._send_command(QUERY_FISCAL_DOCUMENT_TLV, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fiscal_document_TLV(answer)

    def _interp_query_fiscal_document_TLV(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FISCAL_DOCUMENT_TLV, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fiscal_type": (answer.pop(0) + answer.pop(0) << 8),
            "length": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fiscal_document_TLV",rc)

        return rc

    CMDMAP[QUERY_FISCAL_DOCUMENT_TLV]=_interp_query_fiscal_document_TLV

    def read_fiscal_document_TLV(self):
        rawdata = b''
        # send command to device."""
        self._send_command(READ_FISCAL_DOCUMENT_TLV, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_read_fiscal_document_TLV(answer)

    def _interp_read_fiscal_document_TLV(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == READ_FISCAL_DOCUMENT_TLV, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "tlv_struct": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("read_fiscal_document_TLV",rc)

        return rc

    CMDMAP[READ_FISCAL_DOCUMENT_TLV]=_interp_read_fiscal_document_TLV

    def query_ofd_data_transfer_receipt(self, fiscal_document_number):
        rawdata = b''
        rawdata += (fiscal_document_number)[:4]
        # send command to device."""
        self._send_command(QUERY_OFD_DATA_TRANSFER_RECEIPT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_ofd_data_transfer_receipt(answer)

    def _interp_query_ofd_data_transfer_receipt(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_OFD_DATA_TRANSFER_RECEIPT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "receipt_data": self._shift(answer, len(answer)),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_ofd_data_transfer_receipt",rc)

        return rc

    CMDMAP[QUERY_OFD_DATA_TRANSFER_RECEIPT]=_interp_query_ofd_data_transfer_receipt

    def begin_fiscal_mode_closing(self):
        rawdata = b''
        # send command to device."""
        self._send_command(BEGIN_FISCAL_MODE_CLOSING, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_begin_fiscal_mode_closing(answer)

    def _interp_begin_fiscal_mode_closing(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == BEGIN_FISCAL_MODE_CLOSING, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("begin_fiscal_mode_closing",rc)

        return rc

    CMDMAP[BEGIN_FISCAL_MODE_CLOSING]=_interp_begin_fiscal_mode_closing

    def close_fiscal_mode(self):
        rawdata = b''
        # send command to device."""
        self._send_command(CLOSE_FISCAL_MODE, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_close_fiscal_mode(answer)

    def _interp_close_fiscal_mode(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == CLOSE_FISCAL_MODE, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "fd_number": self._shift(answer, 4),
            "fiscal_feature": self._shift(answer, 4),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("close_fiscal_mode",rc)

        return rc

    CMDMAP[CLOSE_FISCAL_MODE]=_interp_close_fiscal_mode

    def query_fd_count_wo_receipt(self):
        rawdata = b''
        # send command to device."""
        self._send_command(QUERY_FD_COUNT_WO_RECEIPT, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_fd_count_wo_receipt(answer)

    def _interp_query_fd_count_wo_receipt(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_FD_COUNT_WO_RECEIPT, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "count": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_fd_count_wo_receipt",rc)

        return rc

    CMDMAP[QUERY_FD_COUNT_WO_RECEIPT]=_interp_query_fd_count_wo_receipt

    def query_current_shift_params(self):
        rawdata = b''
        # send command to device."""
        self._send_command(QUERY_CURRENT_SHIFT_PARAMS, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_query_current_shift_params(answer)

    def _interp_query_current_shift_params(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == QUERY_CURRENT_SHIFT_PARAMS, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
            "shift_status": (answer.pop(0) + answer.pop(0) << 8),
            "shift_number": (answer.pop(0) + answer.pop(0) << 8),
            "check_number": (answer.pop(0) + answer.pop(0) << 8),
        })
        # A post processing rc = f(rc) 

        rc = self._wrap("query_current_shift_params",rc)

        return rc

    CMDMAP[QUERY_CURRENT_SHIFT_PARAMS]=_interp_query_current_shift_params

    def begin_shift_opening(self):
        rawdata = b''
        # send command to device."""
        self._send_command(BEGIN_SHIFT_OPENING, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_begin_shift_opening(answer)

    def _interp_begin_shift_opening(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == BEGIN_SHIFT_OPENING, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("begin_shift_opening",rc)

        return rc

    CMDMAP[BEGIN_SHIFT_OPENING]=_interp_begin_shift_opening

    def begin_shift_closing(self):
        rawdata = b''
        # send command to device."""
        self._send_command(BEGIN_SHIFT_CLOSING, self._get_password(), bytearray(rawdata))
        # receive answer from device."""
        answer = self._receive_answer()
        assert type(answer) in [bytes, bytearray]
        answer = bytearray(answer)
        # Interprete the answer
        return self._interp_begin_shift_closing(answer)

    def _interp_begin_shift_closing(self, answer):
        assert bytes([answer.pop(0), answer.pop(0)]) == BEGIN_SHIFT_CLOSING, "wrong initial byte"
        self._error_proc(answer)
        rc = OrderedDict({
        # This is empty interpretation body.

        })
        # A post processing rc = f(rc) 

        rc = self._wrap("begin_shift_closing",rc)

        return rc

    CMDMAP[BEGIN_SHIFT_CLOSING]=_interp_begin_shift_closing


class StateMachine(BaseStateMachine):
    """Definition of the protocol state machine"""

    def state_pc_unknown(self):
        self._send_char(b'\x05')
        return self.state_pc_determ

    def state_pc_determ(self):
        ch = self._recv_char()
        if ch == b'\x06':
            return self.state_pc_wait
        if ch == b'\x15':
            return self.state_pc_sstx
        if ch == '':
            return self.state_pc_nolink
        else:
            raise RuntimeError("wrong char")

    def state_pc_wait(self):
        ch = self._recv_char()
        if ch == b'\x02':
            return self.state_pc_length
        if ch == '':
            return self.state_pc_nolink
        if len(ch)>0:
            return self.state_pc_nolink
        else:
            raise RuntimeError("wrong char")

    def state_pc_sstx(self):
        self._send_char(b'\x02')
        return self.state_pc_send

    def state_pc_send(self):
        self._send_data(self.data)
        return self.state_pc_sent

    def state_pc_sent(self):
        ch = self._recv_char()
        if ch == b'\x06':
            return self.state_pc_wait
        if len(ch)>0:
            return self.state_pc_trysend
        else:
            raise RuntimeError("wrong char")

    def state_pc_receive(self):
        self.data = self._recv_data(self.size)
        return self.state_pc_crc

    def state_pc_trysend(self):
        self.send_tries-=1
        if self.send_tries >= 0:
            return self.state_pc_send
        if self.send_tries <= 0:
            return self.state_pc_nolink
        # Testing pc-trysend

    def state_pc_nolink(self):
        self._error('nolink')

    def state_pc_length(self):
        self.size = self._recv_byte()
        return self.state_pc_receive

    def state_pc_crc(self):
        self.crc = self._recv_char()
        self.crc_calculated = self._calculate_crc()
        return self.state_pc_check

    def state_pc_checkline(self):
        self.recv_tries-=1
        if self.recv_tries >= 0:
            return self.state_pc_unknown
        if self.recv_tries <= 0:
            return self.state_pc_nolink
        # Testing pc-checkline

    def state_pc_check(self):
        if self.crc == self.calculated_crc:
            return self.state_pc_ack
        if self.crc != self.calculated_crc:
            return self.state_pc_nak
        # Testing pc-check

    def state_pc_ack(self):
        self._send_char(b'\x06')
        return self.state_pc_fin

    def state_pc_nak(self):
        self._send_char(b'\x15')
        return self.state_pc_checkline

    def state_pc_fin(self):
        ch = self._recv_char()
        if ch == b'\xFF':
            return self.state_pc_good
        if ch == '':
            return self.state_pc_checkline
        else:
            raise RuntimeError("wrong char")

    def state_pc_good(self):
        self._good('good')
