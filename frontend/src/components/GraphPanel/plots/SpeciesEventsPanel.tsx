import React, { useEffect, useRef, useState, useContext } from 'react'
import Plot from 'react-plotly.js'
import { loadState, savePartialState } from '@/tools/localStorage'
import Box from '@mui/material/Box'
import Select, { StylesConfig } from 'react-select'
import CircularProgress from '@mui/material/CircularProgress'
import { useGetCollectionSpeciesEventsQuery, useGetCollectionListQuery } from '@/services/api'
import { PredictionMax } from '@/generated/api'
import { generateDatesInYear, getYearDaysCount, generateTimeLabels, getTimeSlotOfDayCount } from '@/tools/timeHandling'
import { PanelToolBarContext } from '../contexts/PanelToolBarContext'
import { firstLetterUpperAndReplaceSpace } from '@/tools/stringHandling'
import { denseSelectStyles } from '../PanelToolBar'

interface SpeciesHistogramPanelProps {
   localStorageId: string
}

export default function SpeciesHistogramPanel({ localStorageId }: SpeciesHistogramPanelProps) {
   const plotRef = useRef<any>(null)
   const context = useContext(PanelToolBarContext)
   const [valuesInit, setValuesInit] = useState(false)
   if (!context) {
      // Handle the case where context is undefined
      throw new Error('ToolBarContext is not provided!')
   }
   const {
      setMainToolBarChilds,
      collectionName,
      classifier,
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

   const [species, setSpecies] = useState<string>('')
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
   const [threshold, setThreshold] = useState<number>(0)

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
               // Apply threshold filter
               const value = item.value >= threshold ? item.value : 0
               dataMap[timeSlot][dayOfYear] = value
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

   useEffect(() => {
      console.log('localStorageId:' + localStorageId, species, threshold)
      if (localStorageId && valuesInit) {
         savePartialState(localStorageId, { species, threshold })
      }
   }, [species, threshold])

   useEffect(() => {
      setMainToolBarChilds(
         <Box sx={{ display: 'flex', gap: 1 }}>
            <Select
               isSearchable
               value={species == '' ? undefined : { value: species, label: firstLetterUpperAndReplaceSpace(species) }}
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
               styles={denseSelectStyles}
            />
            <input
               type="number"
               value={threshold}
               min={0}
               max={1}
               step={0.05}
               onChange={(e) => setThreshold(Number(e.target.value))}
               style={{
                  width: '80px',
                  height: '30px',
                  padding: '0 8px',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
               }}
            />
         </Box>
      )
   }, [speciesList, species, threshold])

   useEffect(() => {
      if (localStorageId && !valuesInit) {
         const state = loadState(localStorageId)
         if (state) {
            if (state.species) setSpecies(state.species)
            if (state.threshold !== undefined) setThreshold(state.threshold)
         }
         setTimeout(() => setValuesInit(true), 0)
      }

      return () => {
         isMounted.current = false
      }
   }, [])

   useEffect(() => {
      updateHeatMapData(data)
   }, [data, threshold])

   useEffect(() => {
      // if one element is not set, clear the heatmap
      if (!classifier || !locationAndDate || !species) {
         setHeatmapData(initHeatMapData(getTimeSlotOfDayCount(10), getYearDaysCount(2023)))
      }
   }, [collectionName, species])

   function getColor(value: number) {
      // Implement your logic to map a value to a color
      return 'rgba(75, 192, 192, 0.2)'
   }
   return (
      <>
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
      </>
   )
}
