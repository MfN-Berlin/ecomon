import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../index'

// Define a type for the slice state
interface UiState {
   drawerVisible: boolean
}

// Define the initial state using that type
const initialState: UiState = {
   drawerVisible: true,
}

export const counterSlice = createSlice({
   name: 'ui',
   // `createSlice` will infer the state type from the `initialState` argument
   initialState,
   reducers: {
      toggleDrawer: (state) => {
         state.drawerVisible = !state.drawerVisible
      },

      // Use the PayloadAction type to declare the contents of `action.payload`
      setDrawerVisible: (state, action: PayloadAction<boolean>) => {
         state.drawerVisible = action.payload
      },
   },
})

export const { toggleDrawer, setDrawerVisible } = counterSlice.actions

// Other code such as selectors can use the imported `RootState` type
export const selectCount = (state: RootState) => state
