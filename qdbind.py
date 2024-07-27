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
    
    def send_recv(self, report, *, wait_power=8):
        self.send(report)
        for i in range(wait_power):
            sleep(0.01 * (2 ** i)) # each iteration wait longer
            rr = self.recv()
            if not (rr.command_class == report.command_class and bytes(rr.command_id) == bytes(report.command_id)):
                breakpoint()
                raise pt.RazerException('command does not match, please close other programs using this device')
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
    # r.arguments[6] = 0x10
    # print(device.get_macro_info(29110).hex(' '))
    # print(device.get_macro_info(1362).hex(' '))
    print(device.get_macro_function(1362))
    # device.set_macro_function(1362, b'\x01\x04\x02\x04')
    