import React, { useContext, useEffect } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { createTheme, ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

import Box from '@mui/material/Box'
import MuiAppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'

import { Outlet } from 'react-router-dom'
import TabNavigation from './components/TabNavigation'

// pages
import Collection from './pages/Collection'
import Start from './pages/Start'
import { store } from './components/JobsProvider'
import { API_PATH } from './consts'
import {useUpdateJobs} from './hooks/jobs'
const mdTheme = createTheme()

function App() {
   // load and update current jobs status store in JobsProvider
   const globalState = useContext(store)
   const { dispatch } = globalState
   const { updateJobs } = useUpdateJobs()
   let lastUpdate = null as Date | null
   useEffect(() => {
      setInterval(() => {
         fetch(`${API_PATH}/jobs/last_update`)
            .then((res) => res.json())
            .then((result) => {
               const tmp = new Date(result.last_update)
               // check if tmp is newer than lastUpdate
        
               if (!lastUpdate || tmp > lastUpdate) {
                  lastUpdate = tmp
                  updateJobs()
                
               }
            })
            .catch((err) => {
               dispatch({ type: 'set_error', error: err })
            })
      }, 1000)
   }, [])

   return (
      <div className="App">
         <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
         <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
         <BrowserRouter>
            <Routes>
               <Route
                  path="/"
                  element={
                     <ThemeProvider theme={mdTheme}>
                        <Box sx={{ display: 'flex' }}>
                           <CssBaseline />
                           <MuiAppBar position="absolute">
                              <TabNavigation />
                           </MuiAppBar>

                           <Box
                              component="main"
                              sx={{
                                 backgroundColor: (theme) =>
                                    theme.palette.mode === 'light' ? theme.palette.grey[100] : theme.palette.grey[900],
                                 flexGrow: 1,
                                 height: '100vh',
                                 overflow: 'auto'
                              }}
                           >
                              <Toolbar />

                              <Outlet />
                           </Box>
                        </Box>
                     </ThemeProvider>
                  }
               >
                  <Route index element={<Start />} />
                  <Route path="collection/:id" element={<Collection />} />
               </Route>
            </Routes>
         </BrowserRouter>
      </div>
   )
}

export default App
