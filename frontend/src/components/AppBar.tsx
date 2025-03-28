import { styled } from '@mui/material/styles'
import * as React from 'react'
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import IconButton from '@mui/material/IconButton'
import MenuIcon from '@mui/icons-material/Menu'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { toggleDrawer } from '../store/slices/ui'
import { useLocation, useParams } from 'react-router-dom'
import { firstLetterUpperAndReplaceSpace, parseCollectionName } from '../tools/stringHandling'
interface AppBarProps extends MuiAppBarProps {
   open?: boolean
   drawerWidth?: number
}

const StyledAppBar = styled(MuiAppBar, {
   shouldForwardProp: (prop) => prop !== 'open' && prop !== 'drawerWidth'
})<AppBarProps>(({ theme, open, drawerWidth }) => ({
   justifyContent: 'start',
   transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
   }),
   ...(open && {
      width: `calc(100% - ${drawerWidth}px)`,
      marginLeft: `${drawerWidth}px`,
      transition: theme.transitions.create(['margin', 'width'], {
         easing: theme.transitions.easing.easeOut,
         duration: theme.transitions.duration.enteringScreen
      })
   })
}))

const Title = () => {
   const location = useLocation()
   const { id } = useParams<{ id: string }>()
   if (id) {
      const collection = parseCollectionName(id)
      return (
         <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {`${collection.model}: ${collection.station} - ${collection.year}`}
         </Typography>
      )
   } else {
      return (
         <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {firstLetterUpperAndReplaceSpace(location.pathname.split('/')[1])|| 'Home'}
         </Typography>
      )
   }
}
export default function AppBar() {
   const dispatch = useAppDispatch()
   const open = useAppSelector((state) => state.ui.drawerOpen)

   const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
      dispatch(toggleDrawer())
   }

   return (
      <StyledAppBar position="fixed" open={open}>
         <Toolbar>
            <IconButton size="large" edge="start" color="inherit" aria-label="menu" sx={{ mr: 2,
               zIndex: (theme) => theme.zIndex.drawer + 1 }} onClick={handleMenu}>
              { (open ? <ChevronLeftIcon /> :  <MenuIcon />)}

            </IconButton>
            <Title />
         </Toolbar>
      </StyledAppBar>
   )
}
