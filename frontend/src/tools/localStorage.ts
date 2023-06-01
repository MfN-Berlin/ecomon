export function loadState(id: string) {
   const serializedState = localStorage.getItem(id)
   if (serializedState === null) {
      return undefined
   }
   return JSON.parse(serializedState)
}
export function saveState(id: string, state: any) {
   const serializedState = JSON.stringify(state)
   localStorage.setItem(id, serializedState)
}

export function removeState(id: string) {
   localStorage.removeItem(id)
}
