<script setup lang="ts">
import { computed, ref } from 'vue';

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

const buttonsLayout = [
  'aim', 'left', 'middle', 'right',
  'forward', 'wheel_up', 'middle_forward', 'wheel_left',
  'backward', 'wheel_down', 'middle_backward', 'wheel_right',
  'bottom'
];

const selectedButton = ref('left');
const hypershift = ref(false);

const buttonFunctionMap: any = {};
for (let hs of [true, false]) {
  for (let b of buttonsLayout) {
    buttonFunctionMap[b + (hs ? '_hypershift' : '')] = bridge(b + (hs ? '_hypershift' : ''), ['', {}],
`
def f(profile, button, hypershift):
  bf = device.get_button_function(
    pt.Button[button.upper()],
    pt.Hypershift.ON if hypershift else pt.Hypershift.OFF,
    %p)
  st = bf.get_subtype()
  if st == 'mouse':
    m = bf.get_mouse()
    if 'fn' in m:
      m['fn'] = m['fn'].name.lower()
    return st, m
  elif st == 'keyboard':
    m = bf.get_keyboard()
    if 'modifier' in m:
      m['modifier'] = [x.name.lower() for x in list(m['modifier'])]
    return st, m
  elif st == 'macro':
    m = bf.get_macro()
    if 'mode' in m:
      m['mode'] = m['mode'].name.lower()
    return st, m
  elif st == 'system':
    m = bf.get_system()
    if 'fn' in m:
      m['fn'] = [x.name.lower() for x in list(m['fn'])]
    return st, m
  elif st == 'dpi_switch':
    m = bf.get_dpi_switch()
    if 'fn' in m:
      m['fn'] = m['fn'].name.lower()
    return st, m
  else:
    return st, getattr(bf, 'get_' + st)()
f(profile, button, hypershift)
`, () => ({button: b, hypershift: hs}),
`
from functools import reduce
def f(profile, button, hypershift, value):
  st = value[0]
  m = value[1]
  if st == 'mouse':
    if 'fn' in m:
      m['fn'] = pt.FnMouse[m['fn'].upper()]
  elif st == 'keyboard':
    if 'modifier' in m:
      m['modifier'] = reduce(lambda x, y: x | y, [pt.FnKeyboardModifier[x.upper()] for x in list(m['modifier'])])
  elif st == 'macro':
    if 'mode' in m:
      m['mode'] = pt.FnClass[m['mode'].upper()]
  elif st == 'system':
    if 'fn' in m:
      m['fn'] = reduce(lambda x, y: x | y, [pt.FnSystem[x.upper()] for x in list(m['fn'])])
  elif st == 'dpi_switch':
    if 'fn' in m:
      m['fn'] = pt.FnDpiSwitch[m['fn'].upper()]
    if 'dpi' in m:
      m['dpi'] = [int(x) for x in m['dpi']]
  bf = pt.ButtonFunction()
  getattr(bf, 'set_' + st)(**m)
  device.set_button_function(bf,
    pt.Button[button.upper()],
    pt.Hypershift.ON if hypershift else pt.Hypershift.OFF,
    %p)
f(profile, button, hypershift, value)
`, (value) => {
  return {button: b, hypershift: hs, value: value};
},
    );
  }
}

</script>
<template>
  <div class="form-control">
    <h2>Button</h2>
    <div class="flex flex-row items-baseline">
      <div class="grid grid-cols-4">
        <button class="btn btn-sm text-xs join-item"
          :class="{'btn-active': selectedButton === b, 'btn-accent': hypershift}"
          v-for="b in buttonsLayout"
          @click="selectedButton = b">{{ b }}</button>
      </div>
    </div>
    <div class="grid grid-cols-2 place-items-baseline">
      <span>Hypershift</span>
      <label class="label cursor-pointer space-x-4">
        <input type="checkbox" class="toggle toggle-sm" v-model="hypershift"/>
      </label>
    </div>
    {{ buttonFunctionMap.aim.value[1].dpi[1] }}
    <button @click="buttonFunctionMap.aim.value[1].dpi[1] = 1200 - buttonFunctionMap.aim.value[1].dpi[1]">test sub</button>
  </div>
</template>
<style lang="scss" scoped>
</style>