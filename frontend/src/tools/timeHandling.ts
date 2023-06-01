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

export function generateDatesInYear(year: number): string[] {
   const month_lengths = [31, year % 4 === 0 ? 28 : 29, 31, 30, 31, 30, 31, 31, 30, 31, 30]
   return month_lengths.reduce((dates, month_length, month) => {
      for (let day = 1; day <= month_length; day++) {
         dates.push(`${month + 1 < 10 ? '0' : ''}${month + 1}/${day < 10 ? '0' : ''}${day}`);
      }
      return dates;
   }, [] as string[])
}
export function getYearDaysCount(year: number): number {
   return year % 4 === 0 ? 366 : 365
}

export function generateTimeLabels(intervalInMinutes: number) {
   let times = [];
   for (let i = 0; i < 24; i++) {
      for (let j = 0; j < 60; j += intervalInMinutes) {
         let hour = i < 10 ? '0' + i : i;
         let minute = j < 10 ? '0' + j : j;
         times.push(hour + ':' + minute);
      }
   }
   return times;
}

export function getTimeSlotOfDayCount(intervalInMinutes: number) {
   return 24 * (60 / intervalInMinutes);
}
