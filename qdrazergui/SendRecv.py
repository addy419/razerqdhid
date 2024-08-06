import re
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.widgets import Static, Label, LoadingIndicator, Button
from textual.containers import Container

from qdrazer.device import Device
import qdrazer.protocol as pt
from .async_wrapper import async_wrapper

from .SlimInput import SlimInput
from .SlimTextArea import SlimTextArea

def transform_string(s):
    def replace(match):
        part, repeat = match.groups()
        return ' '.join([part] * int(repeat))

    return re.sub(r'\b(.+)\*(\d+)\b', replace, s)

class SendRecv(Static):
    
    DEFAULT_CSS = '''
    SendRecv {
        layout: vertical;
        
        .title {
            width: 100%;
            text-align: center;
        }
        
        .main {
            layout: grid;
            grid-size: 5;
            grid-columns: auto auto auto 1fr;
            grid-gutter: 0 1;
            width: 100%;
            height: auto;
            
            .command-input {
                min-width: 10;
                width: 10;
                max-width: 10;
            }
            
            SlimTextArea {
                min-height: 2;
                height: 2;
            }
            
            Button {
                row-span: 2;
            }
            
            .status-output {
                display: block;
                &.busy {
                    display: none;
                }
            }
            
            LoadingIndicator {
                display: none;
                &.busy {
                    display: block;
                }
            }
        }
    }
    '''
    
    device = reactive(Device)
    status = reactive('')
    response = reactive('')
    busy = reactive(False)
    
    def compose(self) -> ComposeResult:
        yield Label('Send command', classes='title')
        with Container(classes='main'):
            yield Label('Command:')
            yield SlimInput(placeholder='0082', classes='command-input')
            yield Label('Argument:')
            yield SlimTextArea(classes='argument-input')
            yield Button('Send', 'primary', classes='send')
            yield Label('Status:')
            with Container(classes='main'):
                yield SlimInput(disabled=True, classes='status-output').data_bind(value=SendRecv.status)
                yield LoadingIndicator()
            yield Label('Response:')
            yield SlimTextArea(disabled=True, classes='response-output')

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class('send'):
            command_input = self.query_one('.command-input', SlimInput).value
            argument_input = self.query_one('.argument-input', SlimTextArea).text
            try:
                command = bytes.fromhex(command_input)
                argument = bytes.fromhex(transform_string(argument_input))
                r = pt.Report.new(command[0], command[1], len(argument))
                r.arguments[:len(argument)] = argument
            except (ValueError, IndexError) as e:
                self.status = 'Fail'
                self.response = f'Input error: {e}'
                return
            self.busy = True
            try:
                rr = await async_wrapper(lambda: self.device.send_recv(r))
            except pt.RazerException as e:
                rr = e.args[1]
            self.busy = False
            self.status = rr.status.name
            self.response = bytes(rr.arguments)[:rr.data_size].hex(' ')
    
    def watch_response(self, s: str) -> None:
        self.query_one('.response-output', SlimTextArea).text = s
    
    def watch_busy(self, b: bool) -> None:
        if b:
            self.query_one('.status-output', SlimInput).add_class('busy')
            self.query_one('LoadingIndicator', LoadingIndicator).add_class('busy')
        else:
            self.query_one('.status-output', SlimInput).remove_class('busy')
            self.query_one('LoadingIndicator', LoadingIndicator).remove_class('busy')