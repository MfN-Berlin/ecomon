import { useEffect, useState } from 'react'

export function usePredictionCount(collectionName: string | undefined) {
   const [predictionCount, setPredictionCount] = useState<number>(0)
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchPredictionCount() {
         fetch('http://127.0.0.1:8000/prefix/' + collectionName + '/predictions/count')
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
