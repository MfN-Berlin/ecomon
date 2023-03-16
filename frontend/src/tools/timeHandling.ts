export function secondsToYearsMonthDaysHoursMinutesSeconds(input: number) {
   const years = Math.floor(input / 31536000)
   const months = Math.floor((input % 31536000) / 2592000)
   const days = Math.floor((input % 2592000) / 86400)
   const hours = Math.floor((input % 86400) / 3600)
   const minutes = Math.floor((input % 3600) / 60)
   const seconds = Math.floor(input % 60)
   return `${years ? years + ' Years  ' : ''}${months ? months + ' Months  ' : ''}${days ? days + ' Days  ' : ''}${hours ? hours + ' Hours  ' : ''
      }${minutes ? minutes + ' Minutes  ' : ''}${seconds ? seconds + ' Seconds  ' : ''}`
}
