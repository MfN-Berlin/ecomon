import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../index'

// Define a type for the slice state
interface UiState {
   drawerOpen: boolean
}

// Define the initial state using that type
const initialState = {
   drawerOpen: true,
} as UiState

export const uiSlice = createSlice({
   name: 'ui',
   // `createSlice` will infer the state type from the `initialState` argument
   initialState,
   reducers: {
      toggleDrawer: (state) => {
         state.drawerOpen = !state.drawerOpen
         setTimeout(() => {
            // dispatch resize event so plotly is resizing
            window.dispatchEvent(new Event('resize'))
         }, 350)
      },

      // Use the PayloadAction type to declare the contents of `action.payload`
      setDrawerOpenState: (state, action: PayloadAction<boolean>) => {
         state.drawerOpen = action.payload
      },
   },
})

export const { toggleDrawer, setDrawerOpenState } = uiSlice.actions

// Other code such as selectors can use the imported `RootState` type
export const selectUi = (state: RootState) => state
export default uiSlice.reducer
