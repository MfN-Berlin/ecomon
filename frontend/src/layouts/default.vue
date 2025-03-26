<script lang="ts" setup></script>
<template>
  <!-- Hidden on smaller than large devices -->
  <transition name="fade">
    <app-navigation-main-bar v-if="!$vuetify.display.lgAndUp"></app-navigation-main-bar>
    <app-bread-crumbs
      v-else
      class="position-sticky top-0"
      :style="{ marginLeft: '220px', zIndex: 1000 }"
      bg-color="surface"
    ></app-bread-crumbs>
  </transition>
  <app-navigation-side-drawer> </app-navigation-side-drawer>

  <slot></slot>
</template>
<style scoped></style>
