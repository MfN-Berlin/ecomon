import * as React from 'react'
import { useContext, useEffect, useState } from 'react'
import Typography from '@mui/material/Typography'
import { useParams } from 'react-router-dom'
import { useCollectionSpeciesList, useCollectionPredictionQuery } from '../hooks/collection'

import { usePredictionCount } from '../hooks/predictions'

import { useRecordCount, useRecordDuration, useFirstRecord, useLastRecord } from '../hooks/records'

import Paper from '@mui/material/Paper'
import Box from '@mui/material/Box'
import Grid from '@mui/material/Unstable_Grid2'
import TextField, { TextFieldProps } from '@mui/material/TextField'
import Stack from '@mui/material/Stack'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
// import LocalizationProvider from '@mui/lab/LocalizationProvider'
// import DateTimePicker from '@mui/lab/DateTimePicker'

import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import Select from 'react-select'

import SendIcon from '@mui/icons-material/Send'
import Button from '@mui/material/Button'
import FormControlLabel from '@mui/material/FormControlLabel'
import Checkbox from '@mui/material/Checkbox'
import CircularProgress from '@mui/material/CircularProgress'
import Divider from '@mui/material/Divider'
import NumberInput from '../components/NumberInput'
import VerticalAlignBottomIcon from '@mui/icons-material/VerticalAlignBottom'
import { API_PATH } from '../consts'
import ChipList from '../components/ChipList'
import { addDbKeyToSpecies, deleteDbKeyFromSpecies } from '../tools/dbKeyHandling'
import { store } from '../components/JobsProvider'
import MaterialTable from '@material-table/core'
import SampleJobStatus from '../components/SampleJobsStatus'
import { useUpdateJobs } from '../hooks/jobs'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)
// Set to Central European Winter time, weird notation offset is inverse
dayjs.tz.setDefault('Etc/GMT-1')
interface CollectionProps {
   children?: React.ReactNode
}

function firstLetterUpperAndReplaceSpace(str: string) {
   return (str.charAt(0).toUpperCase() + str.substr(1).toLowerCase()).replace(/_/g, ' ')
}

export default function Collection(props: CollectionProps) {
   const { id } = useParams()
   const { collectionSpeciesList, loading: speciesLoading, update: updateSpeciesList } = useCollectionSpeciesList(id)
   const { predictionCount, loading: predictionLoading } = usePredictionCount(id)
   const { recordCount, loading: recordLoading } = useRecordCount(id)
   const { recordDuration, loading: durationLoading } = useRecordDuration(id)
   const { firstRecord, loading: firstRecordLoading } = useFirstRecord(id)
   const { lastRecord, loading: lastRecordLoading } = useLastRecord(id)
   const {
      predictionQueryResponse,
      loading: queryLoading,
      updateQuery,
      abortQuery,
      clearResponse
   } = useCollectionPredictionQuery(id)
   const [selectedSpecies, setSelectedSpecies] = useState<string>()
   const [from, setFrom] = useState<Date | null>()
   const [until, setUntil] = useState<Date | null>()
   const [thresholdMin, setThresholdMin] = useState<number>(0)
   const [thresholdMax, setThresholdMax] = useState<number>(1)
   const [binWidth, setBinWidth] = useState<number>(0.025)
   const [sampleSize, setSampleSize] = useState<number>(100)
   const [hasIndex, setHasIndex] = useState<boolean>(false)
   const [filterFrequency, setFilterFrequency] = useState<number>(100)
   const [useFilter, setFilterUse] = useState<boolean>(false)
   const [useFixTimezone, setFixTimezone] = useState<boolean>(true)
   const [timeZone, setTimeZone] = useState<number>(1)

   const globalState = useContext(store)
   const { state } = globalState
   const { updateJobs } = useUpdateJobs()

   // effects
   useEffect(() => {
      setFrom(firstRecord ? firstRecord.record_datetime : null)
   }, [firstRecord])
   useEffect(() => {
      setUntil(lastRecord ? lastRecord.record_datetime : null)
   }, [lastRecord])

   // effect clear prediction query response on change
   useEffect(() => {
      abortQuery()
      clearResponse()
      // eslint-disable-next-line
   }, [selectedSpecies, from, until])

   useEffect(() => {
      updateSpeciesList()
   }, [state.jobs])

   // Event handlers
   function handleQueryButtonClick() {
      if (selectedSpecies)
         updateQuery({
            species: selectedSpecies,
            start_datetime: from?.toISOString(),
            end_datetime: until?.toISOString(),
            threshold_min: thresholdMin,
            threshold_max: thresholdMax
         })
   }
   // download file from url
   function createSampleButtonClick(random: boolean) {
      const url = `${API_PATH}/sample`
      fetch(url, {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json'
         },
         body: JSON.stringify({
            prefix: id,
            species: selectedSpecies,
            sample_size: sampleSize,
            start_datetime: from?.toISOString(),
            end_datetime: until?.toISOString(),
            threshold_min: thresholdMin,
            threshold_max: thresholdMax,
            random,
            high_pass_frequency: useFilter ? filterFrequency : undefined,
            zip_hours_off_set: 1 // UTC+1
         })
      })
         .then((res) => res.json())
         .then((data) => {
            // setLoading(false)
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
            end_datetime: until?.toISOString()
         })
      })
         .then((res) => res.json())
         .then((data) => {
            // setLoading(false)
         })
   }
   function secondsToYearsMonthDaysHoursMinutesSeconds(input: number) {
      const years = Math.floor(input / 31536000)
      const months = Math.floor((input % 31536000) / 2592000)
      const days = Math.floor((input % 2592000) / 86400)
      const hours = Math.floor((input % 86400) / 3600)
      const minutes = Math.floor((input % 3600) / 60)
      const seconds = Math.floor(input % 60)
      return `${years ? years + ' Years  ' : ''}${months ? months + ' Months  ' : ''}${days ? days + ' Days  ' : ''}${
         hours ? hours + ' Hours  ' : ''
      }${minutes ? minutes + ' Minutes  ' : ''}${seconds ? seconds + ' Seconds  ' : ''}`
   }

   async function handleAddSpeciesIndex(item: { label: string; key: string }): Promise<void> {
      console.log(item)
      id && (await addDbKeyToSpecies(id, item.key))
      await updateSpeciesList()
   }

   async function handleDeleteSpeciesIndex(item: { label: string; key: string }): Promise<void> {
      console.log(item)
      id && (await deleteDbKeyFromSpecies(id, item.key))
      await updateSpeciesList()
   }
   return (
      <Box sx={{ flexGrow: 1, padding: 2 }}>
         <LocalizationProvider dateAdapter={AdapterDayjs} dateLibInstance={dayjs.tz}>
            <Grid container spacing={1}>
               <Grid xs={12}>
                  <ChipList
                     addDialogTitle={'Add database index to species'}
                     addDialogContentText={'Select a species to add a database index to'}
                     ensureDelete={true}
                     onAdd={handleAddSpeciesIndex}
                     onDelete={handleDeleteSpeciesIndex}
                     deleteDialogTitleTemplate={(species) => `Drop database index of  ${species.label}?`}
                     label="Species with DB-Index:"
                     items={collectionSpeciesList
                        .filter((x) => x.has_index)
                        .map((item) => ({
                           label: firstLetterUpperAndReplaceSpace(item.name),
                           key: item.name
                        }))}
                     pendingItems={state.jobs
                        .filter((x) => x.collection === id && x.status === 'pending' && x.type === 'add_index')
                        .map((item) => ({
                           label: firstLetterUpperAndReplaceSpace(item.metadata?.column_name),
                           key: item.metadata?.column_name
                        }))}
                     options={collectionSpeciesList
                        .filter((x) => !x.has_index)
                        .map((item) => ({
                           label: firstLetterUpperAndReplaceSpace(item.name),
                           key: item.name
                        }))}
                  ></ChipList>
               </Grid>
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
                           value={
                              durationLoading
                                 ? 'loading...'
                                 : secondsToYearsMonthDaysHoursMinutesSeconds(recordDuration)
                           }
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
               {/* <Grid xs={12} md={7} xl={4} margin="4px">
                    <SpeciesKeyTable isLoading={speciesLoading} data={
                        collectionSpeciesList.sort().map(item => ({
                            name: firstLetterUpperAndReplaceSpace(item.name), hasIndex: item.has_index
                        })) || []} />

                </Grid> */}

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
                           Query Parameters
                        </Typography>
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
                           minDateTime={dayjs(firstRecord?.record_datetime)}
                           // @ts-ignore
                           maxDateTime={dayjs(lastRecord?.record_datetime)}
                           ampm={false}
                           loading={firstRecordLoading || lastRecordLoading}
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
                           minDateTime={dayjs(firstRecord?.record_datetime)}
                           // @ts-ignore
                           maxDateTime={dayjs(lastRecord?.record_datetime)}
                           ampm={false}
                           loading={firstRecordLoading || lastRecordLoading}
                           onChange={(value: Date | null) => {
                              if (value) {
                                 setUntil(value)
                              }
                           }}
                        />
                        <Stack direction="row" spacing={0} justifyContent="space-evenly" alignItems="stretch">
                           <div style={{ minWidth: '250px' }}>
                              <Select
                                 isClearable
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
                        <Stack direction="row" spacing={2}>
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
                        <Stack direction="row" spacing={2} justifyContent="space-around">
                           <NumberInput
                              numberValue={binWidth}
                              numberType={'float'}
                              onNumberChange={setBinWidth}
                              label="Bin Width"
                              sx={{
                                 width: '100%'
                              }}
                           />

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
                        </Stack>
                        <Stack direction="row" spacing={2}>
                           <Button
                              variant="contained"
                              disabled={!selectedSpecies}
                              endIcon={<SendIcon />}
                              sx={{
                                 padding: 1.5,
                                 width: '100%'
                              }}
                              onClick={getPredictionsButtonClick}
                           >
                              {' '}
                              Get Predictions
                           </Button>
                           <Button
                              variant="contained"
                              disabled={!selectedSpecies}
                              endIcon={<SendIcon />}
                              sx={{
                                 padding: 1.5,
                                 width: '100%'
                              }}
                              onClick={handleQueryButtonClick}
                           >
                              {' '}
                              Query
                           </Button>
                        </Stack>
                     </Stack>
                  </Paper>
               </Grid>

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
                           Query Results
                        </Typography>
                        {predictionQueryResponse && !queryLoading ? (
                           <React.Fragment>
                              <TextField
                                 id="predictionsCount"
                                 label="Predictions count"
                                 variant="standard"
                                 value={queryLoading ? 'Loading...' : predictionQueryResponse?.predictions_count}
                                 InputProps={{
                                    readOnly: true
                                 }}
                              />
                              <TextField
                                 id="speciesCount"
                                 label="Predictions over Threshold"
                                 variant="standard"
                                 value={durationLoading ? 'loading...' : predictionQueryResponse?.species_count}
                                 InputProps={{
                                    readOnly: true
                                 }}
                              />
                              <Divider light />
                              <Stack
                                 direction={{ md: 'column', lg: 'row' }}
                                 spacing={2}
                                 justifyContent="space-evenly"
                                 alignItems="stretch"
                              >
                                 <Typography
                                    variant="h6"
                                    component="h6"
                                    align="left"
                                    sx={{
                                       marginTop: 1,
                                       marginLeft: 2,
                                       paddingBottom: 0.5
                                    }}
                                 >
                                    Create Random Sample
                                 </Typography>
                                 <Stack direction="row" spacing={2}>
                                    <NumberInput
                                       label="Highpass frequency"
                                       style={{ width: 130 }}
                                       numberValue={filterFrequency}
                                       numberType={'int'}
                                       onNumberChange={setFilterFrequency}
                                    />
                                    <FormControlLabel
                                       control={
                                          <Checkbox
                                             value={useFilter}
                                             onChange={() => {
                                                setFilterUse(!useFilter)
                                             }}
                                          />
                                       }
                                       label="high pass"
                                    />
                                 </Stack>
                              </Stack>
                              <NumberInput
                                 label="Sample Size"
                                 numberType={'int'}
                                 numberValue={sampleSize}
                                 onNumberChange={setSampleSize}
                              ></NumberInput>
                              <Stack
                                 direction={{ xs: 'column', sm: 'row' }}
                                 spacing={2}
                                 justifyContent="space-evenly"
                                 alignItems="center"
                              >
                                 <Button
                                    color="secondary"
                                    variant="contained"
                                    disabled={!selectedSpecies || sampleSize >= predictionQueryResponse?.species_count}
                                    endIcon={<AddCircleOutlineIcon />}
                                    sx={{
                                       padding: 1.5
                                    }}
                                    onClick={() => createSampleButtonClick(true)}
                                 >
                                    {' '}
                                    Create Random Sample
                                 </Button>
                                 <Button
                                    color="primary"
                                    variant="contained"
                                    disabled={!selectedSpecies || predictionQueryResponse?.species_count === 0}
                                    endIcon={<AddCircleOutlineIcon />}
                                    sx={{
                                       padding: 1.5
                                    }}
                                    onClick={() => createSampleButtonClick(false)}
                                 >
                                    {' '}
                                    Create Full Sample
                                 </Button>
                              </Stack>
                           </React.Fragment>
                        ) : queryLoading ? (
                           <Grid>
                              <CircularProgress />
                           </Grid>
                        ) : (
                           ''
                        )}
                     </Stack>
                  </Paper>
               </Grid>

               <Grid xs={12}>
                  <MaterialTable
                     title="Jobs"
                     columns={[
                        {
                           title: 'Type',
                           field: 'type',
                           sorting: true
                        },
                        {
                           title: 'status',
                           field: 'status',
                           sorting: true,

                           render: (rowData) => (
                              <SampleJobStatus
                                 status={rowData.status}
                                 progress={rowData.progress}
                                 error={rowData.error}
                                 url={`${API_PATH}/random_sample/file/${rowData.metadata.filename}`}
                              />
                           )
                        },

                        {
                           title: 'species',
                           field: 'metadata.species',
                           sorting: true,
                           type: 'string'
                        },

                        {
                           title: '>= Threshold ',
                           field: 'metadata.threshold_min',
                           sorting: true,
                           type: 'numeric'
                        },
                        {
                           title: '<= Threshold ',
                           field: 'metadata.threshold_max',
                           sorting: true,
                           type: 'numeric'
                        },
                        {
                           title: 'from',
                           field: 'metadata.from',
                           sorting: true,
                           type: 'datetime'
                        },
                        {
                           title: 'until',
                           field: 'metadata.until',
                           sorting: true,
                           type: 'datetime'
                        },
                        {
                           title: 'high pass',
                           field: 'metadata.high_pass_frequency',
                           sorting: true,
                           type: 'string'
                        },
                        {
                           title: 'random',
                           field: 'metadata.random',
                           sorting: true,
                           type: 'boolean'
                        },
                        {
                           title: 'samples',
                           field: 'metadata.samples',
                           sorting: true,
                           type: 'numeric'
                        },
                        {
                           title: 'created',
                           field: 'created_at',
                           sorting: true,
                           type: 'datetime'
                        }
                     ]}
                     actions={[
                        (rowData) => ({
                           icon: 'delete',
                           tooltip: 'Delete Job',
                           disabled: rowData.status === 'pending' || rowData.status === 'running',
                           onClick: (event, rowData) => {
                              if (window.confirm('Are you sure you want to delete?')) {
                                 // if rowData is not an array
                                 if (!Array.isArray(rowData)) {
                                    fetch(`${API_PATH}/jobs/${rowData.id}`, {
                                       method: 'DELETE'
                                    }).finally(updateJobs)
                                 }
                              }
                           }
                        })
                     ]}
                     data={state.jobs
                        .filter(
                           (x) =>
                              (x.collection === id && x.type === 'create_sample') ||
                              x.type === 'calc_bin_sizes' ||
                              x.type === 'calc_predictions'
                        )
                        .map((x) => {
                           // if random field is missing it is a random sample (backwards compatibility)
                           if (x.type === 'create_sample') {
                              x.metadata.random = !(x.metadata.random === false)
                              if (typeof x.metadata.threshold !== 'undefined') {
                                 x.metadata.threshold_min = x.metadata.threshold
                              }
                              if (typeof x.metadata.threshold_max === 'undefined') {
                                 x.metadata.threshold_max = 1
                              }
                              // for legacy data if from is missing
                              if (!x.metadata.from) x.metadata.from = x.metadata.from_date
                           }

                           return x
                        })}
                     options={{
                        pageSize: 10,
                        paging: true,
                        filtering: false,

                        // @ts-ignore
                        cellStyle: {
                           padding: '2px',
                           paddingLeft: '5px',
                           paddingRight: '5px'
                        }
                     }}
                  >
                     {' '}
                  </MaterialTable>
               </Grid>
            </Grid>
         </LocalizationProvider>
      </Box>
   )
}
