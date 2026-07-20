# How to Create a New Page to Display Data from a Table

## Overview
Follow this pattern to create a new data table page that fetches and displays records from any database table, with pagination, sorting, and search capabilities.

### Step-by-Step Guide
#### Step 1: Ensure Database Table Exists in Hasura
Your PostgreSQL table must be tracked by Hasura with proper permissions.

Check:

* Table exists in Hasura metadata (hasura/metadata/databases/ecomon/tables/)
* Select permissions granted to the user role
* Object relationships defined for foreign keys

**Example structure for public_your_table.yaml:**

```
table:
  name: your_table
  schema: public
object_relationships:
  - name: related_entity
    using:
      foreign_key_constraint_on: related_entity_id
select_permissions:
  - role: user
    permission:
      columns: [id, name, related_entity_id, created_at, ...]
      filter: {}
```

#### Step 2: Add Query Key Constant
**File: **
frontend/src/utils/consts.ts

Add your table to the QUERY_KEYS enum:

```
export const enum QUERY_KEYS {
  // ... existing keys
  yourTable = "yourTable",  // singular, lowercase
}
```

#### Step 3: Create API Composable
**File:**
frontend/src/composables/api/yourTable.ts

```
// 1. Define the item type matching your GraphQL response
export type YourTableItem = {
  id: number;
  name: string;
  related_entity_id: number;
  // ... other fields
  related_entity?: {
    id: number;
    name: string;
  };
};

// 2. Create the paginated GraphQL query function
export const GqlGetYourTablePaginated = async (variables: any) => {
  const config = useRuntimeConfig();

  // Convert order_by format
  const order_by = variables.order_by.length > 0
    ? variables.order_by.map((order: any) => {
        const obj: any = {};
        obj[order.key] = order.order;
        return obj;
      })
    : [{ id: "desc" }];

  // Use where only if not empty
  const where = Object.keys(variables.where).length === 0 ? null : variables.where;

  try {
    // Query for paginated items
    const itemsResult = await $fetch(config.public.GQL_HOST, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: {
        query: `
          query getYourTablePaginated(
            $limit: Int!
            $offset: Int!
            $order_by: [your_table_order_by!]!
            $where: your_table_bool_exp
          ) {
            your_table(
              limit: $limit
              offset: $offset
              order_by: $order_by
              where: $where
            ) {
              id
              name
              related_entity_id
              created_at
              related_entity {
                id
                name
              }
            }
          }
        `,
        variables: { limit: variables.limit, offset: variables.offset, order_by, where },
      },
    });

    // Query for total count
    const countResult = await $fetch(config.public.GQL_HOST, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: {
        query: `
          query getYourTableTotalCount($where: your_table_bool_exp) {
            your_table(where: $where) {
              id
            }
          }
        `,
        variables: { where },
      },
    });

    const items = itemsResult.data?.your_table || [];
    const count = countResult.data?.your_table?.length || 0;

    return {
      items,
      total: { aggregate: { count } },
    };
  } catch (error) {
    console.error("Error fetching data:", error);
    return { items: [], total: { aggregate: { count: 0 } } };
  }
};

// 3. Export the paginated composable
export const useYourTablePaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.yourTable,
  paginatedQueryFn: GqlGetYourTablePaginated,
});
```

**Note**: If your_table_aggregate is available in your Hasura schema, you can simplify the count query to:

```
query getYourTableTotalCount($where: your_table_bool_exp) {
  your_table_aggregate(where: $where) {
    aggregate {
      count
    }
  }
}
```

#### Step 4: Create the Page Component
**File:**
frontend/src/pages/your-table/index.vue

```
<script setup lang="ts">
import type { YourTableItem } from "~/composables/api/yourTable";
import { useYourTablePaginated } from "~/composables/api/yourTable";

// Optional: Set full-width layout for better table display
definePageMeta({ layout: "full-width" });

// Pagination options
const paginationOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
  { value: 100, title: '100' },
];

// Initialize paginated composable
const {
  page,
  itemsPerPage,
  sortBy,
  items,
  totalItems,
  isLoading: loading,
  handleReset,
  handleSearch
} = useYourTablePaginated();

// Set default sorting (optional)
sortBy.value = [{ key: 'id', order: 'desc' }];

// Utility for nested properties
function getNested(obj: any, key: string) {
  return key.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
}

// Define table headers
const headers = [
  {
    title: "ID",
    key: "id",
    align: "end",
    sortable: true,
    search: false  // Disable search for this column
  },
  {
    title: "Name",
    key: "name",
    align: "start",
    sortable: true,
    search: { operator: "_like", type: "text" }  // Text search with LIKE
  },
  {
    title: "Related Entity",
    key: "related_entity.name",  // Nested property
    align: "start",
    sortable: true,
    search: { operator: "_like", type: "text" }
  },
  {
    title: "Created",
    key: "created_at",
    align: "start",
    sortable: true,
    search: false
  },
] as const;
</script>

<template>
  <v-container fluid>
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="items"
      :items-length="totalItems"
      :loading="loading"
      item-value="id"
      :items-per-page-options="paginationOptions"
    >
      <!-- Custom row template for nested data -->
      <template #item="{ item }">
        <tr>
          <td v-for="header in headers" :key="header.key">
            {{ getNested(item, header.key) }}
          </td>
        </tr>
      </template>
    </v-data-table-server>
  </v-container>
</template>
```

#### Step 5: Add Navigation Link
**File:**
…/src/components/app/navigation/SideDrawer.vue

Find the appropriate section (usually "Data Tables") and add:

```
{
  icon: "mdi-icon-name",  // Choose a Material Design icon
  text: "Your Table",
  route: "/your-table"
}
```

#### Step 6: Verify Everything Works
1. Navigation link appears and routes to /your-table
2. Table loads data without errors
3. Pagination controls work
4. Sorting by clicking column headers works
5. Search/filtering works on searchable columns
