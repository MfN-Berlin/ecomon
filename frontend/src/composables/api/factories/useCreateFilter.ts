import { computed, ref, readonly, watch } from "vue";
import { useRoute } from "vue-router";

type FilterVariables = {
  search: string;
  limit: number;
  offset: number;
};

export default function useCreateFilter<TData, TVariables extends FilterVariables>({
  baseQueryKey,
  filterQueryFn
}: {
  baseQueryKey: string;
  filterQueryFn: (variables: TVariables) => Promise<{ data: TData }>;
}) {
  const { onError, throwErrorIfNoData } = useErrorHandling({});

  return function useLocationFilter({ itemsPerPage = 20, searchTerm = "" }) {
    const route = useRoute();

    const _itemsPerPage = ref(itemsPerPage);
    const _searchTerm = ref(searchTerm);
    const queryClient = useQueryClient();

    async function queryFn({ pageParam = 0 }: { pageParam?: number }) {
      // Explicitly cast the object to TVariables
      const variables = {
        search: `%${_searchTerm.value}%`,
        limit: _itemsPerPage.value + 1,
        offset: pageParam
      } as TVariables;

      const res = await filterQueryFn(variables);
      console.log("queryFilterFn", res);

      throwErrorIfNoData(res.data, 500, `Error fetching ${baseQueryKey} filter`);
      return { data: res.data, nextCursor: pageParam + _itemsPerPage.value };
    }

    const {
      data: _data,
      error,
      fetchNextPage,
      isFetchingNextPage,
      isFetching,
      isLoading,
      isError
    } = useInfiniteQuery({
      queryKey: [baseQueryKey, "filter", route.params.filter],
      queryFn: queryFn,
      getNextPageParam: (lastPage) => (lastPage && lastPage.nextCursor) || _itemsPerPage.value,
      initialPageParam: 0
    });

    watch(error, (error) => {
      if (error) onError(error);
    });

    function onSearchTermChanged(term: string) {
      _searchTerm.value = term;
      queryClient.invalidateQueries({ queryKey: [baseQueryKey, "filter", route.params.filter] });
    }

    const data = computed(() => {
      return _data.value?.pages.flatMap((page) => page?.data) || [];
    });

    return {
      data,
      isFetching,
      isFetchingNextPage,
      isLoading,
      isError,
      error,
      fetchNextPage,
      onSearchTermChanged,
      searchTerm: readonly(_searchTerm)
    };
  };
}
