import React, { useEffect, useRef, useState } from 'react'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Paper from '@mui/material/Paper'

interface DataTableProps {
   columnLabels?: string[]
   rowLabels?: string[]
   data: string[][]
}

export default function DataTable({ columnLabels, rowLabels, data }: DataTableProps) {
   return (
      <TableContainer component={Paper} sx={{ padding: 0 }}>
         <Table aria-label="simple table" sx={{ padding: 0 }}>
            {rowLabels && (
               <TableHead>
                  <TableRow>
                     {columnLabels && (
                        <TableCell component="th" scope="row" align="right">
                           {columnLabels[0]}
                        </TableCell>
                     )}
                     {rowLabels.map((row, rowIndex) => (
                        <TableCell component="th" scope="row" align="center">
                           {row}
                        </TableCell>
                     ))}
                  </TableRow>
               </TableHead>
            )}
            <TableBody>
               {data.map((row, rowIndex) => (
                  <TableRow key={`row-${rowIndex}`} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                     {columnLabels && (
                        <TableCell component="th" scope="row" align={rowIndex === 0 ? 'right' : 'center'}>
                           {rowLabels ? <b>{columnLabels[rowIndex + 1]}</b> : columnLabels[rowIndex]}
                        </TableCell>
                     )}
                     {row.map((cell, colIndex) => (
                        <TableCell key={`cell-${rowIndex}-${colIndex}`} align="center">
                           {cell}
                        </TableCell>
                     ))}
                  </TableRow>
               ))}
            </TableBody>
         </Table>
      </TableContainer>
   )
}
