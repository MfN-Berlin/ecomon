import { ref } from 'vue';

export const useModelGet = useCreateGet(QUERY_KEYS.models, GqlGetModelById);
export const useModelList = useCreateList(QUERY_KEYS.models, GqlGetModelList);
export const useModelFilter = useCreateFilter({
  baseQueryKey: QUERY_KEYS.models,
  filterQueryFn: GqlFilterModel
});

export const useModelUpdate = useCreateMutation(QUERY_KEYS.models, GqlUpdateModel);
export const useModelInsert = useCreateMutation(QUERY_KEYS.models, GqlInsertModel);
export const useModelDelete = useCreateMutation(QUERY_KEYS.models, GqlDeleteModel);

export const useModelPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.models,
  paginatedQueryFn: GqlGetModelsPaginated
});

export const useInferenceSiteTimespan = useCreateAction(GqlInferenceSiteTimespan);

/**
 * Fetch all models (id and name).
 * Returns a reactive object: { data, pending, error, fetchAllModels }
 */
export const useAllModels = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<{ id: string; name: string }[]>([]);

  /**
   * Fetch all models with id and name.
   */
  const fetchAllModels = async () => {
    pending.value = true;
    error.value = null;

    try {
      const config = useRuntimeConfig();

      const result = await $fetch(config.public.GQL_HOST, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          query: `
            query getAllModels {
              models(order_by: {name: asc}) {
                id
                name
              }
            }
          `,
        }
      });

      data.value = result.data?.models ?? [];
    } catch (err) {
      error.value = err;
      console.error('Error fetching all models:', err);
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchAllModels
  };
};