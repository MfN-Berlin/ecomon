<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useSiteGet(id.value);
const { mutate, isPending } = useSiteUpdate();
</script>
<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
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
          @submit="
            (data) => {
              mutate(data);
            }
          "
        ></sites-form>

        <sites-model-site-controls class="mt-4" :siteId="id" />
        <sites-create-voucher class="mt-4" :siteId="id" :siteName="data.name" />
      </v-col>
      <v-col cols="12" md="6">
        <sites-reports v-if="data" :site="data" />
        <sites-directory-list v-if="data" class="mt-4" :siteId="id" :data="data.site_directories" />
      </v-col>
    </v-row>
  </v-container>
</template>
