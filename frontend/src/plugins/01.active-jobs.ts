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

  // watch(data, (value, oldValue) => {
  //   // find finished jobs which are not in the old value
  //   console.log("value", value);
  //   if (value && oldValue) {
  //     const finishedJobs = value.jobs.filter((job) => !oldValue?.jobs.find((j) => j?.id === job?.id));
  //     console.log("current value", JSON.stringify(value, null, 2));
  //     console.log("finished jobs", JSON.stringify(finishedJobs, null, 2));
  //   }
  // });

  return {
    provide: {
      activeJobs: data
    }
  };
});
