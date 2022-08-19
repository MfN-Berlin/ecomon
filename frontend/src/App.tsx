import React from 'react'
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

const mdTheme = createTheme()

function App() {
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
