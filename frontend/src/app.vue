<script lang="ts" setup>
import { useDisplay } from "vuetify";

// Ensure you import the correct function based on your Vuetify version
import { useUiStore } from "@/stores/ui";

const uiStore = useUiStore();
const display = useDisplay();
onMounted(() => {
  uiStore.setDrawerVisibility(display.lgAndUp.value);
});
</script>

<template>
  <v-app id="inspire">
    <AppToastProvider />
    <NuxtLayout>
      <NuxtLoadingIndicator />
      <v-main class="d-flex flex-column" style="height: 100vh">
        <app-bread-crumbs bg-color="surface"></app-bread-crumbs>

        <div class="flex-grow-1 left-0 right-0 min-h-0 overflow-y-auto">
          <NuxtPage></NuxtPage>
        </div>

        <app-audio-player />
        <app-dialog />
      </v-main>
    </NuxtLayout>
  </v-app>
</template>

<style></style>
