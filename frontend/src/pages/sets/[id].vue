<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const router = useRouter();
const id = computed(() => parseInt(router.currentRoute.value.params.id as string));

const { data, isFetching } = useSetGet(id.value);
const { mutate, isPending } = useSetsUpdate({ redirect: true, redirectBasePath: "/sets" });
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <sets-form
          v-if="data"
          :loading="isFetching || isPending"
          :data="{
            id: data?.id,
            name: data?.name,
            remarks: data?.remarks,
            created_at: data?.created_at,
            updated_at: data?.updated_at
          }"
          @submit="
            (data) => {
              mutate(data);
            }
          "
        ></sets-form>
      </v-col>
      <v-col cols="12" md="6">
        <!-- <sets-information v-if="data" :data="data.site_information" />
        <sets-directory-list v-if="data" class="mt-4" :siteId="data.id" :data="data.site_directories" /> -->
      </v-col>
    </v-row>
  </v-container>
</template>
