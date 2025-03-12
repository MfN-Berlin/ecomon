<script setup lang="ts">
definePageMeta({ layout: "submenu" });
const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useModelGet(id);
const { mutate, isPending } = useModelUpdate();
</script>
<template>
  <v-container>
    <models-form
      v-if="data"
      :loading="isFetching || isPending"
      :data="{
        id: data?.id,
        name: data?.name,
        short_name: data?.short_name,
        endpoint: data?.endpoint,
        remarks: data?.remarks,
        created_at: data?.created_at,
        updated_at: data?.updated_at
      }"
      @submit="
        (data) => {
          mutate(data);
        }
      "
    ></models-form>
  </v-container>
</template>
