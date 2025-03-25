<script setup lang="ts">
const props = defineProps<{
  errors: {
    type: string;
    message: string;
  }[];
}>();
const ErrorTypeTitleMap = {
  [RECORD_ERRORS.FILE_READ_ERROR]: "File Read Error",
  [RECORD_ERRORS.MISSING_FILE_PREFIX]: "Missing or Wrong File Prefix",
  [RECORD_ERRORS.RECORD_DATETIME_FORMAT]: "Record Datetime Format",
  [RECORD_ERRORS.DURATION_MISSMATCH]: "Duration Missmatch",
  [RECORD_ERRORS.SAMPLERATE_MISSMATCH]: "Samplerate Missmatch"
};
const ErrorTypeIconMap = {
  [RECORD_ERRORS.FILE_READ_ERROR]: "mdi-document-alert",
  [RECORD_ERRORS.MISSING_FILE_PREFIX]: "mdi-form-textbox",
  [RECORD_ERRORS.RECORD_DATETIME_FORMAT]: "mdi-calendar-range",
  [RECORD_ERRORS.DURATION_MISSMATCH]: "mdi-clock",
  [RECORD_ERRORS.SAMPLERATE_MISSMATCH]: "mdi-music"
};
</script>
<template>
  <v-card v-bind="$attrs">
    <v-card-title>File Import Errors</v-card-title>
    <v-card-text>
      <v-list>
        <v-list-item v-for="error in props.errors" :key="error.type">
          <v-alert
            color="error"
            :text="error.message"
            :title="ErrorTypeTitleMap[error.type as keyof typeof ErrorTypeTitleMap]"
            :icon="ErrorTypeIconMap[error.type as keyof typeof ErrorTypeIconMap]"
          >
          </v-alert>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>
