<script setup lang="ts">
definePageMeta({ layout: "default" });
const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useRecordGet(id);
const { mutate, isPending } = useRecordUpdate();
const deleteAction = useActionAndRoute({
  action: () => deleteMutate({ id: id.value }),
  gotoUrl: "/records"
});

import { saveAs } from "file-saver";
import { ref, computed } from "vue";

// Store inference results from child
const inferenceResults = ref<any[]>([]);

// Handler for results emitted from inference-results-table
function handleInferenceResults(results: any[]) {
  inferenceResults.value = results;
};

// Download inference results as CSV
function downloadInferenceCsv() {
  if (!inferenceResults.value.length) return;
  const keys = ["filepath", "datetime", "start_time", "end_time", "model", "label", "confidence"];
  const csvRows = [
    keys.join(","),
    ...inferenceResults.value.map(row => {
      const modelName = row.model?.name || ""; // Access model.name
      const labelName = row.label?.name || ""; // Access label.name
      const filePath = data.value?.filepath || "";
      const recordDateTime = data.value?.record_datetime || "";

      return [
        `"${String(filePath)}"`,
        `"${String(recordDateTime)}"`,
        `"${String(row.start_time ?? "")}"`,
        `"${String(row.end_time ?? "")}"`,
        `"${String(modelName)}"` ,
        `"${String(labelName)}"`,
        `"${String(row.confidence ?? "")}"`
      ].join(",");
    })
  ];
  const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8" });
  saveAs(blob, `inference_results_${id.value}.csv`);
}
// Download record data as CSV (optional, for completeness)
function downloadRecordCsv() {
  if (!data.value) return;
  const record = data.value;
  const keys = Object.keys(record);
  const csvRows = [
    keys.join(","),
    keys.map(k => `"${String(record[k] ?? "")}"`).join(",")
  ];
  const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8" });
  saveAs(blob, `record_${record.id}.csv`);
}

const confidence = 0.7; // Set your confidence threshold

</script>
<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="5">
        <records-form
          v-if="data"
          :loading="isFetching || isPending"
          :data="{
            id: data?.id,
            site_id: data?.site_id,
            filepath: data?.filepath,
            filename: data?.filename,
            record_datetime: data?.record_datetime,
            duration: data?.duration,
            channels: data?.channels,
            sample_rate: data?.sample_rate,
            mime_type: data?.mime_type,
            errors: data?.errors,
            created_at: data?.created_at,
            updated_at: data?.updated_at
          }"
          :readonly="true"
          @delete="deleteAction"
          @submit="
            (data) => {
              const payload = { ...data };
              delete payload.id;
              mutate(payload);
            }
          "
        ></records-form>
        <records-errors
          v-if="data?.errors && data.errors.length > 0"
          :errors="data.errors"
          class="mx-auto mt-4"
          max-width="800"
        />
      </v-col>
      <v-col cols="12" md="7">
        <v-btn
          class="mb-2"
          color="primary"
          prepend-icon="mdi-download"
          @click="downloadInferenceCsv"
          :disabled="!inferenceResults.length"
        >
          Download Inference Results >= {{confidence}}
        </v-btn>
        <inference-results-table
          :record-id="id"
          @update:results="handleInferenceResults"
          :confidence="confidence"
        />
      </v-col>
    </v-row>
  </v-container>
</template>