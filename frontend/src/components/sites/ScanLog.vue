<script lang="ts" setup>
import { loggers } from "winston";

const props = defineProps<{
  siteId: number;
}>();
const open = ref(false);
const { data: logs, refetch } = useGetSiteJobsByTopic({
  siteId: props.siteId,
  _or: [{ topic: { _eq: "scan_directories" } }, { topic: { _eq: "delete_records_from_site" } }]
});

watch(open, (val) => {
  if (val) {
    refetch();
  }
});
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-eye"
    >Scan Log
    <v-dialog v-model="open" width="auto" max-width="800px" class="h-75" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" title="Scan Log"></v-toolbar>

        <v-card-text class="h-75 overflow-y-auto">
          <v-timeline class="h-75 mr-6" align="start" side="end">
            <v-timeline-item
              v-for="log in logs"
              :key="log.id"
              dot-color="primary"
              :icon="log.topic === 'scan_directories' ? 'mdi-plus' : 'mdi-delete'"
              :color="log.error ? 'error' : 'primary'"
              size="small"
            >
              <div class="d-flex">
                <common-date-time-text
                  class="me-4"
                  :time="log.created_at"
                  size="small"
                ></common-date-time-text>
                <div>
                  <strong>{{ log.metadata?.directories?.join(", ") }}</strong>
                  <div v-if="log.topic === 'scan_directories'" class="text-caption">
                    Added Records:
                    {{ log.result?.added_records }}
                  </div>
                  <div v-else class="text-caption">
                    Deleted Records:
                    {{ log.result?.deleted_records }}
                  </div>
                  <div v-if="log.error" class="text-caption">
                    {{ log.error }}
                  </div>
                </div>
              </div>
            </v-timeline-item>
          </v-timeline>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
