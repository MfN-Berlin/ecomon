<script setup lang="ts">
const { $logger } = useNuxtApp();
const props = defineProps<{
  loading?: boolean | Ref<boolean> | undefined;
}>();
const { loading } = toRefs(props);
const emit = defineEmits<{
  (e: "loadMore"): void;
}>();

const trigger = ref(null);
useIntersectionObserver(trigger, ([{ isIntersecting }]) => {
  $logger.debug("InfiniteScroller trigger element isIntersecting", isIntersecting);
  if (isIntersecting && !loading.value) {
    emit("loadMore");
  }
});
</script>

<template>
  <slot name="content"></slot>
  <span ref="trigger"></span>
  <slot v-if="loading" name="loading"></slot>
</template>
