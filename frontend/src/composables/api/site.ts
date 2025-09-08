import { ref } from 'vue';

export const useSiteGet = useCreateGet(QUERY_KEYS.sites, GqlGetSiteById);
export const useSiteList = useCreateList(QUERY_KEYS.sites, GqlGetSiteList);
export const useSiteFilter = useCreateFilter({
  baseQueryKey: QUERY_KEYS.sites,
  filterQueryFn: GqlFilterSite
});

export const useSiteUpdate = useCreateMutation(QUERY_KEYS.sites, GqlUpdateSite);
export const useSiteInsert = useCreateMutation(QUERY_KEYS.sites, GqlInsertSite);
export const useSiteDelete = useCreateMutation(QUERY_KEYS.sites, GqlDeleteSite);

export const useSiteDirectoryInsert = useCreateMutation(QUERY_KEYS.sites, GqlInsertSiteDirectory, {
  dataCacheField: "site_id"
});
export const useSiteDirectoryDelete = useCreateMutation(QUERY_KEYS.sites, GqlDeleteSiteDirectory, {
  dataCacheField: "site_id"
});

export const useSiteListDataDirectories = useCreateList(QUERY_KEYS.dataDirectories, GqlListDataDirectories);

export const useSitePaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.sites,
  paginatedQueryFn: GqlGetSitesPaginated
});

export const useSiteScanAllDirectories = useCreateAction(GqlScanAllSiteDirectories);

export const useSiteScanDirectory = useCreateAction(GqlScanSiteDirectory);

export const useSiteGetFirstAndLastRecordDate = useCreateGet(
  QUERY_KEYS.siteFirstLastRecordDate,
  GqlGetSiteFirstAndLastRecordDate
);

/**
 * Fetch all sites (id and name).
 * Returns a reactive object: { data, pending, error, fetchAllSites }
 */
export const useAllSites = () => {
  const pending = ref(false);
  const error = ref(null);
  const data = ref<{ id: string; name: string }[]>([]);

  /**
   * Fetch all sites with id and name.
   */
  const fetchAllSites = async () => {
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
            query getAllSites {
              sites(order_by: [{prefix: asc}, {name: asc}]) {
                id
                name
                prefix
              }
            }
          `,
        }
      });

      const sites = result.data?.sites ?? [];
      data.value = sites;

    } catch (err) {
      error.value = err;
      console.error('Error fetching all sites:', err);
    } finally {
      pending.value = false;
    }
  };

  return {
    data,
    pending,
    error,
    fetchAllSites
  };
};