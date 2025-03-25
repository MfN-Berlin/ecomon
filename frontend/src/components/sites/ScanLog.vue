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

const colorMap: Record<string, string> = {
  failed: "error",
  done: "primary",
  canceled: "warning"
};

watch(open, (val) => {
  if (val) {
    refetch();
  }
});
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-eye">
    Scan Log
    <v-dialog v-model="open" width="auto" max-width="800px" class="h-75" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-eye"></v-icon>
          <v-toolbar-title>Add / Delete Directory Log</v-toolbar-title>
        </v-toolbar>
        <v-card-text class="h-75 overflow-y-auto">
          <v-timeline class="h-75 mr-6" align="start" side="end">
            <v-timeline-item
              v-for="log in logs"
              :key="log.id"
              :dot-color="colorMap[log.status]"
              :icon="log.topic === 'scan_directories' ? 'mdi-plus' : 'mdi-delete'"
              size="small"
            >
              <div class="d-flex">
                <div class="d-flex flex-column">
                  <common-date-time-text
                    icon="mdi-clock-start"
                    class="me-4"
                    :time="log.created_at"
                    size="small"
                  ></common-date-time-text>
                  <common-date-time-duration
                    icon="mdi-clock-fast"
                    :start="log.created_at"
                    :end="log.updated_at"
                    size="small"
                  ></common-date-time-duration>
                </div>
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
                  <div v-if="log.error" class="text-caption">Error: {{ log.error }}</div>
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
