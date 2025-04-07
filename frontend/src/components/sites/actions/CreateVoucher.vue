<script lang="ts" setup>
import type { Label } from "@/composables/api/useModelLabelsList";

const props = defineProps<{
  siteId: number;
  siteName: string;
}>();

const defaults = {
  padding: 5,
  filterFrequency: 100,
  applyFilter: true,
  samplePerSpecies: 10
};
const open = ref(false);

const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const selectedModelId = ref<number | null>(null);
const selectedLabels = ref<Label[]>([]);
const selectedAllLabels = ref<boolean>(false);
const selectedPadding = ref<number>(defaults.padding);
const selectedApplyFilter = ref<boolean>(defaults.applyFilter);
const selectedSamplePerSpecies = ref<number>(defaults.samplePerSpecies);
const selectedFilterFrequency = ref<number>(defaults.filterFrequency);

const { $dayjs } = useNuxtApp();
const { mutate, isPending: createVoucherSamplesPending } = useCreateVoucherSamples();

function createVoucher() {
  mutate({
    modelId: selectedModelId.value!,
    siteId: props.siteId,
    labelIds: selectedLabels.value.map((label) => label.id),
    sampleCount: selectedSamplePerSpecies.value,
    startDatetime: $dayjs(selectedStartDateTime.value).local().toISOString(),
    endDatetime: $dayjs(selectedEndDateTime.value).local().toISOString(),
    audioPaddingMs: selectedPadding.value,
    highPassFilterFrequencyHz: selectedFilterFrequency.value
  });
}
function reset() {
  console.log("reset");
  selectedPadding.value = defaults.padding;
  selectedApplyFilter.value = defaults.applyFilter;
  selectedSamplePerSpecies.value = defaults.samplePerSpecies;
  selectedFilterFrequency.value = defaults.filterFrequency;
}

onMounted(() => {
  reset();
});
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
              <common-audio-sample-options
                v-model:padding="selectedPadding"
                v-model:filter-frequency="selectedFilterFrequency"
                v-model:apply-filter="selectedApplyFilter"
                variant="outlined"
              />

              <v-number-input
                v-model="selectedSamplePerSpecies"
                class="mt-4"
                reverse
                controlVariant="stacked"
                label="Sample per Species"
                density="compact"
                :hideInput="false"
                :inset="false"
              ></v-number-input>
            </v-col>
            <v-col cols="12" md="6">
              <data-model-labels-select
                v-model:selected-labels="selectedLabels"
                v-model:select-all="selectedAllLabels"
                :model-id="selectedModelId"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
          <v-btn
            color="primary"
            :loading="createVoucherSamplesPending"
            :disabled="
              !((selectedModelId !== null || selectedModelId !== undefined) && selectedLabels.length > 0)
            "
            @click="createVoucher"
            >Create Voucher</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
