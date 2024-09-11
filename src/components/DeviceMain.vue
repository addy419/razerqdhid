<script setup lang="ts">
import { inject } from 'vue';
import type { Ref } from 'vue';
import MouseInfo from './MouseInfo.vue';
const runPython = inject<Ref<Function | null>>('runPython');

</script>
<template>
  <h1>Razer Basilisk V3 Tools</h1>
  <div v-if="!runPython">Python is not loaded</div>
  <div v-else>
    <Suspense>
      <MouseInfo :py="runPython" />
      <template #fallback>
        <div>Loading...</div>
      </template>
    </Suspense>
  </div>
</template>