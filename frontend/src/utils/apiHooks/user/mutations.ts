import { addToUnplanned, removeCourse } from 'utils/api/plannerApi';
import { createUserMutationHook } from './hookHelpers';

export const useRemoveCourseMutation = createUserMutationHook([['planner']], removeCourse);

export const useAddToUnplannedMutation = createUserMutationHook([['planner']], addToUnplanned);
