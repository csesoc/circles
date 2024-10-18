import { getUserCourses, getUserDegree, getUserPlanner } from 'utils/api/userApi';
import { createUserQueryHook } from './hookHelpers';

export const useUserCourses = createUserQueryHook(['planner', 'courses'], getUserCourses);

export const useUserPlanner = createUserQueryHook(['planner'], getUserPlanner);

export const useUserDegree = createUserQueryHook(['degree'], getUserDegree);
