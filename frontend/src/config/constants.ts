import getMostRecentPastTerm from 'utils/getMostRecentPastTerm';

export const FEEDBACK_LINK =
  'https://docs.google.com/forms/d/e/1FAIpQLSdGoxb-1fRRLySEi5j4Gy_ERWt3XWTBwyKJaDWlTqhy8Xdlxw/viewform?usp=sf_link';

// Don't forget to update live year in the backend too
export const LIVE_YEAR = 2025;
export const CURR_YEAR = new Date().getFullYear();
export const TERM = `${CURR_YEAR + (getMostRecentPastTerm(CURR_YEAR).T === 3 ? 1 : 0)}-T${
  (getMostRecentPastTerm(CURR_YEAR).T + 0) % 3
}`;
export const TIMETABLE_API_URL = `https://timetable.devsoc.app/api/terms/${TERM}/courses`;

// Global colors - currently only being used in LiquidProgressChart
export const lightYellow = '#f9b01e';
export const lightGrey = '#565652';
export const darkGrey = '#323739';
export const yellow = '#FAAD14';
export const purple = '#9254de';
export const lightPurple = '#efdbff';

// export const inDev = false;
export const inDev = import.meta.env.MODE !== 'production';

export const MAX_COURSES_OVERFLOW = 80;
export const COURSES_INITIALLY_COLLAPSED = 16;
