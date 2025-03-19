<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();

const { data: modelList } = useModelList();
const selectedModel = ref<number | null>(null);
const startDateTime = ref<Date | null>(null);
const endDateTime = ref<Date | null>(null);

const selectedStartDateTime = ref<string>("2025-03-19 12:00:00");

const dialog = ref(false);
</script>

<template>
  <v-card :class="$attrs.class">
    <v-card-title>Model Controls</v-card-title>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn prepend-icon="mdi-plus" color="primary" variant="tonal" @click="dialog = true"
        >Start Inference</v-btn
      >
    </v-card-actions>
    <v-card-text>
      <CommonDateTimePicker v-model="selectedStartDateTime" label="Start Date Time" />
      <v-list>
        <v-list-item v-for="model in modelList" :key="model.id">
          <v-list-item-title>{{ model.name }}</v-list-item-title>
          <v-list-item-action> </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>Start Inference</v-card-title>
      <v-card-text>
        <v-select
          v-model="selectedModel"
          :items="modelList"
          item-title="name"
          item-value="id"
          label="Model"
        />
      </v-card-text>
      <v-card-actions></v-card-actions>
    </v-card>
  </v-dialog>
</template>
