from textwrap import dedent
from textual.app import ComposeResult
from textual.widgets import Static, Markdown
from textual.reactive import reactive

from qdrazer.device import Device

class MouseInfo(Static):
    
    DEFAULT_CSS = '''
    
    '''
    
    device = reactive(Device)
    
    def compose(self) -> ComposeResult:
        yield Markdown(dedent(f'''
            # Mouse info
        '''))
    
    def watch_device(self, old_device: Device, new_device: Device) -> None:
        try:
            self.query_one(Markdown).update(dedent(f'''
                # Mouse info
                
                - Device: {new_device.get_info_manufacturer()} {new_device.get_info_product()}
                - Serial: {new_device.get_serial().decode('utf-8')}, FW Ver {'.'.join(str(x) for x in new_device.get_firmware_version())}
            '''))
        except NotImplementedError:
            pass