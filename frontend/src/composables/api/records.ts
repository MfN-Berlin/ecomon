export const useRecordGet = useCreateGet(QUERY_KEYS.records, GqlGetRecordById);
export const useRecordUpdate = useCreateMutation(QUERY_KEYS.records, GqlUpdateRecord);

export const useRecordsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.records,
  paginatedQueryFn: GqlGetRecordsPaginated,
});
