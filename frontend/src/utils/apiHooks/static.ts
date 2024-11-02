import { getCourseInfo, getCoursePrereqs } from 'utils/api/coursesApi';
import { fetchAllDegrees, getProgramStructure } from 'utils/api/programsApi';
import { getCourseTimetable } from 'utils/api/timetableApi';
import { getCourseRating } from 'utils/api/unilectivesApi';
import { createStaticQueryHook } from './hookHelpers';

export const useCourseRatingQuery = createStaticQueryHook<
  ['courseRating', string],
  [string],
  Awaited<ReturnType<typeof getCourseRating>>
>((code) => ['courseRating', code], getCourseRating);

const getCourseExtendedInfo = async (courseCode: string) => {
  return Promise.allSettled([
    getCourseInfo(courseCode),
    getCoursePrereqs(courseCode),
    getCourseTimetable(courseCode)
  ]);
};

export const useCourseInfoQuery = createStaticQueryHook<
  ['courseInfo', string],
  [string],
  Awaited<ReturnType<typeof getCourseExtendedInfo>>
>((code) => ['courseInfo', code], getCourseExtendedInfo);

export const useProgramsQuery = createStaticQueryHook<
  ['programs'],
  [],
  Awaited<ReturnType<typeof fetchAllDegrees>>
>(() => ['programs'], fetchAllDegrees);

export const useStructureQuery = createStaticQueryHook<
  ['structure', string, string[]],
  [string, string[]],
  Awaited<ReturnType<typeof getProgramStructure>>
>((programCode, specs) => ['structure', programCode, specs], getProgramStructure);
