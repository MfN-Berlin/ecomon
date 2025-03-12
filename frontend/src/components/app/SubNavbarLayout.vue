<template>
  <transition name="fade">
    <app-navigation-main-bar v-if="!$vuetify.display.lgAndUp"></app-navigation-main-bar>
  </transition>

  <app-navigation-side-drawer> </app-navigation-side-drawer>
  <v-navigation-drawer width="190" mobile-breakpoint="sm">
    <slot name="sub-nav-bar"></slot>
  </v-navigation-drawer>
  <slot name="content"></slot>
</template>
