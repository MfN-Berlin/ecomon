import { useEffect } from 'react'
import * as React from 'react'
import Grid from '@mui/material/Unstable_Grid2'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import TextField, { TextFieldProps } from '@mui/material/TextField'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import { secondsToYearsMonthDaysHoursMinutesSeconds } from '../../tools/timeHandling'
import { useCollectionStats } from './Context/CollectionStatsContext'

import { useGetCollectionReportQuery } from '../../services/api'
import DBIndexChipList from './DBIndexChipList'
import Histogram from '../../components/Histogram'
import CollectionStatsHistograms from './CollectionStatsHistograms'

dayjs.extend(utc)
dayjs.extend(timezone)
// Set to Central European Winter time, weird notation offset is inverse
dayjs.tz.setDefault('Etc/GMT-1')

interface CollectionStatsProps {
   collectionId: string | undefined
}
export default function CollectionStats({ collectionId: id }: CollectionStatsProps) {
   const { data: report, refetch, isFetching } = useGetCollectionReportQuery(id)

   const {
      setReport,
      setLoading,
      lastRecordDatetime,
      firstRecordDatetime,
      recordCount,
      recordDuration,
      predictionCount,
      loading
   } = useCollectionStats()

   useEffect(() => {
      if (id) {
         refetch()
      }
   }, [id, refetch])
   useEffect(() => {
      console.log('report:', report)
      setReport(report)
   }, [report])
   useEffect(() => {
      console.log('isFetching:', isFetching)
      setLoading(isFetching)
   }, [isFetching])

   return (
      <Grid container spacing={0}>
         <Grid container xs={12} md={6} spacing={2}>
            <Grid xs={12}>
               <Typography variant="subtitle2" component="div" align="left" sx={{ paddingBottom: 2 }}>
                  Collection Stats:
               </Typography>
            </Grid>
            <Grid xs={6}>
               <Stack direction="column" spacing={1}>
                  <DateTimePicker
                     renderInput={(props: TextFieldProps) => <TextField {...props} />}
                     label="First Recording starts at"
                     inputFormat="YYYY/MM/DD HH:mm:ss"
                     value={dayjs(firstRecordDatetime)}
                     readOnly={true}
                     ampm={false}
                     loading={loading}
                     onChange={(value: Date | null) => {}}
                  />
                  <DateTimePicker
                     renderInput={(props: TextFieldProps) => <TextField {...props} />}
                     label="Last Recording starts at"
                     inputFormat="YYYY/MM/DD HH:mm:ss"
                     value={dayjs(lastRecordDatetime)}
                     readOnly={true}
                     ampm={false}
                     loading={loading}
                     onChange={(value: Date | null) => {}}
                  />
               </Stack>
            </Grid>

            <Grid xs={6}>
               <Stack direction="column" spacing={1}>
                  <TextField
                     id="recordCount"
                     label="Recording Count"
                     value={isFetching ? 'Loading...' : recordCount}
                     InputProps={{
                        readOnly: true
                     }}
                  />
                  <TextField
                     id="predictionCount"
                     label="Prediction Count"
                     value={isFetching ? 'loading...' : predictionCount}
                     InputProps={{
                        readOnly: true
                     }}
                  />
               </Stack>
            </Grid>

            <Grid xs={4}>
               <TextField
                  id="recordDuration"
                  label="Summed Duration of Recordings"
                  value={isFetching ? 'loading...' : secondsToYearsMonthDaysHoursMinutesSeconds(recordDuration)}
                  InputProps={{
                     readOnly: true
                  }}
               />
            </Grid>

            <Grid xs={12} md={12}>
               <DBIndexChipList />
            </Grid>
         </Grid>
         <Grid container xs={12} md={6} spacing={0}>
            {report && <CollectionStatsHistograms report={report} />}
         </Grid>
      </Grid>
   )
}
