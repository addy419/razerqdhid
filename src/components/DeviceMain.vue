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
  <div class="profile">
    Profile:
    <button class="small" :class="{active: activeProfile === 'direct'}" :disabled="!hasProfile('direct')" @click="activeProfile = 'direct'">Direct</button>
    <button class="small" :class="{active: activeProfile === 'white'}" :disabled="!hasProfile('white')" @click="activeProfile = 'white'">White</button>
    <button class="small" :class="{active: activeProfile === 'red'}" :disabled="!hasProfile('red')" @click="activeProfile = 'red'">Red</button>
    <button class="small" :class="{active: activeProfile === 'green'}" :disabled="!hasProfile('green')" @click="activeProfile = 'green'">Green</button>
    <button class="small" :class="{active: activeProfile === 'blue'}" :disabled="!hasProfile('blue')" @click="activeProfile = 'blue'">Blue</button>
    <button class="small" :class="{active: activeProfile === 'cyan'}" :disabled="!hasProfile('cyan')" @click="activeProfile = 'cyan'">Cyan</button>
  </div>
  <main>
    <div class="menu">
      <button :class="{active: activeTab === 'basic'}" @click="activeTab = 'basic'">Basic</button>
      <button :class="{active: activeTab === 'info'}" @click="activeTab = 'info'">Info</button>
    </div>
    <div class="main">
      <div v-if="!runPython">Python is not loaded</div>
      <div v-else>
        <Suspense>
          <div>
            <BasicConfig v-if="activeTab === 'basic'" :py="runPython" :active-profile="activeProfile" />
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
<style lang="scss" scoped>
  button:hover, button.active {
    background-color: rgba(255, 255, 255, 0.5);
  }
  main {
    display: flex;
    flex-direction: row;
    .menu {
      flex-grow: 0;
      padding: 0.5em 0.5em;
      display: flex;
      flex-direction: column;
      & > button {
        padding: 0.5em 1em;
        background-color: rgba(255, 255, 255, 0.2);
        &:hover, &.active {
          background-color: rgba(255, 255, 255, 0.5);
        }
      }
    }
    .main {
      padding: 0.5em 0.5em;
    }
  }
</style>