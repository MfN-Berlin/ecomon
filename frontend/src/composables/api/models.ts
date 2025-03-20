export const useModelGet = useCreateGet(QUERY_KEYS.models, GqlGetModelById);
export const useModelList = useCreateList(QUERY_KEYS.models, GqlGetModelList);
export const useModelFilter = useCreateFilter({
  baseQueryKey: QUERY_KEYS.models,
  filterQueryFn: GqlFilterModel
});

export const useModelUpdate = useCreateMutation(QUERY_KEYS.models, GqlUpdateModel);
export const useModelInsert = useCreateMutation(QUERY_KEYS.models, GqlInsertModel);
export const useModelDelete = useCreateMutation(QUERY_KEYS.models, GqlDeleteModel);

export const useModelPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.models,
  pagniatedQueryFn: GqlGetModelsPagniated
});

export const useInferenceSiteTimespan = useCreateAction(GqlAnalyseSiteTimespan);
