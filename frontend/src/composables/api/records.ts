import { ref } from 'vue';

export const useRecordGet = useCreateGet(QUERY_KEYS.records, GqlGetRecordById);
export const useRecordUpdate = useCreateMutation(QUERY_KEYS.records, GqlUpdateRecord);

export const useRecordsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.records,
  paginatedQueryFn: GqlGetRecordsPaginated,
});

/**
 * Fetch a list of unique years from records.
 * Returns a reactive object: { data, pending, error, fetchYears }
 */
export const useRecordYears = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<number[]>([]);

  /**
   * Fetch all unique years from records.
   */
  const fetchYears = async () => {
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
            query getRecordYears {
              records {
                record_datetime
              }
            }
            `,
        }
      });

      // Extract years from record_datetime and get unique values
      data.value = Array.from(
        new Set(
          (result.data?.records ?? [])
            .map((r: any) => new Date(r.record_datetime).getFullYear())
            .filter((y: number) => !isNaN(y))
        )
      ).sort((a, b) => a - b);
    } catch (err) {
      error.value = err;
      console.error('Error fetching record years:', err);
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchYears
  };
};