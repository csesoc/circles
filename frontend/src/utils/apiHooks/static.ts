import { getCourseRating } from 'utils/api/unilectivesApi';
import { createStaticQueryHook } from './hookHelpers';

export const useCourseRatingQuery = createStaticQueryHook<
  ['courseRating', string],
  [string],
  Awaited<ReturnType<typeof getCourseRating>>
>((code) => ['courseRating', code], getCourseRating);

export const x = 100;
