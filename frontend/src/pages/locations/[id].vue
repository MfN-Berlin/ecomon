<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useLocationGet(id.value);
const { mutate, isPending } = useLocationUpdate();
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
      @submit="
        (data) => {
          mutate(data);
        }
      "
    ></locations-form>
  </v-container>
</template>
