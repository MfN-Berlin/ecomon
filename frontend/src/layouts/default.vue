<script lang="ts" setup></script>
<template>
  <!-- Hidden on smaller than large devices -->
  <transition name="fade">
    <app-navigation-main-bar v-if="!$vuetify.display.lgAndUp"></app-navigation-main-bar>
  </transition>

  <app-navigation-side-drawer> </app-navigation-side-drawer>

  <slot></slot>
</template>
<style scoped></style>
