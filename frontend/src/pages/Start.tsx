import * as React from 'react'
import Grid from '@mui/material/Unstable_Grid2'

import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Box from '@mui/material/Box'

import { API_PATH } from '../consts'

import MaterialTable from '@material-table/core'
import SampleJobStatus from '../components/SampleJobsStatus'
import { useContext } from 'react'
import { store } from '../components/JobsProvider'
import TabPanel from '../components/TabPanel'
import { useUpdateJobs } from '../hooks/jobs'

export default function Title() {
   const globalState = useContext(store)
   const { state, dispatch } = globalState
   const [value, setValue] = React.useState(0)
   const { updateJobs } = useUpdateJobs()
   const handleChange = (event: React.SyntheticEvent, newValue: number) => {
      setValue(newValue)
   }
   function a11yProps(index: number) {
      return {
         id: `simple-tab-${index}`,
         'aria-controls': `simple-tabpanel-${index}`
      }
   }
   return (
      <Box sx={{ width: '100%', paddingX: '10px' }}>
         <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
               <Tab label="Samples" {...a11yProps(0)} />
               <Tab label="Index Jobs" {...a11yProps(1)} />
            </Tabs>
         </Box>
         <TabPanel value={value} index={0}>
            <Grid xs={12}>
               <MaterialTable
                  columns={[
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
                        title: 'Collection',
                        field: 'metadata.prefix',
                        sorting: true,
                        type: 'string'
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
                        field: 'metadata.from_date',
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
                                 }).finally(() => {
                                    updateJobs()
                                 })
                              }
                           }
                        }
                     })
                  ]}
                  data={state.jobs
                     .filter((x) => x.type === 'create_sample')
                     .map((x) => {
                        // if random field is missing it is a random sample (backwards compatibility)
                        x.metadata.random = !(x.metadata.random === false)
                        if (typeof x.metadata.threshold !== 'undefined') {
                           x.metadata.threshold_min = x.metadata.threshold
                        }
                        if (typeof x.metadata.threshold_max === 'undefined') {
                           x.metadata.threshold_max = 1
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
         </TabPanel>
         <TabPanel value={value} index={1}>
            <Grid xs={12}>
               <MaterialTable
                  title="Samples"
                  columns={[
                     {
                        title: 'status',
                        field: 'status',
                        sorting: true,
                        render: (rowData) => (
                           <SampleJobStatus status={rowData.status} progress={rowData.progress} error={rowData.error} />
                        )
                     },
                     {
                        title: 'column_name',
                        field: 'metadata.column_name',
                        sorting: true,
                        type: 'string'
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

                        onClick: (event, rowData) => {
                           if (window.confirm('Are you sure you want to delete?')) {
                              // if rowData is not an array
                              if (!Array.isArray(rowData)) {
                                 fetch(`${API_PATH}/jobs/${rowData.id}`, {
                                    method: 'DELETE'
                                 }).finally(() => {
                                    updateJobs()
                                 })
                              }
                           }
                        }
                     })
                  ]}
                  data={state.jobs.filter((x) => x.type === 'add_index')}
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
         </TabPanel>
      </Box>
   )
}
