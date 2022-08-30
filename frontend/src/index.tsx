import React from 'react'

import './index.css'
import App from './App'

import { render } from 'react-dom'
import { JobsProvider } from './components/JobsProvider'
const container = document.getElementById('root')
render(
   <JobsProvider>
      <App />
   </JobsProvider>,
   container
)
