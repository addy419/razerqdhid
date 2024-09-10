<script setup lang="ts">
import { inject } from 'vue';
import type { Ref } from 'vue';
const runPython = inject<Ref<Function | null>>('runPython');
async function foo(){
  if (!runPython?.value) {
    return;
  }
  console.log(await runPython.value(`
    import hid
    hid.set_await_js(await_js)
    from basilisk_v3.device import BasiliskV3Device
    d = BasiliskV3Device()
    d.connect()
    print(d.get_serial())
  `));
}
</script>

<template>
  <div>
    <a href="https://vitejs.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
    <button @click="foo">request</button>
    <button @click="enume">enum</button>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
