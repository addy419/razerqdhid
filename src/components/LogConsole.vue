<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps<{
  messages: string[]
}>();

const consoleRef = ref<HTMLElement | null>(null);

const isAtBottom = (element: HTMLElement) => {
  return element.scrollTop > (element.scrollHeight - element.offsetHeight - 100);
};

onMounted(() => {
  const observer = new MutationObserver(() => {
    if (consoleRef.value && isAtBottom(consoleRef.value)) {
      consoleRef.value.scrollTop = consoleRef.value.scrollHeight;
    }
  });

  if (consoleRef.value) {
    observer.observe(consoleRef.value, { childList: true });
  }

  onBeforeUnmount(() => {
    observer.disconnect();
  });
});
</script>

<template>
  <ul class="console dark-bg" ref="consoleRef">
    <li v-for="(msg, index) in messages" :key="index">{{ msg }}</li>
  </ul>
</template>

<style lang="scss" scoped>
.console {
  height: 10em;
  padding: 1em;
  width: calc(100% - 4em);
  box-sizing: border-box;
  overflow-y: auto;
}
</style>