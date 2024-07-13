import hid

from qdrazer.device import Device
import qdrazer.protocol as pt
from time import sleep

class BasiliskV3WiredDevice(Device):
    vid = 0x1532
    pid = 0x0099
    ifn = 3
    
    def connect(self):
        self.path = None
        for it in hid.enumerate():
            if self.vid == it['vendor_id'] and self.pid == it['product_id'] and it['interface_number'] == self.ifn:
                self.path = it['path']

        if self.path is None:
            raise RuntimeError('No matching device')
        
        self.hid_device = hid.Device(path=self.path)
    
    def close(self):
        self.hid_device.close()
    
    def print_info(self):
        print(f"device manufacturer: {self.hid_device.manufacturer}")
        print(f"product: {self.hid_device.product}")
        print(f"serial: {self.hid_device.serial}")

        print(self.hid_device.get_indexed_string(1))
        print(self.hid_device.get_indexed_string(2))
    
    def send(self, report):
        report.calculate_crc()
        send_data = b'\x00' + bytes(report)
        print('send:', send_data)
        self.hid_device.send_feature_report(send_data)
    
    def recv(self):
        data = self.hid_device.get_feature_report(0, 91)
        print('recv:', data)
        data = data[1:] # remove report id
        return pt.Report.from_buffer(bytearray(data))
    
    def send_recv(self, report):
        self.send(report)
        for i in range(4):
            sleep(0.01 * (i + 1)) # each iteration wait longer
            rr = self.recv()
            if rr.status == pt.Status.OK:
                return rr
            elif rr.status == pt.Status.BUSY:
                continue
            else:
                raise pt.RazerException('report execution failed')
        raise pt.RazerException('report timeout')

if __name__ == '__main__':
    device = BasiliskV3WiredDevice()
    device.connect()
    # print(device.get_serial())
    # print(device.get_firmware_version())
    # print(device.get_device_mode())
    # print(device.set_device_mode(0, 0))
    # print(device.set_scroll_smart_reel(False))
    # r = pt.Report.new(0x02, 0x0c, 10)
    # for i, b in enumerate(bytearray(bytes.fromhex('00 60 00 06 01 0600000000'))):
    #     r.arguments[i] = b
    # for kk in range(256):
    #     sleep(0.5)
        # r.arguments[5] = int(input('key: '), base=16)
        # print(r)
    # try:
    #     print(device.send_recv(r))
    # except Exception as e:
    #     print(e)
    # # else:
    #     print('success')
    # r = pt.RemapArgument.new(pt.Button.AIM, pt.Hypershift.OFF, profile=pt.Profile.CURRENT)
    # r.set_keyboard(pt.FnKeyboardModifier.LEFT_ALT | pt.FnKeyboardModifier.RIGHT_CONTROL, 0x04, turbo=100)
    # print(r.get_keyboard())
    # device.set_remap_button(r)
    # print(device.set_dpi_stages([(4000, 4000), (4100, 4100), (4200, 4200), (4300, 4300), (4400, 4400)], 1, profile=pt.Profile.DIRECT))
    print(device.get_dpi_stages(profile=pt.Profile.DIRECT))