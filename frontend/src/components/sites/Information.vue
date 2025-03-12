<script setup lang="ts">
import type { GetSiteByIdQuery } from "#gql";


const { data } = defineProps<{
  data: SiteInformationProps;
}>();
const items = computed(() => [
  {
    icon: "mdi-calendar-start",
    title: "First Record",
    value: data.first_record || "N/A"
  },
  {
    icon: "mdi-calendar-end",
    title: "Last Record",
    value: data.last_record || "N/A"
  },
  {
    icon: "mdi-counter",
    title: "Record Count",
    value: data.record_count
  },
  {
    icon: "mdi-timer",
    title: "Records Duration",
    value: data.record_duration
  },
  {
    icon: "mdi-image-broken",
    title: "Corrupted Record Count",
    value: data.corrupted_record_count
  }
]);
</script>

<template>
  <v-sheet v-bind="$attrs">
    <v-list disabled>
      <v-list-subheader>REPORTS</v-list-subheader>

      <v-list-item v-for="(item, i) in items" :key="i">
        <template v-slot:prepend>
          <v-icon :icon="item.icon"></v-icon>
        </template>

        <v-list-item-title>{{ item.value }}</v-list-item-title>
        <v-list-item-subtitle>{{ item.title }}</v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-sheet>
</template>
