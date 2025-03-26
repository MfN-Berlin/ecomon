<script setup lang="ts">
type BreadcrumbItem = {
  text: string;
  disabled?: boolean;
  href?: string;
};
const router = useRouter();
const items = ref<BreadcrumbItem[]>([]);

function updateBreadCrumbs(path: string) {
  const pathSplits = path.split("/").slice(1);
  items.value = [
    {
      text: "Home",
      href: "/"
    },
    ...pathSplits.map((path, index) => {
      return {
        text: path.charAt(0).toUpperCase() + path.slice(1),
        href: "/" + pathSplits.slice(0, index + 1).join("/"),
        disabled: index === pathSplits.length - 1
      };
    })
  ];
}

onMounted(() => {
  updateBreadCrumbs(router.currentRoute.value.path);
});

router.afterEach((to) => {
  updateBreadCrumbs(to.path);
});
</script>
<template>
  <v-breadcrumbs density="compact" v-bind="$attrs">
    <template v-slot:prepend>
      <v-icon icon="mdi-home" size="small"></v-icon>
    </template>
    <template v-for="(item, index) in items" :key="index">
      <v-breadcrumbs-item :disabled="item.disabled">
        <nuxt-link v-if="!item.disabled" :to="item.href">
          {{ item.text }}
        </nuxt-link>
        <span v-else>
          {{ item.text }}
        </span>
      </v-breadcrumbs-item>
      <v-breadcrumbs-divider v-if="index < items.length - 1"> / </v-breadcrumbs-divider>
    </template>
  </v-breadcrumbs>
</template>

<style scoped>
a {
  color: var(--v-primary-base);
  text-decoration: none;
}
</style>
