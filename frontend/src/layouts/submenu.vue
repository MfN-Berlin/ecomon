<script lang="ts" setup>
const locations = useLocationFilter({});
const models = useModelFilter({});
const sites = useSiteFilter({});

const route = useRoute();

const active = computed(() => {
  if (route.path.startsWith("/locations")) {
    return locations;
  } else if (route.path.startsWith("/models")) {
    return models;
  } else if (route.path.startsWith("/sites")) {
    return sites;
  }
  return null;
});

const data = computed(() => (active.value ? active.value.data.value : []));
const loading = computed(() => (active.value ? active.value.isFetching.value : false));

const rootPath = computed(() => {
  if (route.path.startsWith("/locations")) {
    return "/locations";
  } else if (route.path.startsWith("/models")) {
    return "/models";
  } else if (route.path.startsWith("/sites")) {
    return "/sites";
  }
  return "";
});

const name = computed(() => {
  return rootPath.value.slice(1, -1);
});

function fetch() {
  active.value?.fetchNextPage();
}

/**
 * 1. Receives the Search Term: It gets the searchTerm string from the app-navigation-sub-bar 
 *    component when the user types in the search box.
 * 2. Identifies the Active Data Source: It looks at the active computed property. This property 
 *    checks the current URL to determine if you are on the /locations, /models, or /sites page.
 * 3. Delegates the Search: It calls the onSearchTermChanged method on whichever data filter 
 *    is currently active.
 * 
 * In simple terms:
 * If you are on the /locations page, this function effectively does:
 * locations.onSearchTermChanged(searchTerm);
 * If you are on the /sites page, it does: sites.onSearchTermChanged(searchTerm);
 * 
 * So, it doesn't perform the search itself. It just ensures the search request gets to 
 * the correct data-handling logic (useLocationFilter, useModelFilter, etc.) to be executed. 
 * 
 * The actual query is deined in: ecomon/frontend/src/queries/sites.gql
 * Also see: ecomon/frontend/src/composables/api/factories/useCreateFilter.ts
 */
function onSearchTermChanged(searchTerm: string) {
  console.log("Search term changed:", searchTerm);
  console.log("Active filter:", active.value);
  // Server-side search handled by the active composable
  active.value?.onSearchTermChanged?.(searchTerm);
}
</script>

<template>
  <app-sub-navbar-layout>
    <template #sub-nav-bar>
      <app-navigation-sub-bar
        :name="name"
        :data="data as Item[]"
        :root-path="rootPath"
        :loading="loading"
        @fetch-next-page="fetch"
        @search="onSearchTermChanged"
      ></app-navigation-sub-bar>
    </template>
    <template #content>
      <slot></slot>
    </template>
  </app-sub-navbar-layout>
</template>