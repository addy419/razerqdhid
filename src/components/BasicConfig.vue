<script setup lang="ts">
import { computed, ModelRef, ref, watch } from 'vue';

import type { RunPython } from '../main';

const props = defineProps<{
  py: RunPython;
  hard?: boolean; // should it interact with hardware or just dummy
  activeProfile: string;
}>();

function bridge<T>(model: ModelRef<T>, getPy: string, getLocals: () => object, setPy: string, setLocals: (value: Exclude<T, undefined>) => object) {
  let modelRef = ref<T>(model.value); // necessary as model of Array doesn't update when assigned with index
  let noWriteOnce = false;
  let noUpdateOnce = false;
  watch(model, (value) => {
    if (noUpdateOnce) { noUpdateOnce = true; return; }
    modelRef.value = value;
  })
  const read = () => {
    if (props.hard) {
      props.py(getPy.replace('%p', 'profile=pt.Profile[profile]'), {
        locals: {profile: props.activeProfile.toUpperCase(), ...getLocals()}
      }).then((r) => {
        noWriteOnce = true;
        modelRef.value = r;
      });
    }
  };
  read();
  watch(() => props.activeProfile, read);
  let lastWrite: number | null = null;
  watch(modelRef, (value) => {
    noUpdateOnce = true;
    model.value = value; // sync outer value
    if (noWriteOnce) { noWriteOnce = false; return; }
    if (!props.hard || value === undefined) { return; }
    if (lastWrite) { clearTimeout(lastWrite); }
    lastWrite = setTimeout(() => { // rate limit the write operation
      lastWrite = null;
      props.py(setPy.replace('%p', 'profile=pt.Profile[profile]'), {
        locals: {profile: props.activeProfile.toUpperCase(), ...setLocals(value as Exclude<T, undefined>)}
      });
    }, 500);
  }, {deep: true});
  return modelRef;
}

const _scrollMode = defineModel<string>('scrollMode');
const scrollMode = bridge(_scrollMode,
  'device.get_scroll_mode(%p).name.lower()', () => ({}),
  'device.set_scroll_mode(pt.ScrollMode[x.upper()], %p)', (value) => ({x: value}),
);
const scrollModeToggle = computed({
  get: () => scrollMode.value === 'freespin',
  set: (value) => scrollMode.value = value ? 'freespin' : 'tactile'
});

const _scrollAcceleration = defineModel<boolean>('scrollAcceleration', {default: undefined});
const scrollAcceleration = bridge(_scrollAcceleration,
  'device.get_scroll_acceleration(%p)', () => ({}),
  'device.set_scroll_acceleration(x, %p)', (value) => ({x: value}),
);

const _scrollSmartReel = defineModel<boolean>('scrollSmartReel', {default: undefined});
const scrollSmartReel = bridge(_scrollSmartReel,
  'device.get_scroll_smart_reel(%p)', () => ({}),
  'device.set_scroll_smart_reel(x, %p)', (value) => ({x: value}),
);

const _pollingRate = defineModel<number>('pollingRate', {default: 1});
const pollingRate = bridge(_pollingRate,
  'device.get_polling_rate(%p)', () => ({}),
  'device.set_polling_rate(x, %p)', (value) => ({x: value}),
);
const pollingRateInput = computed({
  get: () => pollingRate.value?.toString(),
  set: (value) => {pollingRate.value = parseInt(value ?? '1')},
});
const pollingRateRange = computed({
  get: () => ({1:4, 2:3, 4:2, 8:1}[pollingRate.value ?? 0] ?? 0),
  set: (value) => {pollingRate.value = {4:1, 3:2, 2:4, 1:8, 0:16}[value] ?? 1},
});

const _dpiXy = defineModel('dpiXy', {default: [0, 0]});
const dpiXy = bridge(_dpiXy,
  'device.get_dpi_xy(%p)', () => ({}),
  'device.set_dpi_xy((x, y), %p)', (value) => ({x: value[0], y: value[1]}),
);

const _dpiStages = defineModel<[[number, number][], number]>('dpiStages', {default: [[], 0]});
const dpiStages = bridge(_dpiStages,
  'device.get_dpi_stages(%p)', () => ({}),
  'device.set_dpi_stages(ds, acs, %p)', (value) => ({ds: JSON.parse(JSON.stringify(value[0])), acs: value[1]}),
);

const dpiStageCount = computed({
  get: () => dpiStages.value?.[0].length ?? 0,
  set: (value) => {
    if (!dpiStages.value) { dpiStages.value = [Array.from({length: value}, () => [800, 800]), 1] }
    dpiStages.value[0] = dpiStages.value[0].slice(0, value);
    dpiStages.value[0] = dpiStages.value[0].concat(Array.from({length: value - dpiStages.value[0].length}, () => [800, 800]));
  }
});

function dpiCopyXY() {
  for (let it of dpiStages.value[0]) {
    it[1] = it[0];
  }
}

</script>
<template>
  <div class="form-control">
    <h2>Scroll</h2>
    <div class="grid grid-cols-2 place-items-baseline">
      <span>Wheel mode</span>
      <label class="label cursor-pointer space-x-4">
        <span class="label-text">Tactile</span>
        <input type="checkbox" class="toggle toggle-sm" v-model="scrollModeToggle"/>
        <span class="label-text">Freespin</span>
      </label>
      <span>Acceleration</span>
      <label class="label cursor-pointer space-x-4">
        <input type="checkbox" class="toggle toggle-sm" v-model="scrollAcceleration"/>
      </label>
      <span>Smart Reel</span>
      <label class="label cursor-pointer space-x-4">
        <input type="checkbox" class="toggle toggle-sm" v-model="scrollSmartReel"/>
      </label>
    </div>
    <h2>Polling rate</h2>
    <div class="flex flex-row gap-4">
      <input type="number" min="1" max="255" class="input input-sm input-bordered w-16" v-model="pollingRateInput"/> 
      <div class="flex-1">
        <input type="range" min="0" max="4" value="0" class="range" step="1" v-model="pollingRateRange" />
        <div class="input-label">
          <span>ms</span><span>125</span><span>250</span><span>500</span><span>1000</span>
        </div>
      </div>
      <span class="w-12">{{ (1000 / (pollingRate ?? 1)).toFixed(0) }}</span>
    </div>
    <h2>DPI</h2>
    <div class="grid grid-rows-2 grid-flow-col place-items-baseline justify-start">
      <span class="mx-2">X:</span>
      <span class="mx-2">Y:</span>
      <template v-for="(xy, index) in dpiStages[0]" :key="index">
        <input type="number" min="100" max="25600" step="100" class="input input-sm input-bordered rounded-none min-w-16" :class="{'input-primary': index + 1 == dpiStages[1]}" v-model="xy[0]"/>
        <input type="number" min="100" max="25600" step="100" class="input input-sm input-bordered rounded-none min-w-16" :class="{'input-primary': index + 1 == dpiStages[1]}" v-model="xy[1]"/>
      </template>
      <span></span>
      <span><button class="btn btn-sm" @click="dpiCopyXY">Y=X</button></span>
    </div>
    <div class="my-2 flex gap-2 place-items-baseline">
      <span class="flex-shrink-0">Stages: </span><input type="number" min="1" max="5" step="1" class="input input-sm input-bordered w-16" v-model="dpiStageCount"/>
      <span class="flex-shrink-0">Active: </span><input type="number" min="1" max="5" step="1" class="input input-sm input-bordered w-16" v-model="dpiStages[1]"/>
      <span class="flex-shrink-0">Current X:</span><input type="number" min="100" max="25600" step="100" class="input input-sm input-bordered rounded-none min-w-16" v-model.number="dpiXy[0]"/>
      <span class="flex-shrink-0">Y:</span><input type="number" min="100" max="25600" step="100" class="input input-sm input-bordered rounded-none min-w-16" v-model.number="dpiXy[1]"/>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.input-label {
  @apply flex w-full justify-between text-xs;
  span {
    @apply w-6 inline-flex justify-center;
  }
}
</style>