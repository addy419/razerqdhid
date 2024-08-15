from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label

@dataclass(eq=False)
class ConfirmScreen(ModalScreen[bool]):  
    '''Screen with a confirm dialog.'''
    
    DEFAULT_CSS = '''
    ConfirmScreen {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    #question {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }

    Button {
        width: 100%;
    }
    '''
    
    question: str = 'Are you sure?'
    ok: str = 'OK'
    cancel: str = 'Cancel'
    
    def __post_init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.question, id='question'),
            Button(self.ok, variant='success', id='ok'),
            Button(self.cancel, id='cancel'),
            id='dialog',
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss(True)
        else:
            self.dismiss(False)


