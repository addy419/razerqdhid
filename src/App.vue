<script setup lang="ts">
import { ref } from 'vue';
import ConnectDevice from './components/ConnectDevice.vue';
import DeviceMain from './components/DeviceMain.vue';
import LogConsole from './components/LogConsole.vue';

const hasDevice = ref(false);

const showConsole = ref(false);

const logs = ref([[new Date(), 'Here be logs']]);
function addLog(text: string) {
  logs.value.push([new Date(), text]);
}
var cl:Function, ce:Function, cw:Function;

if(window.console && console.log){
	cl = console.log;
	console.log = function(){
		addLog([...arguments].map(x => x.toString()).join(', '));
		cl.apply(this, arguments)
	}
}

if(window.console && console.warn){
	cw = console.warn;
	console.warn = function(){
		addLog(['Warn', ...arguments].map(x => x.toString()).join(', '));
		cw.apply(this, arguments)
	}
}

if(window.console && console.error){
	ce = console.error;
	console.error = function(){
	  addLog(['Error', ...arguments].map(x => x.toString()).join(', '));
		ce.apply(this, arguments)
	}
}

window.addEventListener("error", (event) => {
  console.error(`${event.type}: ${event.message}`);
});
window.addEventListener("unhandledrejection", (event) => {
  console.error(`${event.type}: ${event.reason}`);
});

</script>

<template>
  <div>
    <ConnectDevice v-if="!hasDevice" @device-created="hasDevice = true" />
    <DeviceMain v-else />
  </div>
  <footer>
    <button @click="showConsole = !showConsole">Console</button>
    <LogConsole v-show="showConsole" :messages="logs" />
  </footer>
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
footer {
  position: fixed;
  display: block;
  bottom: 0;
  padding: 1em 0;
  width: 100%;
}
</style>
