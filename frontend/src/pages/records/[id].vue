<script setup lang="ts">
definePageMeta({ layout: "default" });
const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useRecordGet(id);
const { mutate, isPending } = useRecordUpdate();
const deleteAction = useActionAndRoute({
  action: () => deleteMutate({ id: id.value }),
  gotoUrl: "/records"
});
</script>
<template>
  <v-container class="">
    <v-row>
      <v-col cols="12" md="6">
        <records-form
          v-if="data"
          :loading="isFetching || isPending"
          :data="{
            id: data?.id,
            site_id: data?.site_id,
            filepath: data?.filepath,
            filename: data?.filename,
            record_datetime: data?.record_datetime,
            duration: data?.duration,
            channels: data?.channels,
            sample_rate: data?.sample_rate,
            mime_type: data?.mime_type,
            errors: data?.errors,
            created_at: data?.created_at,
            updated_at: data?.updated_at
          }"
          @delete="deleteAction"
          @submit="
            (data) => {
              const payload = { ...data };
              delete payload.id;
              mutate(payload);
            }
          "
        ></records-form>
        <records-errors
          v-if="data?.errors && data.errors.length > 0"
          :errors="data.errors"
          class="mx-auto mt-4"
          max-width="800"
        />
      </v-col>
      <v-col cols="12" md="6">
        <inference-results-table :record-id="id"></inference-results-table>
      </v-col>
    </v-row>
  </v-container>
</template>
