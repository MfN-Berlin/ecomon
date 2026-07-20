<script lang="ts" setup>
import { ref } from "vue";
import { useRuntimeConfig } from '#imports';

import { useUiStore } from "~/stores/ui";

const uiStore = useUiStore();
const config = useRuntimeConfig();

export type NavigationPoint = {
  icon?: string;
  text: string;
  route?: string;
  action?: () => void;
  childs?: NavigationPoint[];
};

const getAirflowUrl = () => {
  // Read apiBaseUrl from environment variable
  const apiBaseUrl = config.public.API_BASE_URL || config.public.apiBaseUrl;

  const isLocalhost = typeof window !== 'undefined' &&
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

  if (apiBaseUrl && !isLocalhost) {
    // Production case: apiBaseUrl is set and not on localhost, use it directly
    return `${apiBaseUrl}/airflow/home`;
  } else {
    // Development case: on localhost or no apiBaseUrl
    const currentPath = window.location.pathname;
    const pathParts = currentPath.split('/').filter(Boolean);
    const detectedSubPath = pathParts.length > 0 ? `/${pathParts[0]}` : devSubPath;

    return `http://localhost${detectedSubPath}/airflow/home`;
  }
};

const links: NavigationPoint[] = [
  { icon: "mdi-home", text: "Home", route: "/" },
  { icon: "mdi-access-point-network", text: "Sites", route: "/sites" },
  { icon: "mdi-map-marker-multiple-outline", text: "Locations", route: "/locations" },
  { icon: "mdi-brain", text: "Models", route: "/models" },
  { icon: "mdi-monitor-dashboard", text: "Dashboard", route: "/dashboard" },
  { icon: "mdi-tag-outline", text: "Voucher (Prototype)", route: "/voucher" },
  {
    icon: "mdi-table",
    text: "Data Tables",
    childs: [
      { icon: "mdi-record-rec", text: "Records", route: "/records" },
      { icon: "mdi-bird", text: "Labels", route: "/labels" },
      { icon: "mdi-gauge", text: "Thresholds", route: "/thresholds" }
    ]
  },
  {
    icon: "mdi-transit-connection-variant",
    text: "Workflow",
    childs: [
      { icon: "mdi-chart-box-outline", text: "Overview", route: "/workflow" },
      { icon: "mdi-play-circle-outline", text: "Jobs", route: "/jobs" },
      {
        icon: "mdi-robot-outline",
        text: "Automation",
        route: getAirflowUrl()
      }
    ]
  },
//  {
//    icon: "mdi-cog-outline",
//    text: "Admin",
//    childs: [
//    ]
//  }
];

const drawerVisible = computed({
  get() {
    return uiStore.drawerVisible;
  },
  set(val) {
    uiStore.setDrawerVisibility(val);
  }
});
</script>

<template>
  <v-navigation-drawer v-model="drawerVisible" :width="230">
    <v-sheet class="px-8 py-2">
      <v-img cover src="/logo.png"></v-img>
    </v-sheet>

    <v-divider></v-divider>

    <v-list color="primary" density="compact" nav>
      <template v-for="{ icon, text, route, childs, action } in links" :key="route">
        <v-list-group v-if="childs" :value="text">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" :prepend-icon="icon" :title="text"></v-list-item>
          </template>
          <v-list-item
            v-for="{ icon: subIcon, text: subText, route: subRoute, action: childAction } in childs"
            :key="subRoute"
            :to="subText !== 'Automation' ? subRoute : undefined"
            :href="subText === 'Automation' ? subRoute : undefined"
            link
            :target="subText === 'Automation' ? '_blank' : undefined"
            @click="childAction"
          >
            <template v-if="subIcon" v-slot:prepend>
              <v-icon>{{ subIcon }}</v-icon>
            </template>
            <v-list-item-title>
              {{ subText }}
              <v-tooltip activator="parent" location="end" v-if="subText === 'Automation'">
                requires additional login
              </v-tooltip>
            </v-list-item-title>
          </v-list-item>
        </v-list-group>
        <v-list-item v-else :to="route" link class="p-0" @click="action">
          <template v-slot:prepend>
            <v-icon>{{ icon }}</v-icon>
          </template>
          <v-list-item-title>{{ text }}</v-list-item-title>
        </v-list-item>
      </template>
    </v-list>
    <v-divider></v-divider>

    <template v-slot:append>
      <app-dark-mode-toggle class="ml-4 mb-2" />
    </template>
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