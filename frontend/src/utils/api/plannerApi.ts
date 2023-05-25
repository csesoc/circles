import axios from 'axios';
import { PlannedToTerm, UnPlannedToTerm } from 'types/planner';
import { getToken } from './userApi';

export const handleAddToUnplanned = async (courseId: string) => {
  const token = getToken();
  try {
    await axios.post('planner/addToUnplanned', { courseCode: courseId }, { params: { token } });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Error at handleAddToUnplanned: ', err);
  }
};

export const handleSetPlannedCourseToTerm = async (data: PlannedToTerm) => {
  const token = getToken();
  try {
    await axios.post('planner/plannedToTerm', data, { params: { token } });
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/restrict-template-expressions, no-console
    console.error(`Error at setPlannedCourseToTerm: ${err}`);
  }
};

export const handleSetUnplannedCourseToTerm = async (data: UnPlannedToTerm) => {
  const token = getToken();
  try {
    await axios.post('planner/unPlannedToTerm', data, { params: { token } });
  } catch (err) {
    // eslint-disable-next-line no-console, @typescript-eslint/restrict-template-expressions
    console.error(`Error at handleSetUnplannedCourseToTerm: ${err}`);
  }
};

export const handleUnscheduleCourse = async (courseId: string) => {
  const token = getToken();
  try {
    await axios.post('planner/unscheduleCourse', { courseCode: courseId }, { params: { token } });
  } catch (err) {
    // eslint-disable-next-line no-console, @typescript-eslint/restrict-template-expressions
    console.error(`Error at handleUnscheduleCourse: ${err}`);
  }
};

export const handleUnscheduleAll = async () => {
  const token = getToken();
  try {
    await axios.post('planner/unscheduleAll', { params: { token } });
  } catch (err) {
    // eslint-disable-next-line no-console, @typescript-eslint/restrict-template-expressions
    console.error(`Error at handleUnscheduleAll: ${err}`);
  }
};
