from textual.widgets import TextArea

class SlimTextArea(TextArea):
    
    DEFAULT_CSS = '''
    SlimTextArea {
        border: none;
        background: $boost;
        &:focus {
            border: none;
            background: $primary-background;
        }
    }
    '''
