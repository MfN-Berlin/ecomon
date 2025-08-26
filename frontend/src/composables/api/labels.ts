export const useLabelsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.labels,
  paginatedQueryFn: GqlGetLabelsPaginated
});


// Simple search composable for labels
export const useLabelsSearch = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref(null);
  
  const searchLabels = async (searchTerm: string) => {
    pending.value = true;
    error.value = null;
    
    try {
      const config = useRuntimeConfig();
      const where = searchTerm 
        ? { name: { _ilike: `${searchTerm}%` } }
        : {};
      
      const result = await $fetch(config.public.GQL_HOST, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          query: `
            query getLabelsList($where: labels_bool_exp, $order_by: [labels_order_by!], $limit: Int) {
              labels(where: $where, order_by: $order_by, limit: $limit) {
                id
                name
              }
            }
          `,
          variables: {
            where,
            order_by: { name: 'asc' },
            limit: 50
          }
        }
      });
      
      data.value = result.data;
    } catch (err) {
      error.value = err;
      console.error('Error searching labels:', err);
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    searchLabels
  };
};