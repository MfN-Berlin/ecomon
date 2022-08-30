import * as React from 'react'
import CircularProgress from '@mui/material/CircularProgress'
import CircularProgressWithLabel from './CircularProgressWithLabel'
import ErrorIcon from '@mui/icons-material/Error'
import IconButton from '@mui/material/IconButton'
import DownloadIcon from '@mui/icons-material/Download'
import DoneIcon from '@mui/icons-material/Done'
interface SampleJobStatusProps {
   status: string
   progress: number
   error: string
   url?: string
}

export default function SampleJobStatus(props: SampleJobStatusProps) {
   // You need to provide the routes in descendant order.
   // This means that if you have nested routes like:
   // users, users/new, users/edit.
   // Then the order should be ['users/add', 'users/edit', 'users'].
   const { status, progress, error, url } = props

   switch (status) {
      case 'pending':
         return <CircularProgress />
      case 'running':
         return <CircularProgressWithLabel value={progress} />
      case 'done':
         return url ? (
            <IconButton
               color="primary"
               aria-label="download sample"
               component="label"
               onClick={() => {
                  window.open(url)
               }}
            >
               <DownloadIcon />
            </IconButton>
         ) : (
            <IconButton color="success" aria-label="job done" component="label">
               <DoneIcon />
            </IconButton>
         )
      case 'failed':
         return (
            <IconButton
               color="error"
               aria-label="show error message"
               component="label"
               onClick={() => {
                  alert(error)
               }}
            >
               <ErrorIcon />
            </IconButton>
         )
      default:
         return <div>Unknown status</div>
   }
}
