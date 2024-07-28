import ctypes
from dataclasses import dataclass
from enum import Enum, Flag
import struct

class EnumProperty:
    def __init__(self, field_name, enum_type):
        self.field_name = field_name
        self.enum_type = enum_type

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.enum_type(getattr(instance, self.field_name))

    def __set__(self, instance, value):
        if not isinstance(value, self.enum_type):
            raise ValueError("Value must be a {} instance".format(self.enum_type.__name__))
        setattr(instance, self.field_name, value.value)

class RazerException(Exception):
    pass

class Status(Enum):
    NEW = 0
    BUSY = 1
    OK = 2
    FAIL = 3
    TIMEOUT = 4
    NOT_SUPPORTED = 5

class Profile(Enum):
    DIRECT = 0x00
    CURRENT = 0x01
    RED = 0x02
    GREEN = 0x03
    BLUE = 0x04
    CYAN = 0x05

class DeviceMode(Enum):
    NORMAL = 0x00
    BOOTLOADER = 0x01
    TEST = 0x02
    DRIVER = 0x03

class ScrollMode(Enum):
    TACTILE = 0
    FREESPIN = 1

class Button(Enum):
    LEFT = 0x01
    RIGHT = 0x02
    MIDDLE = 0x03
    BACKWARD = 0x04
    FORWARD = 0x05
    WHEEL_UP = 0x09
    WHEEL_DOWN = 0x0a
    BOTTOM = 0x0e
    AIM = 0x0f
    WHEEL_LEFT = 0x34
    WHEEL_RIGHT = 0x35
    MIDDLE_BACKWARD = 0x60
    MIDDLE_FORWARD = 0x6a

class Hypershift(Enum):
    OFF = 0x00
    ON = 0x01

class FnClass(Enum):
    DISABLED = 0x00
    MOUSE = 0x01
    KEYBOARD = 0x02
    MACRO_FIXED = 0x03
    MACRO_HOLD = 0x04
    MACRO_TOGGLE = 0x05
    DPI_SWITCH = 0x06
    PROFILE_SWITCH = 0x07
    SYSTEM = 0x09
    CONSUMER = 0x0a
    DOUBLE_CLICK = 0x0b
    HYPERSHIFT_TOGGLE = 0x0c
    KEYBOARD_TURBO = 0x0d
    MOUSE_TURBO = 0x0e
    MACRO_SEQUENCE = 0x0f
    SCROLL_MODE_TOGGLE = 0x12

class FnMouse(Enum):
    LEFT = 0x01
    RIGHT = 0x02
    MIDDLE = 0x03
    BACKWARD = 0x04
    FORWARD = 0x05
    WHEEL_UP = 0x09
    WHEEL_DOWN = 0x0a
    WHEEL_LEFT = 0x68
    WHEEL_RIGHT = 0x69

class FnKeyboardModifier(Flag):
    LEFT_CONTROL = 0x01
    LEFT_SHIFT = 0x02
    LEFT_ALT = 0x04
    LEFT_GUI = 0x08
    RIGHT_CONTROL = 0x10
    RIGHT_SHIFT = 0x20
    RIGHT_ALT = 0x40
    RIGHT_GUI = 0x80

class FnDpiSwitch(Enum):
    NEXT = 0x01
    PREV = 0x02
    FIXED = 0x05
    NEXT_LOOP = 0x06
    PREV_LOOP = 0x07

class FnSystem(Flag):
    POWER_DOWN = 0x01
    SLEEP = 0x02
    WAKE_UP = 0x04

class LiftConfig(Enum):
    SYM_1 = 0x0100
    SYM_2 = 0x0101
    SYM_3 = 0x0102
    ASYM_12 = 0x0200
    ASYM_13 = 0x0201
    ASYM_23 = 0x0202
    CONFIG1 = 0x0300
    CONFIG2 = 0x0400
    CALIB = 0x0500

class MacroOpType(Enum):
    KEYBOARD_DOWN = 0x01
    KEYBOARD_UP = 0x02
    MOUSE_BUTTON = 0x08
    MOUSE_WHEEL = 0x0a
    DELAY_1 = 0x11
    DELAY_2 = 0x12

macro_op_length = {
    MacroOpType.KEYBOARD_DOWN: 1,
    MacroOpType.KEYBOARD_UP: 1,
    MacroOpType.MOUSE_BUTTON: 1,
    MacroOpType.MOUSE_WHEEL: 1,
    MacroOpType.DELAY_1: 1,
    MacroOpType.DELAY_2: 2,
}

class transaction_parts(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("device", ctypes.c_uint8, 3),
        ("id", ctypes.c_uint8, 5),
    ]

class transaction_id_union(ctypes.Union):
    _fields_ = [
        ("id", ctypes.c_uint8),
        ("parts", transaction_parts),
    ]

class command_id_parts(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("direction", ctypes.c_uint8, 1),
        ("id", ctypes.c_uint8, 7),
    ]

class command_id_union(ctypes.Union):
    _fields_ = [
        ("id", ctypes.c_uint8),
        ("parts", command_id_parts),
    ]

class Report(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("_status", ctypes.c_uint8),
        ("transaction_id", transaction_id_union),
        ("remaining_packets", ctypes.c_uint16),
        ("protocol_type", ctypes.c_uint8),
        ("data_size", ctypes.c_uint8),
        ("command_class", ctypes.c_uint8),
        ("command_id", command_id_union),
        ("arguments", ctypes.c_uint8 * 80),
        ("crc", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8),
    ]
    status = EnumProperty('_status', Status)

    def calculate_crc(self):
        crc = 0
        report = bytearray(self)
        for i in range(2, 88):
            crc ^= report[i]
        self.crc = crc
        return crc
        
    @classmethod
    def new(cls, command_class, command_id, data_size):
        new_report = cls()
        new_report.status = Status.NEW
        new_report.transaction_id.id = 0x1f # basilisk v3
        new_report.remaining_packets = 0x00
        new_report.protocol_type = 0x00
        new_report.command_class = command_class
        new_report.command_id.id = command_id
        new_report.data_size = data_size
        return new_report


class ButtonFunction(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("_fn_class", ctypes.c_uint8),
        ("fn_value_length", ctypes.c_uint8),
        ("fn_value", ctypes.c_uint8 * 5),
    ]
    fn_class = EnumProperty('_fn_class', FnClass)
    
    def set_fn_class(self, fn_class):
        self.fn_class = fn_class
        return self
    
    def set_fn_value(self, b):
        self.fn_value_length = len(b)
        self.fn_value[:len(b)] = b
        return self
    def get_fn_value(self):
        return bytes(self.fn_value[:self.fn_value_length])

    def set_disable(self):
        self.fn_class = FnClass.DISABLED
        self.set_fn_value(b'')
        return self
    
    def set_mouse(self, fn, *, turbo=None, double_click=False):
        if double_click:
            self.fn_class = FnClass.DOUBLE_CLICK
            self.set_fn_value(struct.pack('>B', fn.value))
        elif turbo is not None:
            self.fn_class = FnClass.MOUSE_TURBO
            self.set_fn_value(struct.pack('>BH', fn.value, turbo))
        else:
            self.fn_class = FnClass.MOUSE
            self.set_fn_value(struct.pack('>B', fn.value))
        return self
    def get_mouse(self):
        if self.fn_class not in (FnClass.MOUSE, FnClass.MOUSE_TURBO, FnClass.DOUBLE_CLICK):
            raise ValueError()
        if self.fn_class in (FnClass.MOUSE, FnClass.DOUBLE_CLICK):
            fn, = struct.unpack('>B', self.get_fn_value())
            double_click = self.fn_class == FnClass.DOUBLE_CLICK
            return dict(fn=FnMouse(fn), double_click=double_click)
        else:
            fn, turbo = struct.unpack('>BH', self.get_fn_value())
            return dict(fn=FnMouse(fn), turbo=turbo)
    
    def set_keyboard(self, modifier, key, *, turbo=None):
        if turbo is None:
            self.fn_class = FnClass.KEYBOARD
            self.set_fn_value(struct.pack('>BB', modifier.value, key))
        else:
            self.fn_class = FnClass.KEYBOARD_TURBO
            self.set_fn_value(struct.pack('>BBH', modifier.value, key, turbo))
        return self
    def get_keyboard(self):
        if self.fn_class not in (FnClass.KEYBOARD, FnClass.KEYBOARD_TURBO):
            raise ValueError()
        if self.fn_class == FnClass.KEYBOARD:
            modifier, key = struct.unpack('>BB', self.get_fn_value())
            modifier = FnKeyboardModifier(modifier)
            return dict(modifier=modifier, key=key)
        else:
            modifier, key, turbo = struct.unpack('>BBH', self.get_fn_value())
            modifier = FnKeyboardModifier(modifier)
            return dict(modifier=modifier, key=key, turbo=turbo)
    
    def set_macro(self, macro_id, *, mode=FnClass.MACRO_FIXED, times=1):
        if mode not in (FnClass.MACRO_FIXED, FnClass.MACRO_HOLD, FnClass.MACRO_TOGGLE, FnClass.MACRO_SEQUENCE):
            raise ValueError()
        self.fn_class = mode
        if mode == FnClass.MACRO_FIXED:
            self.set_fn_value(struct.pack('>HB', macro_id, times))
        else:
            self.set_fn_value(struct.pack('>H', macro_id))
        return self
    def get_macro(self):
        if self.fn_class not in (FnClass.MACRO_FIXED, FnClass.MACRO_HOLD, FnClass.MACRO_TOGGLE, FnClass.MACRO_SEQUENCE):
            raise ValueError()
        mode = self.fn_class
        if mode == FnClass.MACRO_FIXED:
            macro_id, times = struct.unpack('>HB', self.get_fn_value())
            return dict(mode=mode, macro_id=macro_id, times=times)
        else:
            macro_id = struct.unpack('>H', self.get_fn_value())
            return dict(mode=mode, macro_id=macro_id)
    
    def set_dpi_switch(self, fn, dpi=None):
        self.fn_class = FnClass.DPI_SWITCH
        if fn == FnDpiSwitch.FIXED:
            self.set_fn_value(struct.pack('>BHH', fn, dpi[0], dpi[1]))
        else:
            self.set_fn_value(struct.pack('>B', fn))
        return self
    def get_dpi_switch(self):
        if self.fn_class != FnClass.DPI_SWITCH:
            raise ValueError()
        if len(self.get_fn_value()) == 5:
            fn, *dpi = struct.unpack('>BHH', self.get_fn_value())
            return dict(fn=fn, dpi=dpi)
        else:
            fn, = struct.unpack('>B', self.get_fn_value())
            return dict(fn=fn)
    
    def set_profile_switch(self, fn=0x04):
        self.fn_class = FnClass.PROFILE_SWITCH
        self.set_fn_value(struct.pack('>B', fn))
        return self
    def get_profile_switch(self):
        if self.fn_class != FnClass.PROFILE_SWITCH:
            raise ValueError()
        fn, = struct.unpack('>B', self.get_fn_value())
        return dict(fn=fn)

    def set_system(self, fn):
        self.fn_class = FnClass.SYSTEM
        self.set_fn_value(struct.pack('>B', fn.value))
    def get_system(self):
        if self.fn_class != FnClass.SYSTEM:
            raise ValueError()
        fn, = struct.unpack('>B', self.get_fn_value())
        return FnSystem(fn)
    
    def set_consumer(self, fn):
        self.fn_class = FnClass.CONSUMER
        self.set_fn_value(struct.pack('>H', fn))
        return self
    def get_consumer(self):
        if self.fn_class != FnClass.CONSUMER:
            raise ValueError()
        fn, = struct.unpack('>H', self.get_fn_value())
        return dict(fn=fn)
    
    def set_hypershift_toggle(self, fn=0x01):
        self.fn_class = FnClass.HYPERSHIFT_TOGGLE
        self.set_fn_value(struct.pack('>B', fn))
        return self
    def get_hypershift_toggle(self):
        if self.fn_class != FnClass.HYPERSHIFT_TOGGLE:
            raise ValueError()
        fn, = struct.unpack('>B', self.get_fn_value())
        return dict(fn=fn)
    
    def set_scroll_mode_toggle(self, fn=0x01):
        self.fn_class = FnClass.SCROLL_MODE_TOGGLE
        self.set_fn_value(struct.pack('>B', fn))
        return self
    def get_scroll_mode_toggle(self):
        if self.fn_class != FnClass.SCROLL_MODE_TOGGLE:
            raise ValueError()
        fn, = struct.unpack('>B', self.get_fn_value())
        return dict(fn=fn)