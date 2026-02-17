export const useRecordModelInferenceResultsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.recordModelInferenceResults,
  paginatedQueryFn: GqlGetRecordModelInferenceResults
});

/**
 * Composable for fetching minutes with acoustic activity
 */
export function useMinutesWithActivity(params: Ref<{
  speciesId: number | null;
  modelId: number | null;
  siteId: number | null;
  year: number | null;
  threshold: number;
} | null>) {
  return useQuery({
    queryKey: computed(() => [QUERY_KEYS.minutesWithActivity, params.value]),
    queryFn: async () => {
      console.log('useMinutesWithActivity queryFn called with params:', params.value);

      if (!params.value || !params.value.speciesId || !params.value.modelId || !params.value.siteId || !params.value.year) {
        console.log('Missing required params, returning 0');
        return 0;
      }

      const startDate = `${params.value.year}-01-01T00:00:00`;
      const endDate = `${params.value.year + 1}-01-01T00:00:00`;

      const variables = {
        modelId: Number(params.value.modelId),
        speciesId: Number(params.value.speciesId),
        siteId: Number(params.value.siteId),
        threshold: params.value.threshold,
        startDate: startDate,
        endDate: endDate
      };

      console.log('GraphQL request variables:', variables);

      try {
        const response = await GqlCountMinutesWithActivity(variables);

        console.log('GraphQL response:', response);
        // Count the results as done in hasura.R
        const count = Array.isArray(response.model_inference_results_max_confidence)
          ? response.model_inference_results_max_confidence.length
          : 0;
        console.log('Returning count:', count);
        return count;
      } catch (error) {
        console.error('GraphQL request failed:', error);
        throw error;
      }
    },
    enabled: computed(() => {
      const isEnabled = !!params.value?.speciesId && !!params.value?.modelId && !!params.value?.siteId && !!params.value?.year;
      console.log('Query enabled:', isEnabled, 'params:', params.value);
      return isEnabled;
    }),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}