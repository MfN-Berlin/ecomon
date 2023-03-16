import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { DefaultApi, Configuration, Report } from '../generated/api';
import { API_PATH } from '../consts'


const apiConfig = new Configuration({
   basePath: API_PATH,

});

const apiClient = new DefaultApi(apiConfig);



// Define a service using a base URL and expected endpoints
export const backendApi = createApi({
   reducerPath: 'api',
   baseQuery: fetchBaseQuery({ baseUrl: API_PATH }),
   endpoints: (builder) => ({
      getCollections: builder.query<Array<string>, void>({
         queryFn: () => {
            return apiClient.getCollectionNames()
         },
      }),
      getCollectionReport: builder.query<Report, string>({
         queryFn: (collectionName) => {
            return apiClient.getCollectionReport(collectionName)
         },
      }),
   })
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetCollectionsQuery, useGetCollectionReportQuery } = backendApi
