<script setup lang="ts">
import type { GetSiteByIdQuery } from "#gql";

type SiteInformationProps = NonNullable<GetSiteByIdQuery["data"]>["site_directories"];
const { siteId, data } = defineProps<{
  siteId: number;
  data: SiteInformationProps;
}>();

const { mutate: deleteFn, isPending: deletePending } = useSiteDirectoryDelete();
const { mutate: addFn, isPending: addPending } = useSiteDirectoryInsert();

const showAddDialog = ref(false);
const { $activeJobs } = useNuxtApp();
const store = useJobsStore();

const currentJobs = computed(() => {
  return $activeJobs.value?.jobs.filter((job) => job.payload.site_id === siteId);
});

const activeJobInfo = computed(() => (directory: string) => {
  const job = currentJobs.value?.find(
    (job) => job.payload.directories.includes(directory) && ["running", "pending"].includes(job.status)
  );
  return job
    ? {
        id: job.id,
        status: job.status,
        progress: job.progress,
        isRunning: job.status === "running"
      }
    : null;
});

function handleDelete(id: number) {
  console.log("delete", id);
  deleteFn({ id });
}
function handleAllSync() {
  console.log("all sync");
}
function handleAdd() {
  showAddDialog.value = true;
}

function handleCancel(id: number) {
  console.log("cancel", id);
  store.cancelJob(id);
}

function handleSync(id: number) {
  console.log("sync", id);
}

function handleSubmit(path: string[]) {
  console.log("submit", path);
  showAddDialog.value = false;
  for (const p of path) {
    addFn({ directory: p, site_id: siteId });
  }
}
</script>

<template>
  <v-sheet v-bind="$attrs">
    <v-list>
      <v-list-subheader> DATA DIRECTORIES </v-list-subheader>
      <v-toolbar flat density="compact" class="w-100" color="surface">
        <v-spacer></v-spacer>
        <v-tooltip text="Sync All Directories">
          <template v-slot:activator="{ props }">
            <v-btn
              icon
              class="mr-2"
              density="compact"
              color="primary"
              variant="tonal"
              v-bind="props"
              @click="handleAllSync"
            >
              <v-icon>mdi-sync</v-icon>
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip text="Add New Directory">
          <template v-slot:activator="{ props }">
            <v-btn
              icon
              class="mr-4"
              density="compact"
              color="primary"
              variant="tonal"
              v-bind="props"
              :loading="addPending"
              @click="handleAdd"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
        </v-tooltip>
      </v-toolbar>
      <v-list-item v-for="(item, i) in data" :key="i">
        <v-list-item-title>{{ item.directory }}</v-list-item-title>
        <template #prepend>
          <v-icon>mdi-folder</v-icon>
        </template>
        <template #append>
          <v-tooltip text="Sync Directory">
            <template v-slot:activator="{ props }">
              <template v-if="activeJobInfo(item.directory)">
                <v-progress-circular
                  v-if="activeJobInfo(item.directory)?.isRunning"
                  :model-value="activeJobInfo(item.directory)?.progress || 0"
                  color="secondary"
                >
                  <v-btn
                    icon="mdi-cancel"
                    size="small"
                    variant="text"
                    v-bind="props"
                    @click="handleCancel(activeJobInfo(item.directory)?.id)"
                  />
                </v-progress-circular>
                <v-chip
                  v-else
                  small
                  :color="activeJobInfo(item.directory)?.status === 'completed' ? 'success' : 'error'"
                >
                  {{ activeJobInfo(item.directory)?.status }}
                </v-chip>
              </template>
              <v-btn
                v-else
                icon="mdi-sync"
                size="small"
                variant="text"
                v-bind="props"
                @click="handleSync(item.id)"
              />
            </template>
          </v-tooltip>

          <v-tooltip text="Delete Directory">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                v-bind="props"
                :disabled="activeJobInfo(item.directory)?.isRunning"
                @click="handleDelete(item.id)"
              />
            </template>
          </v-tooltip>
        </template>
      </v-list-item>
    </v-list>
  </v-sheet>
  <v-dialog v-model="showAddDialog" persistent max-width="500px">
    <sites-data-directory-browser @select="handleSubmit" @cancel="showAddDialog = false" />
  </v-dialog>
</template>
