<script lang="ts" setup>
type DateTimeTextProps = {
  start: string;
  end: string;
  icon?: string | null;
  format?: string;
  showFullDuration?: boolean;
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
  format: "D[d] H[h] m[m]",
  showFullDuration: false,
  size: "medium",
  icon: null,
  preventLocal: false
});

const startTime = computed(() => {
  if (props.preventLocal) {
    return $dayjs.utc(props.start);
  }
  return $dayjs.utc(props.start).local();
});

const endTime = computed(() => {
  if (props.preventLocal) {
    return $dayjs.utc(props.end);
  }
  return $dayjs.utc(props.end).local();
});

const formattedDuration = computed(() => {
  const start = startTime.value;
  const end = endTime.value;

  // Calculate duration in milliseconds
  const durationMs = end.diff(start);

  if (durationMs < 0) {
    return "Invalid duration";
  }

  // For short durations or when full duration is requested
  if (props.showFullDuration) {
    const duration = $dayjs.duration(durationMs);
    return duration.format(props.format);
  }

  // Human-readable format
  const seconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);

  if (years > 0) {
    return years === 1 ? "1 year" : `${years} years`;
  } else if (months > 0) {
    return months === 1 ? "1 month" : `${months} months`;
  } else if (days > 0) {
    return days === 1 ? "1 day" : `${days} days`;
  } else if (hours > 0) {
    return hours === 1 ? "1 hour" : `${hours} hours`;
  } else if (minutes > 0) {
    return minutes === 1 ? "1 minute" : `${minutes} minutes`;
  } else {
    return seconds === 1 ? "1 second" : `${seconds} seconds`;
  }
});
</script>
<template>
  <span :class="`${sizeMap[props.size]}`">
    <v-icon v-if="props.icon" :icon="props.icon" :size="props.size" class="mr-1"></v-icon>
    <time :datetime="`${startTime.toISOString()}/${endTime.toISOString()}`"> {{ formattedDuration }} </time>
  </span>
</template>
