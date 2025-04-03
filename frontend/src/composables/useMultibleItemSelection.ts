export function useMultipleItemSelection<TItem>() {
  const selectedItems = ref<TItem[]>([]);

  const selectAll = ref<boolean>(false);

  const select = (item: TItem) => {
    // check if item is already in selectedItems

    selectedItems.value.push(item);

    return { selectedItems, selectAll, select };
  };
}
