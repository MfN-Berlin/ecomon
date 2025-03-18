export const useCancelJob = useCreateAction(GqlCancelJob);

export const useGetJobsPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.jobs,
  pagniatedQueryFn: GqlGetJobsPagniated
});

export const useGetSiteJobsByTopic = useCreateList(QUERY_KEYS.siteJobs, GqlGetSiteJobsByTopic);
