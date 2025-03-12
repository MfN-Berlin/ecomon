export default function useCreateAction<
  TResponse extends { data?: unknown },
  TVariables extends Record<string, unknown>
>(getQueryFn: (variables: TVariables) => Promise<TResponse>) {
  return () => {
    type TData = TResponse["data"] extends infer D ? (D extends undefined ? never : D) : never;
    const { onError } = useErrorHandling({
      redirect: false
    });
    const isPending = ref(false);
    const error = ref<Error | null>(null);
    async function mutate(variables: TVariables): Promise<TData | undefined> {
      try {
        isPending.value = true;
        const res = await getQueryFn(variables);
        return res.data as TData;
      } catch (error) {
        onError(error);
      } finally {
        isPending.value = false;
      }
    }

    return { mutate, isPending, error };
  };
}
