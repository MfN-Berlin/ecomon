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

export const DEFAULT_VALUES = {
   hasIndex: true,
   thresholdMin: 0.0,
   binWidth: 0.02,
   thresholdMax: 1.0,
   sampleSize: 100,
   filterFrequency: 100,
   useFilter: false,

}

export const API_PATH = getApiPath()
