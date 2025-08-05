export const useLabelsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.labels,
  paginatedQueryFn: GqlGetLabelsPaginated
});
