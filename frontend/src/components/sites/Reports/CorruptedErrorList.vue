<script lang="ts" setup>
const props = defineProps<{
  reportDateString: string;
  corruptedFiles: {
    id: number;
    filename: string;
    errors: string;
  }[];
}>();

const open = ref(false);
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-image-broken">
    Corrupted files
    <v-dialog v-model="open" max-width="800px" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-image-broken"></v-icon>
          <v-toolbar-title>Corrupted Files in Report {{ reportDateString }}</v-toolbar-title>
        </v-toolbar>
        <v-card-text class="h-75 overflow-y-auto">
          <v-virtual-scroll :height="600" :items="corruptedFiles">
            <template v-slot:default="{ item }">
              <v-list-item>
                <span class="text-subtitle-2 mb-0"
                  >File:
                  <NuxtLink :to="`/records/${item.id}`">{{ item.filename }} </NuxtLink>
                </span>

                <records-errors :errors="item.errors" :title="false" density="compact" direction="column" />
              </v-list-item>
              <v-divider />
            </template>
          </v-virtual-scroll>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
