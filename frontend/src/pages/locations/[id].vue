<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useLocationGet(id.value);
const { mutate, isPending } = useLocationUpdate();
const { mutate: deleteMutate, isPending: deletePending } = useLocationDelete();
const deleteAction = useActionAndRoute({
  action: () => deleteMutate({ id: id.value }),
  gotoUrl: "/locations"
});
</script>
<template>
  <v-container>
    <locations-form
      v-if="data"
      :loading="isFetching || isPending"
      :data="{
        id: data?.id,
        name: data?.name,
        lat: data?.lat,
        long: data?.long,
        remarks: data?.remarks,
        created_at: data?.created_at,
        updated_at: data?.updated_at
      }"
      :show-delete-button="true"
      :delete-button-dialog-title="`Delete Location: ${data?.name}?`"
      :delete-button-dialog-message="`Are you sure you want to delete location ${data?.name}?`"
      :delete-button-loading="deletePending"
      @delete="deleteAction"
      @submit="
        (data) => {
          mutate(data);
        }
      "
    ></locations-form>
  </v-container>
</template>
