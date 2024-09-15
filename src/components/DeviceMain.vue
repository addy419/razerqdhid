<script setup lang="ts">
import { inject, ref } from 'vue';
import type { Ref } from 'vue';
import MouseInfo from './MouseInfo.vue';
import BasicConfig from './BasicConfig.vue';
import type { RunPython } from '../main';
import ProfileConfig from './ProfileConfig.vue';
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
</script>
<template>
  <h1>Razer Basilisk V3 Tools</h1>
  <div>
    Profile:
    <button class="btn btn-sm rounded-none"
      v-for="p in allProfileList"
      :class="{'btn-active': activeProfile === p}" :disabled="!hasProfile(p)"
      @click="activeProfile = p">{{ p }}</button>
  </div>
  <main class="flex flex-row">
    <div class="flex flex-col">
      <button class="btn rounded-none" :class="{'btn-active': activeTab === 'basic'}" @click="activeTab = 'basic'; refreshKey++; ">Basic</button>
      <button class="btn rounded-none" :class="{'btn-active': activeTab === 'profile'}" @click="activeTab = 'profile'; refreshKey++; ">Profile</button>
      <button class="btn rounded-none" :class="{'btn-active': activeTab === 'info'}" @click="activeTab = 'info'; refreshKey++; ">Info</button>
    </div>
    <div class="w-md p-2">
      <div v-if="!runPython">Python is not loaded</div>
      <div v-else>
        <Suspense>
          <div>
            <BasicConfig v-if="activeTab === 'basic'"
              :key="refreshKey" :py="runPython" :active-profile="activeProfile" hard/>
            <MouseInfo v-if="activeTab === 'info'"
              :key="refreshKey" :py="runPython" />
            <ProfileConfig v-if="activeTab === 'profile'"
              :key="refreshKey" :py="runPython" @update="updateHasProfileList" />
          </div>
          <template #fallback>
            <div>Loading...</div>
          </template>
        </Suspense>
      </div>
    </div>
  </main>
</template>
