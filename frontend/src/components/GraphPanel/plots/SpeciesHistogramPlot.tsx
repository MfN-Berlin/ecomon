import React, { useEffect, useRef, useState, useContext, ChangeEvent } from 'react'
import Plot from 'react-plotly.js'
import Select from 'react-select'
import Multiselect from 'multiselect-react-dropdown'
import CircularProgress from '@mui/material/CircularProgress'

import FileDownloadIcon from '@mui/icons-material/FileDownload'
import IconButton from '@material-ui/core/IconButton'
import { apiClient } from '@/services/api'
import { loadState, savePartialState } from '@/tools/localStorage'
import { PanelToolBarContext } from '../contexts/PanelToolBarContext'
import { firstLetterUpperAndReplaceSpace } from '@/tools/stringHandling'
import { denseSelectStyles } from '../PanelToolBar'
import { Box, Input, TextField } from '@mui/material'
import { makeStyles, styled } from '@mui/styles'

import { Theme } from '@mui/material/styles'
import InputLabel from '@material-ui/core/InputLabel'

interface SpeciesHistogramPlotProps {
   localStorageId: string
}
type HistogramData = {
   [species: string]: number[]
}
const BIN_SIZE = 0.01
const BIN_SIZES = Array(10)
   .join()
   .split(',')
   .map((_, i) => ({ label: ((i + 1) * BIN_SIZE).toFixed(3), value: (i + 1) * BIN_SIZE }))
console.log(BIN_SIZES)
const SMALLEST_BIN_SIZE = { label: 'BIN_SIZE', value: BIN_SIZE }
const useStyles = makeStyles((theme: Theme) => ({
   customTextField: {
      '& .MuiInputLabel-root': {
         color: '#fff'
      }
   }
})) as any

export default function SpeciesHistogramPlot({ localStorageId }: SpeciesHistogramPlotProps) {
   const plotRef = useRef<any>(null)
   const context = useContext(PanelToolBarContext)
   const classes = useStyles()
   const previousCollection = useRef('')

   if (!context) {
      // Handle the case where context is undefined
      throw new Error('ToolBarContext is not provided!')
   }
   const { setMainToolBarChilds, setAdditionalToolBarChilds, collectionName, speciesList, isSpeciesListFetching } =
      context

   const [valuesInit, setValuesInit] = useState(false)
   const [selectedSpecies, setSelectedSpecies] = useState<{ label: string; value: string }[]>([])
   const [rawDataMap, setRawDataMap] = useState<HistogramData>({})
   const [isFetchingData, setIsFetchingData] = useState(false)
   const [dataMap, setDataMap] = useState<HistogramData>({})
   const [xLabels, setXLabels] = useState<string[]>([])
   const [lowerBorder, setLowerBorder] = useState<number>(0.0)
   const [binSize, setBinSize] = useState<{ value: number; label: string }>(SMALLEST_BIN_SIZE)

   const isMounted = useRef(true)
   useEffect(() => {
      if (localStorageId && !valuesInit) {
         const state = loadState(localStorageId)
         setSelectedSpecies((state && state.selectedSpecies) || [])
         setLowerBorder((state && state.lowerBorder) || 0.0)
         setValuesInit(true)
      }

      return () => {
         isMounted.current = false
      }
   }, [])

   const handleDownloadCsv = () => {
      const header = ['Species', ...xLabels]
      const result = Object.entries(dataMap).map(([key, values]) => [key, ...values])

      const csvContent = 'data:text/csv;charset=utf-8,' + [header, ...result].join('\n')
      const encodedUri = encodeURI(csvContent)
      const link = document.createElement('a')
      link.setAttribute('href', encodedUri)
      link.setAttribute('download', 'data.csv')
      document.body.appendChild(link)
      link.click()
   }

   useEffect(() => {
      const fetchSpeciesData = async () => {
         console.log('Fetching data')
         const newDataMap: HistogramData = {}
         setIsFetchingData(true)
         for (let species of selectedSpecies) {
            console.log(`Fetching ${collectionName} data for species: `, species)
            try {
               const { data } = await apiClient.getCollectionPredictionsSpeciesHistogram(collectionName, species.value)
               if (data) {
                  console.log('Data fetched: ' + data.slice(0, 10).join(', '))
                  newDataMap[species.value] = data
                  console.log(`Data ${collectionName} fetched for species: `, species.label)
               }
            } catch (e) {
               setIsFetchingData(false)
               console.log(`Error fetching data for ${collectionName} and species: ${species.value}`, collectionName)
            }
         }
         setRawDataMap(newDataMap)
         setIsFetchingData(false)
      }

      if (previousCollection.current !== collectionName) {
         console.log('Resetting data map')
         setRawDataMap({})
         setDataMap({})
         previousCollection.current = collectionName
         fetchSpeciesData()
      } else {
         fetchSpeciesData()
      }
   }, [selectedSpecies, collectionName])

   useEffect(() => {
      if (localStorageId && valuesInit) {
         savePartialState(localStorageId, {
            selectedSpecies,
            lowerBorder
         })
      }
      setAdditionalToolBarChilds(
         <Multiselect
            isObject={true}
            selectedValues={selectedSpecies}
            loading={isSpeciesListFetching}
            options={speciesList?.map((species) => ({
               label: firstLetterUpperAndReplaceSpace(species.name),
               value: species.name
            }))}
            displayValue="label" // Property name to display in the dropdown options
            onSelect={(selectedList) => {
               setSelectedSpecies(selectedList)
            }}
            onRemove={(selectedList) => {
               setSelectedSpecies(selectedList)
            }}
         />
      )
   }, [selectedSpecies, isSpeciesListFetching, speciesList, lowerBorder])

   useEffect(() => {
      calculateXLabels()
   }, [binSize, lowerBorder])

   useEffect(() => {
      setMainToolBarChilds(
         <>
            <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
               <InputLabel htmlFor="binSizeSelect" shrink style={{ marginBottom: '-5px', color: 'white' }}>
                  Bin Size
               </InputLabel>
               <Select
                  aria-label="Bin Size"
                  inputId="binSizeSelect"
                  id="binSizeSelect"
                  value={binSize}
                  options={BIN_SIZES}
                  onChange={(item: any) => {
                     if (item) {
                        setBinSize(item)
                     } else {
                        setBinSize(SMALLEST_BIN_SIZE)
                     }
                  }}
                  styles={denseSelectStyles}
               />
            </div>
            <TextField
               type="number"
               InputProps={{
                  inputProps: { min: 0, max: 1, step: BIN_SIZE },
                  style: { backgroundColor: 'white' }
               }}
               value={lowerBorder}
               onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  const newValue = parseFloat(e.target.value)
                  if (isNaN(newValue) || newValue < 0 || newValue > 1) return

                  setLowerBorder(newValue)
               }}
               label="Lower Border"
               variant="standard"
               size="small"
               className={classes.customTextField}
               style={{ marginLeft: '5px', width: '80px' }}
            />
            <IconButton edge="end" color="inherit" key="download-csv" onClick={handleDownloadCsv}>
               <FileDownloadIcon />
            </IconButton>
         </>
      )
   }, [binSize, dataMap, xLabels])

   useEffect(() => {
      const newDataMap: HistogramData = {}

      for (const species in rawDataMap) {
         newDataMap[species] = aggregateBins(rawDataMap[species], binSize.value)
      }

      setDataMap(newDataMap)
   }, [binSize, rawDataMap, lowerBorder])

   function aggregateBins(data: number[], newBinSize: number) {
      const binRatio = newBinSize / BIN_SIZE // The number of original bins that will be combined into a single bin
      const result: number[] = []

      for (let i = 0; i < data.length; i += binRatio) {
         // Sum the counts for the bins that will be combined
         const binSum = data.slice(i, i + binRatio).reduce((sum, count) => sum + count, 0)
         if (i * BIN_SIZE < lowerBorder) {
            continue
         }
         result.push(binSum)
      }

      return result
   }

   // function getColor(value: number) {
   //    // Implement your logic to map a value to a color
   //    return 'rgba(75, 192, 192, 0.2)'
   // }
   function calculateXLabels() {
      let labels: string[] = []
      // adding floating point numbers is not a good idea
      for (let i = 0; i < 0.99999; i = i + binSize.value) {
         if (i < lowerBorder) {
            continue
         }
         console.log(i)
         labels.push(i.toFixed(3))
      }
      console.log('Labels: ', labels)
      setXLabels(labels)
   }

   return (
      <>
         <Plot
            data={Object.keys(dataMap).map((species) => ({
               x: xLabels,
               y: dataMap[species],
               type: 'scatter', // or 'bar' for a bar plot
               mode: 'lines',
               //marker: { color: getColor(species) },  // You may want to change color for different species
               name: species
            }))}
            layout={{
               xaxis: {
                  title: 'Value',
                  autorange: true // Ensures x-axis is scaled automatically
               },
               yaxis: {
                  title: 'Count',
                  range: [0, 'max']
               },
               margin: {
                  t: 10 // Top margin
               },
               autosize: true // Enable automatic resizing
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
