import React, { useContext, useEffect } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import { Outlet } from 'react-router-dom'
import AppBar from './components/AppBar'
import DrawerMenu from './components/DrawerMenu'
import Main from './components/Main'
// pages
import Collection from './pages/Collection'
import Start from './pages/Start'
import { store } from './components/JobsProvider'
import { API_PATH } from './consts'
import { useUpdateJobs } from './hooks/jobs'
import { useAppSelector } from './store/hooks'
import theme from './theme'
import { EvaluationApi } from './generated/api'
import Evaluation from './pages/Evaluation'

function App() {
   // load and update current jobs status store in JobsProvider
   const drawerOpen = useAppSelector((state) => state.ui.drawerOpen)
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
               console.log('lastUpdate:' + result.last_update, tmp)
               if (!lastUpdate || tmp > lastUpdate) {
                  lastUpdate = tmp
                  console.log('update Job:')
                  updateJobs()
               }
            })
            .catch((err) => {
               dispatch({ type: 'set_error', error: err })
            })
      }, 5000)
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
                     <ThemeProvider theme={theme}>
                        <Box sx={{ display: 'flex' }}>
                           <CssBaseline />
                           <AppBar />
                           <DrawerMenu drawerWidth={250} />
                           <Main open={drawerOpen} drawerWidth={250}>
                              <Box
                                 component="main"
                                 sx={{
                                    flexGrow: 1,
                                    height: '100vh',
                                    overflow: 'auto',
                                    padding: '0px',
                                    marginTop: '0px'
                                 }}
                              >
                                 <Toolbar />

                                 <Outlet />
                              </Box>
                           </Main>
                        </Box>
                     </ThemeProvider>
                  }
               >
                  <Route index element={<Start />} />
                  <Route path="collection/:id" element={<Collection />} />
                  <Route path="evaluation" element={<Evaluation />} />
               </Route>
            </Routes>
         </BrowserRouter>
      </div>
   )
}

export default App
