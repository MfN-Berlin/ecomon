// Define the Thresholds type for the items
// This should match what's returned from the GraphQL query
export type ThresholdItem = {
  id: number;
  label_id: number;
  model_id: number;
  threshold: number;
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
 */
export const GqlGetThresholdsPaginated = async (variables: any) => {
  const config = useRuntimeConfig();

  console.log("GqlGetThresholdsPaginated called with:", JSON.parse(JSON.stringify(variables)));

  // Convert order_by from the format used by useCreatePaginated
  // [{key: "field", order: "asc"}] to Hasura format [{field: "asc"}]
  const order_by = variables.order_by.length > 0
    ? variables.order_by.map((order: any) => {
        const obj: any = {};
        obj[order.key] = order.order;
        return obj;
      })
    : [{ id: "desc" }];

  // Convert where conditions - use only if not empty
  const where = Object.keys(variables.where).length === 0 ? null : variables.where;

  console.log("Query variables:", { limit: variables.limit, offset: variables.offset, order_by, where });

  try {
    // Get the paginated items
    const itemsResult = await $fetch(config.public.GQL_HOST, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        query: `
          query getThresholdsPaginated(
            $limit: Int!
            $offset: Int!
            $order_by: [thresholds_order_by!]!
            $where: thresholds_bool_exp
          ) {
            thresholds(
              limit: $limit
              offset: $offset
              order_by: $order_by
              where: $where
            ) {
              id
              label_id
              model_id
              threshold
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
          limit: variables.limit,
          offset: variables.offset,
          order_by,
          where,
        },
      },
    });

    console.log("Thresholds items result:", itemsResult);

    // Get the total count
    const countResult = await $fetch(config.public.GQL_HOST, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        query: `
          query getThresholdsTotalCount($where: thresholds_bool_exp) {
            thresholds(where: $where) {
              id
            }
          }
        `,
        variables: {
          where,
        },
      },
    });

    console.log("Thresholds count result:", countResult);

    // Check the actual data structure
    const items = itemsResult.data?.thresholds || [];
    const count = countResult.data?.thresholds?.length || 0;

    console.log("Items:", items);
    console.log("Count:", count);

    return {
      items,
      total: { aggregate: { count } },
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
