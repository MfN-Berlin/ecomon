<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const { mutate, isPending } = useLocationInsert({ redirect: "onSuccess", redirectBasePath: "/locations" });
</script>
<template>
  <v-container>
    <h1 class="text-headline pb-4">Create Location:</h1>
    <locations-form :loading="isPending" @submit="mutate"></locations-form>
  </v-container>
</template>
