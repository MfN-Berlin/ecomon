import * as React from 'react'
import { styled } from '@mui/material/styles'

type MainProps = {
   open?: boolean
   drawerWidth?: number
   children: React.ReactNode
}

const MainStyled = styled('main', {
   shouldForwardProp: (prop) => prop !== 'open' && prop !== 'drawerWidth'
})<MainProps>(({ theme, open, drawerWidth }) => ({
   flexGrow: 1,
   padding: theme.spacing(1),
   transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
   }),
   marginLeft: `-${open ? 0 : drawerWidth}px`,
   ...(open && {
      transition: theme.transitions.create('margin', {
         easing: theme.transitions.easing.easeOut,
         duration: theme.transitions.duration.enteringScreen
      }),
      marginLeft: 0
   })
}))

const Main = (props: MainProps) => {
   const { open, drawerWidth, children, ...otherProps } = props
   return (
      <MainStyled open={open} drawerWidth={drawerWidth} {...otherProps}>
         {children}
      </MainStyled>
   )
}

export default Main
