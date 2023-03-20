// QueryResultContext.tsx
import React, { createContext, useContext, useState } from 'react'
import { QueryResponse } from '../../../hooks/collection'
interface QueryResult {
   result: QueryResponse | undefined
   loading: boolean
   setResult: (result: QueryResponse | undefined) => void
   setLoading: (loading: boolean) => void
}

const QueryResultContext = createContext<QueryResult | undefined>(undefined)

export const QueryResultProvider: React.FC = ({ children }) => {
   const [result, setResult] = useState<QueryResponse>()
   const [loading, setLoading] = useState<boolean>(false)
   return (
      <QueryResultContext.Provider value={{ result, setResult, loading, setLoading }}>
         {children}
      </QueryResultContext.Provider>
   )
}

export const useQueryResult = (): QueryResult => {
   const context = useContext(QueryResultContext)
   if (!context) {
      throw new Error('useQueryResult must be used within a QueryResultProvider')
   }
   return context
}
