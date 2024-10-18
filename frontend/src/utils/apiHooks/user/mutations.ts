import { setupDegreeWizard } from 'utils/api/degreeApi';
import {
  addToUnplanned,
  removeAll,
  removeCourse,
  setPlannedCourseToTerm,
  setUnplannedCourseToTerm,
  toggleIgnoreFromProgression,
  toggleLockTerm,
  unscheduleAll,
  unscheduleCourse,
  updateCourseMark
} from 'utils/api/plannerApi';
import {
  hideYear,
  importUser,
  resetUserDegree,
  showYears,
  toggleShowMarks,
  toggleSummerTerm,
  updateDegreeLength,
  updateStartYear
} from 'utils/api/userApi';
import { createUserMutationHook } from './hookHelpers';

export const useRemoveCourseMutation = createUserMutationHook([['planner']], removeCourse);

export const useAddToUnplannedMutation = createUserMutationHook([['planner']], addToUnplanned);

export const useUpdateMarkMutation = createUserMutationHook(
  [
    ['planner', 'courses'],
    ['planner', 'validation']
  ],
  updateCourseMark
);

export const useRemoveAllCoursesMutation = createUserMutationHook([['planner']], removeAll);

export const useResetDegreeMutation = createUserMutationHook(true, resetUserDegree);

export const useToggleLockTermMutation = createUserMutationHook([['planner']], toggleLockTerm); // TODO-olli: technically no need to courses

export const useUpdateDegreeLengthMutation = createUserMutationHook(
  [['planner'], ['settings']],
  updateDegreeLength
);

export const useUpdateStartYearMutation = createUserMutationHook([['planner']], updateStartYear);

export const useToggleSummerTermMutation = createUserMutationHook([['planner']], toggleSummerTerm);

export const useToggleMarksMutation = createUserMutationHook([['settings']], toggleShowMarks);

export const useHideYearMutation = createUserMutationHook([['settings']], hideYear);

export const useShowYearsMutation = createUserMutationHook([['settings']], showYears);

export const useSetupDegreeWizardMutation = createUserMutationHook(true, setupDegreeWizard);

export const useToggleIgnoreFromProgressionMutation = createUserMutationHook(
  [['planner']],
  toggleIgnoreFromProgression
);

export const useUnscheduleAllMutation = createUserMutationHook([['planner']], unscheduleAll);

export const useUnscheduleCourseMutation = createUserMutationHook([['planner']], unscheduleCourse); // TODO-olli: figure out how to get query client into onMutate for baseOptions

// could change baseOptions to be (queryClient) => { options }
export const useSetPlannedCourseToTermMutation = createUserMutationHook(
  [['planner']],
  setPlannedCourseToTerm
);

export const useSetUnplannedCourseToTermMutation = createUserMutationHook(
  [['planner']],
  setUnplannedCourseToTerm
);

export const useImportUserMutation = createUserMutationHook(true, importUser);
