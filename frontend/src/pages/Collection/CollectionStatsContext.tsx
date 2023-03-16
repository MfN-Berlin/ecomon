import React, { createContext, useContext, useState } from 'react'
import { Record } from '../../hooks/records'
interface CollectionStats {
   predictionCount: number
   recordCount: number
   recordDuration: number
   firstRecord: Record | undefined
   lastRecord: Record | undefined
   predictionLoading: boolean
   recordLoading: boolean
   durationLoading: boolean
   firstRecordLoading: boolean
   lastRecordLoading: boolean
   setPredictionCount: (predictionCount: number) => void
   setRecordCount: (recordCount: number) => void
   setRecordDuration: (recordDuration: number) => void
   setFirstRecord: (firstRecord: Record | undefined) => void
   setLastRecord: (lastRecord: Record | undefined) => void
   setPredictionLoading: (predictionLoading: boolean) => void
   setRecordLoading: (recordLoading: boolean) => void
   setDurationLoading: (durationLoading: boolean) => void
   setFirstRecordLoading: (firstRecordLoading: boolean) => void
   setLastRecordLoading: (lastRecordLoading: boolean) => void
}

const CollectionStatsContext = createContext<CollectionStats | undefined>(undefined)

export const CollectionStatsProvider: React.FC = ({ children }) => {
   const [predictionCount, setPredictionCount] = useState<number>(0)
   const [recordCount, setRecordCount] = useState<number>(0)
   const [recordDuration, setRecordDuration] = useState<number>(0)
   const [firstRecord, setFirstRecord] = useState<Record | undefined>()
   const [lastRecord, setLastRecord] = useState<Record | undefined>()
   const [predictionLoading, setPredictionLoading] = useState<boolean>(false)
   const [recordLoading, setRecordLoading] = useState<boolean>(false)
   const [durationLoading, setDurationLoading] = useState<boolean>(false)
   const [firstRecordLoading, setFirstRecordLoading] = useState<boolean>(false)
   const [lastRecordLoading, setLastRecordLoading] = useState<boolean>(false)
   return (
      <CollectionStatsContext.Provider
         value={{
            predictionCount,
            recordCount,
            recordDuration,
            firstRecord,
            lastRecord,
            predictionLoading,
            recordLoading,
            durationLoading,
            firstRecordLoading,
            lastRecordLoading,
            setPredictionCount,
            setRecordCount,
            setRecordDuration,
            setFirstRecord,
            setLastRecord,
            setPredictionLoading,
            setRecordLoading,
            setDurationLoading,
            setFirstRecordLoading,
            setLastRecordLoading
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
