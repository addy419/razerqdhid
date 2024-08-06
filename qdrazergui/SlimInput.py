from textual.widgets import Input

class SlimInput(Input):
    
    DEFAULT_CSS = '''
    SlimInput {
        border: none;
        height: 1;
    }
    SlimInput:focus {
        border: none;
        background: $primary-background;
    }
    SlimInput>.input--cursor {
        background: $surface;
        color: $text;
        text-style: reverse;
    }
    SlimInput>.input--placeholder, SlimInput>.input--suggestion {
        color: $text-disabled;
    }
    SlimInput.-invalid {
        border: none;
    }
    SlimInput.-invalid:focus {
        border: none;
    }
    
    '''
