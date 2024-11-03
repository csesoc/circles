import { getCourseChildren, getCourseInfo, getCoursePrereqs } from 'utils/api/coursesApi';
import { fetchAllDegrees, getProgramGraph, getProgramStructure } from 'utils/api/programsApi';
import { getSpecialisationsForProgram, getSpecialisationTypes } from 'utils/api/specsApi';
import { getCourseTimetable } from 'utils/api/timetableApi';
import { getCourseRating } from 'utils/api/unilectivesApi';
import { createStaticQueryHook } from './hookHelpers';

export const useCourseRatingQuery = createStaticQueryHook(
  (code) => ['courseRating', code],
  getCourseRating
);

const getCourseExtendedInfo = async (courseCode: string) => {
  return Promise.allSettled([
    getCourseInfo(courseCode),
    getCoursePrereqs(courseCode),
    getCourseTimetable(courseCode)
  ]);
};

export const useCourseInfoQuery = createStaticQueryHook(
  (code) => ['courseInfo', code],
  getCourseExtendedInfo
);

export const useProgramsQuery = createStaticQueryHook(() => ['programs'], fetchAllDegrees);

export const useStructureQuery = createStaticQueryHook(
  (programCode, specs) => ['structure', programCode, specs],
  getProgramStructure
);

export const useCourseChildrenQuery = createStaticQueryHook(
  (courseCode) => ['course', 'children', courseCode],
  getCourseChildren
);

export const useCoursePrereqsQuery = createStaticQueryHook(
  (courseCode) => ['course', 'prereqs', courseCode],
  getCoursePrereqs
);

export const useAllDegreesQuery = createStaticQueryHook(() => ['programs'], fetchAllDegrees);

export const useSpecsForProgramQuery = createStaticQueryHook(
  (programCode, specType) => ['specialisations', programCode, specType],
  getSpecialisationsForProgram
);

export const useSpecTypesQuery = createStaticQueryHook(
  (programCode) => ['specialisations', 'types', programCode],
  getSpecialisationTypes
);

export const useProgramGraphQuery = createStaticQueryHook(
  (programCode, specs) => ['graph', { code: programCode, specs }],
  getProgramGraph
);
