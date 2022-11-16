import * as React from 'react'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import HomeIcon from '@mui/icons-material/Home'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import { Link, useLocation } from 'react-router-dom'

import { useCollectionList } from '../hooks/collection'

export default function TabNavigation() {
   // You need to provide the routes in descendant order.
   // This means that if you have nested routes like:
   // users, users/new, users/edit.
   // Then the order should be ['users/add', 'users/edit', 'users'].
   const { collectionList, loading } = useCollectionList()

   const location = useLocation()
   const currentTab = location.pathname

   return (
      <React.Fragment>
         {loading ? (
            <div>Loading...</div>
         ) : (
            <Tabs
               value={currentTab}
               indicatorColor="secondary"
               textColor="inherit"
               aria-label={'home ' + collectionList.join(' ')}
               variant="scrollable"
               scrollButtons
               allowScrollButtonsMobile
            >
               <Tab aria-label="Home" value="/" to="/" component={Link} icon={<HomeIcon />} />
               {loading ? (
                  <Tab label="Loading ..." key="loading" disabled iconPosition="start" icon={<HourglassEmptyIcon />} />
               ) : (
                  collectionList.map((item) => (
                     <Tab
                        label={item}
                        key={item}
                        aria-label={item}
                        value={'/collection/' + item}
                        to={'/collection/' + item}
                        component={Link}
                     />
                  ))
               )}
            </Tabs>
         )}
      </React.Fragment>
   )
}
