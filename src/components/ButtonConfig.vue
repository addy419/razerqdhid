<script setup lang="ts">
import { computed, ref } from 'vue';

import { RunPython } from '../main';
import { BridgeData, BridgeStatus, makeBridge } from './bridge';
import { hidKeyboardCode } from './hidcode';

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
const selectedHypershift = ref(false);

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
  ct = bf.get_category()
  if ct == 'mouse':
    m = bf.get_mouse()
    if 'fn' in m:
      m['fn'] = m['fn'].name.lower()
    return ct, m
  elif ct == 'keyboard':
    m = bf.get_keyboard()
    if 'modifier' in m:
      m['modifier'] = [x.name.lower() for x in list(m['modifier'])]
    return ct, m
  elif ct == 'macro':
    m = bf.get_macro()
    if 'mode' in m:
      m['mode'] = m['mode'].name.lower()
    return ct, m
  elif ct == 'system':
    m = bf.get_system()
    if 'fn' in m:
      m['fn'] = [x.name.lower() for x in list(m['fn'])]
    return ct, m
  elif ct == 'dpi_switch':
    m = bf.get_dpi_switch()
    if 'fn' in m:
      m['fn'] = m['fn'].name.lower()
    return ct, m
  else:
    return ct, getattr(bf, 'get_' + ct)()
f(profile, button, hypershift)
`, () => ({button: b, hypershift: hs}),
`
def f(profile, button, hypershift, value):
  from functools import reduce
  ct = value[0]
  m = value[1]
  if ct == 'mouse':
    if 'fn' in m:
      m['fn'] = pt.FnMouse[m['fn'].upper()]
  elif ct == 'keyboard':
    if 'modifier' in m:
      m['modifier'] = reduce((lambda x, y: x | y), [pt.FnKeyboardModifier[x.upper()] for x in list(m['modifier'])], pt.FnKeyboardModifier(0))
  elif ct == 'macro':
    if 'mode' in m:
      m['mode'] = pt.FnClass[m['mode'].upper()]
  elif ct == 'system':
    if 'fn' in m:
      m['fn'] = reduce((lambda x, y: x | y), [pt.FnSystem[x.upper()] for x in list(m['fn'])], pt.FnKeyboardModifier(0))
  elif ct == 'dpi_switch':
    if 'fn' in m:
      m['fn'] = pt.FnDpiSwitch[m['fn'].upper()]
    if 'dpi' in m:
      m['dpi'] = [int(x) for x in m['dpi']]
  bf = pt.ButtonFunction()
  getattr(bf, 'set_' + ct)(**m)
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
const functionCategoryList = [
  'disabled', 'mouse', 'keyboard', 'macro', 'dpi_switch', 'profile_switch',
  'system', 'consumer', 'hypershift_toggle', 'scroll_mode_toggle'
];

const selectedButtonFunction = computed({
  get: () => {
    if (selectedHypershift.value) {
      return buttonFunctionMap[selectedButton.value + '_hypershift'].value;
    }
    return buttonFunctionMap[selectedButton.value].value;
  },
  set: (value) => {
    if (selectedHypershift.value) {
      buttonFunctionMap[selectedButton.value + '_hypershift'].value = value;
    }
    buttonFunctionMap[selectedButton.value].value = value;
  }
});

const fnMouse = ['left', 'right', 'middle', 'backward', 'forward', 'wheel_up', 'wheel_down', 'wheel_left', 'wheel_right'];
const fnKeyboardModifier = ['left_control', 'left_shift', 'left_alt', 'left_gui', 'right_control', 'right_shift', 'right_alt', 'right_gui'];
function resetFunctionCategory(newCategory: string) {
  if (selectedButtonFunction.value[0] === newCategory) {
    return;
  }
  if (newCategory === 'disabled') {
    selectedButtonFunction.value = ['disabled', {}];
  } else if (newCategory === 'mouse') {
    selectedButtonFunction.value = ['mouse', {'fn': 'left', 'double_click': false, 'turbo': null}];
  } else if (newCategory === 'keyboard') {
    selectedButtonFunction.value = ['keyboard', {'key': 0x04, 'modifier': [], 'turbo': null}];
  }
}

function toggleKeyboardModifier(m: string) {
  if (selectedButtonFunction.value[1].modifier.includes(m)) {
    // included, remove
    const i = selectedButtonFunction.value[1].modifier.indexOf(m)
    selectedButtonFunction.value[1].modifier.splice(i, 1);
  } else {
    selectedButtonFunction.value[1].modifier.push(m);
  }
}

</script>
<template>
  <div class="form-control">
    <h2>Button</h2>
    <div class="flex flex-row items-baseline">
      <div class="grid grid-cols-4">
        <button class="btn btn-sm text-xs"
          :class="{'btn-active': selectedButton === b, 'btn-warning': selectedHypershift}"
          v-for="b in buttonsLayout"
          @click="selectedButton = b">{{ b }}</button>
      </div>
    </div>
    <div class="flex flex-row gap-4 place-items-center">
      <span>Hypershift</span>
      <label class="label cursor-pointer space-x-4">
        <input type="checkbox" class="toggle toggle-sm" v-model="selectedHypershift"/>
      </label>
    </div>
    <h2>Function</h2>
    <div class="grid grid-cols-4 items-baseline">
      <button class="btn btn-sm"
        v-for="b in functionCategoryList"
        :class="{'btn-active': selectedButtonFunction[0] === b}"
        @click="resetFunctionCategory(b)"
        >{{ b }}</button>
    </div>
    <div v-if="selectedButtonFunction[0] == 'disabled'">
      <span>Disabled</span>
    </div>
    <div v-else-if="selectedButtonFunction[0] == 'mouse'">
      <div class="flex flex-row gap-4 place-items-center">
        <span>Mouse button function</span>
        <select class="select w-full max-w-xs" v-model="selectedButtonFunction[1].fn">
          <option v-for="fn in fnMouse" :value="fn">{{ fn }}</option>
        </select>
      </div>
      <div class="flex flex-row gap-4 place-items-center">
        <label class="label cursor-pointer space-x-4">
          <input type="radio"
            :checked="selectedButtonFunction[1].turbo == null && !selectedButtonFunction[1].double_click"
            @change="selectedButtonFunction[1].turbo = null; selectedButtonFunction[1].double_click = false;" />
          <span>Single Click</span>
        </label>
      </div>
      <div class="flex flex-row gap-4 place-items-center">
        <label class="label cursor-pointer space-x-4">
          <input type="radio"
            :checked="selectedButtonFunction[1].double_click"
            @change="selectedButtonFunction[1].turbo = null; selectedButtonFunction[1].double_click = true;" />
          <span>Double Click</span>
        </label>
      </div>
      <div class="flex flex-row gap-4 place-items-center">
        <label class="label cursor-pointer space-x-4">
          <input type="radio"
            :checked="selectedButtonFunction[1].turbo != null"
            @change="selectedButtonFunction[1].turbo = 200; selectedButtonFunction[1].double_click = false;" />
          <span>Turbo</span>
        </label>
        <span>Trigger every</span>
        <input type="number" min="1" max="65535" class="input input-sm input-bordered w-24"
          :disabled="selectedButtonFunction[1].turbo == null"
          :value="selectedButtonFunction[1].turbo ?? 0"
          @change="(event) => {selectedButtonFunction[1].turbo = parseInt(event.target?.value) || 200}"/>
        <span>ms</span>
        <span>({{
          isFinite(1000 / selectedButtonFunction[1].turbo)
          ? (1000 / selectedButtonFunction[1].turbo).toFixed(1)
          : '-'
        }} times / s)</span>
      </div>
    </div>
    <div v-else-if="selectedButtonFunction[0] == 'keyboard'">
      <div class="flex flex-row gap-4 place-items-center">
        <span>Key: </span>
        <input type="number" min="0" max="255" class="input input-sm input-bordered w-24"
          :value="selectedButtonFunction[1].key ?? 0"
          @change="(event) => {selectedButtonFunction[1].key = parseInt(event.target?.value) || 0x04}"/>
        <select class="select w-full max-w-xs" v-model="selectedButtonFunction[1].key">
          <option v-for="[code, name] in Object.entries(hidKeyboardCode)" :value="parseInt(code)">{{ code }} {{ name }}</option>
        </select>
      </div>
      <span>Modifiers: </span>
      <div class="grid grid-cols-4 gap-2 place-items-center">
        <label class="label cursor-pointer space-x-4" v-for="m in fnKeyboardModifier">
          <input type="checkbox" class="checkbox checkbox-sm"
            :checked="selectedButtonFunction[1].modifier.includes(m)"
            @change="toggleKeyboardModifier(m)" />
          <span>{{ m }}</span>
        </label>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
</style>