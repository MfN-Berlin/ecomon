<script setup lang="ts">
const props = defineProps<{
  rangeStartDateTime: Date;
  rangeEndDateTime: Date;
}>();

const selectedStartDateTime = defineModel<Date>("startDateTime");
const selectedEndDateTime = defineModel<Date>("endDateTime");

function selectYear(year: number) {
  selectedStartDateTime.value = new Date(`${year}-01-01`);
  selectedStartDateTime.value.setHours(0, 0, 0, 0);
  selectedEndDateTime.value = new Date(`${year}-12-31`);
  selectedEndDateTime.value.setHours(23, 59, 59, 999);
}
</script>
<template>
  <CommonYearSelectBar
    class="mb-4"
    :start-date="props.rangeStartDateTime"
    :end-date="props.rangeEndDateTime"
    @select="selectYear"
  />

  <CommonDateTimePicker
    v-model="selectedStartDateTime"
    icon="mdi-calendar-start"
    prepend-inner-icon="mdi-calendar-start"
    dialog-title="Select Start Timestamp"
    label="Start Timestamp"
  />

  <CommonDateTimePicker
    v-model="selectedEndDateTime"
    icon="mdi-calendar-end"
    prepend-inner-icon="mdi-calendar-end"
    dialog-title="Select End Timestamp"
    label="End Timestamp"
  />
</template>
