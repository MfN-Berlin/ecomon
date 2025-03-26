<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
  siteName: string;
}>();
const open = ref(false);
const { data: logs, refetch } = useGetSiteJobsByTopic({
  siteId: props.siteId,
  _or: [{ topic: { _eq: "scan_directories" } }, { topic: { _eq: "delete_records_from_site" } }]
});

watch(open, (val) => {
  if (val) {
    refetch();
  }
});
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-cards-outline">
    Create Voucher
    <v-dialog v-model="open" width="auto" max-width="800px" class="h-75" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-cards-outline"></v-icon>
          <v-toolbar-title>Create Voucher for {{ siteName }}</v-toolbar-title>
        </v-toolbar>
        <v-card-text class="h-75 overflow-y-auto">
          <v-select
            v-model="selectedModel"
            prepend-inner-icon="mdi-brain"
            :items="modelList"
            item-title="name"
            item-value="id"
            label="Model"
            :loading="modelListLoading" />

          <CommonYearSelectBar
            class="mb-4"
            :start-date="firstRecordDate"
            :end-date="lastRecordDate"
            @select="selectYear" />

          <CommonDateTimePicker
            v-model="selectedStartDateTime"
            icon="mdi-calendar-start"
            prepend-inner-icon="mdi-calendar-start"
            dialog-title="Select Start Timestamp"
            label="Start Timestamp" />

          <CommonDateTimePicker
            v-model="selectedEndDateTime"
            icon="mdi-calendar-end"
            prepend-inner-icon="mdi-calendar-end"
            dialog-title="Select End Timestamp"
            label="End Timestamp"
        /></v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
