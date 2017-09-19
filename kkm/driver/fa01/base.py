from collections import namedtuple
from enum import IntFlag, Enum, IntEnum

# Flags = namedtuple("Flags", "controlroll, checkroll, "
#                    "uppersensor, lowersensor, "
#                    "decimal, eklz, opsensor, checksensor, "
#                    "termalcontrol, termalcheck, cover, "
#                    "moneybox, rightsensor "
#                    )


class Value(object):
    def __init__(self, val):
        self.val = val

    def __getattr__(self, name):
        name = "_" + name
        return self.val == getattr(self.__class__, name)


class KKMFlags (IntFlag):
    _check_roll = 0x0002
    _decimal_point = 0x0010
    _op_check = 0x0080
    _term_level = 0x2000
    _cover = 0x0400
    _present_paper = 0x0800

    # def __getattr__(self, name):
    #     name = "_" + name
    #     return bool(self.val & getattr(self.__class__, name))


class PrintFlag(IntFlag):
    control = 1 << 0
    check = 1 << 1
    backing_document = 1 << 2
    slip_check = 1 << 3
    wrapping = 1 << 6
    delay = 1 << 7

    # Флаги (1 байт)
    # Бит 0 – контрольная лента,
    # Бит 1 – чековая лента,
    # Бит 2 – подкладной документ,
    # Бит 3 – слип-чек,
    # Бит 6 – перенос строк5,
    # Бит 7 – отложенная печать


class FaFlags(IntFlag):
    fa1 = 1 << 0
    fa2 = 1 << 1
    license = 1 << 2
    overflow = 1 << 3
    battery = 1 << 4
    last_record_correct = 1 << 5
    shift_open = 1 << 6
    day_ended = 1 << 7
    reserved0 = 1 << 8
    aspd = 1 << 9
    blocked = 1 << 10
    reserved1 = 1 << 11
    records_brocken = 1 << 12
    fiscal_records_brocken = 1 << 13
    reserved2 = 1 << 14
    last_record_is_shift_total = 1 << 15


class KKMMode(IntEnum):
    DataOutput = 1
    OpenShiftOpen = 2
    OpenShiftTimeout24 = 3
    ClosedShift = 4
    WaitingForDateConfirmation = 5
    OpenDocument = 6
    Sell = 8
    TechnologicalReset = 9
    TestRun = 10


class KKMSubMode(IntEnum):
    PaperLoaded = 0
    PaperPassiveAbsence = 1
    PaperActiveAbsence = 2
    AfterActiveAbsence = 3
    PrintingFullFiscalReports = 4
    PrintingOperation = 5


class ChipCode(IntEnum):
    Check = 0
    FPMemory1 = 1
    FPRAM = 1
    FPMemory2 = 2
    Clock = 3
    EEPROM = 4
    CPU = 5
    FPFlash = 5
    KKTFlash = 6
    KKTRAM = 7
    FSImage = 8
    LinuxImage = 9
    Executable = 0x0A
    # KKTFlash = 0x86  # DATA size 128 Bytes


class DocumentType(IntEnum):
    Sell = 0
    Purchase = 1
    SellReturn = 2
    PurchaseReturn = 3


class BaseApi(object):

    def _wrap(self, wrapper_name, value):
        keys = value.keys()
        # print(wrapper_name, keys)
        cls = namedtuple(wrapper_name, keys)
        return cls._make(value.values())

    def _error_proc(self, answer):
        error = answer.pop(0)
        if error:
            raise RuntimeError("error {}".format(error))

    def _oper_number(self, value):
        # if value <= 0 or value > 30:
        #    raise ValueError('value \'{}\' must be in 1..30'.format(value))
        return value

    def _fa_error(self, value):
        return value

    def _ecpt_error(self, value):
        return value

    def _to_string(self, value):
        if b'\x00' in value:
            value = value.split(b'\x00', 1)[0]
        return value.decode('cp1251')

    def _shift(self, answer, count):
        rc = answer[:count]
        del answer[:count]
        return rc

    def _to_money(self, value):
        # print(value)
        return value

    def _interp_rest_field_structure(self, answer):
        return answer


class BaseStateMachine(object):
    def __init__(self, timeouts=None, tries=None, sleeps=None):

        if timeouts is None:
            timeouts = {"send": 40, "receive": 50}
        if tries is None:
            tries = {"send": 10, "receive": 10}
        if sleeps is None:
            sleeps = {"send": 0.125, "receive": 0.125}

        self.timeouts = timeouts
        self.tries = tries
        self.reset(None)

    def reset(self, data):
        self.state = self.state_pc_unknown
        self.send_tries = self.tries["send"]
        self.recv_tries = self.tries["receive"]
        self.size = None
        self.crc = None
        self.calculated_crc = None
        self.data = data

    def _good(self):
        pass

    def _error(self, error):
        raise RuntimeError('link error: {}'.format(error))

    def run(self, data):
        self.reset(data)

        # import pudb
        # pu.db

        if self.data is None:
            raise ValueError('empty data')
        while self.state != self.state_pc_good:
            # print("PC:STATE:{}".format(self.state.__name__))
            self.state = self.state()
            # print("PC:new STATE:{}".format(self.state.__name__))

    def _recv_byte(self):
        return ord(self._recv_char())
