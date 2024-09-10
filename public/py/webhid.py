import ctypes
import enum
import asyncio

from pyodide.code import run_js
from pyodide.ffi import to_js
import js

__all__ = ['HIDException', 'DeviceInfo', 'Device', 'enumerate', 'BusType', 'webhid_request']

class HIDException(Exception):
    pass

class BusType(enum.Enum):
    UNKNOWN = 0x00
    USB = 0x01
    BLUETOOTH = 0x02
    I2C = 0x03
    SPI = 0x04

devices = []

def enumerate(vid=0, pid=0):
    global devices
    new_devices = []
    for i, d in zip(range(1<<20), devices):
        dd = {
            'path': i,
            'vendor_id': d.vendorId,
            'product_id': d.productId,
            'serial_number': '',
            'manufacturer_string': '',
            'product_string': d.productName,
            'usage_page': d.collections[0].usagePage,
            'usage': d.collections[0].usage,
            'interface_number': -1,
            'fio_count': (d.collections[0].featureReports.length, d.collections[0].inputReports.length, d.collections[0].outputReports.length),
        }
        new_devices.append(dd)
    return new_devices

def find_device(vid=None, pid=None, serial=None, path=None):
    if path:
        return devices[path]
    elif serial:
        raise ValueError('serial is not available in webhid')
    elif vid and pid:
        for d in devices:
            if d.vendorId == vid and d.productId == pid:
                return d
            raise ValueError('no device with vid pid found')
    else:
        raise ValueError('specify vid/pid or path')

class Device(object):
    def __init__(self, vid=None, pid=None, serial=None, path=None):
        self.__dev = find_device(vid, pid, serial, path)
        print(await_sync(self.__dev.open()))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def write(self, data):
        report_id, data = data[0], data[1:]
        p = self.__dev.sendReport(report_id, data)
        if not self.nonblocking:
            return sync_wait(p)

    def read(self, size, timeout=None):
        raise NotImplementedError()

    def get_input_report(self, report_id, size):
        raise NotImplementedError()

    def send_feature_report(self, data):
        report_id, data = data[0], data[1:]
        p = self.__dev.sendFeatureReport(report_id, data)
        if not self.nonblocking:
            return sync_wait(p)

    def get_feature_report(self, report_id, size):
        p = self.__dev.receiveFeatureReport(report_id)
        return p

    def close(self):
        if self.__dev:
            self.__dev.close()
            self.__dev = None

    @property
    def nonblocking(self):
        return getattr(self, '_nonblocking', 0)

    @nonblocking.setter
    def nonblocking(self, value):
        setattr(self, '_nonblocking', value)

    @property
    def manufacturer(self):
        return ''

    @property
    def product(self):
        return self.__dev.productName

    @property
    def serial(self):
        return ''

    def get_indexed_string(self, index, max_length=255):
        return ''
