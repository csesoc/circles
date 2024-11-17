import axios from 'axios';
import {
  CoursesResponse,
  DegreeResponse,
  PlannerResponse,
  SettingsResponse,
  UserResponse
} from 'types/userResponse';
import { UserJson } from 'utils/export';
import { withAuthorization } from './authApi';

export const getUser = async (token: string): Promise<UserResponse> => {
  const user = await axios.get(`user/data/all`, { headers: withAuthorization(token) });
  return user.data as UserResponse;
};

export const importUser = async (token: string, user: UserJson): Promise<void> => {
  await axios.put(`user/import`, user, { headers: withAuthorization(token) });
};

export const getUserDegree = async (token: string): Promise<DegreeResponse> => {
  const degree = await axios.get(`user/data/degree`, { headers: withAuthorization(token) });
  return degree.data as DegreeResponse;
};

export const getUserIsSetup = async (token: string): Promise<boolean> => {
  const res = await axios.get<boolean>('/user/isSetup', {
    headers: withAuthorization(token)
  });

  return res.data;
};

export const getUserPlanner = async (token: string): Promise<PlannerResponse> => {
  const planner = await axios.get(`user/data/planner`, {
    headers: withAuthorization(token)
  });
  return planner.data as PlannerResponse;
};

export const getUserCourses = async (token: string): Promise<CoursesResponse> => {
  const courses = await axios.get(`user/data/courses`, {
    headers: withAuthorization(token)
  });
  return courses.data as CoursesResponse;
};

export const getUserSettings = async (token: string): Promise<SettingsResponse> => {
  const settings = await axios.get(`user/data/settings`, {
    headers: withAuthorization(token)
  });
  return settings.data as SettingsResponse;
};

export const toggleShowMarks = async (token: string): Promise<void> => {
  await axios.post(`user/settings/toggleShowMarks`, {}, { headers: withAuthorization(token) });
};

export const hideYear = async (token: string, yearIndex: number): Promise<void> => {
  await axios.post(`user/settings/hideYear`, { yearIndex }, { headers: withAuthorization(token) });
};

export const showYears = async (token: string): Promise<void> => {
  await axios.post(`user/settings/showYears`, {}, { headers: withAuthorization(token) });
};

export const resetUserDegree = async (token: string): Promise<void> => {
  await axios.post(`user/reset`, {}, { headers: withAuthorization(token) });
};

export const updateDegreeLength = async (token: string, numYears: number): Promise<void> => {
  await axios.put('/user/updateDegreeLength', { numYears }, { headers: withAuthorization(token) });
};

export const toggleSummerTerm = async (token: string): Promise<void> => {
  await axios.post('/user/toggleSummerTerm', {}, { headers: withAuthorization(token) });
};

export const updateStartYear = async (token: string, year: string): Promise<void> => {
  await axios.put(
    '/user/updateStartYear',
    { startYear: parseInt(year, 10) },
    { headers: withAuthorization(token) }
  );
};
