import { useQuery, type UseQueryReturnType } from "@tanstack/vue-query";

export default function useCreateList<TListResponse extends { data: unknown }, TListQuery>(
  queryKeyRoot: string,
  listQueryFn: (args: TListQuery) => Promise<TListResponse>
) {
  // Use type assertion to properly infer data types

  type TListData = TListResponse["data"];

  function useListFn(param?: Ref<TListQuery> | TListQuery): UseQueryReturnType<TListData, Error> {
    const { onError } = useErrorHandling({});
    const _params = toRef(param);
    const queryKey = computed(() =>
      _params && _params.value ? [queryKeyRoot, "list", _params.value] : [queryKeyRoot, "list"]
    );
    async function queryFn(): Promise<TListData> {
      const res = await listQueryFn(_params.value);
      const data = res.data as TListData;
      if (!data) throw new Error("No data received");

      // onErrorInData(data);
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

  return useListFn;
}
