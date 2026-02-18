<script setup lang="ts">
import PageControls from '~/components/dashboard/PageControls.vue';
import VoucherForm from '~/components/voucher/Form.vue';

definePageMeta({ layout: "full-width" });

// Initialize data fetching composables
const sitesList = useAllSites();
const modelList = useAllModels();
const yearsList = useRecordYears();

// Fetch data
sitesList.fetchAllSites();
modelList.fetchAllModels();
yearsList.fetchYears();

// Species handling
const speciesLabelsSearch = useLabelsSearch();
const preservedSpeciesSelection = ref(null);

// Transform site data for v-select component
const sites = computed(() => {
  if (!sitesList.data.value) return [];

  return sitesList.data.value.map(site => ({
    title: `${site.prefix}, ${site.name}`,
    value: site.id
  }));
});

// Handle selection updates from PageControls
const selectedParams = ref({
  model: null,
  sites: [],
  year: null,
  species: null,
  threshold: 0.5 // Add threshold to selectedParams
});

// Watch for changes in selections to trigger species search
watch(
  () => [
    selectedParams.value.model,
    selectedParams.value.sites,
    selectedParams.value.year
  ],
  ([model, sites, year]) => {
    // Store the current species selection before search
    if (selectedParams.value.species) {
      preservedSpeciesSelection.value = selectedParams.value.species;
    }

    // Clear any pending search operations
    if (speciesLabelsSearch.pendingSearch) {
      speciesLabelsSearch.pendingSearch.cancel();
    }

    // Only search for species when all required parameters are available
    if (model && sites && Array.isArray(sites) && sites.length > 0 && year) {
      console.log("Searching for species with:",
        "Model:", model.value,
        "Sites:", sites.map(site => site.value),
        "Year:", year);

      speciesLabelsSearch.searchLabels(model.value, sites.map(site => site.value), year);
    } else {
      // Only clear species data if required parameters are missing
      if (speciesLabelsSearch.data.value) {
        speciesLabelsSearch.data.value = null;
      }
      console.log("Not all parameters available for species search");
    }
  },
  { immediate: true, deep: true }
);

// Watch for when species search completes and restore the selection
watch(
  () => speciesLabelsSearch.data.value,
  (labels) => {
    if (labels && labels.labels && labels.labels.length > 0) {
      console.log("Fetched species labels:", labels);

      // Restore the preserved species selection if it exists in the new data
      if (preservedSpeciesSelection.value) {
        const speciesExists = labels.labels.some(
          species => species.id === preservedSpeciesSelection.value
        );

        if (speciesExists) {
          console.log("Restoring species selection:", preservedSpeciesSelection.value);
          selectedParams.value.species = preservedSpeciesSelection.value;
        } else {
          console.log("Previously selected species not available in new site");
          preservedSpeciesSelection.value = null;
        }
      }
    }
  },
  { immediate: true }
);

const formattedSpecies = computed(() => {
  // Check if we're currently loading species data
  if (speciesLabelsSearch.pending.value) {
    return [{
      title: "Loading species...",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }

  // Extract the raw species data
  const speciesData = speciesLabelsSearch.data?.value?.labels;

  if (!speciesData) {
    // Create a placeholder message
    return [{
      title: "Please choose a classifier, a site and a year to display species",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }

  // For empty arrays, show a different message
  if (Array.isArray(speciesData) && speciesData.length === 0) {
    return [{
      title: "No species found with current selections",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }

  // Process the data
  try {
    return speciesData.map(species => ({
      title: species.name,
      value: species.id,
      isPlaceholder: false
    }));
  } catch (e) {
    console.error("Error processing species data:", e);
    return [{
      title: "Error processing species data",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }
});

const handleSelectionUpdate = (selection) => {
  // Safely update each property individually
  if ('model' in selection) selectedParams.value.model = selection.model;
  if ('sites' in selection) selectedParams.value.sites = selection.sites;
  if ('year' in selection) selectedParams.value.year = selection.year;
  if ('species' in selection && selection.species !== undefined) {
    selectedParams.value.species = selection.species;
  }
  if ('threshold' in selection) selectedParams.value.threshold = selection.threshold;
};

// Create params for minutes query
const minutesParams = computed(() => {
  const { model, sites, year, species, threshold } = selectedParams.value;

  if (!model || !sites || sites.length === 0 || !year || !species) {
    return null;
  }

  return {
    speciesId: species,
    modelId: model.value,
    siteId: sites[0].value,
    year: year,
    threshold: threshold
  };
});

// Use the composable
const {
  data: minutesWithActivity,
  isFetching: isLoadingMinutes,
  isError: isMinutesError
} = useMinutesWithActivity(minutesParams);

// Voucher data state
const voucherData = ref([]);
const isLoadingVoucher = ref(false);

// Handle create voucher
const handleCreateVoucher = async (sampleNumber: number) => {
  const params = minutesParams.value;

  if (!params) {
    console.error('Cannot create voucher: missing required parameters');
    return;
  }

  try {
    isLoadingVoucher.value = true;
    const data = await fetchVoucherDataSampled({
      ...params,
      sampleSize: sampleNumber
    });
    console.log('Voucher data:', data);
    voucherData.value = data;
  } catch (error) {
    console.error('Error creating voucher:', error);
  } finally {
    isLoadingVoucher.value = false;
  }
};

</script>

<template>
  <v-container style="max-width: 100%;">
    <v-row>
      <!-- Left column with controls -->
      <v-col cols="4">
        <PageControls
          :available-models="modelList.data?.value || []"
          :available-sites="sites"
          :available-years="yearsList.data?.value || []"
          :available-species="formattedSpecies"
          :default-threshold="selectedParams.threshold"
          @update:selection="handleSelectionUpdate"
        />
      </v-col>

      <!-- Right column for voucher content -->
      <v-col cols="8">
        <VoucherForm
          :selected-species="selectedParams.species"
          :minutes-with-activity="minutesWithActivity"
          :is-loading-minutes="isLoadingMinutes"
          :is-minutes-error="isMinutesError"
          :threshold="selectedParams.threshold"
          @update:threshold="handleSelectionUpdate({ threshold: $event })"
          @create-voucher="handleCreateVoucher"
        />

        <!-- Voucher content card -->
        <v-card>
          <v-card-text v-if="voucherData.length === 0 && !isLoadingVoucher" class="d-flex align-center justify-center" style="min-height: 400px;">
            <div class="text-center pa-5">
              <v-icon icon="mdi-tag-outline" size="large" color="grey" class="mb-3"></v-icon>
              <p class="text-body-1 text-grey-darken-1">
                Select parameters and click "Create voucher" to view data
              </p>
            </div>
          </v-card-text>

          <v-card-text v-else-if="isLoadingVoucher" class="d-flex align-center justify-center" style="min-height: 400px;">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </v-card-text>

          <v-card-text v-else>
            <v-data-table
              :items="voucherData"
              :items-per-page="10"
              density="compact"
            >
              <template v-slot:headers>
                <tr>
                  <th>Site</th>
                  <th>Record Datetime</th>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Species</th>
                  <th>Confidence</th>
                </tr>
              </template>
              <template v-slot:item="{ item }">
                <tr>
                  <td>{{ item.record.site?.prefix }}, {{ item.record.site?.name || item.record.site_id }}</td>
                  <td>{{ new Date(item.record.record_datetime).toLocaleString() }}</td>
                  <td>{{ item.start_time }}</td>
                  <td>{{ item.end_time }}</td>
                  <td>{{ item.label.name }}</td>
                  <td>{{ item.confidence.toFixed(3) }}</td>
                </tr>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
</style>