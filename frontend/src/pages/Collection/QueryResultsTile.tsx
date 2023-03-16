import * as React from 'react'
import Grid from '@mui/material/Unstable_Grid2'
import TextField from '@mui/material/TextField'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import NumberInput from '../../components/NumberInput'
import Checkbox from '@mui/material/Checkbox'
import Button from '@mui/material/Button'
import FormControlLabel from '@mui/material/FormControlLabel'
import Divider from '@mui/material/Divider'
import CircularProgress from '@mui/material/CircularProgress'

import { API_PATH } from '../../consts'
import { useQueryResult } from './QueryResultContext'
import { useCollectionStats } from './CollectionStatsContext'
import { useQueryParameters } from './QueryParameterContext'

interface CollectionStatsProps {
   collectionId: string | undefined
}
export default function QueryParameters({ collectionId: id }: CollectionStatsProps) {
   const { result: predictionQueryResponse, loading: queryLoading } = useQueryResult()
   const { firstRecord, lastRecord, firstRecordLoading, lastRecordLoading, durationLoading } = useCollectionStats()
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
      sampleSize,
      setSampleSize,
      hasIndex,
      setHasIndex,
      filterFrequency,
      setFilterFrequency,
      useFilter,
      setFilterUse,
      selectedSpecies,
      setSelectedSpecies
   } = useQueryParameters()

   function createSampleButtonClick(random: boolean) {
      const url = `${API_PATH}/sample`
      console.log('useFilter:', useFilter)
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
                                    checked={useFilter}
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
   )
}
