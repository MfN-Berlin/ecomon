<script setup lang="ts">
import { useField, useForm, useIsFormDirty } from "vee-validate";

import schema, { type Location } from "./schema";
import type { FormProps, WithId } from "@/utils/generic-types";

const {
  data,
  cancelLabel = "cancel",
  okLabel = "submit",
  loading = false
} = defineProps<FormProps<Location>>();
const emit = defineEmits<{
  (e: "submit", payload: WithId<Location>): void;
  (e: "reset"): void;
}>();
const { handleSubmit, handleReset, resetForm } = useForm({
  validationSchema: schema
});

const dirty = useIsFormDirty();

const { value: name, errorMessage: nameError } = useField<Location["name"]>("name");
const { value: remarks, errorMessage: remarksError } = useField<Location["remarks"]>("remarks");
const { value: lat, errorMessage: latError } = useField<Location["lat"]>("lat");
const { value: long, errorMessage: longError } = useField<Location["long"]>("long");

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
  console.log("propsUpdateForm", data);
  resetForm({
    values: {
      name: data?.name,
      remarks: data?.remarks,
      lat: data?.lat,
      long: data?.long
    }
  });
};

const markers = computed(() => {
  return data
    ? [
        {
          id: data.id!,
          lat: data.lat,
          long: data.long
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
    @submit="submit"
    @reset="handleReset"
  >
    <BaseMap :markers="markers" />
    <v-text-field v-model="name" :error-messages="nameError" label="Name" density="compact"></v-text-field>
    <v-textarea
      v-model="remarks"
      :error-messages="remarksError"
      label="Remarks"
      density="compact"
    ></v-textarea>
    <v-number-input
      v-model="lat"
      type="number"
      :precision="6"
      :error-messages="latError"
      label="Latitude"
      density="compact"
    ></v-number-input>
    <v-number-input
      v-model="long"
      type="number"
      :precision="6"
      :error-messages="longError"
      label="Longitude"
      density="compact"
    ></v-number-input>
  </BaseForm>
</template>

<style scoped>
.label {
  width: 60px; /* Adjust this value based on your preferred width */
}
</style>
