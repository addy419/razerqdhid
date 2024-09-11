<script setup lang="ts">
import { inject } from 'vue';
import type { Ref } from 'vue';
const emit = defineEmits(['deviceCreated']);
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
    device = BasiliskV3Device()
    device.connect()
    print('device created', device.get_serial())
  `);
  emit('deviceCreated');
}

function hasHid(){
  return new Boolean(navigator.hid);
}
</script>
<template>
  <h1>Razer Basilisk V3 Tools</h1>
  <div>Browser must support WebHID to work, Click request and select device</div>
  <div>You browser <span v-if="hasHid()">probably supports WebHID</span><span v-else>does not support WebHID</span></div>
  <button @click="requestDevice">Request</button>
</template>