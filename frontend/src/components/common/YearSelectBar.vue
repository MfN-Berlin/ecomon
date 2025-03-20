<script setup lang="ts">
const props = defineProps<{
  startDate?: Date | null;
  endDate?: Date | null;
}>();
const emit = defineEmits<{
  (e: "select", year: number): void;
}>();

const years = computed(() => {
  if (!props.startDate || !props.endDate) {
    return [];
  }

  const startYear = props.startDate.getFullYear();
  const endYear = props.endDate.getFullYear();
  const years: number[] = [];
  console.log("startYear", startYear);
  console.log("endYear", endYear);
  for (let year = endYear; year >= startYear; year--) {
    years.push(year);
  }

  return years;
});
</script>
<template>
  <v-slide-group v-if="years.length > 0" show-arrows v-bind="$attrs">
    <v-slide-group-item v-for="year in years" :key="year" v-slot="{ isSelected, toggle }">
      <v-tooltip :text="`Select ${year}`">
        <template v-slot:activator="{ props: tooltipProps }">
          <v-btn
            v-bind="tooltipProps"
            :color="isSelected ? 'secondary' : undefined"
            class="ma-1"
            @click="
              (event: any) => {
                emit('select', year);
                toggle(event);
              }
            "
            >{{ year }}</v-btn
          >
        </template>
      </v-tooltip>
    </v-slide-group-item>
  </v-slide-group>
</template>
