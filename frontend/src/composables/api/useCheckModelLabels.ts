export default function useCheckModelLabels() {
  const loading = ref<boolean>(false);
  const { onError } = useErrorHandling();
  async function checkModelLabels(modelId: number, labelIds: number[]) {
    loading.value = true;
    try {
      const result = await Promise.all(
        labelIds.map((labelId) => GqlDoesModelLabelExist({ modelId, labelId }))
      );
      return result.map((r) => r.data?.length > 0);
    } catch (error) {
      onError(error);
    } finally {
      loading.value = false;
    }
    return [];
  }

  return { checkModelLabels, loading };
}
