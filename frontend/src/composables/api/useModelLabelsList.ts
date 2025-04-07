import type { GetModelLabelsListQuery } from "#gql";

type Options = {
  itemsPerPage?: number;
  defaultSearchTerm: string;
};
export type Label = GetModelLabelsListQuery["data"][0]["label"];

export default function useModelLabelsList(options?: Options) {
  const itemsPerPage = options?.itemsPerPage || 10;
  const search = ref(options?.defaultSearchTerm || "");
  const queryClient = useQueryClient();
  const modelId = ref<number | null>(null);
  const isManuallyFetching = ref(false);

  async function queryFn({ pageParam = 0 }: { pageParam?: number }) {
    console.log("useModelLabelsList queryFn: ", pageParam);

    if (modelId.value === null || modelId.value === undefined) {
      return {
        data: [],
        nextCursor: undefined
      };
    }

    const res = await GqlGetModelLabelsList({
      limit: itemsPerPage + 1, // fetch one more item to check if there are more items to fetch
      offset: pageParam,
      search: `%${search.value}%`,
      modelId: modelId.value
    });

    // remove the last item if there are more items to fetch
    console.log("useModelLabelsList queryFn res: ", res.data);
    const data = res.data.slice(0, res.data.length - 1);
    const hasMoreItems = res.data.length > itemsPerPage;
    const nextCursor = hasMoreItems ? pageParam + itemsPerPage : undefined;

    console.log("useModelLabelsList result: ", modelId.value, pageParam, data.length, nextCursor);
    return {
      data,
      nextCursor
    };
  }
  const queryKey = computed(() => [QUERY_KEYS.modelLabels, modelId.value, search.value]);

  watch(search, (val) => {
    console.log("useModelLabelsList:", val);

    queryClient.invalidateQueries({ queryKey, exact: false });
  });

  watch(modelId, (val) => {
    console.log("useModelLabelsList modelId:", val);
    if (val) {
      queryClient.invalidateQueries({ queryKey });
    }
  });

  function setModelId(id: number | null | undefined) {
    console.log("Setting model ID:", id);
    if (id !== null && id !== undefined) {
      modelId.value = id;
    } else {
      modelId.value = null;
    }
  }

  const {
    data,
    error,
    fetchNextPage,

    isFetchingNextPage,
    isFetching,
    isLoading,
    isError,
    hasNextPage
  } = useInfiniteQuery({
    queryKey,
    queryFn: queryFn,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 0,
    enabled: !!modelId.value // Only enable the query when modelId is set
  });

  // Wrap fetchNextPage to prevent concurrent calls

  const labels = computed(() => {
    console.log("useModelLabelsList labels computed: ", data.value);
    return (
      data.value?.pages.flatMap((page) =>
        page.data.map((label) => ({
          ...label
        }))
      ) || []
    );
  });

  return {
    modelId,
    search,
    labels,
    isFetching: computed(() => isFetching.value || isLoading.value || isManuallyFetching.value),
    isFetchingNextPage: computed(() => isFetchingNextPage.value || isManuallyFetching.value),
    isLoading,
    isError,
    error,
    hasNextPage,
    fetchNextPage,
    setModelId
  };
}
