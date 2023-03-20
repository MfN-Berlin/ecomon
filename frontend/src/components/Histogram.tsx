import React, { useEffect, useRef, useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import zoomPlugin from 'chartjs-plugin-zoom'
import { AnyAsyncThunk } from '@reduxjs/toolkit/dist/matchers'
import HighlightOffIcon from '@mui/icons-material/HighlightOffSharp'
import IconButton from '@mui/material/IconButton'
import { margin } from '@mui/system'
import { TypedChartComponent } from 'react-chartjs-2/dist/types'
ChartJS.register(
   CategoryScale,
   LinearScale,
   BarElement,
   Tooltip,

   zoomPlugin
)

export interface HistogramData {
   range: string
   count: number
}

interface HistoProps {
   data: HistogramData[]
   title?: string
   zoom?: 'x' | 'y' | 'xy' | undefined
}

export default function Histogram({ data, title, zoom }: HistoProps) {
   const chartRef = useRef<any>(null)
   const [isZoomed, setIsZoomed] = useState(false)
   const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
         legend: {
            position: 'top' as const
         },
         title: {
            display: typeof title !== undefined,
            text: title
         },
         scales: {
            yAxes: [
               {
                  type: 'logarithmic',
                  ticks: {
                     min: 0,
                     max: 10000000
                  }
               }
            ]
         },
         zoom: {
            pan: {
               enabled: typeof zoom !== 'undefined',
               mode: zoom
               // pan options and/or events
            },
            limits: {
               // axis limits
               y: {
                  min: 0
               },
               x: {
                  min: 0
               }
            },
            zoom: {
               wheel: { enabled: typeof zoom !== 'undefined' },
               mode: zoom,
               overScaleMode: 'x' as const
               // zoom options and/or events
            },
            drag: {
               enabled: { enabled: typeof zoom !== 'undefined' },
               mode: zoom
            }
         }
      }
   }

   const histData = {
      labels: data.map((bin) => bin.range),
      datasets: [
         {
            label: 'Dataset 1',
            data: data.map((bin) => bin.count),
            backgroundColor: 'rgba(255, 99, 132, 0.5)'
         }
      ]
   }

   useEffect(() => {
      if (chartRef.current) {
         chartRef.current.resetZoom()
      }
   }, [data])

   const handleResize = () => {
      if (chartRef.current) {
         chartRef.current.resize()
         chartRef.current.resetZoom()
      }
   }

   useEffect(() => {
      // set zoom and reset liteners

      window.addEventListener('resize', handleResize)
      return () => {
         window.removeEventListener('resize', handleResize)
      }
   }, [])

   return (
      <div style={{ position: 'relative', height: '100%', width: '100%' }}>
         {isZoomed && (
            <IconButton
               onClick={() => {
                  chartRef.current.resetZoom()
                  setIsZoomed(false)
               }}
               aria-label="reset zoom"
               style={{ position: 'absolute', top: '0px', right: '0px', marginTop: '-15px' }}
            >
               <HighlightOffIcon />
            </IconButton>
         )}
         <Bar ref={chartRef} onWheel={() => setIsZoomed(true)} options={options} data={histData} />
      </div>
   )
}
