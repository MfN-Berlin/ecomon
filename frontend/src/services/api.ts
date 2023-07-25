import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { DefaultApi, Configuration, Report, PredictionMax, Species } from '../generated/api'
import { API_PATH } from '../consts'


const apiConfig = new Configuration({
   basePath: API_PATH
})

export const apiClient = new DefaultApi(apiConfig)

// Define a service using a base URL and expected endpoints
export const backendApi = createApi({
   reducerPath: 'api',
   baseQuery: fetchBaseQuery({ baseUrl: API_PATH }),
   endpoints: (builder) => ({
      getCollections: builder.query<Array<string>, void>({
         queryFn: () => {
            return apiClient.getCollectionNames()
         }
      }),
      getCollectionReport: builder.query<Report, string | undefined>({
         queryFn: (collectionName) => {
            // Hack to undefined to empty string
            return apiClient.getCollectionReport(collectionName || '')
         }
      }),
      getCollectionSpeciesEvents: builder.query<PredictionMax[], { collectionName: string; species: string }>({
         queryFn: ({ collectionName, species }) => {
            // Hack to undefined to empty string
            return apiClient.getCollectionPredictionsSpeciesMax(collectionName, species)
         }
      }),
      getCollectionSpeciesHistogram: builder.query<number[], { collectionName: string; species: string }>({
         queryFn: ({ collectionName, species }) => {
            // Hack to undefined to empty string
            return apiClient.getCollectionPredictionsSpeciesHistogram(collectionName, species)
         }
      }),

      getCollectionSpeciesList: builder.query<Species[], { collectionName: string }>({
         queryFn: ({ collectionName }) => {
            // Hack to undefined to empty string

            return apiClient.getCollectionSpecies(collectionName)
         }
      }),
      getCollectionList: builder.query<Array<string>, void>({
         queryFn: () => {
            return apiClient.getCollectionNames()
         }
      })
   })
})
// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints

export const {
   useGetCollectionsQuery,
   useGetCollectionReportQuery,
   useGetCollectionSpeciesEventsQuery,
   useGetCollectionSpeciesListQuery,
   useGetCollectionListQuery,
   useGetCollectionSpeciesHistogramQuery
} = backendApi
