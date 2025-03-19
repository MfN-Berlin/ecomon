<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();

const { data: firstAndLastRecordDate, refetch } = useSiteGetFirstAndLastRecordDate(props.siteId);
const { data: modelList } = useModelList();
const selectedModel = ref<number | null>(null);
const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const dialog = ref(false);
watch(dialog, (val) => {
  if (val) {
    refetch();
  }
});
watch(firstAndLastRecordDate, (val) => {
  console.log("firstAndLastRecordDate", val);
  if (val && val.length > 0) {
    selectedStartDateTime.value = new Date(val[0].first_record_date);
    selectedEndDateTime.value = new Date(val[0].last_record_date);
  }
});
</script>

<template>
  <v-card :class="$attrs.class">
    <v-card-title color="">Model Controls</v-card-title>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn prepend-icon="mdi-plus" color="primary" variant="tonal" @click="dialog = true"
        >Start Inference</v-btn
      >
    </v-card-actions>
    <v-card-text>
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
      <v-toolbar color="primary">
        <v-toolbar-title>Start Inference</v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <v-select
          v-model="selectedModel"
          :items="modelList"
          item-title="name"
          item-value="id"
          label="Model"
        />
        <CommonDateTimePicker
          v-model="selectedStartDateTime"
          dialog-title="Select Start Timestamp"
          label="Start Timestamp"
        />
        <CommonDateTimePicker
          v-model="selectedEndDateTime"
          dialog-title="Select End Timestamp"
          label="End Timestamp"
        />
      </v-card-text>

      <v-card-actions>
        <v-btn text="cancel" min-width="100" @click="dialog = false"></v-btn>
        <v-btn text="ok" min-width="100" color="primary" variant="tonal"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
