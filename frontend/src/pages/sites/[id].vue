<!--
  Site Details Page Component

  Description:
  This page displays details for a single site. It is responsible for
  fetching and rendering all relevant information pertaining to the site,
  such as its name, location, description, and any associated metadata.

  Responsibilities:
  - Retrieve site data from a data source or API.
  - Render the site's detailed information for the user.
  - Manage component state and lifecycle events to ensure up-to-date display.

  Additional Notes:
  - Ensure error handling is implemented for data fetching failures.
  - Optimize performance by loading only necessary data on mount.
  - Maintain a clean and user-friendly interface for better user experience.
-->
<script setup lang="ts">
// Use submenu layout for consistent navigation
definePageMeta({ layout: "submenu" });

const router = useRouter();
// Extract site ID from route parameters
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));
// Fetch site data using the computed ID
const { data, isFetching } = useSiteGet(id.value);
const { mutate, isPending } = useSiteUpdate();
const { mutate: deleteMutate, isPending: deletePending } = useSiteDelete();
// Combined delete action that removes site and navigates to sites list
const deleteAction = useActionAndRoute({
  action: () => {
    console.log("deleting site", id.value);
    deleteMutate({ id: id.value });
  },
  gotoUrl: "/sites"
});
</script>
<template>
  <v-container>
    <!-- Sticky action bar with site-specific actions -->
    <v-row class="position-sticky">
      <v-col cols="12">
        <sites-actions :site-id="id" :site-name="data?.name ?? ''" />
      </v-col>
    </v-row>
    <v-row>
      <!-- Left column: Site form and model controls -->
      <v-col cols="12" md="6">
        <!-- Site details form with edit/delete capabilities -->
        <sites-form
          v-if="data"
          :loading="isFetching || isPending"
          :data="{
            id: data?.id,
            name: data?.name,
            prefix: data?.prefix,
            location_id: data.location?.id,
            record_regime_recording_duration: data?.record_regime_recording_duration,
            record_regime_pause_duration: data?.record_regime_pause_duration,
            sample_rate: data?.sample_rate,
            remarks: data?.remarks,
            created_at: data?.created_at,
            updated_at: data?.updated_at
          }"
          :show-delete-button="true"
          :delete-button-loading="deletePending"
          @submit="
            (data) => {
              mutate(data);
            }
          "
          @delete="
            () => {
              console.log('deleting site fomr event', id);
              deleteAction();
            }
          "
        ></sites-form>
        <!-- Model site controls for data processing -->
        <sites-model-site-controls class="mt-4" :siteId="id" />
      </v-col>
      <!-- Right column: Reports and directory management -->
      <v-col cols="12" md="6">
        <!-- Site reports and analytics -->
        <sites-reports v-if="data" :site="data" />
        <!-- Directory listing for site data management -->
        <sites-directory-list v-if="data" class="mt-4" :siteId="id" :data="data.site_directories" />
      </v-col>
    </v-row>
  </v-container>
</template>
