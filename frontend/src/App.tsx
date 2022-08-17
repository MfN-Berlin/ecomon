import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from './pages/Dashboard';

// pages
import Collection from './pages/Collection';
import Start from './pages/Start';

function App() {
    return (
        <div className="App">
            <link
                rel="stylesheet"
                href="https://fonts.googleapis.com/icon?family=Material+Icons"
            />
            <link
                rel="stylesheet"
                href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
            />
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Dashboard />}>
                        <Route index element={<Start />} />
                        <Route path="collection/:id" element={<Collection />} />
                        {/* <Route path="contact" element={<Contact />} />
                <Route path="*" element={<NoPage />} /> */}
                    </Route>
                </Routes>
            </BrowserRouter>

        </div>
    );
}

export default App;
