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
        additional_docker_arguments: data?.additional_docker_arguments,
        additional_model_arguments: data?.additional_model_arguments,
        window_size: data?.window_size,
        step_size: data?.step_size,
        remarks: data?.remarks,
        created_at: data?.created_at,
        updated_at: data?.updated_at
      }"
      @submit="
        (data) => {
          const payload = { ...data };
          delete payload.name;
          mutate(payload);
        }
      "
    ></models-form>
  </v-container>
</template>
