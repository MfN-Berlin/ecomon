<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
  siteName: string;
}>();
const open = ref(false);

const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const selectedModel = ref<number | null>(null);
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
          <data-model-select v-model="selectedModel" />
          <data-site-time-span-picker
            v-model:start-date-time="selectedStartDateTime"
            v-model:end-date-time="selectedEndDateTime"
            :site-id="siteId"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
