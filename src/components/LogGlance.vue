<script setup lang="ts">
import { computed, ref } from 'vue';

const props = defineProps<{
  messages: [Date, string][]
}>();

const len = 19;
const msgLen = computed(() => props.messages.length);
const msgStart = computed(() => Math.floor(msgLen.value / len) * len);
// rolling
const indices = computed(() => {
  return [...Array(len).keys()].map((it) => msgStart.value + it).map((it) => it >= msgLen.value ? it - len : it);
})
</script>

<template>
  <div>
    <span v-for="i in indices" :class="{'even:bg-base-100 odd:bg-base-300': msgStart % 2 == 0, 'odd:bg-base-100 even:bg-base-300': msgStart % 2 == 1}">
      <span v-if="i < 0" class="inline-block w-8 px-1">..</span>
      <span v-else class="inline-block w-8 px-1"
        :class="{
          'bg-warn text-warn-content': messages[i][1].match(/\bwarn\b|\bwarning\b/ig),
          'bg-error text-error-content': messages[i][1].match(/\berror\b/ig),
          'bg-info text-info-content': i == msgLen - 1,
          'transition-colors': i < msgLen - 1
        }">{{ messages[i][1].slice(0, 2) }}</span>
    </span>
  </div>
</template>

<style lang="scss" scoped>
</style>