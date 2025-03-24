<script setup lang="ts">
const {
  loading = false,
  dirty = false,
  cancelLabel = "cancel",
  okLabel = "submit",
  created_at = "",
  updated_at = ""
} = defineProps<{
  loading: boolean;
  dirty: boolean;
  cancelLabel: string;
  okLabel: string;
  created_at?: string;
  updated_at?: string;
}>();

const emit = defineEmits<{
  (e: "submit" | "reset"): void;
}>();
</script>

<template>
  <v-form
    :disabled="loading"
    @submit.prevent="
      () => {
        emit('submit');
      }
    "
  >
    <v-card class="mx-auto" max-width="800">
      <v-card-text>
        <slot></slot>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :disabled="loading" @click="emit('reset')"> {{ cancelLabel }} </v-btn>
        <v-btn class="me-4" type="submit" color="primary" variant="tonal" :disabled="!dirty || loading">
          {{ okLabel }}
        </v-btn>
      </v-card-actions>
      <slot name="footer"></slot>
      <v-container v-if="created_at" fluid class="d-flex flex-column flex-sm-row">
        <div class="d-flex pr-2">
          <div class="text-caption label">Created:</div>
          <div class="text-caption">
            <common-date-time-text class="font-weight-bold" :time="created_at as string" />
          </div>
        </div>
        <div v-if="updated_at" class="d-flex">
          <div class="text-caption label">Updated:</div>
          <div class="text-caption">
            <common-date-time-text class="font-weight-bold" :time="updated_at as string" />
          </div>
        </div>
      </v-container>
      <v-progress-linear v-if="loading" indeterminate color="secondary" height="5" />
    </v-card>
  </v-form>
</template>
