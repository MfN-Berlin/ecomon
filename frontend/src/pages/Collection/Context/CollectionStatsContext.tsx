import React, { createContext, useContext, useState } from 'react'
import { Report } from '../../../generated/api/index'
interface CollectionStats {
   predictionCount: number
   recordCount: number
   recordDuration: number
   corruptedRecordCount: number
   firstRecordDatetime: Date | null
   lastRecordDatetime: Date | null
   loading: boolean
   setLoading: (loading: boolean) => void
   setReport: (report: Report | undefined) => void
}

const CollectionStatsContext = createContext<CollectionStats | undefined>(undefined)

export const CollectionStatsProvider: React.FC = ({ children }) => {
   const [predictionCount, setPredictionCount] = useState<number>(0)
   const [recordCount, setRecordCount] = useState<number>(0)
   const [recordDuration, setRecordDuration] = useState<number>(0)
   const [firstRecordDatetime, setFirstRecordDate] = useState<Date | null>(null)
   const [lastRecordDatetime, setLastRecordDate] = useState<Date | null>(null)
   const [corruptedRecordCount, setCorruptedRecordCount] = useState<number>(0)
   const [loading, setLoading] = useState<boolean>(false)
   function setReport(report: Report | undefined) {
      if (report === undefined) {
         setPredictionCount(0)
         setRecordCount(0)
         setRecordDuration(0)
         setCorruptedRecordCount(0)
         setFirstRecordDate(null)
         setLastRecordDate(null)
         return
      }
      setPredictionCount(report.predictions_count)
      setRecordCount(report.records_count)
      setRecordDuration(report.summed_records_duration)
      setFirstRecordDate(new Date(report.first_record_datetime))
      setLastRecordDate(new Date(report.last_record_datetime))
      setCorruptedRecordCount(report.corrupted_record_count)
   }
   return (
      <CollectionStatsContext.Provider
         value={{
            predictionCount,
            recordCount,
            recordDuration,
            firstRecordDatetime,
            lastRecordDatetime,
            corruptedRecordCount,
            loading,
            setReport,
            setLoading
         }}
      >
         {children}
      </CollectionStatsContext.Provider>
   )
}

export const useCollectionStats = (): CollectionStats => {
   const context = useContext(CollectionStatsContext)
   if (!context) {
      throw new Error('useCollectionStats must be used within a CollectionStatsProvider')
   }
   return context
}
