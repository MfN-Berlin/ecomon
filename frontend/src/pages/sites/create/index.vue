<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const { mutate, isPending } = useSiteInsert({ redirect: "onSuccess", redirectBasePath: "/sites" });
const router = useRouter();
</script>
<template>
  <v-container>
    <h1 class="text-headline pb-4">Create Collection:</h1>
    <sites-form :loading="isPending" @submit="mutate" @reset="router.back()"></sites-form>
  </v-container>
</template>
