import { configureStore } from '@reduxjs/toolkit'
// Or from '@reduxjs/toolkit/query/react'
import { setupListeners } from '@reduxjs/toolkit/query'
import { backendApi } from '../services/api'
import { uiSlice } from './slices/ui'
export const store = configureStore({
   reducer: {
      // Add the generated reducer as a specific top-level slice
      [backendApi.reducerPath]: backendApi.reducer,
      [uiSlice.name]: uiSlice.reducer,
   },
   // Adding the api middleware enables caching, invalidation, polling,
   // and other useful features of `rtk-query`.
   middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(backendApi.middleware),
})


// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch

// optional, but required for refetchOnFocus/refetchOnReconnect behaviors
// see `setupListeners` docs - takes an optional callback as the 2nd arg for customization
setupListeners(store.dispatch)
