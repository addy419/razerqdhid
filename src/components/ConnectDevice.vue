<script setup lang="ts">
import { ref, inject, computed } from 'vue';
import type { Ref } from 'vue';
import PythonRunner from './PythonRunner.vue';
const emit = defineEmits(['deviceCreated', 'deviceNotCreated']);
const runPython = inject<Ref<Function | null>>('runPython');

const customPath = ref(null);

async function requestDevice(){
  if (!runPython?.value) {
    return;
  }
  await runPython.value(`
    import hid
    hid.set_await_js(await_js)
    from basilisk_v3.device import BasiliskV3Device
    globals()['original_sr_with'] = BasiliskV3Device.sr_with
    def sr_with(self, *args, **kwargs):
        print(f's: {hex(args[0])} {args[1:]}, {kwargs}')
        r = original_sr_with(self, *args, **kwargs)
        print(f'r: {r}')
        return r
    BasiliskV3Device.sr_with = sr_with
    import qdrazer.protocol as pt
    device = BasiliskV3Device()
    if custom_path is not None:
      hid.enumerate()
    device.connect(path=custom_path)
    print('device created', device.get_serial())
  `, {add: {custom_path: customPath.value}});
  emit('deviceCreated');
}
async function noHardwareMode(){
  if (!runPython?.value) {
    return;
  }
  await runPython.value(`
    import hid
    hid.set_await_js(await_js)
    import qdrazer.protocol as pt
    print('no hardware mode')
  `);
  emit('deviceNotCreated');
}

function hasHid(){
  return Boolean(navigator.hid);
}

const customVid = ref(0);
const customPid = ref(0);

async function setCustomVidPid() {
  await runPython.value(`
    from basilisk_v3.device import BasiliskV3Device
    BasiliskV3Device.vid = int(vid)
    BasiliskV3Device.pid = int(pid)
  `, {locals: {vid: customVid.value, pid: customPid.value}});
}

const isPythonReady = computed(() => {
  return Boolean(runPython?.value);
});

</script>
<template>
  <div class="w-min-[30em] *:my-2">
    <h1>Razer Basilisk V3 Onboard Memory Tools</h1>
    <div>Browser must support WebHID to work, Click request and select device</div>
    <div>Select Razer Basilisk V3 or (1532:0099)</div>
    <div><a href="https://developer.mozilla.org/en-US/docs/Web/API/WebHID_API#browser_compatibility" class="link">You browser</a> <span class="bg-success text-success-content" v-if="hasHid()">probably supports WebHID</span><span class="bg-error text-error-content" v-else>does not support WebHID</span></div>
    <button class="btn btn-primary block w-96" @click="requestDevice" :class="{'btn-disabled': !isPythonReady}">Request</button>
    <button class="btn block w-96" @click="noHardwareMode" :class="{'btn-disabled': !isPythonReady}">No hardware mode</button>
    <div v-if="!isPythonReady"><span class="loading loading-spinner"></span><span>Loading python</span></div>
    <PythonRunner :py="runPython ?? (() => null)" />
    <details>
      <summary class="opacity-30">Custom VID/PID</summary>
      <div>
        <div>Do not change this if you don't know what you are doing</div>
        <div>It may damage your hardware if it's not a Basilisk V3</div>
        <div>VID: <input type="text" class="input input-bordered input-sm" @change="(event) => customVid = parseInt(event.target?.value) ?? 0"/></div>
        <div>PID: <input type="text" class="input input-bordered input-sm" @change="(event) => customPid = parseInt(event.target?.value) ?? 0"/></div>
        <button class="btn btn-sm btn-error" @click="setCustomVidPid">Set</button>
        <div>Custom path: <input type="text" class="input input-bordered input-sm" @change="(event) => customPath = JSON.parse(event.target?.value)"/></div>
      </div>
    </details>
  </div>
</template>