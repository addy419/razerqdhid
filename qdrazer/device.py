import ctypes
import struct
from enum import Enum

from . import protocol as pt

class Device:
    
    def send(self, report):
        raise NotImplementedError
    
    def recv(self):
        raise NotImplementedError
    
    def send_recv(self, report):
        raise NotImplementedError

    def set_device_mode(self, mode, param):
        # 0: normal, 1: bootloader, 2: test, 3: driver
        r = pt.Report.new(0x00, 0x04, 0x02)
        r.arguments[0] = mode.value
        r.arguments[1] = param
        self.send_recv(r)

    def get_device_mode(self):
        r = pt.Report.new(0x00, 0x84, 0x02)
        rr = self.send_recv(r)
        return pt.DeviceMode(rr.arguments[0]), rr.arguments[1]

    def get_serial(self):
        r = pt.Report.new(0x00, 0x82, 0x16)
        rr = self.send_recv(r)
        return rr.arguments[0:16].hex()

    def get_firmware_version(self):
        r = pt.Report.new(0x00, 0x81, 0x08)
        rr = self.send_recv(r)
        return rr.arguments[0:3]

    def set_scroll_mode(self, mode: pt.ScrollMode, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x14, 0x02)
        r.arguments[0] = profile
        r.arguments[1] = mode.value
        self.send_recv(r)
    def get_scroll_mode(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x94, 0x02)
        r.arguments[0] = profile
        rr = self.send_recv(r)
        return pt.ScrollMode(rr.arguments[1])
    
    def set_scroll_acceleration(self, is_on: bool, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x16, 0x02)
        r.arguments[0] = profile
        r.arguments[1] = int(is_on)
        self.send_recv(r)
    def get_scroll_acceleration(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x96, 0x02)
        r.arguments[0] = profile
        rr = self.send_recv(r)
        return bool(rr.arguments[1])
    
    def set_scroll_smart_reel(self, is_on: bool, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x17, 0x02)
        r.arguments[0] = profile
        r.arguments[1] = int(is_on)
        self.send_recv(r)
    def get_scroll_smart_reel(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x97, 0x02)
        r.arguments[0] = profile
        rr = self.send_recv(r)
        return bool(rr.arguments[1])

    def set_remap_button(self, remap_arg):
        r = pt.Report.new(0x02, 0x0c, 0x0a)
        r.arguments[:0x0a] = bytes(remap_arg)
        self.send_recv(r)
    def get_remap_button(self, remap_arg):
        r = pt.Report.new(0x02, 0x8c, 0x0a)
        r.arguments = bytes(remap_arg)
        rr = self.send_recv(r)
        return pt.RemapArgument.from_buffer_copy(rr.arguments)

    def set_polling_rate(self, delay_ms):
        r = pt.Report.new(0x00, 0x05, 0x01)
        r.arguments[0] = delay_ms
        self.send_recv(r)
    def get_polling_rate(self):
        r = pt.Report.new(0x00, 0x85, 0x01)
        rr = self.send_recv(r)
        return rr.arguments[0]
    
    def set_dpi_xy(self, dpi, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x04, 0x05, 0x07)
        r.arguments[:7] = struct.pack('>BHHxx', profile.value, dpi[0], dpi[1])
        self.send_recv(r)
    def get_dpi_xy(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x04, 0x85, 0x07)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        return rr.arguments[0]
    
    def set_dpi_stages(self, dpi_stages, active_stage, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x04, 0x06, 0x26) # at most 5, more will fail
        r.arguments[:3] = struct.pack('>BBB', profile.value, active_stage, len(dpi_stages))
        for i, (x, y) in enumerate(dpi_stages):
            r.arguments[3+7*i:3+7*i+7] = struct.pack('>BHHxx', i, x, y)
        self.send_recv(r)
    def get_dpi_stages(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x04, 0x86, 0x26)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        active_stage = rr.arguments[1]
        dpi_stages_len = rr.arguments[2]
        dpi_stages = []
        for i in range(dpi_stages_len):
            ii, x, y = struct.unpack('>BHHxx', bytes(rr.arguments[3+7*i:3+7*i+7]))
            dpi_stages.append((x, y))
        return dpi_stages, active_stage


