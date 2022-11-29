import React from 'react'

import './index.css'
import App from './App'

import { render } from 'react-dom'
import { JobsProvider } from './components/JobsProvider'
import { store } from './store'
import { Provider } from 'react-redux'

const container = document.getElementById('root')
render(
   <Provider store={store}>
      <JobsProvider>
         <App />
      </JobsProvider>
   </Provider>,
   container
)
