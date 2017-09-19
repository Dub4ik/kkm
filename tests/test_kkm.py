# encoding:utf-8
from nose.tools import nottest
from kkm.driver.fa01 import Driver, GET_CURRENT_STATE_SHORT
import kkm.driver.atol.control_symbols as symbol
import socket

from kkm.driver.fa01 import PrintFlag
from decimal import Decimal

#import kkm.driver.fa01.base as base

import pprint
import threading
import tools

EMULATION = False

BADADDR = False

import sys
import pprint
import time

# raise RuntimeError(sys.path)

#from kkm.driver.atol import Driver
if not EMULATION:
    if BADADDR:
        kkmDev = Driver(
            url="socket://192.168.114.10:7779?logging=debug", password=30)
    else:
        kkmDev = Driver(
            url="socket://192.168.114.10:7778?logging=debug", password=30)
else:
    kkmDev = Driver(
        url="socket://127.0.0.1:7778", password=30)

    # kkmDev = Driver(url="loop://", password=30)
    # kkmDev.debug_sleep = 2


api = kkmDev

# PAY VKP-80K-ФА

t1 = "06 02 10 10 00 1e b2 0a 04 00 00 9e 2d 00 00 00 75 02 00 66"

dump_data = tools.load()
# pprint.pprint(dump_data)

if EMULATION:
    class SimpleEmulator(threading.Thread):

        def run(self):
            if device is None:
                raise RuntimeError('device has not been set up')
            self.running = True
            while self.running:
                #print("EMU: wait")
                time.sleep(1)
                while device.in_waiting:
                    c = device.read(device.in_waiting)
                    print("EMU: RCV: {}".format(c))
                    if c == symbol.ACK:
                        time.sleep(2)
                    if c == symbol.ENQ:
                        device.write(symbol.NAK)
                        print("EMU: SND: {}".format(symbol.NAK))
                        time.sleep(2)
                    if c == symbol.STX:
                        continue
                    elif c == b'\x05\x10\x1e\x00\x00\x00\x0b':
                        data = bytes.fromhex(t1)

                        device.write(data)
                        print("EMU: SND DATA: {}".format(data))
                        time.sleep(2)
                    else:
                        print("Garbage: {}".format(c))

        def stop(self):
            self.running = False

    emu = SimpleEmulator()

    class DumpEmulator(threading.Thread):
        def run(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 7778))
            sock.listen(1)
            while True:
                conn, addr = sock.accept()
                while True:
                    data = conn.recv(1)
                    if data == b'\0x00':
                        break
                    elif data == b"\x06":
                        conn.send(b"\xff")
                    elif data == b"\x05":
                        conn.send(b"\x15")
                    elif data == b"\x02":
                        l = conn.recv(1)
                        le = ord(l)
                        data = conn.recv(le + 1)
                        data = b'\x02' + l + data
                        conn.send(b'\x06')
                        ex = dump_data[data].pop(1)
                        conn.sendall(ex)
                break

    dmp = DumpEmulator()


def as_bytes(dump):
    return bytes.fromhex(dump.replace(":", " "))


class TestBasic:
    def setUp(self):
        pass

    def test_test(self):
        pass

    @nottest
    def test_open_device(self):
        if EMULATION:
            emu.start()
            print("Emulator started")

        rc = kkmDev.get_status()
        pprint.pprint(rc._asdict())
        if EMULATION:
            emu.stop()
            emu.join()

    @nottest
    def test_dump(self):
        if EMULATION:
            dmp.start()
            print("EMULATION started")
            time.sleep(0.5)

        kkmDev.open_device()
        device = kkmDev._device
        for seq in dump_data.keys():
            # seq = as_bytes(seq)
            if seq.startswith(b'\02'):
                cmd = bytes([seq[2]])
                print("KEY:", seq)
                pwd = kkmDev._kkm_password
                if cmd in b'\xf7\xfc\x6b':
                    pwd = None
                    data = seq[3:-1]
                elif cmd == b'\xff':
                    cmd = bytes(seq[2:4])
                    data = seq[8:-1]
                    # assert False, (cmd, data)
                else:
                    data = seq[7:-1]
                print("CMD:", cmd, data)
                rc = kkmDev._atol_send_data_sequence(cmd, pwd, data)
                print("RECEIVED:{}".format(rc))
        kkmDev._device.write(b'\x00')
        kkmDev._device.write(b'\x00')
        kkmDev._device.write(b'\x00')
        kkmDev._device.write(b'\x00')
        kkmDev._device.write(b'\x00')
        kkmDev._device.write(b'\x00')

    @nottest
    def test_proto_decoding(self):
        # pprint.pprint(kkmDev.CMDMAP)
        for rows in dump_data.values():
            for row in rows:
                if row == b'\x06':
                    continue
                r = bytearray(row)
                if len(r) < 2:
                    continue
                r.pop(0)
                r.pop(0)
                r.pop()
                cmd = hex(r[0])
                try:
                    # pprint.pprint(kkmDev.interprete(r)._asdict())
                    kkmDev.interprete(r)
                except Exception as e:
                    print(cmd)
                    print("ERR: Error {} {}".format(e, row))
                    print("ERR:{}".format(kkmDev._last_interprete_method))

                if len(r) != 0:
                    print(cmd)
                    print("ERR:NOT_ALL", kkmDev._last_interprete_method)
                    print("ERR: ROW {}".format(row))
                    print("REST BYTES: {}".format(r))

    def test_id(self):
        #serid = kkmDev.getKKMId()
        pass

    @nottest
    def test_barcode(self):
        kkmDev._gen_barcode("519A5ED5B67E")

    @nottest
    def test_command_0(self):
        data = "06 02 10 10 00 1e b2 0a 04 00 00 9e 2d 00 00 00 75 02 00 66"
        data = bytes.fromhex(data)
        data = bytearray(data)
        print(data)
        ACK = data.pop(0)
        assert ACK == 0x06
        assert data.pop(0) == 0x02  # STX
        l = data.pop(0)
        CRC = data.pop(-1)
        print("Length:", l)
        print(data, GET_CURRENT_STATE_SHORT)
        rc = api._interp_get_current_state_short(
            data)
        assert rc
        print(data)
        pprint.pprint(rc._asdict())
        assert len(data) == 0

    @nottest
    def test_issue_cmd(self):
        pf = PrintFlag.check | PrintFlag.slip_check
        message = 'Проверка Русского Языка!'
        kkmDev.open_device()
        print('RC print:', kkmDev.print(pf, message))
        print('RC cut:', kkmDev.cut_check(True))

    def test_stop_emu_thread(self):
        pass

    def test_decimal(self):
        assert Decimal("1234.56")

    def test_amount_to_bytes(self):
        rc = api._amount_to_bytes('1234.56')
        # print(rc)
        assert rc == b'\x00\x00\x12\x34\x56'


"""
            self.kkm = kkmDev =
            kkmSerialNumber = kkmDev.getKKMId()
        except Exception, msg:
            self.mode = 1
            self.ShowError(msg or 'Не найден кассовый аппарат или не определён серийный номер.')
            raise
"""
