import { useEffect, useState } from 'react'
import { API_PATH } from '../consts'
interface Record {
   id: number
   filepath: string
   filename: string
   record_datetime: Date
   duration: number
   channels: number
}

export function useRecordCount(collectionName: string | undefined) {
   const [recordCount, setRecordCount] = useState<number>(0)
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchRecordCount() {
         fetch(`${API_PATH}/prefix/${collectionName}/records/count`)
            .then((res) => res.json())
            .then((data) => {
               setRecordCount(data)
               setLoading(false)
            })
      }
      setLoading(true)
      fetchRecordCount()
   }, [collectionName])

   return { recordCount, loading }
}

export function useRecordDuration(collectionName: string | undefined) {
   const [recordDuration, setRecordDuration] = useState<number>(0)
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchRecordDuration() {
         fetch(`${API_PATH}/prefix/${collectionName}/records/duration`)
            .then((res) => res.json())
            .then((data) => {
               setRecordDuration(data)
               setLoading(false)
            })
      }
      setLoading(true)
      fetchRecordDuration()
   }, [collectionName])

   return { recordDuration, loading }
}

export function useFirstRecord(collectionName: string | undefined) {
   const [firstRecord, setFirstRecord] = useState<Record>()
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchRecordDuration() {
         fetch(`${API_PATH}/prefix/${collectionName}/records/first`)
            .then((res) => res.json())
            .then((data) => {
               data.record_datetime = new Date(data.record_datetime)
               setFirstRecord(data)
               setLoading(false)
            })
      }
      setLoading(true)
      fetchRecordDuration()
   }, [collectionName])
   return { firstRecord, loading }
}

export function useLastRecord(collectionName: string | undefined) {
   const [lastRecord, setLastRecord] = useState<Record>()
   const [loading, setLoading] = useState(true)

   useEffect(() => {
      async function fetchRecordDuration() {
         fetch(`${API_PATH}/prefix/${collectionName}/records/last`)
            .then((res) => res.json())
            .then((data) => {
               data.record_datetime = new Date(data.record_datetime)
               console.log('recieved data: ', data)
               setLastRecord(data)
               setLoading(false)
            })
      }
      setLoading(true)
      fetchRecordDuration()
   }, [collectionName])
   return { lastRecord, loading }
}
