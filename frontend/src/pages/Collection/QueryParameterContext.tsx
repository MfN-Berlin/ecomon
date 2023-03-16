import React, { createContext, useContext, useState } from 'react'
import { DEFAULT_VALUES } from '../../consts'
interface QueryParameters {
   from: Date | null
   until: Date | null
   thresholdMin: number
   thresholdMax: number
   binWidth: number
   sampleSize: number
   hasIndex: boolean
   filterFrequency: number
   useFilter: boolean
   selectedSpecies: string | undefined
   setFrom: React.Dispatch<React.SetStateAction<Date | null>>
   setUntil: React.Dispatch<React.SetStateAction<Date | null>>
   setThresholdMin: React.Dispatch<React.SetStateAction<number>>
   setThresholdMax: React.Dispatch<React.SetStateAction<number>>
   setBinWidth: React.Dispatch<React.SetStateAction<number>>
   setSampleSize: React.Dispatch<React.SetStateAction<number>>
   setHasIndex: React.Dispatch<React.SetStateAction<boolean>>
   setFilterFrequency: React.Dispatch<React.SetStateAction<number>>
   setFilterUse: React.Dispatch<React.SetStateAction<boolean>>
   setSelectedSpecies: React.Dispatch<React.SetStateAction<string | undefined>>
}

const QueryParametersContext = createContext<QueryParameters | undefined>(undefined)

export const QueryParametersProvider: React.FC = ({ children }) => {
   const [from, setFrom] = useState<Date | null>(null)
   const [until, setUntil] = useState<Date | null>(null)
   const [thresholdMin, setThresholdMin] = useState<number>(DEFAULT_VALUES.thresholdMin)
   const [thresholdMax, setThresholdMax] = useState<number>(DEFAULT_VALUES.thresholdMax)
   const [binWidth, setBinWidth] = useState<number>(DEFAULT_VALUES.binWidth)
   const [sampleSize, setSampleSize] = useState<number>(DEFAULT_VALUES.sampleSize)
   const [hasIndex, setHasIndex] = useState<boolean>(DEFAULT_VALUES.hasIndex)
   const [filterFrequency, setFilterFrequency] = useState<number>(DEFAULT_VALUES.filterFrequency)
   const [useFilter, setFilterUse] = useState<boolean>(DEFAULT_VALUES.useFilter)
   const [selectedSpecies, setSelectedSpecies] = useState<string | undefined>(undefined)

   return (
      <QueryParametersContext.Provider
         value={{
            from,
            setFrom,
            until,
            setUntil,
            thresholdMax,
            setThresholdMax,
            thresholdMin,
            setThresholdMin,
            binWidth,
            setBinWidth,
            sampleSize,
            setSampleSize,
            hasIndex,
            setHasIndex,
            filterFrequency,
            setFilterFrequency,
            useFilter,
            setFilterUse,
            selectedSpecies,
            setSelectedSpecies
         }}
      >
         {children}
      </QueryParametersContext.Provider>
   )
}

export const useQueryParameters = (): QueryParameters => {
   const context = useContext(QueryParametersContext)
   if (!context) {
      throw new Error('useQueryParameters must be used within a QueryParametersProvider')
   }
   return context
}
