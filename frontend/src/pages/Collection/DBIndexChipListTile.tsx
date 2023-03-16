import * as React from 'react'
import { useEffect } from 'react'
import Grid from '@mui/material/Unstable_Grid2'
import ChipList from '../../components/ChipList'
import { useCollectionSpeciesList } from '../../hooks/collection'
import { addDbKeyToSpecies, deleteDbKeyFromSpecies } from '../../tools/dbKeyHandling'
import { firstLetterUpperAndReplaceSpace } from '../../tools/stringHandling'
import { Job } from '../../components/JobsProvider'

interface DBIndexChipListProps {
   collectionId: string | undefined
   jobs: Job[]
}

export default function DBIndexChipList({ collectionId: id, jobs }: DBIndexChipListProps) {
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
      <Grid xs={12}>
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
      </Grid>
   )
}
