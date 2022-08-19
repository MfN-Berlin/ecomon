import { useEffect, useState } from 'react'
import { API_PATH } from '../consts'

export function usePredictionCount(collectionName: string | undefined) {
   const [predictionCount, setPredictionCount] = useState<number>(0)
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchPredictionCount() {
         fetch(`${API_PATH}/prefix/${collectionName}/predictions/count`)
            .then((res) => res.json())
            .then((data) => {
               setPredictionCount(data)
               setLoading(false)
            })
      }
      setLoading(true)
      fetchPredictionCount()
   }, [collectionName])

   return { predictionCount, loading }
}
