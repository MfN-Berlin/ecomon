export const useLocationGet = useCreateGet(QUERY_KEYS.locations, GqlGetLocationById);
export const useLocationList = useCreateList(QUERY_KEYS.locations, GqlGetLocationList);
export const useLocationFilter = useCreateFilter({
  baseQueryKey: QUERY_KEYS.locations,
  filterQueryFn: GqlFilterLocation
});

export const useLocationUpdate = useCreateMutation(QUERY_KEYS.locations, GqlUpdateLocation);
export const useLocationInsert = useCreateMutation(QUERY_KEYS.locations, GqlInsertLocation);
export const useLocationDelete = useCreateMutation(QUERY_KEYS.locations, GqlDeleteLocation);

export const useLocationPagniated = useCreatePagniated({
  baseQueryKey: QUERY_KEYS.locations,
  pagniatedQueryFn: GqlGetLocationsPagniated
});
