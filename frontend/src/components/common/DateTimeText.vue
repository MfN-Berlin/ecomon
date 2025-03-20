<template>
  <span :class="`${sizeMap[props.size]}`">
    <time :datetime="time.toISOString()"> {{ formattedDate }} </time>
  </span>
</template>

<script lang="ts" setup>
type DateTimeTextProps = {
  time: string;
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
const { $dayjs } = useNuxtApp();
const props = withDefaults(defineProps<DateTimeTextProps>(), {
  relativeTime: true,
  relativeTimeSpan: 1000 * 60 * 60 * 24, // 1 day
  showSeconds: false,
  showTime: true,
  showDate: true,
  size: "medium"
});
const time = computed(() => {
  if (props.preventLocal) {
    return $dayjs.utc(props.time);
  }
  return $dayjs.utc(props.time).local();
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
