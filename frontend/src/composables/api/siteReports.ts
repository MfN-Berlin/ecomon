// plugins/graphql-subscription.ts
import type {
  SubscripeReportsBySiteIdSubscription,
  SubscripeReportsBySiteIdSubscriptionVariables
} from "#gql/default";
import { SubscripeReportsBySiteIdDocument } from "#gql/default";

export const useSiteReportList = useCreateList(QUERY_KEYS.siteReportsList, GqlGetSiteReportList);

export const useGetSiteReportById = useCreateGet(QUERY_KEYS.siteReports, GqlGetSiteReportById);
export const useGetSiteReportMonthlyHistogram = useCreateGet(
  QUERY_KEYS.siteReportsMonthlyHistogram,
  GqlGetSiteReportMonthlyHistogram
);
export const useGetSiteReportDailyHistogram = useCreateGet(
  QUERY_KEYS.siteReportsDailyHistogram,
  GqlGetSiteReportDailyHistogram
);
export const useGetSiteReportDurationHistogram = useCreateGet(
  QUERY_KEYS.siteReportsDurationHistogram,
  GqlGetSiteReportDurationHistogram
);

export const useGetSiteReportRecordsHeatmap = useCreateGet(
  QUERY_KEYS.siteReportsRecordsHeatmap,
  GqlGetSiteReportRecordsHeatmap
);

export function useSubscribeReportsBySiteId(siteId: number) {
  const { subscribe } = useGqlSubscription();
  const { $toast } = useNuxtApp();

  const { data, error, pending, unsubscribe } = subscribe<
    SubscripeReportsBySiteIdSubscription,
    SubscripeReportsBySiteIdSubscriptionVariables
  >(SubscripeReportsBySiteIdDocument, { siteId });

  watch(error, (value) => {
    $toast.error("Error in active jobs subscription", {
      description: value as string
    });
  });

  return { data, error, pending, unsubscribe };
}

export const useCreateSiteReport = useCreateAction(GqlCreateSiteDataReport);
