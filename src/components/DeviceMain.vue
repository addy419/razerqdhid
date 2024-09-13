<script setup lang="ts">
import { inject, ref } from 'vue';
import type { Ref } from 'vue';
import MouseInfo from './MouseInfo.vue';
import BasicConfig from './BasicConfig.vue';
const runPython = inject<Ref<Function | null>>('runPython');
const activeProfile = ref('white');
const activeTab = ref('basics');
const hasProfileList = ref(['direct', 'white', 'red']);
function hasProfile(name: string) {
  return hasProfileList.value.indexOf(name) !== -1;
}
</script>
<template>
  <h1>Razer Basilisk V3 Tools</h1>
  <div>
    Profile:
    <button class="btn btn-sm rounded-none" :class="{active: activeProfile === 'direct'}" :disabled="!hasProfile('direct')" @click="activeProfile = 'direct'">Direct</button>
    <button class="btn btn-sm rounded-none" :class="{active: activeProfile === 'white'}" :disabled="!hasProfile('white')" @click="activeProfile = 'white'">White</button>
    <button class="btn btn-sm rounded-none" :class="{active: activeProfile === 'red'}" :disabled="!hasProfile('red')" @click="activeProfile = 'red'">Red</button>
    <button class="btn btn-sm rounded-none" :class="{active: activeProfile === 'green'}" :disabled="!hasProfile('green')" @click="activeProfile = 'green'">Green</button>
    <button class="btn btn-sm rounded-none" :class="{active: activeProfile === 'blue'}" :disabled="!hasProfile('blue')" @click="activeProfile = 'blue'">Blue</button>
    <button class="btn btn-sm rounded-none" :class="{active: activeProfile === 'cyan'}" :disabled="!hasProfile('cyan')" @click="activeProfile = 'cyan'">Cyan</button>
  </div>
  <main class="flex flex-row">
    <div class="flex flex-col">
      <button class="btn rounded-none" :class="{active: activeTab === 'basic'}" @click="activeTab = 'basic'">Basic</button>
      <button class="btn rounded-none" :class="{active: activeTab === 'info'}" @click="activeTab = 'info'">Info</button>
    </div>
    <div class="p-2">
      <div v-if="!runPython">Python is not loaded</div>
      <div v-else>
        <Suspense>
          <div>
            <BasicConfig v-if="activeTab === 'basic'" :py="runPython" :active-profile="activeProfile" hard />
            <MouseInfo v-if="activeTab === 'info'" :py="runPython" />
          </div>
          <template #fallback>
            <div>Loading...</div>
          </template>
        </Suspense>
      </div>
    </div>
  </main>
</template>
