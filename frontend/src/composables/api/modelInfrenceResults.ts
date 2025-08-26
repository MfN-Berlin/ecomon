export const useRecordModelInferenceResultsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.recordModelInferenceResults,
  paginatedQueryFn: GqlGetRecordModelInferenceResults
});
