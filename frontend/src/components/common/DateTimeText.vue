<template>
  <span :class="`${sizeMap[props.size]}`" v-bind="$attrs">
    <v-icon v-if="props.icon" :icon="props.icon" :size="props.size" class="mr-1"></v-icon>
    <time :datetime="time.toISOString()"> {{ formattedDate }} </time>
  </span>
</template>

<script lang="ts" setup>
type DateTimeTextProps = {
  time: string;
  icon?: string | null;
  relativeTime?: boolean;
  relativeTimeSpan?: number;
  showSeconds?: boolean;
  showTime?: boolean;
  showDate?: boolean;
  size?: "small" | "medium" | "large";
  preventLocal?: boolean;
};

const sizeMap = {
  small: "text-caption",
  medium: "text-body-2",
  large: "text-h6"
};
const { $dayjs, $currentTime } = useNuxtApp();
const props = withDefaults(defineProps<DateTimeTextProps>(), {
  relativeTime: true,
  relativeTimeSpan: 1000 * 60 * 60 * 24, // 1 day
  showSeconds: false,
  showTime: true,
  showDate: true,
  size: "medium",
  icon: null
});
const time = ref($dayjs.utc(props.time).local() ? $dayjs.utc(props.time).local() : $dayjs.utc(props.time));

watch($currentTime, () => {
  const value = $dayjs.utc(props.time).local() ? $dayjs.utc(props.time).local() : $dayjs.utc(props.time);
  if (value != time.value) {
    time.value = value;
  }
});
const formattedDate = computed(() => {
  const timestamp = time.value;
  const now = $dayjs();
  const diff = now.diff(timestamp);

  if (props.relativeTime && diff <= props.relativeTimeSpan) {
    return timestamp.fromNow();
  } else {
    const formatOptions: Intl.DateTimeFormatOptions = {};

    if (props.showDate) {
      formatOptions.year = "numeric";
      formatOptions.month = "2-digit";
      formatOptions.day = "2-digit";
    }
    if (props.showTime) {
      formatOptions.hour = "2-digit";
      formatOptions.minute = "2-digit";
      if (props.showSeconds) {
        formatOptions.second = "2-digit";
      }
      formatOptions.hourCycle = "h23";
    }

    return new Intl.DateTimeFormat(undefined, formatOptions).format(timestamp.toDate());
  }
});
</script>
