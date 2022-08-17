import * as React from 'react';
import Typography from '@mui/material/Typography';
import { Link } from "react-router-dom";
import NavPoints from '../components/NavPoints';


export default function Title() {
    return (
        <div>
            <h1>Start Page</h1>
            <Link to="/collection">Blogs</Link>

        </div>
    );
}
