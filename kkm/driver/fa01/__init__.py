from .api import Api, StateMachine
from .commands import *
import kkm.driver.atol as atol
import logging
import serial
from ..atol import control_symbols as symbol, \
    constants as const, commands as cmd, modes
from ...exceptions import *
import sys
from .base import *
from kkm.driver.atol.implementation import number2atol
from decimal import Decimal, getcontext

log = logging.getLogger(__name__)
DEBUG_SLEEP = 0  # seconds
DEBUG = False

getcontext().prec = 2


class Driver(Api):
    def __init__(self, port=None, baudrate=None, password=0, url=None):
        self._port = port
        self._baudrate = baudrate
        self._kkm_password = None
        self.set_password(password)
        self._url = url
        self._state_machine = None

    def set_password(self, password):
        old = self._kkm_password
        self._kkm_password = password
        return old

    def open_device(self):
        """
        Проверить наличие блокировки устройства
        Заблокировать или вывалиться с ошибкой
        """
        log.info('> Open device.')
        try:
            if self._url:
                self._device = serial.serial_for_url(self._url)
            else:
                self._device = serial.Serial(**self._params)
                super().open_device()
        except Exception as E:
            raise CommonError(
                'System error at opening KKM device: {}'.format(E))
        if not self._device:
            raise CommonError('Unknown error at opening KKM device')
        log.debug('> Open device completed.')
        self._state_machine = Machine(self._device)
        return self._device

    def close_device(self):
        self._device.close()
        self._device = None
        self._state_machine = None

    def _atol_send_data_sequence(self, command, password, data):
        assert len(command) in [1, 2], "wrong command length"
        if password is not None:
            if type(password) in [bytes, bytearray, str]:
                assert len(password) > 0, "empty password"
            else:
                password = password.to_bytes(4, sys.byteorder)
            data = command + bytes(password) + data
        else:
            data = command + data

        # data=bytearray(data)
        data_length = len(data)
        data = data_length.to_bytes(1, sys.byteorder) + data
        crc = bytes((atol.atol_calc_crc(data),))
        data = data + crc
        try:
            self._state_machine.run(data=data)
        except OSError as e:  # for Linux
            exc = sys.exc_info()
            if exc[1].errno == 19:
                log.error(DeviceNotFoundError())
                raise DeviceNotFoundError()
            else:
                log.error(e)
                raise KKMConnectionErr()
        # except Exception as e:  # win32file raise common exception, not OSError as Linux
        #    log.error(e)
        #    raise KKMConnectionErr()
        return self._state_machine.data

    _send_command = _atol_send_data_sequence

    def _get_password(self):
        return self._kkm_password

    def _receive_answer(self):
        data = self._state_machine.data
        if data is not None:
            return data
        else:
            raise RuntimeError('no answer')

    def get_status(self):
        log.debug('> Get status.')
        response = self._atol_send_data_sequence(b'\x10',
                                                 self._kkm_password, b'')
        #raise RuntimeError(response)
        response = bytearray(response)
        log.debug("To Interprete: {}".format(response))
        log.debug("Expecting cmd: {}".format(GET_CURRENT_STATE_SHORT))
        return self._interp_get_current_state_short(response, GET_CURRENT_STATE_SHORT)

    def is_check_open(self):
        rc = self.get_current_state_short()
        mode = rc.mode
        return mode in [KKMMode.OpenDocument, KKMMode.Sell]

    def is_shift_timed_out(self):
        rc = self.get_current_state_short()
        return rc.mode == KKMMode.OpenShiftTimeout24

    def is_shift_open(self):
        if self.is_check_open():
            return True
        rc = self.get_current_state_short()
        return rc.mode == KKMMode.OpenShiftOpen

    def payment(self, summ):
        # self.close_check(...)
        pass

    def print_string(self, text):
        text = self.yo_patch(text)
        return self.print(PrintFlag.check, text)

    def yo_patch(self, t):
        a = t.replace("ё", "е").replace("Ё", "Е")
        return a

    def print_custom(self, text,
                     flags=None,
                     magnify=False,
                     center=False,
                     fmt=False,
                     spacing=None,
                     width=40
                     ):
        text = self.yo_patch(text)
        # self.print_bold or wit font
        if flags is None:
            flags = PrintFlag.check
        if magnify:
            width //= 2
        if center:
            text = text.center(width)
        if magnify:
            return self.print_bold(flags, text)
        else:
            return self.print(PrintFlag.check, text)

    def by_pass(self, text):
        pass

    def reset_mode(self):
        pass

    def set_registration_mode(self):
        pass

    def set_zreport_mode(self):
        pass

    def barcode_print(self, barcode):
        return self.print_ean13(barcode.encode('ascii'))  # FIXME: QRCode?

    def report(self):
        pass

    def interprete(self, answer):
        m = self.__class__.CMDMAP
        f = bytes([answer[0]])
        if f == b'\xFF':
            f += bytes([answer[1]])
        m = self._last_interprete_method = m[f]
        return m(self, answer)

    def _gen_barcode(self, data, barcode_type='code39'):
        import barcode
        from barcode.writer import ImageWriter
        GEN = barcode.get_barcode_class(barcode_type)
        rc = GEN(data, writer=ImageWriter())
        print(rc, GEN, data)
        rc.save(barcode_type)

    def _amount_to_bytes(self, amount, width=5, pos=2):
        if type(amount) == Decimal:
            amount = str(amount)
        assert type(amount) == str, "must be str: {}:{}".format(
            amount, type(amount))
        amount = amount.strip()
        assert not amount.startswith('-')
        amount = amount.replace(',', '.')
        dp = amount.find('.')
        if dp == -1:
            amount += '0' * pos
        else:
            dd = len(amount) - 1 - dp
            assert dd <= 2
            ad = pos - dd
            amount += '0' * ad
            i, r = amount.split('.')
            assert len(r) == pos
            amount = i + r
        #number = number2atol(amount, width=width)
        amount = int(amount)
        answer = amount.to_bytes(width, byteorder=sys.byteorder)
        assert len(answer) == width, "format error: {}:{}".format(
            answer, len(answer))
        return answer


class Machine(StateMachine):
    def __init__(self, device, **kwargs):
        super(Machine, self).__init__(**kwargs)
        self.device = device
        self.debug_sleep = DEBUG_SLEEP

    def _write_device(self, data):
        device = self.device
        device.write_timeout = self.timeouts["send"]
        device.write(data)
        if DEBUG:
            print("PC:SND:{}".format(data))
        self._debug_sleep()

    def _read_device(self, count=1):
        device = self.device
        device.timeout = self.timeouts["receive"]
        data = device.read(count)
        # log.debug('Received :{}'.format(data))
        if DEBUG:
            print("PC:RCV:{}".format(data))
        return data

    def _debug_sleep(self):
        if self.debug_sleep:
            import time
            time.sleep(self.debug_sleep)

    def _send_char(self, ch):
        assert type(ch) in [bytes, bytearray]
        return self._write_device(ch)

    def _recv_char(self):
        return self._read_device(1)

    def _send_data(self, data):
        return self._write_device(data)

    def _recv_data(self, count):
        return self._read_device(count)

    def _calculate_crc(self):
        data = bytes([self.size]) + self.data
        # print("CRC CALC DATA:{}".format(data))
        self.calculated_crc = bytes((atol.atol_calc_crc(data),))
        # print("CRC:{} = {} (CALC)".format(self.crc, self.calculated_crc))

    def run(self, data):
        cnt = 10
        while cnt:
            try:
                return super(Machine, self).run(data)
            except RuntimeError as e:
                if str(e).startswith("wrong char"):
                    self._device.read()

                cnt -= 1
        raise RuntimeError("protocol error")
