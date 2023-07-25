import React, { useEffect, useState } from 'react'
import { useGetCollectionSpeciesListQuery } from '@/services/api'
import { Species } from '@/generated/api'
export interface IPanelToolBar {
   mainToolBarChilds: JSX.Element | null
   setMainToolBarChilds: React.Dispatch<React.SetStateAction<JSX.Element | null>>
   additionalToolBarChilds: JSX.Element | null
   setAdditionalToolBarChilds: React.Dispatch<React.SetStateAction<JSX.Element | null>>
   collectionName: string
   setCollectionName: React.Dispatch<React.SetStateAction<string>>
   classifier: string
   setClassifier: React.Dispatch<React.SetStateAction<string>>
   locationAndDate: string
   setLocationAndDate: React.Dispatch<React.SetStateAction<string>>
   isSpeciesListFetching: boolean
   speciesList: Species[] | undefined
}

export const PanelToolBarContext = React.createContext<IPanelToolBar | undefined>(undefined)

export const PanelToolBarProvider: React.FC = ({ children }) => {
   const [mainToolBarChilds, setMainToolBarChilds] = useState<JSX.Element | null>(null)
   const [additionalToolBarChilds, setAdditionalToolBarChilds] = useState<JSX.Element | null>(null)
   const [collectionName, setCollectionName] = useState<string>('')
   const [classifier, setClassifier] = useState<string>('')
   const [locationAndDate, setLocationAndDate] = useState<string>('')

   const {
      data: speciesList,
      isFetching: isSpeciesListFetching,
      refetch: refetchSpeciesList
   } = useGetCollectionSpeciesListQuery({ collectionName })

   const value = {
      mainToolBarChilds,
      setMainToolBarChilds,
      additionalToolBarChilds,
      setAdditionalToolBarChilds,
      collectionName,
      setCollectionName,
      classifier,
      setClassifier,
      locationAndDate,
      setLocationAndDate,
      isSpeciesListFetching,
      speciesList
   }
   useEffect(() => {
      refetchSpeciesList()
   }, [collectionName])

   return <PanelToolBarContext.Provider value={value}>{children}</PanelToolBarContext.Provider>
}
