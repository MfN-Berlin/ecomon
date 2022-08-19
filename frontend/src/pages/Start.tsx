import * as React from 'react'
import { Link } from 'react-router-dom'

export default function Title() {
   return (
      <div>
         <h1>Start Page</h1>
         <Link to="/collection">Blogs</Link>
      </div>
   )
}
