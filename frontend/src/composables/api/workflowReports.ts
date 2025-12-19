import { ref } from 'vue';

/**
 * Fetch ready site IDs from workflow_reports where visible_in_ui is true.
 * Returns a reactive object: { data, pending, error, fetchReadySites }
 */
export const useReadySites = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<number[]>([]);

  /**
   * Fetch site IDs marked as visible in UI from workflow_reports.
   */
  const fetchReadySites = async () => {
    pending.value = true;
    error.value = null;

    try {
      const config = useRuntimeConfig();

      console.log('🔍 Fetching ready sites from:', config.public.GQL_HOST);

      const result = await $fetch(config.public.GQL_HOST, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          query: `
            query GetReadySites {
              workflow_reports(
                distinct_on: [site_id]
                where: {
                  visible_in_ui: {_eq: true}
                  site_id: {_is_null: false}
                }
                order_by: [{site_id: asc}, {report_date: desc}]
              ) {
                site_id
              }
            }
          `,
        }
      });

      console.log('📦 Raw GraphQL result:', result);
      console.log('📊 Result data:', result.data);
      console.log('📋 Workflow reports:', result.data?.workflow_reports);

      const siteIds = result.data?.workflow_reports?.map((r: any) => r.site_id) ?? [];

      console.log('✅ Extracted site IDs:', siteIds);
      console.log('   - Type:', typeof siteIds);
      console.log('   - Is Array:', Array.isArray(siteIds));
      console.log('   - Length:', siteIds.length);

      data.value = siteIds;

    } catch (err) {
      console.error('❌ Error fetching ready sites:', err);
      error.value = err;
      // Fallback to empty array on error
      data.value = [];
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchReadySites
  };
};

/**
 * Fetch all workflow reports.
 * Returns a reactive object: { data, pending, error, fetchReports }
 */
export const useWorkflowReports = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<any>(null);

  /**
   * Fetch the latest workflow reports (one per prefix).
   */
  const fetchReports = async () => {
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
            query GetLatestWorkflowReports {
              workflow_reports(
                distinct_on: [prefix]
                order_by: [{prefix: asc}, {report_date: desc}]
              ) {
                id
                report_date
                prefix
                site_id
                wav_size_bytes
                wav_count
                record_count
                db_import
                birdid_medium_processed
                birdid_medium
                birdid_medium_visible
                visible_in_ui
                created_at
              }
            }
          `,
        }
      });

      if (result.errors) {
        console.error('GraphQL errors:', result.errors);
        error.value = result.errors[0]?.message || 'GraphQL query failed';
      } else {
        data.value = result.data;
      }

    } catch (err: any) {
      console.error('Error fetching workflow reports:', err);
      error.value = err.message || 'Failed to fetch reports';
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchReports
  };
};