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

export const useSitePagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.sites,
  pagniatedQueryFn: GqlGetSitesPagniated
});

export const useSiteScanAllDirectories = useCreateAction(GqlScanAllSiteDirectories);

export const useSiteScanDirectory = useCreateAction(GqlScanSiteDirectory);
