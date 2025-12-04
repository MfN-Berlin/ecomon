<template>
  <v-container fluid class="pa-0 ma-0">
    <v-row no-gutters>
      <v-col cols="12" class="pa-0">
        <v-data-table
          :headers="headers"
          :items="reports"
          :loading="pending"
          :items-per-page="25"
          class="elevation-0 custom-table-margin"
          density="compact"
        >
          <template #item.db_import="{ item }">
            <span :class="getStatusColor(item.db_import)">
              {{ item.db_import }}
            </span>
          </template>
          <template #item.birdid_medium="{ item }">
            <span :class="getStatusColor(item.birdid_medium)">
              {{ item.birdid_medium }}
            </span>
          </template>
          <template #item.report_date="{ item }">
            {{ formatDate(item.report_date) }}
          </template>
          <template #item.visible_in_ui="{ item }">
            <v-icon v-if="item.visible_in_ui" color="green">mdi-check</v-icon>
            <v-icon v-else color="red">mdi-close</v-icon>
          </template>
          <template #bottom>
            <table>
              <colgroup>
                <col style="width: 200px;" />
                <col style="width: 240px;" />
                <col style="width: 60px;" />
                <col style="width: 180px;" />
                <col style="width: 120px;" />
                <col style="width: 120px;" />
                <col style="width: 120px;" />
                <col style="width: 120px;" />
                <col style="width: 150px;" />
                <col style="width: 130px;" />
              </colgroup>
              <tfoot>
                <tr class="totals-row">
                  <td class="v-data-table__td"><strong>Totals:</strong></td>
                  <td class="v-data-table__td"></td>
                  <td class="v-data-table__td"></td>
                  <td class="v-data-table__td v-data-table-column--align-end">{{ (totalSize / (1024**4)).toFixed(4) }} TB</td>
                  <td class="v-data-table__td v-data-table-column--align-end">{{ totalWavCount.toLocaleString() }}</td>
                  <td class="v-data-table__td v-data-table-column--align-end">
                    {{ totalRecords.toLocaleString() }}
                    <span v-if="totalRecords > 0 && totalWavCount > 0">
                      ({{ ((totalWavCount / totalRecords) * 100).toFixed(2) }}%)
                    </span>
                  </td>
                  <td class="v-data-table__td v-data-table-column--align-center"></td>
                  <td class="v-data-table__td v-data-table-column--align-end">
                    {{ totalProcessed.toLocaleString() }}
                    <span v-if="totalRecords > 0 && totalProcessed > 0">
                      ({{ ((totalProcessed / totalRecords) * 100).toFixed(2) }}%)
                    </span>
                  </td>
                  <td class="v-data-table__td v-data-table-column--align-center"></td>
                  <td class="v-data-table__td"></td>
                </tr>
              </tfoot>
            </table>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
// Page setup
definePageMeta({
  layout: "default",
});

// State
const pending = ref(false);
const data = ref<any>(null);
const error = ref<string | null>(null);

// Fetch workflow reports
const fetchReports = async () => {
  pending.value = true;
  error.value = null;

  try {
    const config = useRuntimeConfig();

    console.log('Fetching from:', config.public.GQL_HOST);

    const result = await $fetch(config.public.GQL_HOST, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: {
        query: `
          query GetLatestWorkflowReports {
            workflow_reports(
              order_by: { report_date: desc, prefix: asc }
            ) {
              id
              report_date
              prefix
              site_id
              wav_size_bytes
              wav_count
              record_count
              db_import
              birdid_medium_processed
              birdid_medium
              birdid_medium_visible
              created_at
            }
          }
        `
      }
    });

    console.log('GraphQL result:', result);

    if (result.errors) {
      console.error('GraphQL errors:', result.errors);
      error.value = result.errors[0]?.message || 'GraphQL query failed';
    } else {
      data.value = result.data;
      console.log('Workflow reports:', data.value?.workflow_reports);
    }
  } catch (err: any) {
    console.error('Error fetching workflow reports:', err);
    error.value = err.message || 'Failed to fetch reports';
  } finally {
    pending.value = false;
  }
};

// Refresh function
const refetch = () => {
  fetchReports();
};

// Get reports from latest date only
const reports = computed(() => {
  if (!data.value?.workflow_reports?.length) {
    console.log('No reports found in data:', data.value);
    return [];
  }

  // Get the most recent report date
  const latestDate = data.value.workflow_reports[0].report_date;

  console.log('Latest date:', latestDate);
  console.log('Total reports:', data.value.workflow_reports.length);

  // Filter to only include reports from that date
  const filtered = data.value.workflow_reports.filter(
    (report: any) => report.report_date === latestDate
  );

  console.log('Filtered reports:', filtered.length);

  return filtered;
});

// Calculate totals
const totalSize = computed(() => {
  return reports.value.reduce((sum, report) => sum + (report.wav_size_bytes || 0), 0);
});

const totalWavCount = computed(() => {
  return reports.value.reduce((sum, report) => sum + (report.wav_count || 0), 0);
});

const totalRecords = computed(() => {
  return reports.value.reduce((sum, report) => sum + (report.record_count || 0), 0);
});

const totalProcessed = computed(() => {
  return reports.value.reduce((sum, report) => sum + (report.birdid_medium_processed || 0), 0);
});

// Table headers
const headers = [
  { title: 'Report Date', key: 'report_date', sortable: true, width: '200px' },
  { title: 'Prefix', key: 'prefix', sortable: true, width: '240px' },
  { title: 'Site ID', key: 'site_id', sortable: true, width: '60px', align: 'end' },
  { title: 'WAV Size', key: 'wav_size_bytes', sortable: true, width: '180px', align: 'end' },
  { title: 'WAV Count', key: 'wav_count', sortable: true, width: '120px', align: 'end' },
  { title: 'Records', key: 'record_count', sortable: true, width: '120px', align: 'end' },
  { title: 'DB Import', key: 'db_import', sortable: true, width: '120px', align: 'center' },
  { title: 'BirdID Medium Processed', key: 'birdid_medium_processed', sortable: true, width: '120px', align: 'end' },
  { title: 'BirdID Medium Status', key: 'birdid_medium', sortable: true, width: '150px', align: 'center'  },
  { title: 'Visible in UI', key: 'visible_in_ui', sortable: true, width: '130px', align: 'center' },
];
// Format bytes to human readable format
const formatBytes = (bytes: number): string => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// Format date to readable format
const formatDate = (date: string): string => {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0'); // Months are 0-based
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

// Get color based on status
const getStatusColor = (status: string): string => {
  console.log('Status:', status); // Debugging line
  if (!status) return 'status-default';
  switch (status.toLowerCase()) {
    case 'ready':
      return 'status-ready';
    case 'ready with losses':
      return 'status-ready-losses';
    case 'pending': // Changed from "update this" to "pending"
      return 'status-pending';
    case 'running':
      return 'status-running';
    default:
      return 'status-default';
  }
};

// Fetch data on mount
onMounted(() => {
  fetchReports();
});
</script>

<style scoped>
.custom-table-margin {
  margin-left: -1em;
}

.totals-row {
  background-color: yellow !important;
}

.totals-row .v-data-table__td {
  padding: 12px 16px !important;
  font-size: 0.875rem;
}
.totals-row .v-data-table-column--align-end,
.totals-row .align-end {
  text-align: right !important;
}

.totals-row .align-center {
  text-align: center !important;
}
.v-data-table {
  width: 95%;
}

/* Status styles */
.status-ready {
  color: white;
  background-color: green !important;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-ready-losses {
  color: black;
  background-color: yellowgreen !important;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-pending {
  color: white;
  background-color: magenta !important;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-running {
  color: black;
  background-color: lightgray !important;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-default {
  color: gray;
}
</style>