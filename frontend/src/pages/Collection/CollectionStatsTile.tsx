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
import { usePredictionCount } from '../../hooks/predictions'
import { useRecordCount, useRecordDuration, useFirstRecord, useLastRecord } from '../../hooks/records'
import { secondsToYearsMonthDaysHoursMinutesSeconds } from '../../tools/timeHandling'
import { useCollectionStats } from './CollectionStatsContext'

dayjs.extend(utc)
dayjs.extend(timezone)
// Set to Central European Winter time, weird notation offset is inverse
dayjs.tz.setDefault('Etc/GMT-1')

interface CollectionStatsProps {
   collectionId: string | undefined
}
export default function CollectionStats({ collectionId: id }: CollectionStatsProps) {
   const { predictionCount, loading: predictionLoading } = usePredictionCount(id)
   const { recordCount, loading: recordLoading } = useRecordCount(id)
   const { recordDuration, loading: durationLoading } = useRecordDuration(id)
   const { firstRecord, loading: firstRecordLoading } = useFirstRecord(id)
   const { lastRecord, loading: lastRecordLoading } = useLastRecord(id)
   const collectionStats = useCollectionStats()
   useEffect(() => {
      collectionStats.setPredictionCount(predictionCount)
   }, [predictionCount])
   useEffect(() => {
      collectionStats.setRecordCount(recordCount)
   }, [recordCount])
   useEffect(() => {
      collectionStats.setRecordDuration(recordDuration)
   }, [recordDuration])
   useEffect(() => {
      collectionStats.setFirstRecord(firstRecord)
   }, [firstRecord])
   useEffect(() => {
      collectionStats.setLastRecord(lastRecord)
   }, [lastRecord])
   useEffect(() => {
      collectionStats.setPredictionLoading(predictionLoading)
   }, [predictionLoading])
   useEffect(() => {
      collectionStats.setRecordLoading(recordLoading)
   }, [recordLoading])
   useEffect(() => {
      collectionStats.setDurationLoading(durationLoading)
   }, [durationLoading])
   useEffect(() => {
      collectionStats.setFirstRecordLoading(firstRecordLoading)
   }, [firstRecordLoading])
   useEffect(() => {
      collectionStats.setLastRecordLoading(lastRecordLoading)
   }, [lastRecordLoading])

   return (
      <Grid xs={12} md={4}>
         <Paper
            sx={{
               padding: 1
            }}
         >
            <Stack direction="column" spacing={2}>
               <Typography
                  variant="h6"
                  component="h6"
                  align="left"
                  sx={{
                     marginTop: 1,
                     marginLeft: 2,
                     paddingBottom: 2
                  }}
               >
                  Stats
               </Typography>
               <DateTimePicker
                  renderInput={(props: TextFieldProps) => <TextField {...props} />}
                  label="First Recording starts at"
                  inputFormat="YYYY/MM/DD HH:mm:ss"
                  value={dayjs(firstRecord?.record_datetime)}
                  readOnly={true}
                  ampm={false}
                  loading={firstRecordLoading}
                  onChange={(value: Date | null) => {}}
               />
               <DateTimePicker
                  renderInput={(props: TextFieldProps) => <TextField {...props} />}
                  label="Last Recording starts at"
                  inputFormat="YYYY/MM/DD HH:mm:ss"
                  value={dayjs(lastRecord?.record_datetime.toISOString())}
                  readOnly={true}
                  ampm={false}
                  loading={lastRecordLoading}
                  onChange={(value: Date | null) => {}}
               />

               <TextField
                  id="recordCount"
                  label="Recording Count"
                  variant="standard"
                  value={recordLoading ? 'Loading...' : recordCount}
                  InputProps={{
                     readOnly: true
                  }}
               />
               <TextField
                  id="recordDuration"
                  label="Summed Duration of Recordings"
                  variant="standard"
                  value={durationLoading ? 'loading...' : secondsToYearsMonthDaysHoursMinutesSeconds(recordDuration)}
                  InputProps={{
                     readOnly: true
                  }}
               />
               <TextField
                  id="predictionCount"
                  label="Prediction Count"
                  variant="standard"
                  value={predictionLoading ? 'loading...' : predictionCount}
                  InputProps={{
                     readOnly: true
                  }}
               />
            </Stack>
         </Paper>
      </Grid>
   )
}
