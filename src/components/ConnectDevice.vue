<script setup lang="ts">
import { inject } from 'vue';
import type { Ref } from 'vue';
const emit = defineEmits(['deviceCreated', 'deviceNotCreated']);
const runPython = inject<Ref<Function | null>>('runPython');
async function requestDevice(){
  if (!runPython?.value) {
    return;
  }
  await runPython.value(`
    import hid
    hid.set_await_js(await_js)
    from basilisk_v3.device import BasiliskV3Device
    original_sr_with = BasiliskV3Device.sr_with
    def sr_with(self, *args, **kwargs):
        print(f's: {hex(args[0])} {args[1:]}, {kwargs}')
        r = original_sr_with(self, *args, **kwargs)
        print(f'r: {r}')
        return r
    BasiliskV3Device.sr_with = sr_with
    import qdrazer.protocol as pt
    device = BasiliskV3Device()
    device.connect()
    print('device created', device.get_serial())
  `);
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
  return new Boolean(navigator.hid);
}
</script>
<template>
  <div class="w-min-[30em] *:my-2">
    <h1>Razer Basilisk V3 Tools</h1>
    <div>Browser must support WebHID to work, Click request and select device</div>
    <div>You browser <span v-if="hasHid()">probably supports WebHID</span><span v-else>does not support WebHID</span></div>
    <button class="btn btn-primary block w-96" @click="requestDevice">Request</button>
    <button class="btn block w-96" @click="noHardwareMode">No hardware mode</button>
  </div>
</template>