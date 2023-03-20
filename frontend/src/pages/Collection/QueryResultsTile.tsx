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
import { useQueryResult } from './Context/QueryResultContext'
import { useCollectionStats } from './Context/CollectionStatsContext'
import { useQueryParameters } from './Context/QueryParameterContext'

interface CollectionStatsProps {
   collectionId: string | undefined
}
export default function QueryParameters({ collectionId: id }: CollectionStatsProps) {
   const { result: predictionQueryResponse, loading: queryLoading } = useQueryResult()
   const { loading } = useCollectionStats()
   const {
      from,
      until,
      thresholdMax,
      thresholdMin,
      sampleSize,
      setSampleSize,
      filterFrequency,
      setFilterFrequency,
      useFilter,
      setFilterUse,
      selectedSpecies
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
      <Paper
         sx={{
            padding: 1,
            elevation: 0,
            width: '100%'
         }}
      >
         <Grid xs={12} container spacing={2}>
            <Grid xs={12}>
               <Typography variant="subtitle2" component="div" align="left" sx={{}}>
                  Query Results
               </Typography>
            </Grid>

            {predictionQueryResponse && !queryLoading ? (
               <React.Fragment>
                  <Grid xs={3}>
                     <Stack direction="column" spacing={1}>
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
                           value={loading ? 'loading...' : predictionQueryResponse?.species_count}
                           InputProps={{
                              readOnly: true
                           }}
                        />
                     </Stack>
                  </Grid>
                  <Grid xs={3}>
                     <Stack direction="column" spacing={1}>
                        <Stack
                           direction="row"
                           spacing={0}
                           justifyContent="space-evenly"
                           alignItems="stretch"
                           sx={{ flex: '1' }}
                        >
                           <div style={{ flexGrow: 1, paddingRight: 10 }}>
                              <NumberInput
                                 label="Highpass frequency"
                                 numberValue={filterFrequency}
                                 numberType={'int'}
                                 onNumberChange={setFilterFrequency}
                              />
                           </div>
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

                        <NumberInput
                           label="Sample Size"
                           numberType={'int'}
                           numberValue={sampleSize}
                           onNumberChange={setSampleSize}
                        ></NumberInput>
                     </Stack>
                  </Grid>
                  <Grid xs={6}>
                     <Stack direction="column" spacing={1}>
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
                  </Grid>
               </React.Fragment>
            ) : queryLoading ? (
               <Grid>
                  <CircularProgress />
               </Grid>
            ) : (
               ''
            )}
         </Grid>
      </Paper>
   )
}
