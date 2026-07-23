// Define the Thresholds type for the items
// This should match what's returned from the GraphQL query
export type ThresholdItem = {
  id: number;
  label_id: number;
  model_id: number;
  threshold: number;
  threshold_type?: string;
  is_final: boolean;
  set_at: string;
  label?: {
    id: number;
    name: string;
  };
  model?: {
    id: number;
    name: string;
  };
};

/**
 * Custom paginated query function for thresholds
 * This fetches thresholds with pagination, filtering, and sorting support
 * Note: Does not use thresholds_aggregate since it's not available in the Hasura schema
 * 
 * IMPORTANT: This query returns only the LATEST threshold (by set_at) for each
 * unique combination of model_id + label_id. Filtering is done client-side
 * after fetching all matching records.
 */
export const GqlGetThresholdsPaginated = async (variables: any) => {
  const config = useRuntimeConfig();

  console.log("GqlGetThresholdsPaginated called with:", JSON.parse(JSON.stringify(variables)));

  // Convert where conditions - use only if not empty
  const where = Object.keys(variables.where).length === 0 ? null : variables.where;

  console.log("Query variables:", { limit: variables.limit, offset: variables.offset, where });

  try {
    // Get ALL matching records (no limit/offset yet) so we can filter to latest per group
    const allItemsResult = await $fetch(config.public.GQL_HOST, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        query: `
          query getAllThresholds($where: thresholds_bool_exp) {
            thresholds(
              where: $where
            ) {
              id
              label_id
              model_id
              threshold
              threshold_type
              is_final
              set_at
              label {
                id
                name
              }
              model {
                id
                name
              }
            }
          }
        `,
        variables: {
          where,
        },
      },
    });

    console.log("All thresholds result:", allItemsResult);

    // Filter to keep only the latest (by set_at) for each model_id + label_id combination
    let allItems: ThresholdItem[] = allItemsResult.data?.thresholds || [];
    console.log("All items with threshold_type:", allItems.map(item => ({ id: item.id, threshold_type: item.threshold_type })));
    const latestMap = new Map<string, ThresholdItem>();
    allItems.forEach((item) => {
      const key = `${item.model_id}_${item.label_id}`;
      const existing = latestMap.get(key);
      if (!existing || new Date(item.set_at) > new Date(existing.set_at)) {
        latestMap.set(key, item);
      }
    });
    
    // Get the filtered items (latest per model+label)
    const filteredItems = Array.from(latestMap.values());
    
    // Get total count of distinct combinations
    const totalCount = filteredItems.length;

    // Apply user's sorting on the filtered items
    // variables.order_by is in Hasura format: [{ field: "asc" }] or [{ label: { name: "asc" } }]
    // We need to extract the sort key and direction, handling nested objects
    const hasura_order_by = variables.order_by.length > 0
      ? variables.order_by
      : [{ id: "desc" }];
    
    if (hasura_order_by && hasura_order_by.length > 0 && filteredItems.length > 0) {
      // Flatten the order_by to get sortKey and direction
      // Simple format: { id: "desc" } -> { sortKey: "id", direction: "desc" }
      // Nested format: { label: { name: "asc" } } -> { sortKey: "label.name", direction: "asc" }
      const flattenOrder = (orderObj: any): { sortKey: string; direction: string } | null => {
        const firstKey = Object.keys(orderObj)[0];
        if (!firstKey) return null;
        
        const value = orderObj[firstKey];
        if (typeof value === 'string') {
          // Simple: { id: "desc" }
          return { sortKey: firstKey, direction: value };
        } else if (typeof value === 'object' && value !== null) {
          // Nested: { label: { name: "asc" } }
          const nestedKey = Object.keys(value)[0];
          return { sortKey: `${firstKey}.${nestedKey}`, direction: value[nestedKey] };
        }
        return null;
      };
      
      const flattened = flattenOrder(hasura_order_by[0]);
      if (!flattened) {
        // Fallback to default sorting
        filteredItems.sort((a, b) => b.id - a.id);
      } else {
        const { sortKey, direction } = flattened;
        
        const getValue = (obj: any, path: string) => {
          if (!path) return undefined;
          return path.split('.').reduce((o: any, k: string) => (o ? o[k] : undefined), obj);
        };
        
        filteredItems.sort((a, b) => {
          const aVal = getValue(a, sortKey);
          const bVal = getValue(b, sortKey);
        
        if (aVal === undefined && bVal === undefined) return 0;
        if (aVal === undefined) return 1;
        if (bVal === undefined) return -1;
        
        // Handle different types
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return direction === 'asc' 
            ? aVal.localeCompare(bVal) 
            : bVal.localeCompare(aVal);
        }
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return direction === 'asc' ? aVal - bVal : bVal - aVal;
        }
        if (typeof aVal === 'boolean' && typeof bVal === 'boolean') {
          return direction === 'asc' 
            ? (aVal === bVal ? 0 : aVal ? 1 : -1) 
            : (aVal === bVal ? 0 : aVal ? -1 : 1);
        }
        
        // Fallback to string comparison
        return direction === 'asc' 
          ? String(aVal).localeCompare(String(bVal)) 
          : String(bVal).localeCompare(String(aVal));
      });
      }
    }

    // Apply pagination on the filtered and sorted items
    const offset = variables.offset || 0;
    const limit = variables.limit || 100;
    const items = filteredItems.slice(offset, offset + limit);

    console.log("Paginated items:", items);
    console.log("Total distinct combinations:", totalCount);

    return {
      items,
      total: { aggregate: { count: totalCount } },
    };
  } catch (error) {
    console.error("Error fetching thresholds:", error);
    // Fallback to empty
    return {
      items: [],
      total: { aggregate: { count: 0 } },
    };
  }
};

// Export the paginated composable
export const useThresholdsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.thresholds,
  paginatedQueryFn: GqlGetThresholdsPaginated,
});

/**
 * GraphQL mutation to update a threshold's is_final status
 */
export const GqlUpdateThresholdIsFinal = async (variables: { id: number; is_final: boolean; threshold_type: string }) => {
  const config = useRuntimeConfig();

  console.log("Updating threshold:", variables);

  try {
    const result = await $fetch(config.public.GQL_HOST, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        query: `
          mutation updateThresholdIsFinal($id: Int!, $is_final: Boolean!, $threshold_type: String!) {
            update_thresholds_by_pk(
              pk_columns: { id: $id }
              _set: { is_final: $is_final, threshold_type: $threshold_type, set_at: "now()" }
            ) {
              id
              is_final
              threshold_type
              set_at
            }
          }
        `,
        variables: {
          id: variables.id,
          is_final: variables.is_final,
          threshold_type: variables.threshold_type,
        },
      },
    });

    console.log("Update threshold result:", result);
    return result;
  } catch (error) {
    console.error("Error updating threshold:", error);
    throw error;
  }
};

// Export the mutation composable
export const useThresholdUpdate = useCreateMutation(
  QUERY_KEYS.thresholds,
  GqlUpdateThresholdIsFinal,
  { dataCacheField: "id" }
);
