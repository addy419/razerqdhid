from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer

from qdbind import BasiliskV3WiredDevice

from .SendRecv import SendRecv
from .MouseInfo import MouseInfo


class MyApp(App):
    
    CSS = '''
    Screen {
        padding: 1 2;
    }
    '''
    
    def __init__(self, *args, **kwargs):
        self.device = BasiliskV3WiredDevice()
        self.device.connect()
        super().__init__(*args, **kwargs)
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            yield MouseInfo().data_bind(device=self.device)
            yield SendRecv().data_bind(device=self.device)

if __name__ == '__main__':
    app = MyApp()
    app.run()