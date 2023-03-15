import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { DefaultApi, Configuration } from '../generated/api';
import { API_PATH } from '../consts'


const isProduction = process.env.NODE_ENV === 'production';
const apiBaseUrl = isProduction
   ? process.env.REACT_APP_API_BASE_URL_PROD
   : process.env.REACT_APP_API_BASE_URL_DEV;

const apiConfig = new Configuration({
   basePath: apiBaseUrl,
});

const apiClient = new DefaultApi(apiConfig);

type Collections = [string]


// Define a service using a base URL and expected endpoints
export const backendApi = createApi({
   reducerPath: 'api',
   baseQuery: fetchBaseQuery({ baseUrl: API_PATH }),
   endpoints: (builder) => ({
      getCollections: builder.query<Collections, string>({
         query: (name) => `prefix/list`,
      }),
   }),
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetCollectionsQuery } = backendApi
