import {
  CourseResponse,
  DegreeResponse,
  PlannerResponse,
  SettingsResponse,
  UserResponse
} from 'types/userResponse';
import { z } from 'zod';

// CoursesResponse does NOT match the db, nor is it minimal
type ExportedCourse = Pick<CourseResponse, 'mark' | 'ignoreFromProgression'>;

export type UserJson = {
  settings: SettingsResponse;
  degree: DegreeResponse;
  planner: PlannerResponse;
  courses: Record<string, ExportedCourse>;
};

const settingsSchema = z.strictObject({
  showMarks: z.boolean(),
  hiddenYears: z.array(z.number().int().nonnegative())
});

const degreeSchema = z.strictObject({
  programCode: z.string().length(4),
  specs: z.array(z.string())
});

const plannerSchema = z.strictObject({
  unplanned: z.array(z.string().length(8)),
  startYear: z.number().int().gte(2019),
  isSummerEnabled: z.boolean(),
  lockedTerms: z.record(z.string(), z.boolean()),
  years: z.array(z.record(z.string(), z.array(z.string().length(8))))
});

const courseSchema = z.strictObject({
  mark: z
    .union([z.number().nonnegative().int(), z.enum(['SY', 'FL', 'PS', 'CR', 'DN', 'HD'])])
    .nullable(),
  ignoreFromProgression: z.boolean()
});

const exportOutputSchema = z.strictObject({
  settings: settingsSchema,
  degree: degreeSchema,
  planner: plannerSchema,
  courses: z.record(z.string().length(8), courseSchema)
});

export const exportUser = (user: UserResponse): UserJson => {
  const courses: UserJson['courses'] = Object.fromEntries(
    Object.entries(user.courses).map(([code, course]) => [
      code,
      {
        mark: course.mark,
        ignoreFromProgression: course.ignoreFromProgression
      }
    ])
  );

  return {
    settings: user.settings,
    degree: user.degree,
    planner: user.planner,
    courses
  };
};

export const importUser = (data: JSON): UserJson => {
  const parsed = exportOutputSchema.safeParse(data);
  if (!parsed.success || parsed.data === undefined) {
    parsed.error.errors.forEach((err) => {
      // eslint-disable-next-line no-console
      console.error(err.message);
    });
    throw new Error('Invalid data');
  }

  return parsed.data;
};
