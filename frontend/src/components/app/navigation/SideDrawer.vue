<script lang="ts" setup>
import { ref } from "vue";

import { useUiStore } from "~/stores/ui";

const uiStore = useUiStore();

export type NavigationPoint = {
  icon?: string;
  text: string;
  route?: string;
  action?: () => void;
  childs?: NavigationPoint[];
};
const links: NavigationPoint[] = [
  { icon: "mdi-home", text: "Home", route: "/" },
  { icon: "mdi-cube-send", text: "Jobs", route: "/jobs" },
  { icon: "mdi-access-point-network", text: "Sites", route: "/sites" },
  { icon: "mdi-file-document-multiple-outline", text: "Sets", route: "/sets" },
  { icon: "mdi-map-marker-multiple-outline", text: "Locations", route: "/locations" },
  { icon: "mdi-brain", text: "Models", route: "/models" },
  {
    icon: "mdi-table",
    text: "Data Tables",
    childs: [
      { icon: "mdi-record-rec", text: "Records", route: "/records" },
      { icon: "mdi-bird", text: "Labels", route: "/labels" }
    ]
  }
];

const drawerVisible = computed({
  get() {
    return uiStore.drawerVisible;
  },
  set(val) {
    uiStore.setDrawerVisibility(val);
  }
});
// Watch for changes in the drawerVisible property and update the store
</script>
<template>
  <v-navigation-drawer v-model="drawerVisible" :width="220">
    <v-sheet class="px-8 py-2">
      <v-img cover src="/logo.png"></v-img>
    </v-sheet>

    <v-divider></v-divider>

    <v-list color="primary" density="compact" nav>
      <nuxt-link to="route" custom>
        <template v-for="{ icon, text, route, childs, action } in links" :key="route">
          <v-list-group v-if="childs" :value="text">
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" :prepend-icon="icon" :title="text"></v-list-item>
            </template>
            <v-list-item
              v-for="{ icon: subIcon, text: subText, route: subRoute, action: childAction } in childs"
              :key="subRoute"
              :to="subRoute"
              link
              @click="childAction"
            >
              <template v-if="subIcon" v-slot:prepend>
                <v-icon>{{ subIcon }}</v-icon>
              </template>
              <v-list-item-title>{{ subText }}</v-list-item-title>
            </v-list-item>
          </v-list-group>
          <v-list-item v-else :to="route" link class="p-0" @click="action">
            <template v-slot:prepend>
              <v-icon>{{ icon }}</v-icon>
            </template>

            <v-list-item-title>{{ text }}</v-list-item-title>
          </v-list-item>
        </template>
      </nuxt-link>
    </v-list>
    <template v-slot:append> </template>
  </v-navigation-drawer>
</template>

<style scoped>
.v-list-item .nuxt-link {
  color: inherit;
  text-decoration: none;
}

.v-list-item--active {
  background-color: rgb(var(--v-theme-background));
}
</style>
