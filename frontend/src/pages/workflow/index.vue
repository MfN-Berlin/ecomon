<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Workflow Overview</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-chart-box-outline</v-icon>
            Workflow Reports
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              @click="refetch"
              :loading="pending"
              prepend-icon="mdi-refresh"
            >
              Refresh
            </v-btn>
          </v-card-title>
          <v-card-text>
            <!-- Show error if any -->
            <v-alert v-if="error" type="error" class="mb-4">
              {{ error }}
            </v-alert>

            <v-data-table
              :headers="headers"
              :items="reports"
              :loading="pending"
              :items-per-page="25"
              class="elevation-1"
            >
                <!-- Format file size -->
              <template #item.wav_size_bytes="{ item }">
                {{ formatBytes(item.wav_size_bytes) }}
              </template>

              <!-- Format report date -->
              <template #item.report_date="{ item }">
                {{ formatDate(item.report_date) }}
              </template>

              <!-- Color code DB Import status -->
              <template #item.db_import="{ item }">
                <v-chip
                  :color="getStatusColor(item.db_import)"
                  size="small"
                  v-if="item.db_import"
                >
                  {{ item.db_import }}
                </v-chip>
              </template>

              <!-- Color code BirdID Medium status -->
              <template #item.birdid_medium="{ item }">
                <v-chip
                  :color="getStatusColor(item.birdid_medium)"
                  size="small"
                  v-if="item.birdid_medium"
                >
                  {{ item.birdid_medium }}
                </v-chip>
              </template>

              <!-- Empty state -->
              <template #no-data>
                <v-alert type="info" class="my-4">
                  No workflow reports available. Reports are generated daily at 3:00 AM.
                </v-alert>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
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

// Table headers
const headers = [
  { title: 'Report Date', key: 'report_date', sortable: true },
  { title: 'Prefix', key: 'prefix', sortable: true },
  { title: 'Site ID', key: 'site_id', sortable: true },
  { title: 'WAV Size', key: 'wav_size_bytes', sortable: true },
  { title: 'WAV Count', key: 'wav_count', sortable: true },
  { title: 'Records', key: 'record_count', sortable: true },
  { title: 'DB Import', key: 'db_import', sortable: true },
  { title: 'BirdID Processed', key: 'birdid_medium_processed', sortable: true },
  { title: 'BirdID Status', key: 'birdid_medium', sortable: true },
  { title: 'Visible in UI', key: 'birdid_medium_visible', sortable: true },
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
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Get color based on status
const getStatusColor = (status: string): string => {
  if (!status) return 'grey';
  switch (status.toLowerCase()) {
    case 'ready':
      return 'success';
    case 'ready with losses':
      return 'warning';
    case 'update this':
      return 'error';
    case 'running':
      return 'info';
    default:
      return 'grey';
  }
};

// Fetch data on mount
onMounted(() => {
  fetchReports();
});
</script>

<style scoped>
/* Add custom styles here if needed */
</style>