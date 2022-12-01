export type Collection = { id: string; station: string; year?: number; model: string }
export function parseCollectionName(name: string): Collection {
   //split name on _ check if part coung is 2

   const parts = name.split('_')
   if (parts.length === 1) {
      return {
         id: name,
         station: name,
         model: 'birdId'
      }
   }
   if (parts.length === 2) {
      return {
         id: name,
         station: parts[0],
         year: parseInt(parts[1]),
         model: 'birdId'
      }
   } else {
      return {
         id: name,
         station: parts[1],
         year: parseInt(parts[2]),
         model: parts[0]
      }
   }
}
