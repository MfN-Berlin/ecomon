export const useRecordModelInferenceResultsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.recordModelInferenceResults,
  paginatedQueryFn: GqlGetRecordModelInferenceResults
});

/**
 * Composable for fetching minutes with acoustic activity
 */
export function useMinutesWithActivity(params: Ref<{
  speciesId: number | null;
  modelId: number | null;
  siteId: number | null;
  year: number | null;
  threshold: number;
} | null>) {
  return useQuery({
    queryKey: computed(() => [QUERY_KEYS.minutesWithActivity, params.value]),
    queryFn: async () => {
      console.log('useMinutesWithActivity queryFn called with params:', params.value);

      if (!params.value || !params.value.speciesId || !params.value.modelId || !params.value.siteId || !params.value.year) {
        console.log('Missing required params, returning 0');
        return 0;
      }

      const startDate = `${params.value.year}-01-01T00:00:00`;
      const endDate = `${params.value.year + 1}-01-01T00:00:00`;

      const variables = {
        modelId: Number(params.value.modelId),
        speciesId: Number(params.value.speciesId),
        siteId: Number(params.value.siteId),
        threshold: params.value.threshold,
        startDate: startDate,
        endDate: endDate
      };

      console.log('GraphQL request variables:', variables);

      try {
        const response = await GqlCountMinutesWithActivity(variables);

        console.log('GraphQL response:', response);
        // Count the results as done in hasura.R
        const count = Array.isArray(response.model_inference_results_max_confidence)
          ? response.model_inference_results_max_confidence.length
          : 0;
        console.log('Returning count:', count);
        return count;
      } catch (error) {
        console.error('GraphQL request failed:', error);
        throw error;
      }
    },
    enabled: computed(() => {
      const isEnabled = !!params.value?.speciesId && !!params.value?.modelId && !!params.value?.siteId && !!params.value?.year;
      console.log('Query enabled:', isEnabled, 'params:', params.value);
      return isEnabled;
    }),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

/**
 * Composable for fetching voucher data
 */
export async function fetchVoucherData(params: {
  speciesId: number;
  modelId: number;
  siteId: number;
  year: number;
  threshold: number;
}) {
  const startDate = `${params.year}-01-01T00:00:00`;
  const endDate = `${params.year + 1}-01-01T00:00:00`;

  const variables = {
    modelId: Number(params.modelId),
    speciesId: Number(params.speciesId),
    siteId: Number(params.siteId),
    threshold: params.threshold,
    startDate: startDate,
    endDate: endDate
  };

  console.log('Fetching voucher data with variables:', variables);

  try {
    const response = await GqlGetVoucherData(variables);
//    console.log('Voucher data response:', response);
    console.log('First item record:', response.model_inference_results_max_confidence[0]?.record);
    return response.model_inference_results_max_confidence;
  } catch (error) {
    console.error('Failed to fetch voucher data:', error);
    throw error;
  }
}

/**
 * Fetch voucher data with random sampling
 */
export async function fetchVoucherDataSampled(params: {
  speciesId: number;
  modelId: number;
  siteId: number;
  year: number;
  threshold: number;
  sampleSize: number;
}) {
  // Fetch all voucher data
  const allData = await fetchVoucherData(params);

  // If sample size is greater than or equal to available data, return all
  if (params.sampleSize >= allData.length) {
    console.log(`Sample size (${params.sampleSize}) >= available data (${allData.length}), returning all data`);
    return allData;
  }

  // Random sampling without replacement
  const sampled = [];
  const indices = new Set<number>();

  while (sampled.length < params.sampleSize) {
    const randomIndex = Math.floor(Math.random() * allData.length);
    if (!indices.has(randomIndex)) {
      indices.add(randomIndex);
      sampled.push(allData[randomIndex]);
    }
  }

  // Sort the sampled data by site prefix, label name, record_datetime, and start_time
  sampled.sort((a, b) => {
    // Sort by site prefix
    const siteCompare = (a.record.site?.prefix || '').localeCompare(b.record.site?.prefix || '');
    if (siteCompare !== 0) return siteCompare;

    // Sort by label name
    const labelCompare = (a.label.name || '').localeCompare(b.label.name || '');
    if (labelCompare !== 0) return labelCompare;

    // Sort by record_datetime
    const dateCompare = new Date(a.record.record_datetime).getTime() - new Date(b.record.record_datetime).getTime();
    if (dateCompare !== 0) return dateCompare;

    // Sort by start_time
    return a.start_time - b.start_time;
  });

  console.log(`Randomly sampled ${sampled.length} records from ${allData.length} total`);
  return sampled;
}