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
        self.hid_device.send_feature_report(send_data)
    
    def recv(self):
        data = self.hid_device.get_feature_report(0, 91)
        data = data[1:] # remove report id
        return pt.Report.from_buffer(bytearray(data))
    
    def send_recv(self, report, *, wait_power=0):
        self.send(report)
        rr = report
        for i in range(15 * (wait_power + 1)):
            sleep(0.01 * (i + 1)) # each iteration wait longer
            rr = self.recv()
            if not (rr.command_class == report.command_class and bytes(rr.command_id) == bytes(report.command_id)):
                raise pt.RazerException('command does not match, please close other programs using this device', rr)
            if rr.status == pt.Status.OK:
                return rr
            elif rr.status == pt.Status.BUSY:
                continue
            else:
                raise pt.RazerException('report execution failed', rr)
        raise pt.RazerException('report timeout', rr)

if __name__ == '__main__':
    original_sr_with = BasiliskV3WiredDevice.sr_with
    def sr_with(self, *args, **kwargs):
        print(f's: {hex(args[0])} {args[1:]}, {kwargs}')
        r = original_sr_with(self, *args, **kwargs)
        print(f'r: {r}')
        return r
    BasiliskV3WiredDevice.sr_with = sr_with
    device = BasiliskV3WiredDevice()
    device.connect()
    print(device.get_sensor_lift_config())
