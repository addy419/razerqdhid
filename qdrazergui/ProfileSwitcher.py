from dataclasses import dataclass
from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, RadioSet, RadioButton, OptionList
from textual.widgets.option_list import Option
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.message import Message

from .Confirm import ConfirmScreen

from qdrazer.device import Device
import qdrazer.protocol as pt

class ProfileSwitcher(Static):
    
    @dataclass
    class Changed(Message):
        profile: pt.Profile
    
    DEFAULT_CSS = '''
    ProfileSwitcher {
        RadioButton:disabled {
            color: $text-disabled;
        }
    }
    '''
    device = reactive(Device)
    profile = reactive(pt.Profile.DEFAULT)
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            with RadioSet():
                yield RadioButton("Direct")
                yield RadioButton("White")
                yield RadioButton("Red")
                yield RadioButton("Green")
                yield RadioButton("Blue")
                yield RadioButton("Cyan")
            yield OptionList(
                Option('x', disabled=True),
                Option('x'),
                Option('x'),
                Option('x'),
                Option('x'),
                Option('x'),
            )
    
    def watch_device(self, old_device: Device, new_device: Device) -> None:
        try:
            self.update_disable()
        except NotImplementedError:
            pass
    
    def watch_profile(self, old_profile: pt.Profile, new_profile: pt.Profile) -> None:
        self.query(RadioButton)[new_profile.value].value = True
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.post_message(type(self).Changed(pt.Profile(event.radio_set.pressed_index)))
    
    def update_disable(self) -> None:
        profile_list = self.device.get_profile_list()
        buttons = self.query(RadioButton)
        options = self.query_one(OptionList)
        for p in pt.Profile:
            if p is pt.Profile.DIRECT:
                options.get_option_at_index(p.value).set_prompt('-')
            elif p in profile_list:
                buttons[p.value].disabled = False
                options.get_option_at_index(p.value).set_prompt('[red]x[/]')
            else:
                buttons[p.value].disabled = True
                options.get_option_at_index(p.value).set_prompt('+')
    
    @work
    async def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        ok = await self.app.push_screen_wait(ConfirmScreen())
        if ok:
            print('ok')
        else:
            print('no ok')
            