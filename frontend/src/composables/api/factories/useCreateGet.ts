import { useQuery, type UseQueryReturnType } from "@tanstack/vue-query";

export default function useCreateGet<TResponse extends { data?: unknown }, TVariables extends { id: number }>(
  queryKey: string,
  getQueryFn: (variables: TVariables) => Promise<TResponse>
) {
  // Use type assertion to properly infer data types
  type TGetData = TResponse["data"] extends infer D ? (D extends undefined ? never : D) : never;

  function useGetFn(id: number | Ref<number>): UseQueryReturnType<TGetData, Error> {
    const { onError, throwErrorIfNoData } = useErrorHandling({
      redirect: true
    });

    async function queryFn(): Promise<TGetData> {
      const variables = { id: unref(id) } as TVariables;
      console.log("queryFn", variables);
      const res = await getQueryFn(variables);
      console.log("queryFn response", res);

      // Add type-safe validation and assertion
      if (!res || typeof res !== "object" || !("data" in res)) {
        throw new Error("Invalid response structure");
      }

      const data = res.data as TGetData;
      throwErrorIfNoData(data, 404, `${queryKey} with id ${id} not found`);
      return data;
    }

    const context = useQuery<TGetData, Error>({
      queryKey: [queryKey, id],
      queryFn,
      retry: 0
    });

    watch(
      () => context.error.value,
      (error) => {
        if (error) onError(error);
      }
    );

    return context;
  }

  return useGetFn;
}
