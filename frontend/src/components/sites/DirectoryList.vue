<script setup lang="ts">
import type { GetSiteByIdQuery } from "#gql";

type SiteInformationProps = NonNullable<GetSiteByIdQuery["data"]>["site_directories"];
const { siteId, data } = defineProps<{
  siteId: number;
  data: SiteInformationProps;
}>();

const { mutate: deleteFn } = useSiteDirectoryDelete();
const { mutate: addFn, isPending: addPending } = useSiteDirectoryInsert();
const { mutate: scanAllDirectories, isPending: scanAllDirectoriesPending } = useSiteScanAllDirectories();
const { mutate: scanDirectory } = useSiteScanDirectory();
const { mutate: cancelJob } = useCancelJob();
const showAddDialog = ref(false);
const { $activeJobs } = useNuxtApp();

const { openDialog } = useDialogStore();

const currentJobs = computed(() => {
  return $activeJobs.value?.jobs.filter((job) => job.payload.site_id === siteId);
});

const siteHasScanningJob = computed(() => {
  return currentJobs.value?.some(
    (job) => job.payload.directories.length > 0 && ["running", "pending"].includes(job.status)
  );
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

function handleAdd() {
  showAddDialog.value = true;
}

function handleSubmit(path: string[]) {
  console.log("submit", path);
  showAddDialog.value = false;
  for (const p of path) {
    addFn({ directory: p, site_id: siteId });
  }
}
function skipAllSyncs() {
  openDialog(`Skip All Syncs`, `Are you sure you want to skip all syncs for this site?`, () => async () => {
    currentJobs.value?.forEach((job) => {
      cancelJob({ jobId: job.id });
    });
  });
}
</script>

<template>
  <v-sheet v-bind="$attrs">
    <v-list>
      <v-list-subheader> DATA DIRECTORIES </v-list-subheader>
      <v-toolbar flat density="compact" class="w-100" color="surface">
        <v-spacer></v-spacer>
        <v-tooltip :text="siteHasScanningJob ? 'Cancel All Syncs' : 'Sync All Directories'">
          <template v-slot:activator="{ props }">
            <template v-if="siteHasScanningJob">
              <v-progress-circular indeterminate color="secondary" v-bind="props">
                <v-btn
                  icon
                  size="small"
                  density="compact"
                  color="primary"
                  variant="tonal"
                  v-bind="props"
                  :disabled="scanAllDirectoriesPending"
                  :loading="scanAllDirectoriesPending"
                  @click="skipAllSyncs()"
                  ><v-icon>mdi-cancel</v-icon></v-btn
                >
              </v-progress-circular>
            </template>
            <v-btn
              v-else
              icon
              class="mr-2"
              density="compact"
              color="primary"
              variant="tonal"
              v-bind="props"
              :disabled="scanAllDirectoriesPending"
              :loading="scanAllDirectoriesPending"
              @click="
                openDialog(
                  `Scan all directories`,
                  `This will rescan all directories for this site and add all new files to the database.`,
                  () => scanAllDirectories({ id: siteId })
                )
              "
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
          <v-tooltip :text="activeJobInfo(item.directory)?.isRunning ? 'Cancel Sync' : 'Sync Directory'">
            <template v-slot:activator="{ props }">
              <template v-if="activeJobInfo(item.directory)">
                <v-progress-circular
                  :indeterminate="!activeJobInfo(item.directory)?.isRunning"
                  :model-value="activeJobInfo(item.directory)?.progress || 0"
                  color="secondary"
                >
                  <v-btn
                    icon="mdi-cancel"
                    size="small"
                    variant="text"
                    v-bind="props"
                    @click="
                      openDialog(
                        `Cancel Job`,
                        `Are you sure you want to cancel job scanning directory ${item.directory}?`,
                        async () => await cancelJob({ jobId: activeJobInfo(item.directory)?.id })
                      )
                    "
                  />
                </v-progress-circular>
              </template>
              <v-btn
                v-else
                icon="mdi-sync"
                size="small"
                variant="text"
                v-bind="props"
                @click="scanDirectory({ id: siteId, directory: item.directory })"
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
                @click="
                  openDialog(
                    `Delete Directory`,
                    `Are you sure you want to delete  ${item.directory} from this site ?`,
                    () => handleDelete(item.id)
                  )
                "
              />
            </template>
          </v-tooltip>
        </template>
      </v-list-item>
    </v-list>
  </v-sheet>
  <v-dialog v-model="showAddDialog" persistent max-width="500px">
    <sites-data-directory-browser
      @select="handleSubmit"
      @cancel="showAddDialog = false"
      :directories="data.map((item) => item.directory)"
    />
  </v-dialog>
</template>
