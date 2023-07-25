import React, { useEffect, useRef, useState, useContext } from 'react'
import { Paper, Button, Grid, Select } from '@mui/material'
import { loadState, savePartialState } from '@/tools/localStorage'
import SpeciesEventsPanel from './plots/SpeciesEventsPanel'
import SpeciesHistogramPlot from './plots/SpeciesHistogramPlot'
import { PanelToolBarProvider } from './contexts/PanelToolBarContext'

import PanelToolBar from './PanelToolBar'

interface GraphPanelProps {
   onRemove?: () => void
   localStorageId: string
}

const PLOT_TYPES = {
   events: 'EVENTS',
   histogram: 'histogram'
}

const plotTypeOptions = [
   {
      value: PLOT_TYPES.events,
      label: 'Events'
   },
   {
      value: PLOT_TYPES.histogram,
      label: 'Histogram'
   }
]

export default function GraphPanel({ onRemove, localStorageId }: GraphPanelProps) {
   const [valuesInit, setValuesInit] = useState(false)
   const [currentPlotType, setCurrentPlotType] = useState<{ value: string; label: string } | undefined>()

   const [isFullscreen, setIsFullscreen] = useState(false)

   const isMounted = useRef(true)

   function toggleFullScreen() {
      setIsFullscreen(!isFullscreen)
      setTimeout(() => {
         // dispatch resize event so plotly is resizing
         window.dispatchEvent(new Event('resize'))
      }, 0)
      // refresh plotlys
   }

   useEffect(() => {
      if (localStorageId && !valuesInit) {
         const state = loadState(localStorageId)
         if (state) {
            setCurrentPlotType(state.plotType)
            setTimeout(() => {
               setValuesInit(true) // this is needed to prevent updating the localStorage with empty values
            }, 0)
         }
      }

      return () => {
         isMounted.current = false
      }
   }, [])
   useEffect(() => {
      if (localStorageId && valuesInit) {
         savePartialState(localStorageId, {
            plotType: currentPlotType
         })
      }
   }, [currentPlotType, localStorageId])

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
         <PanelToolBarProvider>
            <PanelToolBar
               localStorageId={localStorageId}
               isFullscreen={isFullscreen}
               onToggleFullScreen={toggleFullScreen}
               onRemove={onRemove}
            ></PanelToolBar>
            <div
               style={{
                  width: '100%',
                  paddingTop: '46.25%', // This will maintain a 16:9 aspect ratio
                  position: 'relative' // This is necessary for the child div to be positioned correctly
               }}
            >
               {currentPlotType === undefined && (
                  <Grid
                     container
                     spacing={5}
                     alignItems="stretch"
                     style={{
                        position: 'absolute', // This will make the plot fill the parent div
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: '10px',
                        height: '100%'
                     }}
                  >
                     {plotTypeOptions.map((option, index) => (
                        <Grid item xs={6} key={index}>
                           <Button
                              variant="contained"
                              color="secondary"
                              fullWidth
                              style={{ height: '100%' }}
                              onClick={() => setCurrentPlotType(option)}
                           >
                              {option.label}
                           </Button>
                        </Grid>
                     ))}
                  </Grid>
               )}

               {currentPlotType && currentPlotType.value === PLOT_TYPES.events && (
                  <SpeciesEventsPanel localStorageId={localStorageId} />
               )}
               {currentPlotType && currentPlotType.value === PLOT_TYPES.histogram && (
                  <SpeciesHistogramPlot localStorageId={localStorageId}></SpeciesHistogramPlot>
               )}
            </div>
         </PanelToolBarProvider>
      </Paper>
   )
}
