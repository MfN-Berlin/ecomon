import * as React from 'react'
import { styled, useTheme } from '@mui/material/styles'
import { Link, useLocation, useParams } from 'react-router-dom'
import Drawer, { DrawerProps as MuiDrawerProps } from '@mui/material/Drawer'
import List from '@mui/material/List'
import Divider from '@mui/material/Divider'
import IconButton from '@mui/material/IconButton'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import InputBase from '@mui/material/InputBase'
import SearchIcon from '@mui/icons-material/Search'

import { useAppSelector, useAppDispatch } from '../store/hooks'
import { setDrawerOpenState } from '../store/slices/ui'
import { useGetCollectionsQuery } from '../services/api'
import { parseCollectionName, groupByModel } from '../tools/stringHandling'
import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import HomeOutlinedIcon from '@mui/icons-material/HomeOutlined';
import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
const DrawerHeader = styled('div')(({ theme }) => ({

   display: 'flex',
   alignItems: 'center',
   padding: theme.spacing(0, 1),
   // necessary for content to be below app bar
   ...theme.mixins.toolbar,
   justifyContent: 'flex-start',
   zIndex: 10,
   backgroundColor: theme.palette.background.default
}))

interface DrawerProps extends MuiDrawerProps {
   drawerWidth?: number
}
export default function PersistentDrawerRight(props: DrawerProps) {
   const { id: routeId } = useParams<{ id: string }>()
   const [filterValue, setFilterValue] = React.useState<string>('')
   const theme = useTheme()
   const open = useAppSelector((state) => state.ui.drawerOpen)
   const { data } = useGetCollectionsQuery()
   const dispatch = useAppDispatch()
   const location = useLocation()
   // const [open, setOpen] = React.useState(true)

   const handleDrawerClose = () => {
      console.log('close')
      dispatch(setDrawerOpenState(false))
   }

   function transformCollectionData(data: string[], filter = '') {
      const filteredData = [...data].filter((item) => item.toLowerCase().includes(filter.toLowerCase()))

      filteredData.sort()
      const collections = filteredData.map((name) => parseCollectionName(name))

      return groupByModel(collections)
   }
   const drawerLinks = [ {
      name: 'Home',
      link: '/',
      icon: <HomeOutlinedIcon />
   },
   {
      name: 'Evaluation',
      link: '/evaluation',
      icon: <AssessmentOutlinedIcon />
   },
   ]

   return (
      <Drawer color="primary"
         sx={{
            zIndex: 0,
            width: props.drawerWidth || 250,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
               width: props.drawerWidth || 250, boxSizing: 'border-box'
            }
         }}
         variant="persistent"
         anchor="left"
         open={open}
      >
         <p></p>
         <p></p>
         <List>
            {drawerLinks.map((item, index) => (
               <ListItemButton key={item.name}  component={Link} to={item.link} selected={item.link === location.pathname}  >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.name} />
               </ListItemButton>


            ))}
          </List>
          <Divider />
         <DrawerHeader>
            <IconButton onClick={handleDrawerClose}>
               {theme.direction === 'rtl' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
            </IconButton>
            <InputBase
               sx={{ ml: 1, flex: 1, width: 130 }}
               placeholder="Search"
               inputProps={{ 'aria-label': 'search' }}
               onChange={(e) => setFilterValue(e.target.value)}
            />
            <IconButton type="button" sx={{ p: '0px' }} aria-label="search">
               <SearchIcon />
            </IconButton>
         </DrawerHeader>


         <List>
            {transformCollectionData(data || [], filterValue).flatMap(({ modelName, collections }, index) => {
               const isOddGroup = index % 2 !== 0
               return [
                  <React.Fragment key={`group-${modelName}`}>
                     <Divider
                        sx={{
                           position: 'sticky',
                           top: 60,
                           backgroundColor: isOddGroup ? '#bababa' : '#f0f0f0',
                           zIndex: 99
                        }}
                     >
                        <ListItemText primary={modelName} />
                     </Divider>
                  </React.Fragment>,
                  ...collections.map(({ id, station, year, model }) => (
                     <ListItemButton
                        key={`item-${id}`}
                        component={Link}
                        to={`/collection/${id}`}
                        sx={{ m: '1px', p: '0px', pl: '24px', backgroundColor: isOddGroup ? '#bababa' : '#f0f0f0' }}
                        selected={id === routeId}
                     >
                        <ListItemText primary={`${station}: ${year}`} />
                     </ListItemButton>
                  ))
               ]
            })}
         </List>
      </Drawer>
   )
}
