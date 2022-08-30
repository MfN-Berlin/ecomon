import * as React from 'react'
import { useState } from 'react'

import AddIcon from '@mui/icons-material/Add'
import Chip from '@mui/material/Chip'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import Button from '@mui/material/Button'
import DialogActions from '@mui/material/DialogActions'
import Select from 'react-select'
import CircularProgress from '@material-ui/core/CircularProgress'

type Item = {
   label: string
   key: string
   icon?: React.ReactNode
}

interface ChipListProps {
   deleteDialogTitleTemnplate?: (item: Item) => string
   label?: string
   items: Item[]
   pendingItems?: Item[]
   options: Item[]
   variant?: 'outlined' | 'filled'
   onDelete?: (item: Item) => void
   onAdd?: (item: Item) => void
   ensureDelete?: boolean
   addDialogContentText?: string
   addDialogTitle?: string
   onPendingItemsChange?: () => void
}

export default function ChipList(props: ChipListProps) {
   const [currentItem, setCurrentItem] = useState<Item>()
   const [loadingDeletion, setLoadingDeletion] = useState(false)
   const [loadingAdd, setLoadingAdd] = useState(false)
   const [showDeleteDialog, setShowDeleteDialog] = useState(false)
   const [showAddDialog, setShowAddDialog] = useState(false)

   function handleDelete(item: Item) {
      if (props.onDelete) {
         props.onDelete(item)
      }
   }
   React.useEffect(() => {
      if (props.onPendingItemsChange) {
         props.onPendingItemsChange()
      }
      console.log('pending changed')},[props.pendingItems])


   return (
      <React.Fragment>
         <Dialog open={showAddDialog} PaperProps={{ style: { overflowY: 'visible' } }}>
            <DialogTitle>{props.addDialogTitle ? props.addDialogTitle : 'Add Item'}</DialogTitle>
            <DialogContent style={{ overflowY: 'visible', paddingBottom: '10' }}>
               <DialogContentText>
                  {props.addDialogContentText ? props.addDialogContentText : 'Select an item to add to the list.'}
               </DialogContentText>

               <Select
                  isClearable
                  options={props.options}
                  onChange={(newValue) => {
                     if (newValue) setCurrentItem(newValue as Item)
                     else setCurrentItem(undefined)
                  }}
               />
            </DialogContent>
            <DialogActions>
               <Button
                  disabled={loadingAdd}
                  onClick={() => {
                     setShowAddDialog(false)
                  }}
               >
                  Cancel
               </Button>
               <Button
                  disabled={currentItem === undefined || loadingAdd}
                  onClick={async () => {
                     setLoadingAdd(true)
                     if (props.onAdd && currentItem) {
                        console.log('adding item', currentItem)
                        const result = await props.onAdd(currentItem)
                        console.log('added item', result)
                     }
                     setCurrentItem(undefined)

                     setLoadingAdd(false)

                     setShowAddDialog(false)
                  }}
               >
                  {loadingAdd && <CircularProgress size={14} />}
                  {!loadingAdd && 'Add'}
               </Button>
            </DialogActions>
         </Dialog>
         <Dialog
            open={showDeleteDialog}
            keepMounted
            onClose={() => setShowDeleteDialog(false)}
            aria-describedby="alert-dialog-slide-description"
         >
            <DialogTitle>
               {props.deleteDialogTitleTemnplate && currentItem
                  ? props.deleteDialogTitleTemnplate(currentItem)
                  : `Do you really want to delete ${currentItem && currentItem.label}`}
            </DialogTitle>

            <DialogActions>
               <Button
                  disabled={loadingDeletion}
                  onClick={() => {
                     setCurrentItem(undefined)
                     setShowDeleteDialog(false)
                  }}
               >
                  Cancel
               </Button>
               <Button
                  onClick={async () => {
                     setLoadingDeletion(true)
                     if (props.onDelete && currentItem) {
                        await props.onDelete(currentItem)
                     }

                     setLoadingDeletion(false)
                     setShowDeleteDialog(false)
                  }}
               >
                  {loadingDeletion && <CircularProgress size={14} />}
                  {!loadingDeletion && 'Delete'}
               </Button>
            </DialogActions>
         </Dialog>
         <Paper variant="outlined">
            {props.label && (
               <Typography
                  variant="overline"
                  component="h6"
                  align="left"
                  sx={{
                     marginTop: 1,
                     marginLeft: 2
                  }}
               >
                  {props.label}
               </Typography>
            )}
            <Box
               sx={{
                  display: 'flex',
                  justifyContent: 'left',
                  flexWrap: 'wrap',
                  listStyle: 'none',
                  p: 0.5,
                  m: 0,
                  maxHeight: 200,
                  overflowY: 'scroll',
                  backgroundColor: '000'
               }}
            >
               {props.onAdd && (
                  <Chip
                     label="Add"
                     sx={{
                        margin: 0.2
                     }}
                     icon={<AddIcon />}
                     color="primary"
                     variant={props.variant}
                     onClick={() => setShowAddDialog(true)}
                  />
               )}
               {props.pendingItems &&
                  props.pendingItems.map((item) => (
                     <Chip
                        label={item.label}
                        key={item.key}
                        sx={{
                           margin: 0.2
                        }}
                        icon={<CircularProgress size={14} />}
                        color="secondary"
                        variant="outlined"
                     />
                  ))}
               ,
               {props.items.map((item) => (
                  <Chip
                     label={item.label}
                     key={item.key}
                     sx={{
                        margin: 0.2
                     }}
                     variant={props.variant}
                     onDelete={() => {
                        if (props.ensureDelete) {
                           setCurrentItem(item)
                           setShowDeleteDialog(true)
                        } else {
                           handleDelete(item)
                        }
                     }}
                  />
               ))}
            </Box>
         </Paper>
      </React.Fragment>
   )
}
