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
   * Fetch the latest workflow reports (one per prefix) and transform data by model.
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
                order_by: [{prefix: asc}, {report_date: desc}, {model_name: asc}]
              ) {
                id
                report_date
                prefix
                site_id
                wav_size_bytes
                wav_count
                record_count
                skipped_records
                db_import
                model_name
                model_processed
                model_visible
                model_status
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
        // Transform data: group by prefix and get latest report per prefix
        const reports = result.data?.workflow_reports || [];

        // Create a map to store the latest report per prefix
        const reportsByPrefix = new Map();

        for (const report of reports) {
          const key = report.prefix;
          if (!reportsByPrefix.has(key)) {
            reportsByPrefix.set(key, {
              id: report.id,
              report_date: report.report_date,
              prefix: report.prefix,
              site_id: report.site_id,
              wav_size_bytes: report.wav_size_bytes,
              wav_count: report.wav_count,
              record_count: report.record_count,
              skipped_records: report.skipped_records,
              db_import: report.db_import,
              created_at: report.created_at,
              models: []
            });
          }

          const prefixData = reportsByPrefix.get(key);
          // Add model data
          prefixData.models.push({
            model_name: report.model_name,
            model_processed: report.model_processed,
            model_visible: report.model_visible,
            model_status: report.model_status,
            visible_in_ui: report.visible_in_ui
          });
        }

        // Convert map to array and flatten model data into top-level fields
        const transformedReports = Array.from(reportsByPrefix.values()).map(report => {
          const transformed = { ...report };

          // Create columns for each model
          for (const model of report.models) {
            transformed[`${model.model_name}_processed`] = model.model_processed;
            transformed[`${model.model_name}_visible`] = model.model_visible;
            transformed[`${model.model_name}_status`] = model.model_status;
          }

          // Store original models array for reference
          transformed.models = report.models;

          return transformed;
        });

        data.value = {
          workflow_reports: transformedReports
        };
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