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
function onSearchTermChanged(searchTerm: string) {
  active.value?.onSearchTermChanged(searchTerm);
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
