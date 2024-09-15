<script setup lang="ts">
import { ref } from 'vue';
import type { RunPython } from '../main';
const props = defineProps<{
  py: RunPython;
}>();
const emit = defineEmits(['update']);

const allProfileList = ['direct', 'white', 'red', 'green', 'blue', 'cyan'];
const profileList = ref<string[]>([]);
const confirmDelete = ref<{ [key: string]: boolean }>(
  allProfileList.reduce((acc:{ [key: string]: boolean },curr)=> (acc[curr]=false,acc),{}));
  // all profile list as key, false as value
async function updateProfileList() {
  const newList = await props.py('[x.name.lower() for x in device.get_profile_list()]');
  profileList.value = newList;
  emit('update', newList);
}
updateProfileList();

async function newProfile(profile: string) {
  await props.py('device.new_profile(pt.Profile[profile.upper()])', {locals: {profile: profile}});
  await updateProfileList();
}

async function deleteProfile(profile: string) {
  confirmDelete.value[profile] = false;
  await props.py('device.delete_profile(pt.Profile[profile.upper()])', {locals: {profile: profile}});
  await updateProfileList();
}

</script>
<template>
  <div class="form-control">
    <h2>Profile</h2>
    <div class="grid grid-cols-4">
      <template v-for="p in allProfileList">
        <span :class="{'opacity-40': !profileList.includes(p), 'text-accent border-r-8': profileList.includes(p)}">{{ p }}</span>
        <button class="btn btn-sm min-w-24 btn-success"
          v-if="p != 'direct' && !profileList.includes(p)"
          @click="newProfile(p)">New</button>
        <button class="btn btn-sm min-w-24 btn-error"
          v-else-if="p != 'direct' && profileList.includes(p) && confirmDelete[p]"
          @click="deleteProfile(p)">Confirm</button>
        <button class="btn btn-sm min-w-24 btn-warning"
          v-else-if="p != 'direct' && profileList.includes(p)"
          @click="confirmDelete[p] = true">Delete</button>
        <span v-else></span>
        <button class="btn btn-sm" :disabled="!profileList.includes(p) && p != 'direct'" >Export</button>
        <button class="btn btn-sm" :disabled="!profileList.includes(p) && p != 'direct'" >Import</button>
      </template>
    </div>
  </div>
</template>