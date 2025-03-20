<script setup lang="ts">
const { $dayjs } = useNuxtApp();
const formattedDate = computed(() => {
  if (!model.value) return "";
  return $dayjs(model.value).format("YYYY-MM-DD HH:mm");
});
const model = defineModel<Date>();
const props = defineProps<{
  dialogTitle?: string;
}>();
const visible = ref(false);
const time = ref("11:15");
const date = ref<Date>(new Date());
watch(visible, (val) => {
  if (val) {
    time.value = $dayjs(model.value).format("HH:mm");
    date.value = model.value ?? new Date();
  }
});
function onOk() {
  const dateString = `${date.value.getFullYear()}-${date.value.getMonth()}-${date.value.getDate()}`;
  const timeString = `${time.value}:00`;
  console.log(`${dateString} ${timeString}`);
  model.value = $dayjs(`${dateString} ${timeString}`).toDate();
  visible.value = false;
}
</script>
<template>
  <v-text-field v-model="formattedDate" v-bind="$attrs">
    <v-dialog v-model="visible" activator="parent" width="auto">
      <template v-slot:default="{ isActive }">
        <v-card class="">
          <v-toolbar v-if="props.dialogTitle" color="primary" :title="props.dialogTitle"> </v-toolbar>
          <v-row no-gutters>
            <v-date-picker v-model="date" class="mt-2" show-adjacent-months></v-date-picker>
            <v-time-picker
              v-model="time"
              format="24hr"
              color="primary"
              header-color="primary"
            ></v-time-picker>
          </v-row>

          <v-card-actions>
            <v-btn text="cancel" min-width="100" @click="isActive.value = false"></v-btn>
            <v-btn text="ok" min-width="100" color="primary" variant="tonal" @click="onOk"></v-btn>
          </v-card-actions>
        </v-card>
      </template>
    </v-dialog>
  </v-text-field>
</template>
