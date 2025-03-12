import type { UseMutationReturnType } from "@tanstack/vue-query";

export default function useCreateUpdate<
  TResponse extends { data?: unknown },
  TVariables extends Record<string, unknown>
>(
  queryKey: string,
  getQueryFn: (variables: TVariables) => Promise<TResponse>,
  options: { dataCacheField?: string } = { dataCacheField: "id" }
) {
  const dataCacheField = options.dataCacheField ?? "id";
  type TData = TResponse["data"] extends infer D ? (D extends undefined ? never : D) : never;

  type Options = { onSuccess?: (data: TData) => void } & (
    | { redirect: true | "onSuccess" | "onError"; redirectBasePath: string }
    | { redirect?: false; redirectBasePath?: string }
  );

  function useFn(
    options: Options = { redirect: false }
  ): UseMutationReturnType<TData, Error, TVariables, unknown> {
    const defaults = { redirect: false };
    const { redirect, redirectBasePath, onSuccess } = { ...defaults, ...options };

    const router = useRouter();
    const invalidateItemCaches = useInvalidateItemCaches(queryKey);
    const { onError, throwErrorIfNoData } = useErrorHandling({
      redirect: !!(redirect === "onError" || redirect === true ? redirect : false)
    });

    async function mutationFn(variables: TVariables): Promise<TData> {
      console.log("mutationFn", variables);
      const res = await getQueryFn(variables);
      console.log("mutationFn response", res);

      throwErrorIfNoData(res.data, 403, `${queryKey} with id ${variables.id} Access Denied`);

      return res.data as TData;
    }

    const context = useMutation<TData, Error, TVariables, unknown>({
      mutationFn,
      onSuccess: (data) => {
        console.log("onSuccess", data);
        invalidateItemCaches((data as Record<string, never>)?.[dataCacheField]);
        if (onSuccess) {
          onSuccess(data);
        }
        if (redirect === "onSuccess" || redirect === true) {
          router.push(`${redirectBasePath}/${(data as Record<string, never>)?.[dataCacheField]}`);
        }
      },
      onError
    });

    return context;
  }

  return useFn;
}
