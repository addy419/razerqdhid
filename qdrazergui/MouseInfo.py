from textwrap import dedent
from textual.app import ComposeResult
from textual.widgets import Static, Markdown
from textual.reactive import reactive

from qdrazer.device import Device

class MouseInfo(Static):
    
    DEFAULT_CSS = '''
    
    '''
    
    device = reactive(Device)
    serial = reactive('')
    
    
    def compose(self) -> ComposeResult:
        yield Markdown(dedent('''
            # Mouse info
            
            - info 1
            - info 2
        '''))