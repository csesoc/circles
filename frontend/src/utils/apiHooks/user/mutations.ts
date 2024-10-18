import {
  addToUnplanned,
  removeAll,
  removeCourse,
  toggleLockTerm,
  updateCourseMark
} from 'utils/api/plannerApi';
import {
  resetUserDegree,
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
