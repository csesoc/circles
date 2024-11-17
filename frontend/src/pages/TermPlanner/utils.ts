import { Grade, Mark, PlannerCourse, Term } from 'types/planner';
import { PlannerResponse } from 'types/userResponse';
import getNumTerms from 'utils/getNumTerms';

const parseMarkToInt = (mark: Mark): number | null => {
  if (typeof mark === 'undefined') return null;
  if (typeof mark === 'string') {
    const letterGradeToIntMap: Record<Grade, number | null> = {
      SY: null,
      FL: 25,
      PS: 55,
      CR: 70,
      DN: 80,
      HD: 90
    };
    return Object.keys(letterGradeToIntMap).includes(mark) ? letterGradeToIntMap[mark] : null;
  }
  return mark;
};

// Checks if no courses have been planned
const isPlannerEmpty = (planner: PlannerResponse) => {
  return planner.years.every((year) =>
    Object.keys(year).every((term) => year[term as Term].length === 0)
  );
};

// Returns a list of terms and rowOffsets that multiterm course will be added to
const getTermsList = (
  currentTerm: Term,
  uoc: number,
  availableTerms: Term[],
  isSummerTerm: boolean,
  instanceNum: number
) => {
  const allTerms = ['T1', 'T2', 'T3'];
  const termsList = [];

  if (isSummerTerm) allTerms.unshift('T0');

  // Remove any unavailable terms
  const terms = allTerms.filter((term) => availableTerms.includes(term as Term)) as Term[];

  let index = terms.indexOf(currentTerm) - 1;
  let rowOffset = 0;
  const numTerms = getNumTerms(uoc, true);

  for (let i = 0; i < instanceNum; i++) {
    if (index < 0) {
      index = terms.length - 1;
      rowOffset -= 1;
    }

    termsList.unshift({
      term: terms[(index + terms.length) % 3],
      rowOffset
    });

    index -= 1;
  }

  rowOffset = 0;
  index = terms.indexOf(currentTerm);

  for (let i = instanceNum; i < numTerms; i++) {
    if (index === terms.length) {
      index = 0;
      rowOffset += 1;
    }

    termsList.push({
      term: terms[index],
      rowOffset
    });

    index += 1;
  }

  return termsList;
};

// Checks whether multiterm course will extend below bottom row of term planner
type MultitermInBoundsPayload = {
  srcTerm: Term | 'unplanned';
  destTerm: Term;
  destRow: number;
  course: PlannerCourse;
  isSummerTerm: boolean;
  numYears: number;
};

const checkMultitermInBounds = (payload: MultitermInBoundsPayload) => {
  const { destTerm, course, isSummerTerm, destRow, numYears, srcTerm } = payload;

  const { UOC: uoc, termsOffered, plannedFor } = course;

  if (!termsOffered.includes(destTerm)) {
    return false;
  }

  const instanceNum =
    srcTerm === 'unplanned' || !plannedFor ? 0 : plannedFor.split(' ').indexOf(srcTerm);
  const termsList = getTermsList(destTerm, uoc, termsOffered, isSummerTerm, instanceNum);

  const { rowOffset: maxRowOffset } = termsList[termsList.length - 1];
  const { rowOffset: minRowOffset } = termsList[0];

  return maxRowOffset < numYears - destRow && minRowOffset + destRow >= 0;
};

export { checkMultitermInBounds, getNumTerms, getTermsList, isPlannerEmpty, parseMarkToInt };
