import { API_PATH } from '../consts'

export async function deleteDbKeyFromSpecies(collectionName: string, speciesName: string) {
   const response = await fetch(`${API_PATH}/prefix/${collectionName}/predictions/${speciesName}/index`, {
      method: 'DELETE'
   })
   return await response.text()
}

export async function addDbKeyToSpecies(collectionName: string, speciesName: string) {
   const response = await fetch(`${API_PATH}/prefix/${collectionName}/predictions/${speciesName}/index`, {
      method: 'PUT'
   })
   return await response.text()
}
