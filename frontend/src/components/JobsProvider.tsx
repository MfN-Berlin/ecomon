import React, { createContext, useReducer } from 'react'
import { API_PATH } from '../consts'

type Job = {
   id: number
   collection: string
   status: 'running' | 'done' | 'failed' | 'pending'
   type:
      | 'add_index'
      | 'drop_index'
      | 'create_sample'
      | 'calc_bin_sizes'
      | 'calc_predictions'
      | 'calc_day_histogram'
      | 'calc_activation'
   metadata: any
   progress: number
   error: string
}

type JobsState = {
   jobs: Job[]
   loading: boolean
   error?: Error
}

type JobsAction =
   | {
        type: 'set_jobs'
        jobs: Job[]
     }
   | {
        type: 'set_loading'
        loading: boolean
     }
   | {
        type: 'set_error'
        error: Error
     }

interface NavProps {
   children?: React.ReactNode
}

const initialState = {
   jobs: new Array<Job>(),
   loading: false
} as JobsState
const store = createContext(
   {} as {
      state: JobsState
      dispatch: React.Dispatch<JobsAction>
   }
)
const { Provider } = store

function jobsReducer(state: JobsState, action: JobsAction): JobsState {
   switch (action.type) {
      case 'set_jobs':
         console.log('set_jobs')
         return {
            ...state,
            jobs: action.jobs
         }
      case 'set_loading':
         return {
            ...state,
            loading: action.loading
         }
      case 'set_error':
         return {
            ...state,
            error: action.error
         }
      default:
         return { ...state, error: new Error('Unhandled Action') }
   }
}

const JobsProvider = (props: NavProps) => {
   const [state, dispatch] = useReducer(jobsReducer, initialState)

   return <Provider value={{ state, dispatch }}> {props?.children} </Provider>
}

export { store, JobsProvider }
