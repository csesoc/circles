import axios from 'axios';
import { CourseTimetable } from 'types/courseCapacity';
import { TIMETABLE_API_URL } from 'config/constants';

export const getCourseTimetable = async (courseCode: string) => {
  const res = await axios.get<CourseTimetable>(`${TIMETABLE_API_URL}/${courseCode}`);
  return res.data;
};
