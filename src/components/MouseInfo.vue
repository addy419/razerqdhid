<script setup lang="ts">
const props = defineProps<{
  py: Function
}>();
const serial = await props.py(`device.get_serial().decode('utf-8')`);
const fwVersion = await props.py(`'.'.join(str(x) for x in device.get_firmware_version())`);
</script>
<template>
  <table><tbody>
    <tr><td>Serial</td><td>{{ serial }}</td></tr>
    <tr><td>Firmware</td><td>{{ fwVersion }}</td></tr>
  </tbody></table>
  
</template>