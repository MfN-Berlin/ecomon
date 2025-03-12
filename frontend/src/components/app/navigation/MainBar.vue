<script setup lang="ts">
import { useUiStore } from "~/stores/ui";

// Adjust the path to your store accordingly
const uiStore = useUiStore();
function toggleDrawer() {
  uiStore.setDrawerVisibility(!uiStore.drawerVisible);
}
</script>
<template>
  <v-app-bar color="primary" density="compact">
    <template v-slot:prepend>
      <v-app-bar-nav-icon @click="toggleDrawer()"></v-app-bar-nav-icon>
    </template>
    <app-bread-crumbs></app-bread-crumbs>
    <v-spacer></v-spacer>
    <template v-slot:append>
      <transition name="fade">
        <v-btn v-if="!$vuetify.display.xs" icon="mdi-dots-vertical"></v-btn>
      </transition>
    </template>
  </v-app-bar>
</template>
