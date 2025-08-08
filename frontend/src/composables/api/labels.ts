export const useLabelsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.labels,
  paginatedQueryFn: GqlGetLabelsPaginated
});


export const useLabelsFilter = useCreateFilter({
  baseQueryKey: QUERY_KEYS.labels,
  filterQueryFn: GqlGetLabelsList
});