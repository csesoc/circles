import { Course } from 'types/api';
import { CourseLegacyOfferings, Term } from 'types/planner';

export type ManyCoursesOfferings = {
  [course: string]: CourseLegacyOfferings;
};

export const courseHasOffering = (course: Course, term: Term): boolean => {
  // TODO: Work out how legacy offerings work now
  return course && course.terms.includes(term);
};
