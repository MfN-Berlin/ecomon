import React, { useContext } from 'react'


import { store } from '../components/JobsProvider'
import { API_PATH } from '../consts'



export function useUpdateJobs() {
   const globalState = useContext(store)
   const { dispatch } = globalState

   function updateJobs() {
      fetch(`${API_PATH}/jobs`)
         .then((res) => res.json())
         .then((jobs) => {
            console.log(jobs)
            dispatch({ type: 'set_jobs', jobs })
         })
         .catch((err) => {
            dispatch({ type: 'set_error', error: err })
         })
   }
   return { updateJobs }

}
