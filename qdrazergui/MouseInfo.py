from textwrap import dedent
from random import randrange
from textual.app import ComposeResult
from textual.widgets import Static, Markdown
from textual.reactive import reactive

from qdrazer.device import Device

from .SlimButton import SlimButton

class MouseInfo(Static):
    
    DEFAULT_CSS = '''
    '''
    
    device = reactive(Device)
    
    def compose(self) -> ComposeResult:
        yield Markdown()
        yield SlimButton('Refresh')
    
    def watch_device(self, old_device: Device, new_device: Device) -> None:
        try:
            _, total, free, recycled = new_device.get_flash_usage()
            profile_list = new_device.get_profile_list()
            macro_count = new_device.get_macro_count()
            rand = randrange(0, 8)
            self.query_one(Markdown).update(dedent(f'''
                # Razer Basilisk V3
                
                - Device: {new_device.get_info_manufacturer()}: {new_device.get_info_product()}
                - Path: {new_device.path.decode('utf-8')}
                - Serial: {new_device.get_serial().decode('utf-8')}, FW Ver {'.'.join(str(x) for x in new_device.get_firmware_version())}
                - Flash: {free/total:.1%} available, {free} free, {recycled} recycled, {total} total
                - Profiles: {', '.join(p.name for p in profile_list)}
                - Macros: {macro_count}
                - {''.join('@' if x == rand else '-' for x in range(8))}
            '''))
        except (NotImplementedError, AttributeError):
            self.query_one(Markdown).update(dedent(f'''
                # Razer Basilisk V3
            '''))
    
    def on_button_pressed(self, event: SlimButton.Pressed) -> None:
        self.watch_device(self.device, self.device)