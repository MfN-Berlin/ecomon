import * as React from 'react'
import Button from '@mui/material/Button'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
import TextField from '@mui/material/TextField'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import IconButton from '@mui/material/IconButton'
import CheckBoxOutlineBlankOutlinedIcon from '@mui/icons-material/CheckBoxOutlineBlankOutlined'
import CheckBoxOutlinedIcon from '@mui/icons-material/CheckBoxOutlined'
import { CircularProgress, Grid } from '@mui/material'
import { useCollectionSpeciesList } from '@/hooks/collection'
import { firstLetterUpperAndReplaceSpace } from '@/tools/stringHandling'
import { evaluationClient } from '@/services/api'
interface CerateVoucherDialogProps {
   collectionId: string | undefined
}

export default function CreateVoucherDialog({ collectionId: id }: CerateVoucherDialogProps) {
   const [open, setOpen] = React.useState(false)
   const [samplesProSpecies, setSamplesProSpecies] = React.useState<number>(10)
   const [filterFrequency, setFilterFrequency] = React.useState<number>(100)
   const [audioPadding, setAudioPadding] = React.useState<number>(5)
   const [filterOn, setFilterOn] = React.useState<boolean>(true)
   const [selectedSpecies, setSelectedSpecies] = React.useState<string[]>([])
   const [speciesFilter, setSpeciesFilter] = React.useState<string>('')
   const { collectionSpeciesList: speciesList, loading: speciesLoading } = useCollectionSpeciesList(id)

   const handleClickOpen = () => {
      setOpen(true)
   }

   const handleClose = () => {
      setOpen(false)
   }

   const handleCreate = async () => {
      // Perform your creation logic here
      await evaluationClient.getSpeciesVouchers({
         collection_name: id || '',
         sample_size: samplesProSpecies,
         high_pass_frequency: filterOn ? filterFrequency : 0,
         audio_padding: audioPadding,
         species_list: selectedSpecies
      })
      handleClose()
   }
   const handleToggleAll = () => {
      if (selectedSpecies.length === speciesList.length) {
         setSelectedSpecies([])
      } else {
         setSelectedSpecies(speciesList.map((sp) => sp.name))
      }
   }

   const handleSpeciesChange = (species: string) => {
      setSelectedSpecies((prevSelected) =>
         prevSelected.includes(species) ? prevSelected.filter((sp) => sp !== species) : [...prevSelected, species]
      )
   }

   const handleSpeciesFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      setSpeciesFilter(event.target.value)
   }

   return (
      <div>
         <Button variant="outlined" onClick={handleClickOpen}>
            Create Voucher
         </Button>
         <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Create Species Voucher of {id} </DialogTitle>
            <DialogContent>
               <DialogContentText>
                  Create {filterOn ? 'filtered' : ''} {samplesProSpecies} Samples for selected Species in this
                  Collection
               </DialogContentText>
               <TextField
                  label="Samples per Species"
                  type="number"
                  value={samplesProSpecies}
                  onChange={(e) => setSamplesProSpecies(parseInt(e.target.value))}
                  fullWidth
                  variant="standard"
               />
               <TextField
                  label="Audio Event Padding"
                  type="number"
                  value={audioPadding}
                  onChange={(e) => setAudioPadding(parseInt(e.target.value))}
                  fullWidth
                  variant="standard"
               />
               <TextField
                  label="Filter Frequency"
                  type="number"
                  value={filterFrequency}
                  onChange={(e) => setFilterFrequency(parseInt(e.target.value))}
                  fullWidth
                  variant="standard"
               />
               <FormControlLabel
                  control={<Checkbox checked={filterOn} onChange={(e) => setFilterOn(e.target.checked)} />}
                  label="Filter On"
               />
               <div>
                  <Grid container alignItems="center" justifyContent="space-between">
                     <Grid item>
                        <DialogContentText>Select Species:</DialogContentText>
                     </Grid>
                     <Grid item>
                        <IconButton onClick={handleToggleAll}>
                           {selectedSpecies.length === speciesList.length ? (
                              <CheckBoxOutlinedIcon />
                           ) : (
                              <CheckBoxOutlineBlankOutlinedIcon />
                           )}
                        </IconButton>{' '}
                        All
                     </Grid>
                     <Grid item style={{ flex: 1, paddingLeft: 50 }}>
                        <TextField
                           label="Filter Species"
                           value={speciesFilter}
                           onChange={handleSpeciesFilterChange}
                           fullWidth
                           variant="standard"
                        />
                     </Grid>
                  </Grid>
                  {speciesLoading ? (
                     <div style={{ display: 'flex', justifyContent: 'center', marginTop: '16px' }}>
                        <CircularProgress />
                     </div>
                  ) : (
                     <div
                        style={{
                           overflowX: 'auto', // horizontal scrolling
                           marginTop: '8px', // spacing from the text above
                           paddingBottom: '8px', // spacing at the bottom
                           height: '250px' // limit height
                        }}
                     >
                        <Grid container spacing={2}>
                           {speciesList
                              .filter((species) =>
                                 firstLetterUpperAndReplaceSpace(species.name)
                                    .toLowerCase()
                                    .includes(speciesFilter.toLowerCase())
                              )
                              .map((species) => (
                                 <Grid item key={species.name} xs={12} sm={6} md={6} lg={6}>
                                    <FormControlLabel
                                       control={
                                          <Checkbox
                                             checked={selectedSpecies.includes(species.name)}
                                             onChange={() => handleSpeciesChange(species.name)}
                                          />
                                       }
                                       label={firstLetterUpperAndReplaceSpace(species.name)}
                                    />
                                 </Grid>
                              ))}
                           <Grid item xs={12} sm={6} md={6} lg={6}></Grid>
                           <Grid item xs={12} sm={6} md={6} lg={6}></Grid>
                        </Grid>
                     </div>
                  )}
               </div>
            </DialogContent>
            <DialogActions>
               <Button onClick={handleClose}>Cancel</Button>
               <Button onClick={handleCreate}>Create</Button>
            </DialogActions>
         </Dialog>
      </div>
   )
}
