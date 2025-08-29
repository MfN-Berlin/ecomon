export const useLabelsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.labels,
  paginatedQueryFn: GqlGetLabelsPaginated
});

// Fetch all unique species labels (id and name) associated with a given record_id and confidence threshold
export const useAllSpeciesLabels = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<{ id: string; name: string }[]>([]);

  /**
   * Fetch all unique species labels for a given recordId, confidence threshold, and (optionally) modelId.
   * @param recordId The record_id to filter model_inference_results by.
   * @param threshold The minimum confidence value to filter by.
   * @param modelId (Optional) The model_id to filter by.
   */
  const fetchAllSpeciesLabels = async (
    recordId: string | number,
    threshold: number = 0,
    modelId?: number | null
  ) => {
    pending.value = true;
    error.value = null;

    try {
      const config = useRuntimeConfig();

      // Build the where clause dynamically
      const where: any = {
        record_id: { _eq: recordId },
        confidence: { _gte: threshold }
      };
      if (modelId != null) {
        where.model_id = { _eq: modelId };
      }

      const result = await $fetch(config.public.GQL_HOST, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          query: `
            query getAllSpeciesLabelsForRecord($where: model_inference_results_bool_exp!) {
              model_inference_results(where: $where) {
                label {
                  id
                  name
                }
              }
            }
          `,
          variables: {
            where
          }
        }
      });
      console.log('Fetched species labels:', result);

      // Extract unique label objects by id
      const seen = new Set();
      const uniqueLabels: { id: string; name: string }[] = [];
      for (const mir of result.data?.model_inference_results ?? []) {
        const label = mir.label;
        if (label && label.id && !seen.has(label.id)) {
          seen.add(label.id);
          uniqueLabels.push({ id: label.id, name: label.name });
        }
      }
      // Sort alphabetically by name
      uniqueLabels.sort((a, b) => a.name.localeCompare(b.name));
      data.value = uniqueLabels;

    } catch (err) {
      error.value = err;
      console.error('Error fetching all species labels for record:', err);
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchAllSpeciesLabels
  };
};

// Simple search composable for labels
// search by label prefix
export const useLabelsSearch = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref(null);
  
  const searchLabels = async (searchTerm: string) => {
    console.log("searchLabels called");
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
      console.log("Raw GraphQL result:", result);

      
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

/**
 * Fetch all unique species labels (id and name) for a list of site IDs, a model, a threshold, and a year.
 * If any argument is missing/None/empty, returns an empty list.
 * @param siteIds Array of site IDs to filter by.
 * @param modelId The model_id to filter by.
 * @param threshold The minimum confidence value to filter by.
 * @param year The year to filter by (record_datetime must be in this year).
 */
export const useAllSpeciesLabelsForSites = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<{ id: string; name: string }[]>([]);

  const fetchAllSpeciesLabelsForSites = async (
    siteIds: (string | number)[] | null | undefined,
    modelId: number | string | null | undefined,
    threshold: number | null | undefined = 0,
    year: number | null | undefined = null
  ) => {
    console.log("fetchAllSpeciesLabelsForSites called");

    // If any required argument is missing, return empty list
    if (
      !siteIds || !Array.isArray(siteIds) || siteIds.length === 0 ||
      modelId == null || threshold == null || year == null
    ) {
      data.value = [];
      return;
    }

    pending.value = true;
    error.value = null;

    try {
      const config = useRuntimeConfig();

      // Build the where clause for the query
      const where: any = {
        site_id: { _in: siteIds },
        model_id: { _eq: modelId },
        confidence: { _gte: threshold },
        // Filter by year using a _gte and _lt range on record_datetime
        record_datetime: {
          _gte: `${year}-01-01T00:00:00`,
          _lt: `${year + 1}-01-01T00:00:00`
        }
      };

      const result = await $fetch(config.public.GQL_HOST, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          query: `
            query getAllSpeciesLabelsForSites($where: model_inference_results_bool_exp!) {
              model_inference_results(where: $where) {
                label {
                  id
                  name
                }
              }
            }
          `,
          variables: {
            where
          }
        }
      });
      console.log("Raw GraphQL result:", result);


      // Extract unique label objects by id
      const seen = new Set();
      const uniqueLabels: { id: string; name: string }[] = [];
      for (const mir of result.data?.model_inference_results ?? []) {
        const label = mir.label;
        if (label && label.id && !seen.has(label.id)) {
          seen.add(label.id);
          uniqueLabels.push({ id: label.id, name: label.name });
        }
      }
      uniqueLabels.sort((a, b) => a.name.localeCompare(b.name));
      data.value = uniqueLabels;

    } catch (err) {
      error.value = err;
      data.value = [];
      console.error('Error fetching all species labels for sites:', err);
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchAllSpeciesLabelsForSites
  };
};

