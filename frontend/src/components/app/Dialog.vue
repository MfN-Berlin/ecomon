<script setup lang="ts">
const store = useDialogStore();
const pending = ref(false);

async function handleConfirm() {
  pending.value = true;
  await store.callbackFn();
  pending.value = false;
  store.visible = false;
}
</script>

<template>
  <v-dialog v-model="store.visible" width="400">
    <v-card>
      <v-card-title class="text-h6"> {{ store.title }} </v-card-title>
      <v-card-text>
        {{ store.message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="text" :disabled="pending" @click="store.visible = false">
          {{ store.options.cancelLabel }}
        </v-btn>
        <v-btn color="error" variant="flat" @click="handleConfirm"> {{ store.options.okLabel }} </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
