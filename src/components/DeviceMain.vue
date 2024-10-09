<script setup lang="ts">
import { inject, ref, computed } from 'vue';
import type { Ref } from 'vue';
import MouseInfo from './MouseInfo.vue';
import BasicConfig from './BasicConfig.vue';
import type { RunPython } from '../main';
import ProfileConfig from './ProfileConfig.vue';
import ButtonConfig from './ButtonConfig.vue';
import MacroConfig from './MacroConfig.vue';
const allProfileList = ['direct', 'white', 'red', 'green', 'blue', 'cyan'];
const runPython = inject<Ref<RunPython | null>>('runPython');
const activeProfile = ref('direct');
const activeTab = ref('basic');
const refreshKey = ref(0);
const hasProfileList = ref(['direct', 'white']);
function hasProfile(name: string) {
  return hasProfileList.value.indexOf(name) !== -1;
}
function updateHasProfileList(value: string[]) {
  value = ['direct'].concat(value);
  hasProfileList.value = value;
  if (!value.includes(activeProfile.value)) {
    activeProfile.value = 'direct';
  }
}
const profileConfigData = ref({
  basic: {},
  button: {},
  macro: {},
});
const profileConfigStatus = ref({
  basic: {},
  button: {},
  macro: {},
});
const isConfigAllIdle = computed(() => {
  for (let [sectionName, sectionValue] of Object.entries(profileConfigStatus.value)) {
    for (let [name, status] of Object.entries(sectionValue)) {
      if (status !== 'idle') {
        return false;
      }
    }
  }
  return true;
});
const enableAllConfigSections = ref(false);


</script>
<template>
  <h1>Razer Basilisk V3 Tools</h1>
  <div>
    Profile:
    <div class="join">
      <button class="btn btn-sm join-item"
        v-for="p in allProfileList"
        :class="{'btn-active': activeProfile === p}" :disabled="!hasProfile(p)"
        @click="activeProfile = p">{{ p }}</button>
    </div>
    <span class="loading loading-spinner loading-sm" v-if="!isConfigAllIdle"></span>
  </div>
  <main class="flex flex-row">
    <div class="join join-vertical">
      <button class="btn join-item" :class="{'btn-active': activeTab === 'basic'}" @click="activeTab = 'basic'; refreshKey++; ">Basic</button>
      <button class="btn join-item" :class="{'btn-active': activeTab === 'button'}" @click="activeTab = 'button'; refreshKey++; ">Button</button>
      <button class="btn join-item" :class="{'btn-active': activeTab === 'macro'}" @click="activeTab = 'macro'; refreshKey++; ">Macro</button>
      <button class="btn join-item" :class="{'btn-active': activeTab === 'profile'}" @click="activeTab = 'profile'; refreshKey++; ">Profile</button>
      <button class="btn join-item" :class="{'btn-active': activeTab === 'info'}" @click="activeTab = 'info'; refreshKey++; ">Info</button>
    </div>
    <div class="w-md p-2">
      <div v-if="!runPython">Python is not loaded</div>
      <div v-else>
        <Suspense>
          <div>
            <BasicConfig v-if="activeTab === 'basic' || enableAllConfigSections" v-show="!enableAllConfigSections"
              :key="refreshKey" :py="runPython" :active-profile="activeProfile" hard
              v-model:bridge-data="profileConfigData.basic" v-model:bridge-status="profileConfigStatus.basic"/>
            <ButtonConfig v-if="activeTab === 'button' || enableAllConfigSections" v-show="!enableAllConfigSections"
              :key="refreshKey" :py="runPython" :active-profile="activeProfile" hard
              v-model:bridge-data="profileConfigData.button" v-model:bridge-status="profileConfigStatus.button"/>
            <MacroConfig v-if="activeTab === 'macro'"
              :key="refreshKey" :py="runPython" :active-profile="activeProfile" hard/>
            <MouseInfo v-if="activeTab === 'info'"
              :key="refreshKey" :py="runPython" />
            <!-- v-show is used to load available profiles when initially loaded -->
            <ProfileConfig v-show="activeTab === 'profile'"
              :key="refreshKey" :py="runPython" @update="updateHasProfileList"
              :is-config-all-idle="isConfigAllIdle"
              v-model:profile-config-data="profileConfigData" v-model:enable-all-config-sections="enableAllConfigSections"/>
          </div>
          <template #fallback>
            <div>Loading...</div>
          </template>
        </Suspense>
      </div>
    </div>
  </main>
</template>
