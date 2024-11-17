import axios from 'axios';
import { UnilectivesCourse } from 'types/unilectives';

export const getCourseRating = async (code: string) => {
  const res = await axios.get<{ course: UnilectivesCourse }>(
    `https://unilectives.devsoc.app/api/v1/course/${code}`
  );
  return res.data.course;
};
