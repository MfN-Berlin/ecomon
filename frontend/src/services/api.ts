import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { API_PATH } from '../consts'

type Collection = string

// Define a service using a base URL and expected endpoints
export const pokemonApi = createApi({
   reducerPath: 'api',
   baseQuery: fetchBaseQuery({ baseUrl: API_PATH }),
   endpoints: (builder) => ({
      getCollections: builder.query<Collection, string>({
         query: () => `prefix/list`,
      }),
   }),
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetCollectionsQuery } = pokemonApi
