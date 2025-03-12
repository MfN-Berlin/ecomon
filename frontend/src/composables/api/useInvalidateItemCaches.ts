export default function useInvalidateItemCaches(baseCacheKey: string) {
  const queryClient = useQueryClient();
  return function invalidateItemCaches(id: string) {
    console.log("invalidateItemCaches", id);
    queryClient.invalidateQueries({
      queryKey: [baseCacheKey, id]
    });
    queryClient.invalidateQueries({
      queryKey: [baseCacheKey, "list"]
    });
    queryClient.invalidateQueries({
      queryKey: [baseCacheKey, "filter"]
    });
  };
}
