import { createClient } from "graphql-ws";
import type { Client } from "graphql-ws";

const client = ref<Client | null>(null);

export default function useWebSocket() {
  const config = useRuntimeConfig();

  if (client.value === null) {
    client.value = createClient({
      url: config.public.GQL_HOST!.replace("http", "ws")
    });
    console.log("client connect to ", config.public.GQL_HOST!.replace("http", "ws"));
  }

  function subscribe<T, V>(
    query: string,
    variables: V extends Record<string, unknown> ? V : undefined,
    options?: {
      onError?: (err: unknown) => void;
      onNext?: (data: T) => void;
      onComplete?: () => void;
    }
  ) {
    // console.debug("Subscribing to query", query);
    const data = ref<T | null | undefined>(null) as Ref<T | null | undefined>;
    const error = ref<unknown>(null);
    const unsubscribe = ref<() => void>(() => {
      console.warn("Unsubscribing from query default empty function was called, Likely and race condition");
    });
    const pending = ref(false);

    const initializeSubscription = async () => {
      console.debug("Initializing subscription");
      if (client.value) {
        unsubscribe.value = client.value.subscribe<T, V>(
          { query, variables },
          {
            next: ({ data: newData }) => {
              pending.value = false;
              data.value = newData as T;
              if (options?.onNext) options.onNext(newData as T);
            },
            error: (err: unknown) => {
              error.value = err;
              if (options?.onError) options.onError(err);
            },
            complete: () => {
              if (options?.onComplete) options.onComplete();
            }
          }
        );
        // onUnmounted(() => {
        //   unsubscribe.value();
        // });
      } else {
        throw new Error("WebSocket client not initialized.");
      }
    };

    initializeSubscription();

    return { data, error, unsubscribe: () => unsubscribe.value(), pending };
  }

  return { subscribe };
}
