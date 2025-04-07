<script setup lang="ts">
const padding = defineModel<number>("padding", { required: true });
const filterFrequency = defineModel<number>("filterFrequency", { required: true });
const applyFilter = defineModel<boolean>("applyFilter", { required: true });
</script>
<template>
  <v-card v-bind="$attrs" subtitle="Audio Sample Options">
    <v-card-text>
      <v-number-input
        v-model="padding"
        reverse
        controlVariant="stacked"
        label="Padding in seconds"
        density="compact"
        :hideInput="false"
        :inset="false"
      ></v-number-input>
      <div class="d-flex ga-2">
        <v-number-input
          v-model="filterFrequency"
          reverse
          controlVariant="stacked"
          label="Filter Frequency"
          density="compact"
          :hideInput="false"
          :inset="false"
        />
        <v-switch v-model="applyFilter" color="primary" label="Apply Filter"></v-switch>
      </div>
    </v-card-text>
  </v-card>
</template>
