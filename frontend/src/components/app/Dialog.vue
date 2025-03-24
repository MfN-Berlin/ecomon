<script setup lang="ts">
const store = useDialogStore();
const pending = ref(false);

async function handleConfirm() {
  pending.value = true;
  await store.onOk();
  pending.value = false;
}
</script>

<template>
  <v-dialog v-model="store.visible" :persistent="store.options.persistent" width="400">
    <v-card>
      <v-toolbar color="primary" class="px-4">
        <v-icon :icon="store.options.icon"></v-icon>
        <v-toolbar-title>{{ store.title }}</v-toolbar-title>
      </v-toolbar>
      <v-card-title class="text-h6"> </v-card-title>
      <v-card-text>
        {{ store.message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="text" :disabled="pending" @click="store.onCancel">
          {{ store.options.cancelLabel }}
        </v-btn>
        <v-btn color="error" variant="flat" autofocus @click="handleConfirm">
          {{ store.options.okLabel }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
