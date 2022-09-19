import { useEffect, useState } from 'react'
import { API_PATH } from '../consts'
interface CollectionInfo {
   name: string
   species_list: string[]
   records_count: number
   predictions_count: number
   indicated_species_columns: string[]
}

interface Species {
   name: string
   has_index: boolean
}

export function useCollectionList() {
   const [collectionList, setCollectionsList] = useState<string[]>([])
   const [loading, setLoading] = useState(true)
   function fetchCollections() {
      fetch(`${API_PATH}/prefix/list`)
         .then((res) => res.json())
         .then((data) => {
            setCollectionsList(data)
            setLoading(false)
         })
   }
   useEffect(() => {
      setLoading(true)
      fetchCollections()
   }, [])

   return { collectionList, loading }
}

export function useCollectionInfo(collectionName: string | undefined) {
   const [collectionInfo, setCollectionInfo] = useState<CollectionInfo>()
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchCollectionInfo() {
         fetch(`${API_PATH}/prefix/` + collectionName)
            .then((res) => res.json())
            .then((data) => {
               setCollectionInfo(data)
               setLoading(false)
            })
      }
      setLoading(true)
      fetchCollectionInfo()
   }, [collectionName])

   return { collectionInfo, loading }
}

export function useCollectionSpeciesList(collectionName: string | undefined) {
   const [collectionSpeciesList, setCollectionSpeciesList] = useState<Species[]>([])
   const [loading, setLoading] = useState(true)

   async function update() {
      async function fetchCollectionSpeciesList() {
         fetch(`${API_PATH}/prefix/${collectionName}/species`)
            .then((res) => res.json())
            .then((data) => {
               // sort Array of Species by name
               data.sort((a: Species, b: Species) => {
                  if (a.name < b.name) {
                     return -1
                  }
                  if (a.name > b.name) {
                     return 1
                  }
                  return 0
               })
               console.log(data)
               setCollectionSpeciesList(data)
               setLoading(false)
            })
      }
      setLoading(true)
      return fetchCollectionSpeciesList()
   }

   useEffect(() => {
      update()
   }, [collectionName])
   // eslint-disable-next-line
   return { collectionSpeciesList, loading, update }
}

interface QueryParameters {
   start_datetime?: string | null
   end_datetime?: string | null
   species: string
   threshold: number
}
interface QueryResponse {
   predictions_count: number
   species_count: number
}

export function useCollectionPredictionQuery(collectionName: string | undefined) {
   const [predictionQueryResponse, setCollectionPredictionQuery] = useState<QueryResponse>()
   const [loading, setLoading] = useState(false)

   const abortController = new AbortController()

   function updateQuery(queryParameters: QueryParameters) {



      if (loading) {
         abortController.abort()
         setLoading(false)
      }


      setLoading(true)

      fetch(`${API_PATH}/prefix/${collectionName}/predictions`, {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json'
         },
         signal: abortController.signal,
         body: JSON.stringify(queryParameters)
      })
         .then((res) => res.json())
         .then((data) => {
            setCollectionPredictionQuery(data)
            setLoading(false)
         })
   }
   function abortQuery() {
      if (loading) {
         abortController.abort()
         setLoading(false)
      }
   }
   function clearResponse() {
      setCollectionPredictionQuery(undefined)
   }

   return {
      predictionQueryResponse,
      loading,
      updateQuery,
      abortQuery,
      clearResponse
   }
}
