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
    // LOG 1: Log the initial value from the URL
    console.log(`[useSearchTrigger] Initialized term from URL query '${routeQueryKey}':`, term.value);
  }

  watchDebounced(
    term,
    (value) => {
      // LOG 2: Log the value received from the input field after debouncing
      console.log(`[useSearchTrigger] Debounced input value:`, value);

      // emit the termChanged event
      debouncedTerm.value = value;

      // LOG 3: Log the value just before calling the search function
      console.log(`[useSearchTrigger] Calling searchFn with:`, value);

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
      // LOG 4: Log when the URL query parameter changes externally
      console.log(`[useSearchTrigger] URL query '${routeQueryKey}' changed to:`, newSearch);

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
