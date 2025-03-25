<script setup lang="ts">
import { useField, useForm, useIsFormDirty } from "vee-validate";

import schema, { type Model } from "./schema";
import type { FormProps, WithId } from "@/utils/generic-types";

const { data, cancelLabel = "cancel", okLabel = "submit", loading = false } = defineProps<FormProps<Model>>();

const emit = defineEmits<{
  (e: "submit", payload: WithId<Model>): void;
  (e: "reset"): void;
}>();
const { handleSubmit, handleReset, resetForm } = useForm({
  validationSchema: schema
});

const dirty = useIsFormDirty();

const { value: site_id, errorMessage: site_idError } = useField("site_id");
const { value: filepath, errorMessage: filepathError } = useField("filepath");
const { value: filename, errorMessage: filenameError } = useField("filename");
const { value: record_datetime, errorMessage: record_datetimeError } = useField("record_datetime");
const { value: duration, errorMessage: durationError } = useField("duration");
const { value: channels, errorMessage: channelsError } = useField("channels");
const { value: sample_rate, errorMessage: sample_rateError } = useField("sample_rate");
const { value: mime_type, errorMessage: mime_typeError } = useField("mime_type");

const submit = handleSubmit((values) => emit("submit", { id: data?.id, ...values }));

const config = useRuntimeConfig();

watch(
  () => data,
  (newData, oldData) => {
    if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
      propsUpdateForm();
    }
  }
);

onMounted(() => {
  console.log("onMounted");
  propsUpdateForm();
});
const propsUpdateForm = () => {
  resetForm({
    values: {
      site_id: data?.site_id,
      filepath: data?.filepath,
      filename: data?.filename,
      record_datetime: data?.record_datetime,
      duration: data?.duration,
      channels: data?.channels,
      sample_rate: data?.sample_rate,
      mime_type: data?.mime_type,
      errors: data?.errors
    }
  });
};
</script>
<template>
  <BaseForm
    v-bind="$attrs"
    :loading="loading"
    :dirty="dirty"
    :cancelLabel="cancelLabel"
    :okLabel="okLabel"
    :created_at="data?.created_at"
    :updated_at="data?.updated_at"
    :hideActions="true"
    @submit="submit"
    @reset="handleReset"
  >
    <v-text-field
      v-model="site_id"
      :error-messages="site_idError"
      label="Site ID"
      density="compact"
    ></v-text-field>

    <v-text-field
      v-model="filepath"
      :error-messages="filepathError"
      label="Filepath"
      density="compact"
    ></v-text-field>
    <v-text-field
      v-model="filename"
      :error-messages="filenameError"
      label="Filename"
      density="compact"
    ></v-text-field>
    <common-date-time-picker
      v-model="record_datetime"
      :error-messages="record_datetimeError"
      label="Record Datetime"
      density="compact"
    ></common-date-time-picker>
    <v-text-field
      v-model="duration"
      :error-messages="durationError"
      label="Duration"
      density="compact"
    ></v-text-field>
    <v-text-field
      v-model="channels"
      :error-messages="channelsError"
      label="Channels"
      density="compact"
    ></v-text-field>
    <v-number-input
      v-model="sample_rate"
      :error-messages="sample_rateError"
      label="Sample Rate"
      density="compact"
    ></v-number-input>
    <v-text-field
      v-model="mime_type"
      :error-messages="mime_typeError"
      label="Mime Type"
      density="compact"
    ></v-text-field>
    <v-container class="d-flex justify-center">
      <common-play-button :src="`${config.public.API_BASE_URL}/static/files/${data?.filepath}`" />
    </v-container>
  </BaseForm>
</template>
<style scoped>
.label {
  width: 60px; /* Adjust this value based on your preferred width */
}
</style>
