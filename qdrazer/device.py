import ctypes
import struct
from enum import Enum

from . import protocol as pt

class Device:
    
    def send(self, report):
        raise NotImplementedError
    
    def recv(self):
        raise NotImplementedError
    
    def send_recv(self, report, *, wait_power=8):
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
        return rr.arguments[0:16]

    def get_firmware_version(self):
        r = pt.Report.new(0x00, 0x81, 0x08)
        rr = self.send_recv(r)
        return rr.arguments[0:3]

    def set_scroll_mode(self, mode: pt.ScrollMode, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x14, 0x02)
        r.arguments[0] = profile.value
        r.arguments[1] = mode.value
        self.send_recv(r)
    def get_scroll_mode(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x94, 0x02)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        return pt.ScrollMode(rr.arguments[1])
    
    def set_scroll_acceleration(self, is_on: bool, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x16, 0x02)
        r.arguments[0] = profile.value
        r.arguments[1] = int(is_on)
        self.send_recv(r)
    def get_scroll_acceleration(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x96, 0x02)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        return bool(rr.arguments[1])
    
    def set_scroll_smart_reel(self, is_on: bool, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x17, 0x02)
        r.arguments[0] = profile.value
        r.arguments[1] = int(is_on)
        self.send_recv(r)
    def get_scroll_smart_reel(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x02, 0x97, 0x02)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        return bool(rr.arguments[1])

    def set_button_function(self, remap_arg):
        r = pt.Report.new(0x02, 0x0c, 0x0a)
        r.arguments[:0x0a] = bytes(remap_arg)
        self.send_recv(r)
    def get_button_function(self, remap_arg):
        r = pt.Report.new(0x02, 0x8c, 0x0a)
        r.arguments = bytes(remap_arg)
        rr = self.send_recv(r)
        return pt.RemapArgument.from_buffer_copy(rr.arguments)

    def set_polling_rate(self, delay_ms, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x00, 0x0e, 0x01)
        r.arguments[0] = profile.value
        r.arguments[1] = delay_ms
        self.send_recv(r)
    def get_polling_rate(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x00, 0x8e, 0x01)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        return rr.arguments[1]
    
    def set_dpi_xy(self, dpi, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x04, 0x05, 0x07)
        r.arguments[:7] = struct.pack('>BHHxx', profile.value, dpi[0], dpi[1])
        self.send_recv(r)
    def get_dpi_xy(self, *, profile=pt.Profile.CURRENT):
        r = pt.Report.new(0x04, 0x85, 0x07)
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        return struct.unpack('>xHHxx', bytes(rr.arguments[:7]))
    
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

    def get_flash_usage(self):
        r = pt.Report.new(0x06, 0x8e, 14)
        rr = self.send_recv(r)
        return struct.unpack('>HIII', bytes(rr.arguments[:14]))
    
    def wait_device_ready(self):
        r = pt.Report.new(0x00, 0x86, 3)
        rr = self.send_recv(r, wait_power=9)
        return True
    
    def get_profile_total_count(self):
        r = pt.Report.new(0x05, 0x8a, 1)
        rr = self.send_recv(r)
        return rr.arguments[0]
    
    def get_profile_available_count(self):
        r = pt.Report.new(0x05, 0x80, 1)
        rr = self.send_recv(r)
        return rr.arguments[0]
    
    def get_profile_list(self):
        length = self.get_profile_available_count()
        r = pt.Report.new(0x05, 0x81, 1 + length)
        rr = self.send_recv(r)
        return list(rr.arguments[1:1+length])
    
    def new_profile(self, profile):
        r = pt.Report.new(0x05, 0x02, 1)
        r.arguments[0] = profile.value
        self.send_recv(r)
    
    def delete_profile(self, profile):
        r = pt.Report.new(0x05, 0x03, 1)
        r.arguments[0] = profile.value
        self.send_recv(r)
    
    def get_profile_info(self, profile):
        r = pt.Report.new(0x05, 0x88, 5 + 64) # read length and 64 bytes
        r.arguments[0] = profile.value
        rr = self.send_recv(r)
        _, _, length = struct.unpack('>BHH', bytes(rr.arguments[:5]))
        data = b""
        while length > 64:
            data += bytes(rr.arguments[5:5+64])
            r = pt.Report.new(0x05, 0x88, 5 + 64)
            r.arguments[:3] = struct.pack('>BH', profile.value, len(data))
            rr = self.send_recv(r)
            length -= 64
        data += bytes(r.arguments[5:5+length])
        return data
    
    def set_profile_info(self, profile, data):
        start = 0
        while len(data) - start > 64:
            r = pt.Report.new(0x05, 0x08, 5 + 64)
            r.arguments[:5] = struct.pack('>BHH', profile.value, start, len(data))
            r.arguments[5:5+64] = data[start:start+64]
            self.send_recv(r)
            start += 64
        r = pt.Report.new(0x05, 0x08, 5 + len(data) - start)
        r.arguments[:5] = struct.pack('>BHH', profile.value, start, len(data))
        r.arguments[5:5+len(data)-start] = data[start:]
        self.send_recv(r)
    
    def get_macro_count(self):
        r = pt.Report.new(0x06, 0x80, 2)
        rr = self.send_recv(r)
        return struct.unpack('>H', bytes(rr.arguments[:2]))[0]

    def get_macro_list(self):
        count = self.get_macro_count()
        macro_list = []
        while count - len(macro_list) > 32:
            r = pt.Report.new(0x06, 0x8b, 4 + 2 * 32)
            r.arguments[:2] = struct.pack('>H', len(macro_list))
            rr = self.send_recv(r)
            macro_list.extend(struct.unpack('>32H', bytes(rr.arguments[4:4+2*32])))
        r = pt.Report.new(0x06, 0x8b, 4 + 2 * (count - len(macro_list)))
        r.arguments[:2] = struct.pack('>H', len(macro_list))
        rr = self.send_recv(r)
        macro_list.extend(struct.unpack('>{}H'.format(count - len(macro_list)), bytes(rr.arguments[4:4+2*(count - len(macro_list))])))
        return macro_list
    
    def get_macro_info(self, macro_id):
        r = pt.Report.new(0x06, 0x8c, 6 + 64) # read length and 64 bytes
        r.arguments[:2] = struct.pack('>H', macro_id)
        rr = self.send_recv(r)
        _, _, length = struct.unpack('>HHH', bytes(rr.arguments[:6]))
        data = b""
        while length > 64:
            data += bytes(rr.arguments[6:6+64])
            r = pt.Report.new(0x06, 0x8c, 6 + 64)
            r.arguments[:4] = struct.pack('>HH', macro_id, len(data))
            rr = self.send_recv(r)
            length -= 64
        data += bytes(r.arguments[6:6+length])
        return data

    def set_macro_info(self, macro_id, data):
        start = 0
        while len(data) - start > 64:
            r = pt.Report.new(0x06, 0x0c, 6 + 64)
            r.arguments[:6] = struct.pack('>HHH', macro_id, start, len(data))
            r.arguments[6:6+64] = data[start:start+64]
            self.send_recv(r)
            start += 64
        r = pt.Report.new(0x06, 0x0c, 6 + len(data) - start)
        r.arguments[:6] = struct.pack('>HHH', macro_id, start, len(data))
        r.arguments[6:6+len(data)-start] = data[start:]
        self.send_recv(r)
    
    def delete_macro(self, macro_id):
        r = pt.Report.new(0x06, 0x03, 2)
        r.arguments[:2] = struct.pack('>H', macro_id)
        self.send_recv(r)
    
    def get_macro_length(self, macro_id):
        r = pt.Report.new(0x06, 0x88, 6)
        r.arguments[:2] = struct.pack('>H', macro_id)
        rr = self.send_recv(r)
        _, length = struct.unpack('>HI', bytes(rr.arguments[:6]))
        return length
    
    def set_macro_length(self, macro_id, length):
        r = pt.Report.new(0x06, 0x08, 6)
        r.arguments[:6] = struct.pack('>HI', macro_id, length)
        self.send_recv(r)
        
    def get_macro_function(self, macro_id):
        length = self.get_macro_length(macro_id)
        data = b''
        while length - len(data) > 72:
            r = pt.Report.new(0x06, 0x89, 7 + 72)
            r.arguments[:7] = struct.pack('>HIB', macro_id, len(data), 72)
            rr = self.send_recv(r)
            data += bytes(rr.arguments[7:7+72])
        r = pt.Report.new(0x06, 0x89, 7 + length - len(data))
        r.arguments[:7] = struct.pack('>HIB', macro_id, len(data), length - len(data))
        rr = self.send_recv(r)
        data += bytes(rr.arguments[7:7+length-len(data)])
        return data
    
    def set_macro_function(self, macro_id, data):
        self.delete_macro(macro_id)
        self.set_macro_length(macro_id, len(data))
        start = 0
        while len(data) - start > 72:
            r = pt.Report.new(0x06, 0x09, 7 + 72)
            r.arguments[:7] = struct.pack('>HIB', macro_id, start, 72)
            r.arguments[7:7+72] = data[start:start+72]
            self.send_recv(r)
            start += 64
        r = pt.Report.new(0x06, 0x09, 7 + len(data) - start)
        r.arguments[:7] = struct.pack('>HIB', macro_id, start, len(data) - start)
        r.arguments[7:7+len(data)-start] = data[start:start+72]
        self.send_recv(r)

