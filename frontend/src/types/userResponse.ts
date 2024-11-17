import { Course } from './api';
import { Mark } from './planner';

export type UserResponse = {
  degree: DegreeResponse;
  planner: PlannerResponse;
  courses: Record<string, CourseResponse>;
  settings: SettingsResponse;
};

export type DegreeResponse = {
  programCode: string;
  specs: string[];
};

export type CourseResponse = {
  code: string;
  mark: Mark;
  plannedFor: string | null;
  title: string;
  isMultiterm: boolean;
  uoc: number;
  ignoreFromProgression: boolean;
};
export type CoursesResponse = Record<string, CourseResponse>;

export type SettingsResponse = {
  showMarks: boolean;
  hiddenYears: number[];
};

export type ValidateResponse = {
  is_accurate: boolean;
  handbook_note: string;
  unlocked: boolean;
  warnings: string[];
};

export type ValidatesResponse = {
  courses_state: Record<string, ValidateResponse>;
};

export type PlannerResponse = {
  unplanned: string[];
  startYear: number;
  isSummerEnabled: boolean;
  lockedTerms: Record<string, boolean>;
  // TODO: Type this better somehow
  years: Record<string, string[]>[];
};

export type Term = {
  Y: string;
  T: string;
};

export const badDegree: DegreeResponse = {
  programCode: '3778',
  specs: []
};

// null coalesced to remove `undefined`. This SHOULD NOT see production
// temp fix while we wait for `prepareUserPayload` to be deprecated
export const badPlanner: PlannerResponse = {
  unplanned: [],
  startYear: 2021,
  isSummerEnabled: false,
  lockedTerms: {},
  years: []
};

export const badValidations: ValidatesResponse = {
  courses_state: {}
};

export const badCourseInfo: Course = {
  title: '',
  code: '',
  UOC: 0,
  description: '',
  study_level: '',
  school: '',
  campus: '',
  raw_requirements: '',
  terms: [],
  is_legacy: false,
  is_accurate: false,
  is_multiterm: false,
  handbook_note: ''
};

export const badCourses: Record<string, CourseResponse> = {};

export const badUser = {
  degree: badDegree,
  planner: badPlanner,
  courses: badCourses
} as UserResponse;
