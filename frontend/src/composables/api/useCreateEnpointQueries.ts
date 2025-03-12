import { useQuery, type UseQueryReturnType } from "@tanstack/vue-query";

export default function useCreateEndpointQueries<
  TGetResponse extends { data?: unknown },
  TGetVariables extends { id: number },
  TListResponse extends { data: unknown }
>(
  queryKey: string,
  getQueryFn: (variables: TGetVariables) => Promise<TGetResponse>,
  listQueryFn: () => Promise<TListResponse>
) {
  // Use type assertion to properly infer data types
  type TGetData = TGetResponse["data"] extends infer D ? (D extends undefined ? never : D) : never;

  type TListData = TListResponse["data"];

  function useGetFn(id: number | Ref<number>): UseQueryReturnType<TGetData, Error> {
    const { onError, onErrorInData } = useErrorHandling({
      redirect: true
    });

    async function queryFn(): Promise<TGetData> {
      const variables = { id: unref(id) } as TGetVariables;
      const res = await getQueryFn(variables);

      // Add type-safe validation and assertion
      if (!res || typeof res !== "object" || !("data" in res)) {
        throw new Error("Invalid response structure");
      }

      const data = res.data as TGetData;
      if (!data) throw new Error("No data received");

      onErrorInData(data);
      return data;
    }

    const context = useQuery<TGetData, Error>({
      queryKey: [queryKey, id],
      queryFn
    });

    watch(
      () => context.error.value,
      (error) => {
        if (error) onError(error);
      }
    );

    return context;
  }

  function useListFn(): UseQueryReturnType<TListData, Error> {
    const { onError, onErrorInData } = useErrorHandling({});

    async function queryFn(): Promise<TListData> {
      const res = await listQueryFn();
      const data = res.data as TListData;
      if (!data) throw new Error("No data received");

      onErrorInData(data);
      return data;
    }

    const context = useQuery<TListData, Error>({
      queryKey: [queryKey, "list"],
      queryFn
    });

    watch(
      () => context.error.value,
      (error) => {
        if (error) onError(error);
      }
    );

    return context;
  }

  return { useGetFn, useListFn };
}
