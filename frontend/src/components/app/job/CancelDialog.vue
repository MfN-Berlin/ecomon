<script setup lang="ts">
import { computed } from "vue";

const store = useJobsStore();

// Proper computed property with get/set for v-model
const showDialog = computed({
  get() {
    return store.currentCancelJobId !== null;
  },
  set(value: boolean) {
    if (!value) {
      store.currentCancelJobId = null;
    }
  }
});
const { mutate: cancelJob, isPending } = useCancelJob();
const { $toast } = useNuxtApp();

// Add computed jobId for template reference
const jobId = computed(() => store.currentCancelJobId);

async function handleConfirmCancel() {
  const res = await cancelJob({ jobId: jobId.value! });
  if (!res?.success) {
    $toast.error(`Failed to cancel job ${jobId.value}`);
  }
  showDialog.value = false;
}
</script>

<template>
  <v-dialog v-model="showDialog" width="400">
    <v-card>
      <v-card-title class="text-h6"> Confirm Job Cancellation </v-card-title>
      <v-card-text>
        Are you sure you want to cancel this synchronization job?
        <div v-if="jobId" class="text-caption mt-2">Job ID: {{ jobId }}</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="text" :disabled="isPending" @click="showDialog = false">
          Cancel
        </v-btn>
        <v-btn
          color="error"
          variant="flat"
          :loading="isPending"
          :disabled="isPending"
          @click="handleConfirmCancel"
        >
          Confirm
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
