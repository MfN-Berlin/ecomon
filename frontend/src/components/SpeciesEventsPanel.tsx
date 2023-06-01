import React, { useEffect, useRef, useState } from 'react'
import Plot from 'react-plotly.js'

import Paper from '@mui/material/Paper'
import Select, { StylesConfig } from 'react-select'
import CircularProgress from '@mui/material/CircularProgress'
import Toolbar from '@mui/material/Toolbar'
import IconButton from '@mui/material/IconButton'
import AppBar from '@mui/material/AppBar'
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'
import FullscreenIcon from '@mui/icons-material/FullscreenExitOutlined'
import FullscreenExitIcon from '@mui/icons-material/FullscreenExitOutlined'
import { multiValueAsValue } from 'react-select/dist/declarations/src/utils'
import { firstLetterUpperAndReplaceSpace } from '../tools/stringHandling'
import {
   useGetCollectionSpeciesEventsQuery,
   useGetCollectionListQuery,
   useGetCollectionSpeciesListQuery
} from '../services/api'
import { PredictionMax } from '../generated/api'
import { generateDatesInYear, getYearDaysCount, generateTimeLabels, getTimeSlotOfDayCount } from '../tools/timeHandling'
import { loadState, saveState, removeState } from '../tools/localStorage'
import Box from '@mui/material/Box'

interface SpeciesEventsPanelProps {
   onRemove?: () => void
   localStorageId?: string
}
const classifierOptions = [
   { value: 'BIRDNET', label: 'Birdnet' },
   { value: 'BIRDID', label: 'BirdId' }
]

const customStyles = {
   option: (provided: any, state: any) => {
      const color = 'black'
      return { ...provided, color }
   }
}

export default function SpeciesEventsPanel({ onRemove, localStorageId }: SpeciesEventsPanelProps) {
   const plotRef = useRef<any>(null)
   const [collectionName, setCollectionName] = useState<string>('')
   const [classifier, setClassifier] = useState<string>('')
   const [locationAndDate, setLocationAndDate] = useState<string>('')
   const [species, setSpecies] = useState<string>('')
   const [isFullscreen, setIsFullscreen] = useState(false)

   const [heatmapData, setHeatmapData] = useState<number[][]>(
      initHeatMapData(getTimeSlotOfDayCount(10), getYearDaysCount(2023))
   )
   const [xLabels, setXLabels] = useState<string[]>(generateDatesInYear(2023))
   const [yLabels, setYLabels] = useState<string[]>(generateTimeLabels(10))
   const isMounted = useRef(true)
   const {
      data,
      refetch: refetchData,
      isFetching: isFetchingData
   } = useGetCollectionSpeciesEventsQuery({
      collectionName,
      species
   })
   const {
      data: collectionList,
      refetch: refetchCollectionList,
      isFetching: isCollectionListFetching
   } = useGetCollectionListQuery()
   const { data: speciesList, isFetching: isSpeciesListFetching } = useGetCollectionSpeciesListQuery({ collectionName })

   function initHeatMapData(x: number, y: number) {
      // create arra whith zeros in the dimension x,y
      let arr = new Array(x)
      for (let i = 0; i < x; i++) {
         arr[i] = new Array(y).fill(undefined)
      }
      return arr
   }

   function updateHeatMapData(data: PredictionMax[] | undefined): any {
      if (data && data.length > 0) {
         const RECORD_INTERVAL = 15
         const YEAR = parseInt(collectionName.split('_')[2])
         console.log(`Init map with x:${getTimeSlotOfDayCount(RECORD_INTERVAL)} y: ${getYearDaysCount(YEAR)}`)
         const dataMap = initHeatMapData(getTimeSlotOfDayCount(RECORD_INTERVAL), getYearDaysCount(YEAR))
         data.forEach((item) => {
            let date = new Date(item.record_datetime)
            let dayOfYear = Math.floor((date.getTime() - new Date(YEAR, 0, 0).getTime()) / 1000 / 60 / 60 / 24)
            let timeSlot = Math.floor((date.getHours() * 60 + date.getMinutes()) / RECORD_INTERVAL) // adjust denominator to match your time slot duration
            try {
               dataMap[timeSlot][dayOfYear] = item.value
            } catch (error) {
               console.log('error on:', item)
               console.log('timeSlot:', timeSlot)
               console.log('dayOfYear:', dayOfYear)
               console.log(error)
            }
         })
         setHeatmapData(dataMap)
         setYLabels(generateTimeLabels(RECORD_INTERVAL))
         setXLabels(generateDatesInYear(YEAR))
      }
   }
   function toggleFullScreen() {
      setIsFullscreen(!isFullscreen)
      setTimeout(() => {
         // dispatch resize event so plotly is resizing
         window.dispatchEvent(new Event('resize'))
      }, 0)
      // refresh plotlys
   }

   useEffect(() => {
      refetchCollectionList()
      if (localStorageId) {
         const state = loadState(localStorageId)
         if (state) {
            setCollectionName(state.collectionName)
            setClassifier(state.classifier)
            setLocationAndDate(state.locationAndDate)
            setSpecies(state.species)
         }
      }

      return () => {
         isMounted.current = false
      }
   }, [])
   useEffect(() => {
      if (localStorageId) {
         saveState(localStorageId, {
            collectionName,
            classifier,
            locationAndDate,
            species
         })
      }
   }, [collectionName, classifier, locationAndDate, species])

   useEffect(() => {
      setCollectionName(`${classifier}_${locationAndDate}`)
   }, [classifier, locationAndDate])
   useEffect(() => {
      console.log('data:', data)
      updateHeatMapData(data)
   }, [data])
   useEffect(() => {
      console.log('isFetchingData:', isFetchingData)
   }, [isFetchingData])
   useEffect(() => {
      // if one element is not set, clear the heatmap
      if (!classifier || !locationAndDate || !species) {
         setHeatmapData(initHeatMapData(getTimeSlotOfDayCount(10), getYearDaysCount(2023)))
      }
   }, [classifier, locationAndDate, species])

   function getColor(value: number) {
      // Implement your logic to map a value to a color
      return 'rgba(75, 192, 192, 0.2)'
   }
   return (
      <Paper
         style={{
            position: isFullscreen ? 'fixed' : 'relative',
            top: 0,
            left: 0,
            zIndex: isFullscreen ? 9999 : undefined,
            height: isFullscreen ? '100%' : 'fit-content',
            width: '100%'
         }}
      >
         <AppBar position="static">
            <Toolbar color="primary">
               <Box sx={{ flexGrow: 1, display: { xs: 'flex' } }}>
                  <Box sx={{ mr: 0.5 }}>
                     {' '}
                     {/* Add this */}
                     <Select
                        isClearable
                        isSearchable
                        value={classifier == '' ? undefined : { value: classifier, label: classifier }}
                        options={classifierOptions}
                        onChange={(item) => {
                           if (item) {
                              setClassifier(item.value)
                           } else {
                              setClassifier('')
                           }
                        }}
                        styles={customStyles}
                     />
                  </Box>
                  <Box sx={{ mr: 0.5 }}>
                     <Select
                        isClearable
                        isSearchable
                        value={locationAndDate == '' ? undefined : { value: locationAndDate, label: locationAndDate }}
                        options={collectionList
                           ?.filter((item) => item.startsWith(classifier))
                           .map((item) => {
                              const locationAndDate = item.split('_').slice(1)
                              return { value: locationAndDate.join('_'), label: locationAndDate.join(' ') }
                           })}
                        onChange={(item) => {
                           console.log(item)
                           if (item) {
                              setLocationAndDate(item.value)
                           } else {
                              setLocationAndDate('')
                           }
                        }}
                        styles={customStyles}
                     />
                  </Box>

                  <Select
                     isClearable
                     isSearchable
                     value={
                        species == '' ? undefined : { value: species, label: firstLetterUpperAndReplaceSpace(species) }
                     }
                     options={speciesList?.map((item) => ({
                        value: item.name,
                        label: firstLetterUpperAndReplaceSpace(item.name)
                     }))}
                     onChange={(item) => {
                        if (item) {
                           setSpecies(item.value)
                        } else {
                           setSpecies('')
                        }
                     }}
                     styles={customStyles}
                  />
               </Box>
               <IconButton edge="end" color="inherit" onClick={() => toggleFullScreen()}>
                  {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
               </IconButton>
               <IconButton edge="end" color="inherit" onClick={onRemove}>
                  <DeleteForeverIcon />
               </IconButton>
            </Toolbar>
         </AppBar>

         <div
            style={{
               width: '100%',
               paddingTop: '56.25%', // This will maintain a 16:9 aspect ratio
               position: 'relative' // This is necessary for the child div to be positioned correctly
            }}
         >
            <Plot
               data={[
                  {
                     z: heatmapData,
                     x: xLabels,
                     y: yLabels,
                     type: 'heatmap',
                     zmin: 0,
                     zmax: 1
                  }
               ]}
               layout={{
                  xaxis: {
                     title: 'Date'
                  },
                  yaxis: {
                     title: 'Time'
                  },
                  margin: {
                     t: 10 // Top margin
                  }
               }}
               useResizeHandler={true}
               style={{
                  position: 'absolute', // This will make the plot fill the parent div
                  top: 0,
                  bottom: 0,
                  left: 0,
                  right: 0
               }}
               config={{ responsive: true }}
               ref={plotRef}
               onClick={(data) => {
                  // data.points is an array of points that were clicked
                  // Each point has various properties like x, y, z, curveNumber, pointNumber, etc.
                  console.log(data.points)
               }}
            />
         </div>

         {isFetchingData && (
            <div
               style={{
                  position: 'absolute',
                  top: 0,
                  bottom: 0,
                  left: 0,
                  right: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 2
               }}
            >
               <CircularProgress />
            </div>
         )}
      </Paper>
   )
}
