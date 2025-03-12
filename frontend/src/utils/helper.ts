import dayjs from "dayjs";

export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function chainFunctions(...funcs: (((...args: any[]) => any) | undefined)[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function (...args: any[]) {
    funcs.forEach((func) => {
      if (func) func(...args);
    });
  };
}

/**
 * Generates an array of numbers from 0 to n-1.
 *
 * @param n - The number of elements in the array.
 * @returns An array of numbers from 0 to n-1.
 */
export function range(n: number): number[] {
  return [...Array(n).keys()];
}
export function generateDayDatesForYearRange(startYear: number, endYear: number): string[] {
  const startDate = dayjs(`${startYear}-01-01`);
  const endDate = dayjs(`${endYear}-12-31`);
  const dates: string[] = [];
  let currentDate = startDate;

  // Loop until we pass the endDate
  while (currentDate.isBefore(endDate) || currentDate.isSame(endDate, "day")) {
    dates.push(currentDate.format("YYYY-MM-DD"));
    currentDate = currentDate.add(1, "day");
  }
  return dates;
}

/**
 * Generates an array of time strings for a given time step in seconds
 * for a day.
 *
 * @param stepSeconds - The time step in seconds.
 * @returns An array of time strings.
 */
export function generateTimeArray(stepSeconds: number): string[] {
  const times: string[] = [];
  const secondsInDay = 24 * 60 * 60;

  for (let seconds = 0; seconds < secondsInDay; seconds += stepSeconds) {
    // Calculate hours and minutes
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    // Format hours and minutes as two-digit strings
    const formattedTime = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;

    times.push(formattedTime);
  }
  return times;
}

/**
 * Checks if the given year is a leap year.
 *
 * @param year - The year to check.
 * @returns True if the year is a leap year, false otherwise.
 */
function isLeapYear(year: number): boolean {
  return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
}

/**
 * Returns the number of days in the given year.
 *
 * @param year - The year for which to determine the number of days.
 * @returns 366 if the year is a leap year, otherwise 365.
 */
function daysInYear(year: number): number {
  return isLeapYear(year) ? 366 : 365;
}

/**
 * Generates an array of the number of days in each year within the given range.
 *
 * @param startYear - The starting year of the range.
 * @param endYear - The ending year of the range.
 * @returns An array of the number of days in each year within the range.
 */
export function generateYearsDayCountsArray(startYear: number, endYear: number): number[] {
  const yearsDaysArray: number[] = [];
  for (let year = startYear; year <= endYear; year++) {
    yearsDaysArray.push(daysInYear(year));
  }
  return yearsDaysArray;
}
