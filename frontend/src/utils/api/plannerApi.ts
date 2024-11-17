import axios from 'axios';
import { CourseMark } from 'types/api';
import { CourseTime } from 'types/courses';
import { PlannedToTerm, UnPlannedToTerm, UnscheduleCourse } from 'types/planner';
import { ValidatesResponse } from 'types/userResponse';
import { withAuthorization } from './authApi';

export const addToUnplanned = async (token: string, courseId: string) => {
  try {
    await axios.post(
      'planner/addToUnplanned',
      { courseCode: courseId },
      { headers: withAuthorization(token) }
    );
  } catch (err) {
    console.error('Error at addToUnplanned: ', err);
  }
};

export const setPlannedCourseToTerm = async (token: string, data: PlannedToTerm) => {
  try {
    await axios.post('planner/plannedToTerm', data, { headers: withAuthorization(token) });
  } catch (err) {
    console.error('Error at setPlannedCourseToTerm: ', err);
  }
};

export const setUnplannedCourseToTerm = async (token: string, data: UnPlannedToTerm) => {
  try {
    await axios.post('planner/unPlannedToTerm', data, { headers: withAuthorization(token) });
  } catch (err) {
    console.error('Error at handleSetUnplannedCourseToTerm: ', err);
  }
};

export const unscheduleCourse = async (token: string, data: UnscheduleCourse) => {
  try {
    await axios.post(
      'planner/unscheduleCourse',
      { courseCode: data.courseCode },
      { headers: withAuthorization(token) }
    );
  } catch (err) {
    console.error('Error at handleUnscheduleCourse: ', err);
  }
};

export const unscheduleAll = async (token: string) => {
  try {
    await axios.post('planner/unscheduleAll', {}, { headers: withAuthorization(token) });
  } catch (err) {
    console.error('Error at handleUnscheduleAll: ', err);
  }
};

export const removeCourse = async (token: string, courseId: string) => {
  try {
    await axios.post(
      'planner/removeCourse',
      { courseCode: courseId },
      { headers: withAuthorization(token) }
    );
  } catch (err) {
    console.error('Error at removeCourse: ', err);
  }
};

export const toggleIgnoreFromProgression = async (token: string, courseId: string) => {
  try {
    await axios.post(
      'planner/toggleIgnoreFromProgression',
      { courseCode: courseId },
      { headers: withAuthorization(token) }
    );
  } catch (err) {
    console.error('Error at toggleIgnoreFromProgression: ', err);
  }
};

export const removeAll = async (token: string) => {
  try {
    await axios.post('planner/removeAll', {}, { headers: withAuthorization(token) });
  } catch (err) {
    console.error('Error at removeAll: ', err);
  }
};

export const validateTermPlanner = async (token: string): Promise<ValidatesResponse> => {
  const res = await axios.get('planner/validateTermPlanner', {
    headers: withAuthorization(token)
  });
  return res.data as ValidatesResponse;
};

export const updateCourseMark = async (token: string, courseMark: CourseMark) => {
  try {
    await axios.put('/user/updateCourseMark', courseMark, {
      headers: withAuthorization(token)
    });
  } catch (e) {
    console.error(e);
  }
};

// TODO: dont steal the CourseTime type here... unify all yearterm representations
export const toggleLockTerm = async (token: string, termyear: CourseTime) => {
  await axios.post(
    '/planner/toggleTermLocked',
    {},
    { params: { termyear: `${termyear.year}${termyear.term}` }, headers: withAuthorization(token) }
  );
};
