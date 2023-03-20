import React from 'react'
import Grid from '@mui/material/Unstable_Grid2'
import Histogram, { HistogramData } from '../../components/Histogram'
import { Report } from '../../generated/api/index'
import Tabs from '@mui/material/Tabs'
import { Tab } from '@mui/material'
import AppBar from '@material-ui/core/AppBar'
import { type } from 'os'
import DataTable from '../../components/DataTable'

interface Props {
   report: Report
}

export default function CollectionStatsHistograms({ report }: Props) {
   const [tabIndex, setTabIndex] = React.useState(0)
   const [data, setData] = React.useState<HistogramData[]>([])
   React.useEffect(() => {
      updateData(tabIndex)
   }, [tabIndex, report])

   function a11yProps(index: number) {
      return {
         id: `full-width-tab-${index}`,
         'aria-controls': `full-width-tabpanel-${index}`
      }
   }
   function updateData(index: number) {
      switch (index) {
         case 0:
            setData(
               report.monthly_summary_query.map((bin) => {
                  return {
                     range: bin.date,
                     count: bin.count
                  }
               })
            )
            break
         case 1:
            setData(
               report.daily_summary_query.map((bin) => {
                  return {
                     range: bin.date,
                     count: bin.count
                  }
               })
            )
            break
         case 2:
            setData(
               report.record_duration_histogram_query.map((bin) => {
                  return {
                     range: bin.duration + 's',
                     count: bin.record_count
                  }
               })
            )
            break
         case 3:
            setData(
               report.record_prediction_count_histogram_query.map((bin) => {
                  return {
                     range: bin.prediction_count + '',
                     count: bin.record_count
                  }
               })
            )
            break
      }
   }

   const handleChange = (event: any, newValue: number) => {
      console.log(newValue)
      setTabIndex(newValue)
      updateData(newValue)
   }

   const histogramInfos = [
      {
         title: 'Monthly Records',
         type: 'bar'
      },
      {
         title: 'Daily Records',
         type: 'bar'
      },
      {
         title: 'Record Durations',
         type: 'table'
      },
      {
         title: 'Record Predictions',
         type: 'table'
      }
   ]

   return (
      <Grid xs={12} container>
         <Grid xs={12}>
            <Tabs
               value={tabIndex}
               onChange={handleChange}
               indicatorColor="primary"
               textColor="inherit"
               variant="fullWidth"
               aria-label="Different Histograms of collection stats"
            >
               {histogramInfos.map((histogramInfo, index) => (
                  <Tab label={histogramInfo.title} {...a11yProps(index)} />
               ))}
            </Tabs>
         </Grid>
         <Grid xs={12}>
            {histogramInfos[tabIndex].type === 'bar' && <Histogram data={data} zoom={'xy'} />}
            {histogramInfos[tabIndex].type === 'table' && (
               <DataTable
                  rowLabels={data.map((item) => item.range)}
                  columnLabels={['', 'Count']}
                  data={[data.map((item) => item.count.toString())]}
               />
            )}
         </Grid>
      </Grid>
   )
}
