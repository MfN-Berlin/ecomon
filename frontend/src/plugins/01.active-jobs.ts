import type { SubscribeActiveJobsSubscription, SubscribeActiveJobsSubscriptionVariables } from "#gql/default";
import { SubscribeActiveJobsDocument } from "#gql/default";

export default defineNuxtPlugin(() => {
  const { subscribe } = useGqlSubscription();
  const { $toast } = useNuxtApp();

  const { data, error } = subscribe<
    SubscribeActiveJobsSubscription,
    SubscribeActiveJobsSubscriptionVariables
  >(SubscribeActiveJobsDocument, {});

  watch(error, (value) => {
    $toast.error("Error in active jobs subscription", {
      description: value as string
    });
  });

  return {
    provide: {
      activeJobs: data
    }
  };
});
