export const useRecordModelInferenceResultsPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.recordModelInferenceResults,
  pagniatedQueryFn: GqlGetRecordModelInferenceResults
});
