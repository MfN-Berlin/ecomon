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

const { value: name, errorMessage: nameError } = useField("name");
const { value: short_name, errorMessage: short_nameError } = useField("short_name");
const { value: additional_docker_arguments, errorMessage: additional_docker_argumentsError } = useField(
  "additional_docker_arguments"
);
const { value: additional_model_arguments, errorMessage: additional_model_argumentsError } = useField(
  "additional_model_arguments"
);
const { value: window_size, errorMessage: window_sizeError } = useField("window_size");
const { value: step_size, errorMessage: step_sizeError } = useField("step_size");
const { value: remarks, errorMessage: remarksError } = useField("remarks");

const submit = handleSubmit((values) => emit("submit", { id: data?.id, ...values }));

watch(
  () => data,
  (newData, oldData) => {
    console.log("watch data", data);
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
      name: data?.name,
      short_name: data?.short_name,
      endpoint: data?.endpoint,
      remarks: data?.remarks
    }
  });
};
</script>
<template>
  <BaseForm
    :loading="loading"
    :dirty="dirty"
    :cancelLabel="cancelLabel"
    :okLabel="okLabel"
    :created_at="data?.created_at"
    :updated_at="data?.updated_at"
    @submit="submit"
    @reset="handleReset"
  >
    <v-text-field v-model="name" :error-messages="nameError" label="Name" density="compact"></v-text-field>
    <v-text-field
      v-model="short_name"
      :error-messages="short_nameError"
      label="Short Name"
      density="compact"
    ></v-text-field>
    <v-text-field
      v-model="additional_docker_arguments"
      :error-messages="additional_docker_argumentsError"
      label="Additional Docker Arguments"
      density="compact"
    ></v-text-field>
    <v-text-field
      v-model="additional_model_arguments"
      :error-messages="additional_model_argumentsError"
      label="Additional Model Arguments"
      density="compact"
    ></v-text-field>
    <v-number-input
      v-model="window_size"
      :error-messages="window_sizeError"
      label="Window Size"
      density="compact"
    ></v-number-input>
    <v-number-input
      v-model="step_size"
      :error-messages="step_sizeError"
      label="Step Size"
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
