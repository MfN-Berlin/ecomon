export type Collection = { id: string; station: string; year?: number; model: string }
export type ModelCollection = { modelName: string; collections: Collection[] };

export function parseCollectionName(name: string): Collection {
   //split name on _ check if part coung is 2

   const parts = name.split('_')
   if (parts.length === 1) {
      return {
         id: name,
         station: name,
         model: 'BIRDID'
      }
   }
   if (parts.length === 2) {
      return {
         id: name,
         station: parts[0],
         year: parseInt(parts[1]),
         model: 'BIRDID'
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
export function firstLetterUpperAndReplaceSpace(str: string) {
   return (str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()).replace(/_/g, ' ');
}


export function groupByModel(collections: Collection[]): ModelCollection[] {
   const result: ModelCollection[] = [];

   collections.forEach((collection) => {
      const index = result.findIndex((item) => item.modelName === collection.model);
      if (index === -1) {
         result.push({ modelName: collection.model, collections: [collection] });
      } else {
         result[index].collections.push(collection);
      }
   });

   return result;
}
