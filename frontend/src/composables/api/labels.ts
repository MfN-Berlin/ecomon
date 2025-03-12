export const useLabelsPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.labels,
  pagniatedQueryFn: GqlGetLabelsPagniated
});
