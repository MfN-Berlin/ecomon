type useSearchOptions = {
  debounce?: number;
  routeQueryKey?: string;
};

export default function useSearchTrigger(
  searchFn: (term: string) => void,
  { debounce = 300, routeQueryKey = "search" }: useSearchOptions
) {
  const route = useRoute();
  const router = useRouter();

  const term = ref("");
  const debouncedTerm = ref(term.value);

  // Initialize the term with the query parameter if it exists
  if (route.query[routeQueryKey]) {
    term.value = (route.query[routeQueryKey] as string) || "";
    debouncedTerm.value = term.value;
  }

  watchDebounced(
    term,
    (value) => {
      // emit the termChanged event
      debouncedTerm.value = value;
      searchFn(value);
      // Update the URL query parameter
      const query = { ...route.query };
      if (term.value === "") {
        // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
        delete query[routeQueryKey];
      } else {
        query[routeQueryKey] = term.value;
      }
      router.replace({ query });
    },
    { debounce: debounce }
  );

  watch(
    () => route.query[routeQueryKey],
    (newSearch) => {
      if (newSearch !== term.value) {
        // if query parameter is undefined, set term to empty string
        term.value = (newSearch as string) || "";
      }
    }
  );
  return {
    model: term,
    value: readonly(debouncedTerm)
  };
}
