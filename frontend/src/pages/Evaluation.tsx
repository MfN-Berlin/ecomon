import * as React from 'react'
import { useEffect } from 'react'
import Grid from '@mui/material/Unstable_Grid2'

import Box from '@mui/material/Box'
import { nanoid } from 'nanoid'
import IconButton from '@mui/material/IconButton'
import AddCircleOutline from '@mui/icons-material/AddCircleOutline'

import GraphPanel from '../components/GraphPanel/index'
import { loadState, saveState, removeState } from '../tools/localStorage'

export default function Title() {
   const [panels, setPanels] = React.useState<string[]>([])

   function addPanel() {
      setPanels([...panels, nanoid()])
   }
   function removePanel(panel: string) {
      setPanels(panels.filter((p) => p !== panel))
      removeState(panel)
   }

   useEffect(() => {
      const savedState = loadState('speciesEventsPanels')
      if (savedState) {
         setPanels(savedState)
      }
   }, [])
   useEffect(() => {
      saveState('speciesEventsPanels', panels)
   }, [panels])

   return (
      <Box sx={{ width: '100%', padding: '2px' }}>

         <Grid container spacing={2}>
            {panels.map((key, index) => (
               <Grid xs={12} sm={12} md={12} lg={6} key={key}>
                  <GraphPanel localStorageId={key} onRemove={() => removePanel(key)} />
               </Grid>
            ))}
            <Grid xs={12} sm={12} md={12} lg={6}>
               <div
                  style={{
                     width: '100%',
                     paddingBottom: '51%', // This will maintain a 16:9 aspect ratio
                     position: 'relative', // This is necessary for the child div to be positioned correctly
                  }}
               >
                  <div
                     style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        justifyContent: 'center', // Horizontally center the content
                        alignItems: 'center', // Vertically center the content
                     }}
                  >
                     <IconButton onClick={addPanel}>
                        <AddCircleOutline sx={{ fontSize: '3rem' }} />
                     </IconButton>
                  </div>
               </div>

            </Grid>
         </Grid>
      </Box>
   )
}
