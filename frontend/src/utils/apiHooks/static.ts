import { getCourseChildren, getCourseInfo, getCoursePrereqs } from 'utils/api/coursesApi';
import { fetchAllDegrees, getProgramGraph, getProgramStructure } from 'utils/api/programsApi';
import { getSpecialisationsForProgram, getSpecialisationTypes } from 'utils/api/specsApi';
import { getCourseTimetable } from 'utils/api/timetableApi';
import { getCourseRating } from 'utils/api/unilectivesApi';
import { createStaticQueryHook } from './hookHelpers';

export const useCourseRatingQuery = createStaticQueryHook(
  (code) => ['courses', code, 'rating'],
  getCourseRating
);

export const useCourseInfoQuery = createStaticQueryHook(
  (code) => ['courses', code, 'info'],
  getCourseInfo
);

export const useCourseTimetableQuery = createStaticQueryHook(
  (code) => ['courses', code, 'timetable'],
  getCourseTimetable
);

export const useCourseChildrenQuery = createStaticQueryHook(
  (code) => ['courses', code, 'children'],
  getCourseChildren
);

export const useCoursePrereqsQuery = createStaticQueryHook(
  (code) => ['courses', code, 'prereqs'],
  getCoursePrereqs
);

export const useAllDegreesQuery = createStaticQueryHook(() => ['programs'], fetchAllDegrees);

export const useStructureQuery = createStaticQueryHook(
  (programCode, specs) => ['programs', programCode, 'structure', specs],
  getProgramStructure
);

export const useSpecsForProgramQuery = createStaticQueryHook(
  (programCode, specType) => ['programs', programCode, 'specialisations', specType],
  getSpecialisationsForProgram
);

export const useSpecTypesQuery = createStaticQueryHook(
  (programCode) => ['programs', programCode, 'specialisation-types'],
  getSpecialisationTypes
);

export const useProgramGraphQuery = createStaticQueryHook(
  (programCode, specs) => ['programs', programCode, 'graph', specs],
  getProgramGraph
);

// TODO: multi queries (as found in termplanner)
