<template>
  <v-system-bar color="primary">
    <div style="width: 240px"></div>
    <app-bread-crumbs></app-bread-crumbs>
    <v-spacer></v-spacer>
    <v-icon v-for="[icon] in links" :key="icon" link>{{ icon }}</v-icon>
  </v-system-bar>
</template>
<script setup lang="ts">
const links = ref<string[][]>([
  ["mdi-tools", "Settings"],
  ["mdi-logout-variant", "Logout"]
]);
</script>
<style scoped></style>
