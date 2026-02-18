<script setup lang="ts">
interface Props {
  selectedSpecies: any;
  minutesWithActivity: number | null;
  isLoadingMinutes: boolean;
  isMinutesError: boolean;
  threshold: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:threshold': [value: number]
  'create-voucher': []
}>();

const maxValueOption = ref('per_recording');
const sampleNumber = ref(100);

// Tooltip texts in English
const tooltipTexts = {
  per_recording: 'Default method: Simple and reliable for any recording length',
  per_minute: 'Ideal method but complex: Handles recordings by minute segments',
  per_signal: 'Advanced method: Ensures non-overlapping signals',
  all: 'For statistical sampling: Includes all values, not just the maximum',
  sample_number: 'Number of samples to draw from the selected recordings'
};
</script>

<template>
  <div>
    <!-- Threshold control -->
    <v-card class="page-controls v-theme--mfnLight mb-4" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
      <v-card-text>
        <div class="control-row horizontal align-inputs">
          <label for="threshold-input" class="label-inline text-right">Threshold</label>
          <div class="input-with-hint">
            <v-text-field
              id="threshold-input"
              :model-value="threshold"
              type="number"
              min="0"
              max="1"
              step="0.01"
              density="compact"
              class="threshold-input"
              @update:model-value="emit('update:threshold', $event)"
            ></v-text-field>
            <span class="hint-text">Range: 0.01 to 1.00</span>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Sampling Method control -->
    <v-card class="page-controls v-theme--mfnLight mb-4" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
      <v-card-text>
        <div class="control-row">
        <label class="label-inline">Sampling Method</label>
        <v-radio-group v-model="maxValueOption" inline class="radio-group-spacing" style="width: 750px">
          <div class="radio-option-container">
            <div class="radio-with-tooltip">
              <v-radio label="Per recording" value="per_recording"></v-radio>
              <v-tooltip
                :text="tooltipTexts.per_recording"
                location="top"
                open-delay="200"
                content-class="tooltip-content"
              >
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                </template>
              </v-tooltip>
            </div>
          </div>

          <div class="radio-option-container">
            <div class="radio-with-tooltip">
              <v-radio label="Per minute" value="per_minute" disabled></v-radio>
              <v-tooltip
                :text="tooltipTexts.per_minute"
                location="top"
                open-delay="200"
                content-class="tooltip-content"
              >
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                </template>
              </v-tooltip>
            </div>
          </div>

          <div class="radio-option-container">
            <div class="radio-with-tooltip">
              <v-radio label="Per signal" value="per_signal" disabled></v-radio>
              <v-tooltip
                :text="tooltipTexts.per_signal"
                location="top"
                open-delay="200"
                content-class="tooltip-content"
              >
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                </template>
              </v-tooltip>
            </div>
          </div>

          <div class="radio-option-container">
            <div class="radio-with-tooltip">
              <v-radio label="All values" value="all" disabled></v-radio>
              <v-tooltip
                :text="tooltipTexts.all"
                location="top"
                open-delay="200"
                content-class="tooltip-content"
              >
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                </template>
              </v-tooltip>
            </div>
          </div>
        </v-radio-group>
      </div>

      <!-- Sample Number Input -->
      <div class="control-row horizontal mt-4" style="width: 750px">
        <label class="label-inline text-right">Sample Number</label>
        <div class="input-with-tooltip">
          <v-text-field
            v-model.number="sampleNumber"
            type="number"
            min="1"
            :max="minutesWithActivity || 1000"
            density="compact"
            class="sample-number-input"
            hide-details
          ></v-text-field>
          <v-tooltip
            :text="tooltipTexts.sample_number"
            location="top"
            open-delay="300"
            content-class="tooltip-content"
          >
            <template v-slot:activator="{ props }">
              <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
            </template>
          </v-tooltip>
          <span class="hint-text activity-hint" style="min-width: 260px;">
            <template v-if="selectedSpecies">
              Available samples with activity:
              <template v-if="isLoadingMinutes">
                Loading...
              </template>
              <template v-else-if="isMinutesError">
                Error
              </template>
              <template v-else>
                {{ minutesWithActivity || 0 }}
              </template>
            </template>
          </span>
          <v-btn
            color="primary"
            size="small"
            class="ml-4"
            :disabled="!selectedSpecies || isLoadingMinutes"
            @click="emit('create-voucher', sampleNumber)"
          >
            Create voucher
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
  </div>
</template>

<style scoped>
/* Threshold input styling */
.threshold-input {
  width: 7em;
  max-width: 7em;
  flex-shrink: 0;
}

.threshold-input :deep(input) {
  text-align: center;
}

/* For horizontal layout controls (label + input + hint on same line) */
.control-row.horizontal {
  flex-direction: row;
  align-items: center;
}

.align-inputs {
  display: grid;
  grid-template-columns: 7em 1fr;
  align-items: center;
  gap: 0.75rem;
}

/* Right-align labels */
.text-right {
  text-align: right;
  margin-right: 0;
}

/* Input with hint on same line */
.input-with-hint {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 1rem;
}

.hint-text {
  color: rgba(0, 0, 0, 0.6);
  font-size: 0.75rem;
  white-space: nowrap;
}

.label-inline {
  margin-right: 1rem;
  margin-bottom: 0;
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}

/* radio buttons */
.control-row {
  display: flex;
  flex-direction: column;
}

.radio-group-spacing {
  margin-top: 0.25rem;
  position: relative;
}

.radio-group-spacing :deep(.v-selection-control-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.radio-option-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin-right: 1em;
}

.radio-with-tooltip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-icon {
  color: rgba(0, 0, 0, 0.4);
  cursor: help;
  opacity: 0.8;
  transition: opacity 0.2s ease;
  margin-bottom: 1px;
}

.info-icon:hover {
  opacity: 1;
  color: rgba(0, 0, 0, 0.6);
}

.tooltip-content {
  max-width: 300px;
  font-size: 0.8125rem;
  line-height: 1.4;
  background-color: rgba(70, 70, 70, 0.95);
  color: white;
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.v-radio :deep(.v-label) {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.87);
  margin-right: 0;
}

.v-radio:disabled :deep(.v-label) {
  color: rgba(0, 0, 0, 0.38);
  opacity: 1;
}

/* Sample Number Input Styles */
.control-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.control-row.horizontal {
  display: grid;
  grid-template-columns: 7em 1fr;
  align-items: center;
  gap: 0.75rem;
}

.sample-number-input {
  width: 100px;
  max-width: 100px;
}

.sample-number-input :deep(input) {
  text-align: center;
}

.input-with-tooltip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: fit-content;
}

.activity-hint {
  margin-left: 0.5rem;
  min-width: 220px;
  display: inline-block;
}

.label-inline {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}
</style>
