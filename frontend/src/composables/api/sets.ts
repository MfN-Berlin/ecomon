export const useSetGet = useCreateGet(QUERY_KEYS.sets, GqlGetSetsById);

export const useSetsUpdate = useCreateMutation(QUERY_KEYS.sets, GqlUpdateSet);
export const useSetsInsert = useCreateMutation(QUERY_KEYS.sets, GqlInsertSet);
export const useSetDelete = useCreateMutation(QUERY_KEYS.sets, GqlDeleteSet);

export const useSetsList = useCreateList(QUERY_KEYS.sets, GqlGetSetsList);
export const useSetsFilter = useCreateFilter({
  baseQueryKey: QUERY_KEYS.sets,
  filterQueryFn: GqlFilterSets
});

export const useSetsPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.sets,
  pagniatedQueryFn: GqlGetSetsPagniated
});
