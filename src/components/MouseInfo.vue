<script setup lang="ts">
import { filesize } from 'filesize';

const props = defineProps<{
  py: Function
}>();
const serial = await props.py(`device.get_serial().decode('utf-8')`);
const fwVersion = await props.py(`'.'.join(str(x) for x in device.get_firmware_version())`);
const flashUsage = await props.py(`device.get_flash_usage()`);
const [_, flashTotal, flashFree, flashRecycled] = flashUsage;

</script>
<template>
  <table><tbody>
    <tr><td colspan="2" class="subtitle">System</td></tr>
    <tr><td>Serial</td><td>{{ serial }}</td></tr>
    <tr><td>Firmware</td><td>{{ fwVersion }}</td></tr>
    <tr><td>Flash</td><td>
      <div>Total {{ filesize(flashTotal) }} ({{ flashTotal }})</div>
      <div>Free  {{ filesize(flashFree) }} ({{ flashFree }})</div>
      <div>Recycled  {{ filesize(flashRecycled) }} ({{ flashRecycled }})</div>
    </td></tr>
  </tbody></table>
  
</template>
<style lang="scss" scoped>
.subtitle {
  text-align: center;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.25em 0.5em;
}
</style>