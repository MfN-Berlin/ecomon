<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();

const { mutate: startInference, isPending: startInferencePending } = useInferenceSiteTimespan();
const { $dayjs } = useNuxtApp();

const selectedModel = ref<number | null>(null);
const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const dialog = ref(false);

const config = useRuntimeConfig();
const isEditAllowed = computed(() => {
  const allowEdit = config.public.ALLOW_EDIT;
  return allowEdit === 'true' || allowEdit === true;
});

async function onStartInference() {
  await startInference({
    siteId: props.siteId,
    modelId: selectedModel.value!,
    startDatetime: $dayjs(selectedStartDateTime.value).local().format("YYYY-MM-DDTHH:mm:ss"),
    endDatetime: $dayjs(selectedEndDateTime.value).local().format("YYYY-MM-DDTHH:mm:ss")
  });
  dialog.value = false;
}
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-brain" :disabled="!isEditAllowed">
    Start Inference
    <v-dialog v-model="dialog" max-width="500" activator="parent">
      <v-card>
        <v-toolbar class="px-4" color="primary" icon="mdi-brain">
          <v-icon icon="mdi-brain"></v-icon>
          <v-toolbar-title>Start Inference</v-toolbar-title>
        </v-toolbar>

        <v-card-text>
          <data-model-select v-model="selectedModel" />
          <data-site-time-span-picker
            v-model:start-date-time="selectedStartDateTime"
            v-model:end-date-time="selectedEndDateTime"
            :site-id="props.siteId"
          />
        </v-card-text>

        <v-card-actions>
          <v-btn prepend-icon="mdi-close" min-width="100" @click="dialog = false">Cancel</v-btn>
          <v-btn
            min-width="100"
            color="primary"
            variant="tonal"
            prepend-icon="mdi-play"
            :disabled="selectedModel === null"
            :loading="startInferencePending"
            @click="onStartInference"
            >Start
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
