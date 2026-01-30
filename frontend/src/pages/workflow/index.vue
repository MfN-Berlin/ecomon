<template>
  <v-container fluid class="pa-0 ma-0">
    <v-row no-gutters>
      <v-col cols="12" class="pa-0">
        <div class="report-header">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div class="report-date">
              <strong>Report Date:</strong> {{ formatDate(reports[0]?.report_date) }}
            </div>
            <v-btn
              variant="text"
              size="small"
              :loading="pending"
              @click="refetch"
              class="refresh-btn"
              icon
            >
              <v-icon>mdi-refresh</v-icon>
              <v-tooltip activator="parent" location="bottom">Refresh Data</v-tooltip>
            </v-btn>
          </div>
        </div>

        <!-- Main Table (Non-Ultrasound) -->
        <v-data-table
          :headers="headers"
          :items="nonUltrasoundReports"
          :loading="pending"
          :items-per-page="25"
          class="elevation-0 custom-table-margin"
          density="compact"
        >
          <template #item.prefix="{ item }">
            <span>{{ item.prefix }}</span>
          </template>
          <template #item.db_import="{ item }">
            <span :class="getStatusColor(item.db_import)">
              {{ getStatusText(item.db_import) }}
            </span>
          </template>

          <!-- Dynamic model status columns -->
          <template v-for="modelName in availableModels" :key="`status-${modelName}`" #[`item.${modelName}_status`]="{ item }">
            <v-tooltip location="top">
              <template #activator="{ props }">
                <span
                  v-bind="props"
                  :class="getStatusColor(item[`${modelName}_status`])"
                  style="cursor: help;"
                >
                  {{ getStatusText(item[`${modelName}_status`]) }}
                </span>
              </template>
              <span>
                Processed: {{ ((item[`${modelName}_processed`] || 0).toLocaleString('de-DE')) }}<br>
                Skipped: {{ (item.skipped_records || 0).toLocaleString('de-DE') }}<br>
                Total Records: {{ (item.record_count || 0).toLocaleString('de-DE') }}
              </span>
            </v-tooltip>
          </template>
          <template #item.wav_size_bytes="{ item }">
            <v-tooltip location="top">
              <template #activator="{ props }">
                <span v-bind="props" style="cursor: help;">
                  {{ formatBytesToMB(item.wav_size_bytes) }}
                </span>
              </template>
              <span>{{ (item.wav_size_bytes || 0).toLocaleString('de-DE') }} bytes</span>
            </v-tooltip>
          </template>
          <!-- Totals row -->
          <template #body.append>
            <tr class="totals-row">
              <td><strong>Totals:</strong></td>
              <td></td>
              <td class="text-end">{{ (totalSize / (1024**4)).toFixed(2) }} TB</td>
              <td class="text-end">{{ totalWavCount.toLocaleString('de-DE') }}</td>
              <td class="text-end">
                {{ totalRecords.toLocaleString() }}
                <span v-if="totalRecords > 0 && totalWavCount > 0">
                  ({{ ((totalRecords / totalWavCount) * 100).toFixed(2) }}%)
                </span>
              </td>
              <td></td>
              <!-- Totals for each model -->
              <template v-for="modelName in availableModels" :key="`totals-${modelName}`">
                <td></td>
              </template>
            </tr>
          </template>
        </v-data-table>

        <!-- Legend -->
        <div class="legend-container">
          <h3 class="legend-title">Status Legend:</h3>
          <div class="legend-items">
            <div class="legend-item">
              <span class="legend-badge status-ready">ready</span>
              <span class="legend-text">All files processed successfully</span>
            </div>
            <div class="legend-item">
              <span class="legend-badge status-ready-losses">ready</span>
              <span class="legend-text">Some recordings could not be read or generated no inferences</span>
            </div>
            <div class="legend-item">
              <span class="legend-badge status-pending">pending</span>
              <span class="legend-text">Processing not complete</span>
            </div>
            <div class="legend-item">
              <span class="legend-badge status-running">running</span>
              <span class="legend-text">Processing currently in progress</span>
            </div>
          </div>
        </div>

        <!-- Ultrasound Table -->
        <div v-if="ultrasoundReports.length > 0" class="ultrasound-section">
          <h2 class="section-title">
            <v-icon size="large" color="black" class="mr-2">mdi-bat</v-icon>
            Ultrasound Sites
          </h2>

          <v-data-table
            :headers="headers"
            :items="ultrasoundReports"
            :loading="pending"
            :items-per-page="25"
            class="elevation-0 custom-table-margin"
            density="compact"
          >
            <template #item.prefix="{ item }">
              <span style="display: inline-flex; align-items: center; gap: 4px;">
                <v-icon size="large" color="black" class="ml-1">
                  mdi-bat
                </v-icon>{{ item.prefix }}
              </span>
            </template>
            <template #item.db_import="{ item }">
              <span :class="getStatusColor(item.db_import)">
                {{ getStatusText(item.db_import) }}
              </span>
            </template>

            <!-- Dynamic model status columns for ultrasound -->
            <template v-for="modelName in availableModels" :key="`us-status-${modelName}`" #[`item.${modelName}_status`]="{ item }">
              <v-tooltip location="top">
                <template #activator="{ props }">
                  <span
                    v-bind="props"
                    :class="getStatusColor(item[`${modelName}_status`])"
                    style="cursor: help;"
                  >
                    {{ getStatusText(item[`${modelName}_status`]) }}
                  </span>
                </template>
                <span>
                  Processed: {{ ((item[`${modelName}_processed`] || 0).toLocaleString('de-DE')) }}<br>
                  Skipped: {{ (item.skipped_records || 0).toLocaleString('de-DE') }}<br>
                  Total Records: {{ (item.record_count || 0).toLocaleString('de-DE') }}
                </span>
              </v-tooltip>
            </template>
            <template #item.wav_size_bytes="{ item }">
              <v-tooltip location="top">
                <template #activator="{ props }">
                  <span v-bind="props" style="cursor: help;">
                    {{ formatBytesToMB(item.wav_size_bytes) }}
                  </span>
                </template>
                <span>{{ (item.wav_size_bytes || 0).toLocaleString('de-DE') }} bytes</span>
              </v-tooltip>
            </template>
            <!-- Ultrasound Totals row -->
            <template #body.append>
              <tr class="totals-row">
                <td><strong>Totals:</strong></td>
                <td></td>
                <td class="text-end">{{ (ultrasoundTotalSize / (1024**4)).toFixed(2) }} TB</td>
                <td class="text-end">{{ ultrasoundTotalWavCount.toLocaleString('de-DE') }}</td>
                <td class="text-end">
                  {{ ultrasoundTotalRecords.toLocaleString() }}
                  <span v-if="ultrasoundTotalRecords > 0 && ultrasoundTotalWavCount > 0">
                    ({{ ((ultrasoundTotalRecords / ultrasoundTotalWavCount) * 100).toFixed(2) }}%)
                  </span>
                </td>
                <td></td>
                <!-- Totals for each model in ultrasound -->
                <template v-for="modelName in availableModels" :key="`us-totals-${modelName}`">
                  <td></td>
                </template>
              </tr>
            </template>
          </v-data-table>
        </div>

      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
// Page setup
definePageMeta({
  layout: "default",
});

// Use the composable from workflowReports.ts
const { data, pending, error, fetchReports } = useWorkflowReports();

// Fetch reports on mount
onMounted(() => {
  fetchReports();

  // Set up automatic polling every 30 seconds
  const pollInterval = setInterval(() => {
    console.log('Auto-refreshing workflow reports...');
    fetchReports();
  }, 30000);

  // Clean up interval on unmount
  onUnmounted(() => {
    clearInterval(pollInterval);
  });
});

// Refresh function
const refetch = () => {
  console.log('Manual refresh triggered');
  fetchReports();
};

// Get reports - simplified since distinct_on handles latest per prefix
const reports = computed(() => {
  if (!data.value?.workflow_reports?.length) {
    console.log('No reports found in data:', data.value);
    return [];
  }

  console.log('📊 Reports fetched:', data.value.workflow_reports.length);

  // Log details of first report
  const firstReport = data.value.workflow_reports[0];
  if (firstReport) {
    console.log('📋 First report:', {
      prefix: firstReport.prefix,
      report_date: firstReport.report_date,
      models: firstReport.models?.length || 0,
      sample_model_status: firstReport.models?.[0]?.model_status,
      avesecho_v1_3_0_status: firstReport['avesecho_v1.3.0_status'],
      birdnetplus_status: firstReport['birdnetplus-v3.0_euna_1k_preview2_status']
    });
  }

  return data.value.workflow_reports;
});

// Check if prefix is ultrasound (ends with U, V, or W)
const isUltrasound = (prefix: string): boolean => {
  if (!prefix) return false;
  const lastChar = prefix.slice(-1).toUpperCase();
  return ['U', 'V', 'W'].includes(lastChar);
};

// Split reports into ultrasound and non-ultrasound
const nonUltrasoundReports = computed(() => {
  return reports.value.filter(report => !isUltrasound(report.prefix));
});

const ultrasoundReports = computed(() => {
  return reports.value.filter(report => isUltrasound(report.prefix));
});

// Calculate totals for non-ultrasound
const totalSize = computed(() => {
  return nonUltrasoundReports.value.reduce((sum, report) => sum + (report.wav_size_bytes || 0), 0);
});

const totalWavCount = computed(() => {
  return nonUltrasoundReports.value.reduce((sum, report) => sum + (report.wav_count || 0), 0);
});

const totalRecords = computed(() => {
  return nonUltrasoundReports.value.reduce((sum, report) => sum + (report.record_count || 0), 0);
});

const totalProcessed = computed(() => {
  return availableModels.value.reduce((sumByModel, modelName) => {
    const modelTotal = nonUltrasoundReports.value.reduce((sum, report) =>
      sum + (report[`${modelName}_processed`] || 0), 0);
    return { ...sumByModel, [modelName]: modelTotal };
  }, {});
});

// Calculate totals for ultrasound
const ultrasoundTotalSize = computed(() => {
  return ultrasoundReports.value.reduce((sum, report) => sum + (report.wav_size_bytes || 0), 0);
});

const ultrasoundTotalWavCount = computed(() => {
  return ultrasoundReports.value.reduce((sum, report) => sum + (report.wav_count || 0), 0);
});

const ultrasoundTotalRecords = computed(() => {
  return ultrasoundReports.value.reduce((sum, report) => sum + (report.record_count || 0), 0);
});

const ultrasoundTotalProcessed = computed(() => {
  return availableModels.value.reduce((sumByModel, modelName) => {
    const modelTotal = ultrasoundReports.value.reduce((sum, report) =>
      sum + (report[`${modelName}_processed`] || 0), 0);
    return { ...sumByModel, [modelName]: modelTotal };
  }, {});
});

// Get all available models from reports
const availableModels = computed(() => {
  const models = new Set<string>();
  reports.value.forEach(report => {
    if (report.models) {
      report.models.forEach((model: any) => {
        models.add(model.model_name);
      });
    }
  });
  const modelArray = Array.from(models).sort();
  console.log('🎯 Available models found:', modelArray);

  // Debug: log what fields are available in first report for each model
  if (reports.value.length > 0 && modelArray.length > 0) {
    const firstReport = reports.value[0];
    console.log('🔍 Checking first report for model fields:');
    modelArray.forEach(modelName => {
      const statusField = `${modelName}_status`;
      const statusValue = firstReport[statusField];
      console.log(`  - ${statusField}: ${statusValue}`);
    });
  }

  return modelArray;
});

// Table headers - now includes dynamic model columns
const headers = computed(() => {
  const baseHeaders = [
    { title: 'Prefix', key: 'prefix', sortable: true, width: '110px' },
    { title: 'Site ID', key: 'site_id', sortable: true, width: '60px', align: 'end' },
    { title: 'WAV Size (MB)', key: 'wav_size_bytes', sortable: true, width: '180px', align: 'end' },
    { title: 'WAV Count', key: 'wav_count', sortable: true, width: '120px', align: 'end' },
    { title: 'Records', key: 'record_count', sortable: true, width: '120px', align: 'end' },
    { title: 'DB Import', key: 'db_import', sortable: true, width: '200px', align: 'center' },
  ];

  // Add dynamic model status columns only
  const modelHeaders = availableModels.value.map(modelName =>
    ({ title: `${modelName}`, key: `${modelName}_status`, sortable: true, width: '200px', align: 'center' })
  );

  return [...baseHeaders, ...modelHeaders];
});

// Format bytes to MB with 2 decimals (1 MB = 1,000,000 bytes, German locale)
const formatBytesToMB = (bytes: number): string => {
  if (!bytes || bytes === 0) return '0,00';
  const mb = Math.round(bytes / 1000000);
  return mb.toLocaleString('DE-de');
};

// Format date to readable format
const formatDate = (date: string): string => {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

// Get display text for status (converts "ready with losses" to "ready")
const getStatusText = (status: string): string => {
  if (!status) return '';
  if (status.toLowerCase() === 'ready with losses') return 'ready';
  return status;
};

// Get color based on status
const getStatusColor = (status: string): string => {
  console.log('Status:', status);
  if (!status) return 'status-default';
  switch (status.toLowerCase()) {
    case 'ready':
      return 'status-ready';
    case 'ready with losses':
      return 'status-ready-losses';
    case 'pending':
      return 'status-pending';
    case 'running':
      return 'status-running';
    default:
      return 'status-default';
  }
};
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

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
}

.report-date {
  margin-bottom: 0;
  font-size: 1.2rem;
}

.refresh-btn {
  opacity: 0.7;
  min-width: 32px !important;
  height: 32px !important;
  margin-left: auto; /* This pushes the button to the right */
  margin-right: 8px; /* Adds space from the right edge */
}

.refresh-btn:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.05) !important;
}

/* Legend styles */
.legend-container {
  margin-top: 24px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
  width: 95%;
}

.legend-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-badge {
  display: inline-block;
  min-width: 120px;
  text-align: center;
  font-size: 0.75rem;
  padding: 2px 4px;
}

.legend-text {
  font-size: 0.875rem;
  color: #555;
}

/* Ultrasound section styles */
.ultrasound-section {
  margin-top: 32px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  color: #333;
}
</style>