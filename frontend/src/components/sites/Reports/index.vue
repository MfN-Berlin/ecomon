<script setup lang="ts">
import type { SiteFragment } from "#gql";
import dayjs from "dayjs";

const props = defineProps<{
  site: SiteFragment;
}>();
const { data: reportList, pending: isLoading } = useSubscribeReportsBySiteId(props.site.id);
const { mutate: createReport, pending: isCreatingReport } = useCreateSiteReport();
const reports = computed(() => {
  return (
    reportList.value?.data?.map((report) => {
      return {
        ...report,
        created_at: dayjs(report.created_at).format("YYYY-MM-DD HH:mm")
      };
    }) || []
  );
});
const selectedReportId = ref<number | null>(null);

// Watch the reports computed for changes and auto-select the first report once it's loaded.
watch(
  reports,
  (newReports) => {
    if (newReports.length > 0 && !selectedReportId.value) {
      selectedReportId.value = newReports[0].id;
    }
  },
  { immediate: true }
);
</script>

<template>
  <v-sheet v-bind="$attrs">
    <v-toolbar title="Report" color="primary" density="compact">
      <div class="pt-5">
        <v-select
          v-model="selectedReportId"
          density="compact"
          :items="reports"
          :loading="isLoading"
          item-title="created_at"
          item-value="id"
        />
      </div>
      <v-tooltip text="Create Report">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-refresh"
            variant="text"
            v-bind="props"
            :disabled="isCreatingReport"
            :loading="isCreatingReport"
            @click="createReport({ id: site.id })"
          />
        </template>
      </v-tooltip>
    </v-toolbar>

    <sites-reports-basic-data v-if="selectedReportId" :reportId="selectedReportId" />
    <sites-reports-visual-data v-if="selectedReportId" :reportId="selectedReportId" :site="site" />
    <div v-else>
      <v-skeleton-loader type="table-row" />
      <v-skeleton-loader type="table-row" />
    </div>
  </v-sheet>
</template>
