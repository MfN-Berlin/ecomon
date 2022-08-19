import * as React from 'react'
import { useEffect, useState } from 'react'

import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import { Link as RouterLink, LinkProps as RouterLinkProps } from 'react-router-dom'

import AssignmentIcon from '@mui/icons-material/Assignment'

interface NavProps {
   children?: React.ReactNode
}

interface ListItemLinkProps {
   icon?: React.ReactElement
   primary: string
   to: string
   key: string
}

function ListItemLink(props: ListItemLinkProps) {
   const { icon, primary, to } = props

   const renderLink = React.useMemo(
      () =>
         React.forwardRef<HTMLAnchorElement, Omit<RouterLinkProps, 'to'>>(function Link(itemProps, ref) {
            return <RouterLink to={to} ref={ref} {...itemProps} role={undefined} />
         }),
      [to]
   )

   return (
      <li key={props.key}>
         <ListItem button component={renderLink}>
            {icon ? <ListItemIcon>{icon}</ListItemIcon> : null}
            <ListItemText primary={primary} />
         </ListItem>
      </li>
   )
}

export default function NavPoints(props: NavProps) {
   const [collections, setItems] = useState<string[]>([])
   useEffect(() => {
      fetch('http://127.0.0.1:8000/prefix/list')
         .then((res) => res.json())
         .then((data) => setItems(data))
   }, [])

   return (
      <>
         {collections.map((item) => (
            <ListItemLink to={'/collection/' + item} key={item} primary={item} icon={<AssignmentIcon />} />
         ))}
      </>
   )
}
