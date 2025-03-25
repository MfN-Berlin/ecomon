<script setup lang="ts">
import { nanoid } from "nanoid";
import { useField, useForm, useIsFormDirty } from "vee-validate";

import schema, { type Site } from "./schema";
import type { FormProps, WithId } from "@/utils/generic-types";

const { data, cancelLabel = "cancel", okLabel = "submit", loading = false } = defineProps<FormProps<Site>>();
const emit = defineEmits<{
  (e: "submit", payload: WithId<Site>): void;
  (e: "reset"): void;
}>();
const { handleSubmit, handleReset, resetForm } = useForm({
  validationSchema: schema
});

const dirty = useIsFormDirty();

const { value: name, errorMessage: nameError } = useField<Site["name"]>("name");
const { value: prefix, errorMessage: prefixError } = useField<Site["prefix"]>("prefix");
const { value: location_id, errorMessage: location_idError } = useField<Site["location_id"]>("location_id");
const { value: record_regime_recording_duration, errorMessage: record_regime_recording_durationError } =
  useField<Site["record_regime_recording_duration"]>("record_regime_recording_duration");
const { value: record_regime_pause_duration, errorMessage: record_regime_pause_durationError } = useField<
  Site["record_regime_pause_duration"]
>("record_regime_pause_duration");
const { value: sample_rate, errorMessage: sample_rateError } = useField<Site["sample_rate"]>("sample_rate");
const { value: remarks, errorMessage: remarksError } = useField<Site["remarks"]>("remarks");

// Add id to the values
const submit = handleSubmit((values) => emit("submit", { id: data?.id, ...values }));

const { data: locationList } = useLocationList();

watch(
  () => data,
  () => {
    propsUpdateForm();
  }
);

onMounted(() => {
  propsUpdateForm();
});

const propsUpdateForm = () => {
  resetForm({
    values: {
      name: data?.name,
      prefix: data?.prefix,
      location_id: data?.location_id,
      record_regime_recording_duration: data?.record_regime_recording_duration,
      record_regime_pause_duration: data?.record_regime_pause_duration,
      sample_rate: data?.sample_rate,
      remarks: data?.remarks
    }
  });
};

const markers = computed(() => {
  const loaction = locationList.value?.find((location) => location.id === location_id.value);
  return loaction
    ? [
        {
          id: data?.id || nanoid(),
          lat: loaction.lat,
          long: loaction.long
        }
      ]
    : [];
});
</script>

<template>
  <BaseForm
    :loading="loading"
    :dirty="dirty"
    :cancelLabel="cancelLabel"
    :okLabel="okLabel"
    :created_at="data?.created_at"
    :updated_at="data?.updated_at"
    @submit="
      () => {
        submit();
      }
    "
    @reset="handleReset"
  >
    <BaseMap :markers="markers" height="200px" />
    <v-text-field v-model="name" :error-messages="nameError" label="Name" density="compact"></v-text-field>
    <v-text-field
      v-model="prefix"
      :error-messages="prefixError"
      label="prefix"
      density="compact"
    ></v-text-field>

    <v-select
      v-model="location_id"
      :item-props="(location) => ({ value: location.id, title: location.name })"
      :items="locationList"
      label="Location"
      :error-messages="location_idError"
    ></v-select>
    <v-number-input
      v-model="record_regime_recording_duration"
      :error-messages="record_regime_recording_durationError"
      label="Recording Duration"
      density="compact"
    ></v-number-input>
    <v-number-input
      v-model="record_regime_pause_duration"
      :error-messages="record_regime_pause_durationError"
      label="Pause Duration"
      density="compact"
    ></v-number-input>
    <v-number-input
      v-model="sample_rate"
      :error-messages="sample_rateError"
      label="Sample Rate"
      density="compact"
    ></v-number-input>
    <v-textarea
      v-model="remarks"
      :error-messages="remarksError"
      label="Remarks"
      density="compact"
    ></v-textarea>
  </BaseForm>
</template>

<style scoped>
.label {
  width: 60px; /* Adjust this value based on your preferred width */
}
</style>
