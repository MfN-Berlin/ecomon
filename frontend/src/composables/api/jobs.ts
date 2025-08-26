export const useCancelJob = useCreateAction(GqlCancelJob);

export const useGetJobsPaginated = useCreatePaginated({
  baseQueryKey: QUERY_KEYS.jobs,
  paginatedQueryFn: GqlGetJobsPaginated
});

export const useGetSiteJobsByTopic = useCreateList(QUERY_KEYS.siteJobs, GqlGetSiteJobsByTopic);
