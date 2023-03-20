import * as React from 'react'
import { useEffect, useContext } from 'react'
import { useParams } from 'react-router-dom'

import Grid from '@mui/material/Unstable_Grid2'
import ChipList from '../../components/ChipList'
import { useCollectionSpeciesList } from '../../hooks/collection'
import { addDbKeyToSpecies, deleteDbKeyFromSpecies } from '../../tools/dbKeyHandling'
import { firstLetterUpperAndReplaceSpace } from '../../tools/stringHandling'
import { Job } from '../../components/JobsProvider'
import { store } from '../../components/JobsProvider'



export default function DBIndexChipList() {
   const { id } = useParams()
   const globalState = useContext(store)
   const { state: { jobs } } = globalState
   const { collectionSpeciesList, loading: speciesLoading, update: updateSpeciesList } = useCollectionSpeciesList(id)
   useEffect(() => {
      updateSpeciesList()
   }, [jobs])

   async function handleAddSpeciesIndex(item: { label: string; key: string }): Promise<void> {
      console.log(item)
      id && (await addDbKeyToSpecies(id, item.key))
      await updateSpeciesList()
   }

   async function handleDeleteSpeciesIndex(item: { label: string; key: string }): Promise<void> {
      console.log(item)
      id && (await deleteDbKeyFromSpecies(id, item.key))
      await updateSpeciesList()
   }

   return (

      <ChipList
         addDialogTitle={'Add database index to species'}
         addDialogContentText={'Select a species to add a database index to'}
         ensureDelete={true}
         onAdd={handleAddSpeciesIndex}
         onDelete={handleDeleteSpeciesIndex}
         deleteDialogTitleTemplate={(species) => `Drop database index of  ${species.label}?`}
         label="Species with DB-Index:"
         items={collectionSpeciesList
            .filter((x) => x.has_index)
            .map((item) => ({
               label: firstLetterUpperAndReplaceSpace(item.name),
               key: item.name
            }))}
         pendingItems={jobs
            .filter((x) => x.collection === id && x.status === 'pending' && x.type === 'add_index')
            .map((item) => ({
               label: firstLetterUpperAndReplaceSpace(item.metadata?.column_name),
               key: item.metadata?.column_name
            }))}
         options={collectionSpeciesList
            .filter((x) => !x.has_index)
            .map((item) => ({
               label: firstLetterUpperAndReplaceSpace(item.name),
               key: item.name
            }))}
      ></ChipList>

   )
}
