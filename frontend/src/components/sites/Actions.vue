<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
  siteName: string;
}>();
</script>

<template>
  <v-card v-bind="$attrs">
    <v-card-actions>
      <sites-actions-create-voucher :site-id="siteId" :site-name="siteName" variant="tonal" />
      <sites-actions-inference :site-id="siteId" variant="tonal"></sites-actions-inference>
    </v-card-actions>
  </v-card>
</template>
