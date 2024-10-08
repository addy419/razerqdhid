<script setup lang="ts">
import { ref, computed } from 'vue';

import { RunPython } from '../main';
import { BridgeData, BridgeStatus, makeBridge } from './bridge';

const props = defineProps<{
  py: RunPython;
  hard?: boolean; // should it interact with hardware or just dummy
  activeProfile: string;
}>();

const bridgeData = defineModel<BridgeData>('bridgeData', {default: {}});
const bridgeStatus = defineModel<BridgeStatus>('bridgeStatus', {default: {}});

const bridge = makeBridge(bridgeData, bridgeStatus, props);

const macroList = bridge<number[]>('macroList', [],
  'device.get_macro_list()', () => ({}),
  '', (value) => ({}),
);

const rr = ref();
async function getMacroFunction(macroId: number) {
  return await props.py(`
def macro_op_to_js(macro_op):
  import struct
  try:
    ct = macro_op.get_category()
    if ct == 'mouse_button':
      return ct, {'button': macro_op.get_mouse_button().name}
    it = getattr(macro_op, 'get_' + ct)()
    if not isinstance(it, dict):
      it = {'value': it}
    return ct, it
  except (IndexError, struct.error):
    return 'custom', {'op_type': macro_op.op_type.value, 'op_value': list(macro_op.op_value)}
[macro_op_to_js(x) for x in pt.MacroOp.list_from_bytes(device.get_macro_function(int(macro_id)))]
  `, {locals: {macro_id: macroId}});
}
async function setMacroFunction(macroId: number, func: object[]) {
  return await props.py(`
def f(macro_id, func):
  class DummyEnum:
    def __init__(self, value):
      self.value = value
  def js_to_macro_op(js):
    import struct
    ct, args = js
    if ct == 'custom':
      macro_op = pt.MacroOp(op_type=DummyEnum(args['op_type']), op_value=bytes(args['op_value']))
    elif ct == 'mouse_button':
      macro_op = pt.MacroOp().set_mouse_button(pt.MacroOpMouseButton[args['button']])
    else:
      macro_op = pt.MacroOp()
      if 'value' in args:
        getattr(macro_op, 'set_' + ct)(args['value'])
      else:
        getattr(macro_op, 'set_' + ct)(**args)
    return macro_op
  fn = pt.MacroOp.list_to_bytes([js_to_macro_op(js) for js in func])
  try:
    device.delete_macro(macro_id)
  except pt.RazerException:
    pass
  device.set_macro_function(macro_id, fn)
f(macro_id, func)
  `, {locals: {macro_id: macroId, func: func}});
}
async function deleteMacro(macroId: number) {
  return await props.py(`
device.delete_macro(macro_id)
  `, {locals: {macro_id: macroId}});
}

getMacroFunction(16570).then((r) => {rr.value = r;});
</script>
<template>
  <div>
    {{ macroList }}
    {{ rr }}
  </div>
</template>