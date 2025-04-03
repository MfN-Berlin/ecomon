<script lang="ts" setup>
import type { Label } from "@/composables/api/useModelLabelsList";

const props = defineProps<{
  siteId: number;
  siteName: string;
}>();
const open = ref(false);

const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const selectedModelId = ref<number | null>(null);
const selectedlabels = ref<Label[]>([]);
const selectedAllLabels = ref<boolean>(false);
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-cards-outline">
    Create Voucher
    <v-dialog v-model="open" width="100%" max-width="1024px" class="h-75" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-cards-outline"></v-icon>
          <v-toolbar-title>Create Voucher for {{ siteName }}</v-toolbar-title>
        </v-toolbar>
        <v-card-text class="h-75 overflow-y-auto">
          <v-row>
            <v-col cols="12" md="6">
              <data-model-select v-model="selectedModelId" />

              <data-site-time-span-picker
                v-model:start-date-time="selectedStartDateTime"
                v-model:end-date-time="selectedEndDateTime"
                :site-id="siteId"
              />
            </v-col>
            <v-col cols="12" md="6">
              <data-model-labels-select
                v-model:selected-labels="selectedlabels"
                v-model:select-all="selectedAllLabels"
                :model-id="selectedModelId"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
