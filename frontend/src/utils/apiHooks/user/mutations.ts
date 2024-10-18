import { addToUnplanned, removeAll, removeCourse, updateCourseMark } from 'utils/api/plannerApi';
import { resetUserDegree } from 'utils/api/userApi';
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
