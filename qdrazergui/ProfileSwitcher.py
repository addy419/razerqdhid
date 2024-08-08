from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Tabs, Tab
import qdrazer.protocol as pt

class ProfileSwitcher(Static):
    
    profile = reactive(pt.Profile.CURRENT)
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab('Direct', id='DIRECT'),
            Tab('Default', id='DEFAULT'),
            Tab('Red', id='RED')
            Tab('Green', id='GREEN'),
            Tab('Blue', id='BLUE'),
            Tab('Cyan', id='CYAN'),
        )
