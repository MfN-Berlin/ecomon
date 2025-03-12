<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const { mutate, isPending } = useModelInsert({ redirect: "onSuccess", redirectBasePath: "/models" });
</script>
<template>
  <v-container>
    <h1 class="text-headline pb-4">Create Model:</h1>
    <models-form :loading="isPending" @submit="mutate"></models-form>
  </v-container>
</template>
