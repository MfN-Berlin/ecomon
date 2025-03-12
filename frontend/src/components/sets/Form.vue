<script setup lang="ts">
import { useField, useForm, useIsFormDirty } from "vee-validate";

import schema, { type Set } from "./schema";
import type { FormProps, WithId } from "@/utils/generic-types";

const { data, cancelLabel = "cancel", okLabel = "submit", loading = false } = defineProps<FormProps<Set>>();
const emit = defineEmits<{
  (e: "submit", payload: WithId<Set>): void;
  (e: "reset"): void;
}>();
const { handleSubmit, handleReset, resetForm } = useForm({
  validationSchema: schema
});

const dirty = useIsFormDirty();

const { value: name, errorMessage: nameError } = useField<Set["name"]>("name");
const { value: remarks, errorMessage: remarksError } = useField<Set["remarks"]>("remarks");

// Add id to the values
const submit = handleSubmit((values) => emit("submit", { id: data!.id!, ...values }));

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
    @submit="
      () => {
        submit();
      }
    "
    @reset="handleReset"
  >
    <v-text-field v-model="name" :error-messages="nameError" label="Name" density="compact"></v-text-field>

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
