import { Term } from './planner';

export type CourseCodes = {
  [courseKey: string]: string;
};

export type CourseList = string[];

export type CourseValidation = {
  is_accurate: boolean;
  unlocked: boolean;
  handbook_note: string;
  warnings: string[];
};

export type CourseUnlocks = {
  direct_unlock: CourseList;
  indirect_unlock: CourseList;
};

export type CourseStates = {
  [courseKey: string]: {
    handbook_note: string;
    is_accurate: boolean;
    unlocked: boolean;
    warnings: string[];
  };
};

export type CourseTime = {
  year: string;
  term: Term;
};
