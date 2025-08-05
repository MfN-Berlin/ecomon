export const useRecordGet = useCreateGet(QUERY_KEYS.records, GqlGetRecordById);
export const useRecordUpdate = useCreateMutation(QUERY_KEYS.records, GqlUpdateRecord);

export const useRecordsPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.records,
  pagniatedQueryFn: GqlGetRecordsPagniated,
  // Set the default items per page for this composable
  defaultOptions: { itemsPerPage: 100 }
});
