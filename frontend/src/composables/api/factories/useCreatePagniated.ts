// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type SearchArgs = {
  [key: string]: { [key: string]: string | number } | undefined;
}; // TO DO improve typeing for where conditions

export type SortByArgs = {
  key: string;
  order: "asc" | "desc";
};

export type OrderByArgs = {
  [key: string]: "asc" | "desc";
};

type PagniatedVariables = {
  limit: number;
  offset: number;
  order_by: OrderByArgs[];
  where: SearchArgs;
};
type StartValues = {
  page?: number;
  search?: SearchArgs;
  itemsPerPage?: number;
  sortBy?: SortByArgs[];
};

type PagniatedResponse<T> = {
  items: T[];
  total: {
    aggregate?: // Add optional modifier here
    | {
          count: number;
        }
      | undefined
      | null;
  };
};

export default function useCreateFilter<TItem, TData extends PagniatedResponse<TItem>>({
  baseQueryKey,
  pagniatedQueryFn
}: {
  baseQueryKey: string;
  pagniatedQueryFn: (variables: PagniatedVariables) => Promise<TData>;
}) {
  // const { onError, throwErrorIfNoData } = useErrorHandling({});

  return function usePagniated({ startValues }: { startValues?: StartValues } = {}) {
    const page = ref(startValues?.page ?? 1);
    const itemsPerPage = ref(startValues?.itemsPerPage ?? 10);
    const offset = computed(() => (page.value - 1) * itemsPerPage.value);
    const limit = computed(() => itemsPerPage.value);

    const search = ref<SearchArgs>(startValues?.search ?? {});
    const searchOperation = computed(() => {
      if (search.value) {
        return {
          _and: search.value
        };
      }
      return {};
    });

    const sortBy = ref<SortByArgs[]>(startValues?.sortBy ?? []);
    const sortByOperation = computed(() => {
      if (sortBy.value.length > 0) {
        return sortBy.value.map((order) => ({
          [order.key]: order.order
        }));
      }

      return [];
    });

    const queryKey = computed(() => [
      baseQueryKey,
      page.value,
      itemsPerPage.value,
      sortBy.value.map((order) => `${order.key}:${order.order}`).join(","),
      searchOperation.value
    ]);

    async function fetchData() {
      return await pagniatedQueryFn({
        limit: limit.value,
        offset: offset.value,
        order_by: sortByOperation.value,
        where: searchOperation.value
      });
    }

    const context = useQuery({
      queryKey: queryKey,
      queryFn: fetchData
    });

    const items = computed(() => {
      return context.data.value?.items ?? [];
    });

    const totalItems = computed(() => {
      return context.data.value?.total?.aggregate?.count ?? 0;
    });
    const handleSearch = (value: SearchArgs) => {
      search.value = {
        ...search.value,
        ...value
      };
      console.log("search", value);
    };

    const handleReset = (value: { key: string }) => {
      search.value = {
        ...search.value,
        [value.key]: undefined
      };
      console.log("reset", value);
    };
    return {
      ...context,
      page,
      itemsPerPage,
      offset,
      limit,
      search,
      sortBy,
      items,
      totalItems,
      handleSearch,
      handleReset
    };
  };
}
