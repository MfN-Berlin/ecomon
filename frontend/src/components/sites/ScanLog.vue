<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();
const open = ref(false);
const { data: logs } = useGetSiteJobsByTopic({
  siteId: props.siteId,
  _or: [{ topic: { _eq: "scan_directories" } }, { topic: { _eq: "delete_records_from_site" } }]
});
defineExpose({
  open: () => {
    open.value = true;
  }
});
</script>

<template>
  <v-dialog v-model="open" max-width="500px" class="h-75">
    <v-card class="h-75">
      <v-card-title class="position-sticky top-0 bg-white" style="z-index: 1000">Scan Log</v-card-title>
      <v-card-text>
        <v-list class="overflow-y-auto h-75" density="compact">
          <template v-for="log in logs" :key="log.id">
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="grey">{{
                  log.topic === "scan_directories" ? "mdi-plus" : "mdi-delete"
                }}</v-icon>
              </template>
              <v-list-item class="text-body-2">{{ log.payload.directories.join(", ") }}</v-list-item>
              <template v-slot:append>
                <common-date-time-text :time="log.created_at as string" size="small" />
              </template>
            </v-list-item>
            <v-divider></v-divider>
          </template>
        </v-list>
      </v-card-text>
      <v-card-actions class="position-sticky bottom-0 bg-white">
        <v-btn @click="open = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
