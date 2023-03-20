import * as React from 'react'
import Grid from '@mui/material/Unstable_Grid2'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import TextField, { TextFieldProps } from '@mui/material/TextField'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import SendIcon from '@mui/icons-material/Send'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import { useQueryParameters } from './Context/QueryParameterContext'
import { useCollectionStats } from './Context/CollectionStatsContext'

import Select from 'react-select'

import NumberInput from '../../components/NumberInput'
import Checkbox from '@mui/material/Checkbox'
import Button from '@mui/material/Button'
import FormControlLabel from '@mui/material/FormControlLabel'
import { API_PATH } from '../../consts'

import { firstLetterUpperAndReplaceSpace } from '../../tools/stringHandling'
import { useCollectionSpeciesList, useCollectionPredictionQuery } from '../../hooks/collection'
import { useEffect } from 'react'
import { useQueryResult } from './Context/QueryResultContext'

dayjs.extend(utc)
dayjs.extend(timezone)
// Set to Central European Winter time, weird notation offset is inverse
dayjs.tz.setDefault('Etc/GMT-1')

interface CollectionStatsProps {
   collectionId: string | undefined
}

export default function QueryParameters({ collectionId: id }: CollectionStatsProps) {
   const { collectionSpeciesList, loading: speciesLoading } = useCollectionSpeciesList(id)
   const { firstRecordDatetime, lastRecordDatetime, loading } = useCollectionStats()
   const { setLoading: setQueryLoading, setResult: setQueryResult } = useQueryResult()
   const {
      predictionQueryResponse,
      loading: queryLoading,
      updateQuery,
      abortQuery,
      clearResponse
   } = useCollectionPredictionQuery(id)

   const {
      from,
      setFrom,
      until,
      setUntil,
      thresholdMax,
      setThresholdMax,
      thresholdMin,
      setThresholdMin,
      binWidth,
      setBinWidth,
      hasIndex,
      setHasIndex,
      selectedSpecies,
      setSelectedSpecies
   } = useQueryParameters()

   useEffect(() => {
      setFrom(firstRecordDatetime)
      setUntil(lastRecordDatetime)
   }, [loading])

   useEffect(() => {
      setQueryResult(predictionQueryResponse)
   }, [predictionQueryResponse])
   useEffect(() => {
      setQueryLoading(queryLoading)
   }, [queryLoading])

   // effect clear prediction query response on change
   useEffect(() => {
      abortQuery()
      clearResponse()
      // eslint-disable-next-line
   }, [selectedSpecies])

   // Event handlers
   function handleQueryButtonClick() {
      console.log('handleQueryButtonClick with selectedSpecies:', selectedSpecies)
      if (selectedSpecies)
         updateQuery({
            species: selectedSpecies,
            start_datetime: from?.toISOString(),
            end_datetime: until?.toISOString(),
            threshold_min: thresholdMin,
            threshold_max: thresholdMax
         })
   }

   function calcBinSizesButtonClick() {
      const url = `${API_PATH}/evaluation/bin-sizes`
      fetch(url, {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json'
         },
         body: JSON.stringify({
            collection_name: id,
            species: selectedSpecies,
            bin_width: binWidth,
            start_datetime: from?.toISOString(),
            end_datetime: until?.toISOString()
         })
      })
         .then((res) => res.json())
         .then((data) => {
            // setLoading(false)
         })
   }
   function getDailyHistogramsButtonClick() {
      const url = `${API_PATH}/evaluation/daily-histograms`
      fetch(url, {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json'
         },
         body: JSON.stringify({
            collection_name: id,
            species: selectedSpecies,
            bin_width: binWidth,
            start_datetime: from?.toISOString(),
            end_datetime: until?.toISOString(),
            request_timezone: 'Etc/GMT-1',
            min_threshold: thresholdMin,
            max_threshold: thresholdMax
         })
      })
         .then((res) => res.json())
         .then((data) => {
            // setLoading(false)
         })
   }
   function getPredictionsButtonClick() {
      const url = `${API_PATH}/evaluation/predictions`
      fetch(url, {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json'
         },
         body: JSON.stringify({
            collection_name: id,
            species: selectedSpecies,
            start_datetime: from?.toISOString(),
            end_datetime: until?.toISOString(),
            request_timezone: 'Etc/GMT-1',
            min_threshold: thresholdMin,
            max_threshold: thresholdMax
         })
      })
         .then((res) => res.json())
         .then((data) => {
            // setLoading(false)
         })
   }
   return (
      <Grid xs={12} container spacing={2}>
         <Grid xs={12} md={12}>
            <Typography variant="subtitle2" component="div" align="left">
               Query Parameters
            </Typography>
         </Grid>
         <Grid xs={4}>
            <Stack direction="column" spacing={1}>
               <DateTimePicker
                  renderInput={(props: TextFieldProps) => (
                     <TextField
                        {...props}
                        inputProps={{
                           ...props.inputProps,
                           readOnly: true
                        }}
                     />
                  )}
                  label="from"
                  value={dayjs(from)}
                  inputFormat="YYYY/MM/DD HH:mm"
                  // @ts-ignore
                  minDateTime={dayjs(firstRecordDatetime)}
                  // @ts-ignore
                  maxDateTime={dayjs(lastRecordDatetime)}
                  ampm={false}
                  loading={loading}
                  onChange={(value: Date | null) => {
                     if (value) {
                        setFrom(value)
                     }
                  }}
               />
               <DateTimePicker
                  renderInput={(props: TextFieldProps) => (
                     <TextField
                        {...props}
                        inputProps={{
                           ...props.inputProps,
                           readOnly: true
                        }}
                     />
                  )}
                  label="until"
                  value={until}
                  inputFormat="YYYY/MM/DD HH:mm"
                  // @ts-ignore
                  minDateTime={dayjs(firstRecordDatetime)}
                  // @ts-ignore
                  maxDateTime={dayjs(lastRecordDatetime)}
                  ampm={false}
                  loading={loading}
                  onChange={(value: Date | null) => {
                     if (value) {
                        setUntil(value)
                     }
                  }}
               />
            </Stack>
         </Grid>

         <Grid xs={4}>
            <Stack direction="column" spacing={1} sx={{ height: '100%' }}>
               <Stack direction="row" spacing={0} justifyContent="space-evenly" alignItems="stretch" sx={{ flex: '1' }}>
                  <div style={{ flexGrow: 1, paddingRight: 10 }}>
                     <Select
                        isClearable
                        styles={{
                           control: (baseStyles, state) => ({
                              ...baseStyles,
                              height: 56
                           })
                        }}
                        isLoading={speciesLoading}
                        onChange={(newValue) => {
                           if (newValue) setSelectedSpecies(newValue.value)
                           else setSelectedSpecies(undefined)
                        }}
                        options={collectionSpeciesList
                           .filter((x) => (hasIndex ? x.has_index : true))
                           .map((x) => ({
                              value: x.name,
                              label: firstLetterUpperAndReplaceSpace(x.name)
                           }))}
                     />
                  </div>
                  <FormControlLabel
                     control={
                        <Checkbox
                           value={hasIndex}
                           onChange={() => {
                              setHasIndex(!hasIndex)
                           }}
                        />
                     }
                     label="has Index"
                  />
               </Stack>
               <NumberInput
                  numberValue={binWidth}
                  numberType={'float'}
                  onNumberChange={setBinWidth}
                  label="Bin Width"
                  sx={{ flex: '0 0 auto' }}
               />
            </Stack>
         </Grid>
         <Grid xs={4}>
            <Stack direction="column" spacing={1}>
               <NumberInput
                  numberValue={thresholdMin}
                  numberType={'float'}
                  onNumberChange={setThresholdMin}
                  label=" >= threshold"
                  sx={{
                     width: '100%'
                  }}
               />

               <NumberInput
                  numberValue={thresholdMax}
                  numberType={'float'}
                  onNumberChange={setThresholdMax}
                  label=" <= threshold"
                  sx={{
                     width: '100%'
                  }}
               />
            </Stack>
         </Grid>
         <Grid xs={3}>
            <Button
               color="primary"
               variant="contained"
               disabled={!selectedSpecies}
               endIcon={<AddCircleOutlineIcon />}
               sx={{
                  width: '100%'
               }}
               onClick={() => calcBinSizesButtonClick()}
            >
               {' '}
               Calculate Bin Sizes
            </Button>
         </Grid>
         <Grid xs={3}>
            <Button
               variant="contained"
               disabled={!selectedSpecies}
               endIcon={<SendIcon />}
               sx={{
                  width: '100%'
               }}
               onClick={getPredictionsButtonClick}
            >
               {' '}
               Get Predictions
            </Button>
         </Grid>
         <Grid xs={3}>
            <Button
               variant="contained"
               disabled={!selectedSpecies}
               endIcon={<SendIcon />}
               sx={{
                  width: '100%'
               }}
               onClick={getDailyHistogramsButtonClick}
            >
               {' '}
               Get Daily Histograms
            </Button>
         </Grid>
         <Grid xs={3}>
            <Button
               variant="contained"
               disabled={!selectedSpecies}
               endIcon={<SendIcon />}
               sx={{
                  width: '100%'
               }}
               onClick={handleQueryButtonClick}
            >
               {' '}
               Query
            </Button>
         </Grid>
      </Grid>
   )
}
