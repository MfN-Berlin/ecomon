<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const { mutate, isPending } = useSetsInsert({ redirect: "onSuccess", redirectBasePath: "/sets" });
</script>
<template>
  <v-container>
    <h1 class="text-headline pb-4">Create Set:</h1>
    <sets-form :loading="isPending" @submit="mutate"></sets-form>
  </v-container>
</template>
