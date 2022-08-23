function getApiPath() {
   console.log(process.env)
   if (process.env.REACT_APP_API_PATH) {
      return process.env.REACT_APP_API_PATH
   }
   if (process.env.NODE_ENV === 'production') {
      return '/api/v1'
   }
   return 'http://localhost:8888'
}

export const API_PATH = getApiPath()
