import { styled } from '@mui/material/styles'
import * as React from 'react'
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import IconButton from '@mui/material/IconButton'
import MenuIcon from '@mui/icons-material/Menu'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { toggleDrawer } from '../store/slices/ui'
import { useParams } from 'react-router-dom'

interface AppBarProps extends MuiAppBarProps {
   open?: boolean
   drawerWidth?: number
}

const StyledAppBar = styled(MuiAppBar, {
   shouldForwardProp: (prop) => prop !== 'open'
})<AppBarProps>(({ theme, open, drawerWidth }) => ({
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
   const { id } = useParams<{ id: string }>()
   if (id)
      return (
         <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {`${id}`}
         </Typography>
      )
   else {
      return (
         <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Home
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
      <StyledAppBar position="fixed" drawerWidth={250} open={open}>
         <Toolbar>
            <IconButton size="large" edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }} onClick={handleMenu}>
               <MenuIcon />
            </IconButton>
            <Title />
         </Toolbar>
      </StyledAppBar>
   )
}
