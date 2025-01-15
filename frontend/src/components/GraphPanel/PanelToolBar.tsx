import React, { useEffect, useRef, useState, useContext } from 'react'

import Select, { StylesConfig } from 'react-select'

import Toolbar from '@mui/material/Toolbar'
import IconButton from '@mui/material/IconButton'
import AppBar from '@mui/material/AppBar'
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'
import FullscreenIcon from '@mui/icons-material/FullscreenExitOutlined'
import FullscreenExitIcon from '@mui/icons-material/FullscreenExitOutlined'
import { loadState, savePartialState } from '../../tools/localStorage'
import { firstLetterUpperAndReplaceSpace } from '../../tools/stringHandling'
import { PanelToolBarContext, IPanelToolBar } from './contexts/PanelToolBarContext'
import Box from '@mui/material/Box'
import { useGetCollectionListQuery } from '../../services/api'

// Sort classifier options alphabetically by label
const classifierOptions = [
   { value: 'birdid', label: 'BirdId' },
   { value: 'birdnet', label: 'Birdnet' }
].sort((a, b) => a.label.localeCompare(b.label))

export const denseSelectStyles = {
   control: (provided: any) => ({
      ...provided,
      minHeight: '30px',
      height: '30px',
      minWidth: '180px'
   }),
   valueContainer: (provided: any) => ({
      ...provided,
      height: '30px',
      padding: '0 6px' // This removes some of the padding inside the control
   }),
   input: (provided: any) => ({
      ...provided,
      margin: '0px'
   }),
   indicatorsContainer: (provided: any) => ({
      ...provided,
      height: '30px'
   }),
   option: (provided: any) => ({
      ...provided,
      padding: '2px 8px', // Less padding here means more dense options
      color: 'black'
   })
}

interface PanelToolBarProps {
   isFullscreen: boolean
   onToggleFullScreen?: () => void
   onRemove?: () => void
   localStorageId: string
}

export default function PanelToolBar({
   localStorageId,
   isFullscreen,
   onToggleFullScreen,
   onRemove
}: PanelToolBarProps) {
   const [valuesInit, setValuesInit] = useState(false)
   const context = useContext(PanelToolBarContext)
   if (!context) {
      // Handle the case where context is undefined
      throw new Error('ToolBarContext is not provided!')
   }

   const {
      mainToolBarChilds,
      additionalToolBarChilds,
      collectionName,
      setCollectionName,
      classifier,
      setClassifier,
      locationAndDate,
      setLocationAndDate,
      isSpeciesListFetching,
      speciesList
   } = context
   const {
      data: collectionList,
      refetch: refetchCollectionList,
      isFetching: isCollectionListFetching
   } = useGetCollectionListQuery()

   useEffect(() => {
      refetchCollectionList()
      if (localStorageId && !valuesInit) {
         const state = loadState(localStorageId)
         if (state) {
            if (state.collectionName && state.collectionName !== '') {
               setCollectionName(state.collectionName)
            }
            if (state.classifier && state.classifier !== '') {
               setClassifier(state.classifier)
            }
            if (state.locationAndDate && state.locationAndDate !== '') {
               setLocationAndDate(state.locationAndDate)
            }

            setTimeout(() => {
               setValuesInit(true) // this is needed to prevent updating the localStorage with empty values
            }, 0)
         }
      }
   }, [])
   useEffect(() => {
      if (localStorageId && valuesInit) {
         savePartialState(localStorageId, {
            collectionName,
            classifier,
            locationAndDate
         })
      }
   }, [collectionName, classifier, locationAndDate, localStorageId])

   useEffect(() => {
      if (classifier === '' || locationAndDate === '') return
      const currentCollectionName = `${classifier}_${locationAndDate}`
      console.log('Set collection name to: ', currentCollectionName)
      setCollectionName(currentCollectionName)
      savePartialState(localStorageId, { collectionName: currentCollectionName })
   }, [classifier, locationAndDate])

   return (
      <>
         <AppBar position="static">
            <Toolbar>
               <Box sx={{ flexGrow: 1, display: { xs: 'flex' } }}>
                  <Box sx={{ mr: 0.5 }}>
                     {' '}
                     {/* Add this */}
                     <Select
                        isSearchable
                        value={classifier === '' ? undefined : { value: classifier, label: classifier }}
                        options={classifierOptions}
                        onChange={(item) => {
                           if (item) {
                              setClassifier(item.value)
                           } else {
                              setClassifier('')
                           }
                        }}
                        styles={denseSelectStyles}
                     />
                  </Box>
                  <Box sx={{ mr: 0.5 }}>
                     <Select
                        isSearchable
                        value={locationAndDate === '' ? undefined : { value: locationAndDate, label: locationAndDate }}
                        options={collectionList
                           ?.filter((item) => item.startsWith(classifier))
                           .map((item) => {
                              const locationAndDate = item.split('_').slice(1)
                              return { value: locationAndDate.join('_'), label: locationAndDate.join(' ') }
                           })
                           .sort((a, b) => a.label.localeCompare(b.label))}
                        onChange={(item) => {
                           console.log(item)
                           if (item) {
                              setLocationAndDate(item.value)
                           } else {
                              setLocationAndDate('')
                           }
                        }}
                        styles={denseSelectStyles}
                     />
                  </Box>
               </Box>
               {mainToolBarChilds}
               <IconButton edge="end" color="inherit" onClick={onToggleFullScreen}>
                  {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
               </IconButton>
               <IconButton edge="end" color="inherit" onClick={onRemove}>
                  <DeleteForeverIcon />
               </IconButton>
            </Toolbar>
         </AppBar>
         {additionalToolBarChilds && <Toolbar> {additionalToolBarChilds}</Toolbar>}
      </>
   )
}
