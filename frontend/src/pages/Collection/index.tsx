import * as React from 'react'
import { useContext } from 'react'
import { useParams } from 'react-router-dom'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import Box from '@mui/material/Box'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import MaterialTable from '@material-table/core'
import Grid from '@mui/material/Unstable_Grid2'

import { API_PATH } from '../../consts'
import { store } from '../../components/JobsProvider'
import SampleJobStatus from '../../components/SampleJobsStatus'
import { useUpdateJobs } from '../../hooks/jobs'

import CollectionStats from './CollectionStatsTile'
import { QueryParametersProvider } from './Context/QueryParameterContext'
import QueryParameters from './QueryParametersTile'
import { CollectionStatsProvider } from './Context/CollectionStatsContext'
import QueryResultsTile from './QueryResultsTile'
import { QueryResultProvider } from './Context/QueryResultContext'
import Paper from '@mui/material/Paper'

dayjs.extend(utc)
dayjs.extend(timezone)
// Set to Central European Winter time, weird notation offset is inverse
dayjs.tz.setDefault('Etc/GMT-1')
interface CollectionProps {
   children?: React.ReactNode
}

export default function Collection(props: CollectionProps) {
   const { id } = useParams()

   const globalState = useContext(store)
   const { state } = globalState
   const { updateJobs } = useUpdateJobs()

   return (
      <QueryParametersProvider>
         <QueryResultProvider>
            <CollectionStatsProvider>
               <LocalizationProvider dateAdapter={AdapterDayjs} dateLibInstance={dayjs.tz}>
                  <Grid container spacing={2}>
                     <CollectionStats collectionId={id} />
                     <QueryParameters collectionId={id} />
                     <QueryResultsTile collectionId={id} />

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
                                    x.collection === id &&
                                    (x.type === 'create_sample' ||
                                       x.type === 'calc_bin_sizes' ||
                                       x.type === 'calc_predictions' ||
                                       x.type === 'calc_daily_histograms')
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
                           style={{
                              padding: '20px',
                              marginLeft: '5px',
                              marginRight: '10px'
                           }}
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
            </CollectionStatsProvider>
         </QueryResultProvider>
      </QueryParametersProvider>
   )
}
