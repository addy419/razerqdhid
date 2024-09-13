<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  py: Function;
  hard?: boolean;
  activeProfile: string;
}>();
const scrollMode = defineModel<string>('scrollMode');
scrollMode.value = scrollMode.value ?? (await props.py(`device.get_scroll_mode(profile=pt.Profile.${props.activeProfile.toUpperCase()}).name`)).toLowerCase();
watch(scrollMode, (value) => { if (!props.hard || value === undefined) { return; } props.py(`device.set_scroll_mode(pt.ScrollMode.${value.toUpperCase()}, profile=pt.Profile.${props.activeProfile.toUpperCase()})`)});

</script>
<template>
  <div class="form-control">
    <h2>Scroll</h2>
    <label class="label cursor-pointer space-x-2">
      <span class="label-text">Tactile</span>
      <input type="checkbox" class="toggle toggle-sm" :checked="scrollMode == 'freespin'" @change="scrollMode = {tactile: 'freespin', freespin: 'tactile'}[scrollMode]" />
      <span class="label-text">Freespin</span>
    </label>

  </div>
</template>
<style lang="scss" scoped>

</style>