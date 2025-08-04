<script lang="ts" setup></script>
<template>
  <v-app>
    <!-- MainBar only visible on narrow screens -->
    <app-navigation-main-bar></app-navigation-main-bar>
    
    <!-- SideDrawer for navigation -->
    <app-navigation-side-drawer></app-navigation-side-drawer>

    <!-- Main content area -->
    <v-main>
      <slot></slot>
    </v-main>
  </v-app>
</template>
<style scoped></style>