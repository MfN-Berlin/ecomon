import * as React from 'react'
import { styled, useTheme } from '@mui/material/styles'

import Drawer, { DrawerProps as MuiDrawerProps } from '@mui/material/Drawer'
import List from '@mui/material/List'
import Divider from '@mui/material/Divider'
import IconButton from '@mui/material/IconButton'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import ListItem from '@mui/material/ListItem'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import InboxIcon from '@mui/icons-material/MoveToInbox'
import MailIcon from '@mui/icons-material/Mail'

import { useAppSelector, useAppDispatch } from '../store/hooks'
import { setDrawerOpenState } from '../store/slices/ui'
import { useGetCollectionsQuery } from '../services/api'

const drawerWidth = 240

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
   open?: boolean
}>(({ theme, open }) => ({
   flexGrow: 1,
   padding: theme.spacing(3),
   transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
   }),
   marginRight: -drawerWidth,
   ...(open && {
      transition: theme.transitions.create('margin', {
         easing: theme.transitions.easing.easeOut,
         duration: theme.transitions.duration.enteringScreen
      }),
      marginRight: 0
   })
}))

const DrawerHeader = styled('div')(({ theme }) => ({
   display: 'flex',
   alignItems: 'center',
   padding: theme.spacing(0, 1),
   // necessary for content to be below app bar
   ...theme.mixins.toolbar,
   justifyContent: 'flex-start'
}))

interface DrawerProps extends MuiDrawerProps {
   drawerWidth?: number
}
export default function PersistentDrawerRight(props: DrawerProps) {
   const theme = useTheme()
   const open = useAppSelector((state) => state.ui.drawerOpen)
   const { data, error, isLoading } = useGetCollectionsQuery('sdfsdfsd')
   const dispatch = useAppDispatch()
   // const [open, setOpen] = React.useState(true)

   const handleDrawerClose = () => {
      console.log('close')
      dispatch(setDrawerOpenState(false))
   }

   return (
      <Drawer
         sx={{
            width: props.drawerWidth || 250,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
               width: props.drawerWidth || 250
            }
         }}
         variant="persistent"
         anchor="left"
         open={open}
      >
         <DrawerHeader>
            <IconButton onClick={handleDrawerClose}>
               {theme.direction === 'rtl' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
            </IconButton>
         </DrawerHeader>
         <Divider />
         <List>
            {['Inbox', 'Starred', 'Send email', 'Drafts'].map((text, index) => (
               <ListItem key={text} disablePadding>
                  <ListItemButton>
                     <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                     <ListItemText primary={text} />
                  </ListItemButton>
               </ListItem>
            ))}
         </List>
         <Divider />
         <List>
            {data.map((text, index) => (
               <ListItem key={text} disablePadding>
                  <ListItemButton>
                     <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                     <ListItemText primary={text} />
                  </ListItemButton>
               </ListItem>
            ))}
         </List>
      </Drawer>
   )
}
