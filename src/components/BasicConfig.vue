<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Ref } from 'vue';

const props = defineProps<{
  py: Function,
  activeProfile: string
}>();
const scrollMode: Ref<string> = ref((await props.py(`device.get_scroll_mode(profile=pt.Profile.${props.activeProfile.toUpperCase()}).name`)).toLowerCase());
watch(scrollMode, (value) => {props.py(`device.set_scroll_mode(pt.ScrollMode.${value.toUpperCase()}, profile=pt.Profile.${props.activeProfile.toUpperCase()})`)});

</script>
<template>
  你好
  <div>{{ scrollMode }}</div>
  <button @click="scrollMode = {tactile: 'freespin', freespin: 'tactile'}[scrollMode]"></button>
</template>
<style lang="scss" scoped>

</style>