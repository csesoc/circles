import React, { useEffect, useRef, useState } from 'react';
import type { OnDragEndResponder, OnDragStartResponder } from 'react-beautiful-dnd';
import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query';
import { Badge } from 'antd';
import { Course } from 'types/api';
import { PlannedToTerm, Term, UnPlannedToTerm, UnscheduleCourse } from 'types/planner';
import {
  badCourseInfo,
  badCourses,
  badPlanner,
  badValidations,
  CoursesResponse,
  PlannerResponse,
  ValidatesResponse
} from 'types/userResponse';
import { getCourseForYearsInfo } from 'utils/api/coursesApi';
import {
  setPlannedCourseToTerm,
  setUnplannedCourseToTerm,
  unscheduleCourse,
  validateTermPlanner
} from 'utils/api/plannerApi';
import { getUserCourses, getUserPlanner } from 'utils/api/userApi';
import openNotification from 'utils/openNotification';
import PageTemplate from 'components/PageTemplate';
import Spinner from 'components/Spinner';
import { LIVE_YEAR } from 'config/constants';
import useToken from 'hooks/useToken';
import { GridItem } from './common/styles';
import OptionsHeader from './OptionsHeader';
import S from './styles';
import TermBox from './TermBox';
import UnplannedColumn from './UnplannedColumn';
import { isPlannerEmpty } from './utils';

const DragDropContext = React.lazy(() =>
  import('react-beautiful-dnd').then((plot) => ({ default: plot.DragDropContext }))
);

const extrapolateCourseYears = (
  data: Record<number, Course>,
  validYears: number[]
): Record<number, Course> => {
  const newData = { ...data };
  let bestYear = validYears.find((year) => !!data[year]) ?? LIVE_YEAR;

  validYears.forEach((year) => {
    if (newData[year]) bestYear = year;
    else newData[year] = { ...newData[bestYear], terms: [] };
  });

  return newData;
};

const badCourseYears = (code: string, validYears: number[]): Record<number, Course> =>
  Object.fromEntries(validYears.map((year) => [year, { ...badCourseInfo, code }]));

// purposefully verbose typing
type CodeToCourseYearsMap = { [code: string]: { [year: number]: Course } };
type YearToCoursesMap = { [year: number]: { [code: string]: Course } };

const TermPlanner = () => {
  const token = useToken();
  const [draggingCourse, setDraggingCourse] = useState('');
  const queryClient = useQueryClient();
  const plannerPicRef = useRef<HTMLDivElement>(null);

  // Planer obj
  const plannerQuery = useQuery({
    queryKey: ['planner'],
    queryFn: () => getUserPlanner(token)
  });
  const planner: PlannerResponse = plannerQuery.data ?? badPlanner;

  // The user's actual courses obj???????
  const coursesQuery = useQuery({
    queryKey: ['courses'],
    queryFn: () => getUserCourses(token)
  });
  const courses: CoursesResponse = coursesQuery.data ?? badCourses;

  const validateQuery = useQuery({
    queryKey: ['validate'],
    queryFn: () => validateTermPlanner(token)
  });
  const validations: ValidatesResponse = validateQuery.data ?? badValidations;

  const validYears = [...Array(planner.years.length).keys()].map((y) => y + planner.startYear);

  // comes in as an { [year]: course }[], which gets auto extrapolated, also preseeded with bad data
  const courseQueries = useQueries({
    queries: Object.keys(courses).map((code: string) => ({
      queryKey: ['course', code, { years: validYears }],
      queryFn: () =>
        getCourseForYearsInfo(
          code,
          validYears.filter((year) => year < LIVE_YEAR)
        ),
      select: (data: Record<number, Course>) => extrapolateCourseYears(data, validYears),
      placeholderData: badCourseYears(code, validYears)
    }))
  });

  // transform the course info data into usable shapes
  const courseInfoFlipped: CodeToCourseYearsMap = Object.fromEntries(
    Object.keys(courses).map((code, index) => [code, courseQueries[index].data!])
  );

  const courseInfos: YearToCoursesMap = Object.fromEntries(
    validYears.map((year) => [
      year,
      Object.fromEntries(
        Object.entries(courseInfoFlipped).map(([code, courseYears]) => [code, courseYears[year]])
      )
    ])
  );

  // Mutations
  const setPlannedCourseToTermMutation = useMutation({
    mutationFn: (data: PlannedToTerm) => setPlannedCourseToTerm(token, data),
    onMutate: (data) => {
      queryClient.setQueryData(['planner'], (prev: PlannerResponse | undefined) => {
        if (!prev) return badPlanner;
        const curr: PlannerResponse = structuredClone(prev);
        curr.years[data.srcRow][data.srcTerm].splice(
          curr.years[data.srcRow][data.srcTerm].indexOf(data.courseCode),
          1
        );
        curr.years[data.destRow][data.destTerm].splice(data.destIndex, 0, data.courseCode);
        return curr;
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['planner']
      });
      queryClient.invalidateQueries({
        queryKey: ['courses']
      });
      queryClient.invalidateQueries({
        queryKey: ['validate']
      });
    },
    onError: (err) => {
      // eslint-disable-next-line no-console
      console.error('Error at setPlannedCourseToTermMutation: ', err);
    }
  });

  const handleSetPlannedCourseToTerm = async (data: PlannedToTerm) => {
    setPlannedCourseToTermMutation.mutate(data);
  };

  const setUnplannedCourseToTermMutation = useMutation({
    mutationFn: (data: UnPlannedToTerm) => setUnplannedCourseToTerm(token, data),
    onMutate: (data) => {
      queryClient.setQueryData(['planner'], (prev: PlannerResponse | undefined) => {
        if (!prev) return badPlanner;
        const curr: PlannerResponse = structuredClone(prev);
        curr.unplanned.splice(curr.unplanned.indexOf(data.courseCode), 1);
        curr.years[data.destRow][data.destTerm].splice(data.destIndex, 0, data.courseCode);
        return curr;
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['planner']
      });
      queryClient.invalidateQueries({
        queryKey: ['courses']
      });
      queryClient.invalidateQueries({
        queryKey: ['validate']
      });
    },
    onError: (err) => {
      // eslint-disable-next-line no-console
      console.error('Error at setUnplannedCourseToTermMutation: ', err);
    }
  });

  const handleSetUnplannedCourseToTerm = async (data: UnPlannedToTerm) => {
    setUnplannedCourseToTermMutation.mutate(data);
  };

  const unscheduleCourseMutation = useMutation({
    mutationFn: (data: UnscheduleCourse) => unscheduleCourse(token, data),
    onMutate: (data) => {
      queryClient.setQueryData(['planner'], (prev: PlannerResponse | undefined) => {
        if (!prev) return badPlanner;
        const curr: PlannerResponse = structuredClone(prev);
        curr.years[data.srcRow as number][data.srcTerm as string].splice(
          curr.years[data.srcRow as number][data.srcTerm as string].indexOf(data.courseCode),
          1
        );
        curr.unplanned.push(data.courseCode);
        return curr;
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['planner']
      });
      queryClient.invalidateQueries({
        queryKey: ['courses']
      });
      queryClient.invalidateQueries({
        queryKey: ['validate']
      });
    },
    onError: (err) => {
      // eslint-disable-next-line no-console
      console.error('Error at unscheduleCourseMutation: ', err);
    }
  });

  const handleUnscheduleCourse = async (data: UnscheduleCourse) => {
    unscheduleCourseMutation.mutate(data);
  };

  const plannerEmpty = isPlannerEmpty(planner);
  useEffect(() => {
    if (plannerEmpty) {
      openNotification({
        type: 'info',
        message: 'Your terms are looking a little empty',
        description:
          'Add courses from the course selector to the term planner and drag courses from the unplanned column'
      });
    }
  }, [plannerEmpty]);

  const handleOnDragStart: OnDragStartResponder = async (result) => {
    const courseCode = result.draggableId.slice(0, 8);
    setDraggingCourse(courseCode);
  };

  const handleOnDragEnd: OnDragEndResponder = async (result) => {
    setDraggingCourse('');
    const { destination, source, draggableId: draggableIdUnique } = result;
    // draggableIdUnique contains course code + term (e.g. COMP151120T1)
    // draggableId only contains the course code (e.g. COMP1511)
    const draggableId = draggableIdUnique.slice(0, 8);

    if (!destination) return; // drag outside container

    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      // drag to same place
      return;
    }

    const destIndex = destination.index;

    if (destination.droppableId === 'unplanned') {
      const srcYear = parseInt(source.droppableId.match(/[0-9]{4}/)?.[0] as string, 10);
      const srcTerm = source.droppableId.match(/T[0-3]/)?.[0] as Term;
      const srcRow = srcYear - planner.startYear;
      handleUnscheduleCourse({
        srcRow,
        srcTerm,
        courseCode: draggableId
      });
      return;
    }
    if (source.droppableId === 'unplanned') {
      const destYear = Number(destination.droppableId.match(/[0-9]{4}/)?.[0]);
      const destTerm = destination.droppableId.match(/T[0-3]/)?.[0] as Term;
      const destRow = destYear - planner.startYear;
      // === move unplanned course to term ===
      const data = {
        destRow,
        destTerm,
        destIndex,
        courseCode: draggableId
      };
      handleSetUnplannedCourseToTerm(data);
    } else {
      const srcYear = parseInt(source.droppableId.match(/[0-9]{4}/)?.[0] as string, 10);
      const srcTerm = source.droppableId.match(/T[0-3]/)?.[0] as Term;
      const srcRow = srcYear - planner.startYear;
      const destYear = Number(destination.droppableId.match(/[0-9]{4}/)?.[0]);
      const destTerm = destination.droppableId.match(/T[0-3]/)?.[0] as Term;
      const destRow = destYear - planner.startYear;
      // === move between terms ===
      const data = {
        srcRow,
        srcTerm,
        destRow,
        destTerm,
        destIndex,
        courseCode: draggableId
      };
      handleSetPlannedCourseToTerm(data);
    }
  };

  return (
    <PageTemplate>
      <OptionsHeader />
      <S.ContainerWrapper>
        {
          // TODO: Fix Suspense by updating to react-query v5
          /* <Suspense fallback={<Spinner text="Loading Table..." />}> */
        }
        {plannerQuery.isPending ||
        coursesQuery.isPending ||
        courseQueries.some((c) => c.isPlaceholderData) ? (
          <Spinner text="Loading Table..." />
        ) : (
          <DragDropContext onDragEnd={handleOnDragEnd} onDragStart={handleOnDragStart}>
            <S.PlannerContainer>
              <S.PlannerGridWrapper $summerEnabled={planner.isSummerEnabled} ref={plannerPicRef}>
                <GridItem /> {/* Empty grid item for the year */}
                {planner.isSummerEnabled && <GridItem>Summer</GridItem>}
                <GridItem>Term 1</GridItem>
                <GridItem>Term 2</GridItem>
                <GridItem>Term 3</GridItem>
                {planner.years.map((year, index) => {
                  // TODO: move this out
                  const iYear = planner.startYear + index;
                  let yearUOC = 0;
                  Object.keys(year).forEach((termKey) => {
                    Object.entries(courseInfoFlipped).forEach(([courseCode, courseInfo]) => {
                      if (year[termKey as Term].includes(courseCode)) {
                        yearUOC += courseInfo[iYear].UOC;
                      }
                    });
                  });

                  return (
                    <React.Fragment key={iYear}>
                      <S.YearGridBox>
                        <S.YearWrapper>
                          <S.YearText $currYear={LIVE_YEAR === iYear}>{iYear}</S.YearText>
                        </S.YearWrapper>
                        <Badge
                          style={{
                            backgroundColor: '#efdbff',
                            color: '#000000'
                          }}
                          size="small"
                          count={`${yearUOC} UOC`}
                        />
                      </S.YearGridBox>
                      {Object.keys(year).map((term) => {
                        const key = `${iYear}${term}`;
                        if (!planner.isSummerEnabled && term === 'T0') return null;
                        const codesForThisTerm = year[term];
                        // TODO: probs map this at TOP-LEVEL
                        const courseInfoForThisTerm = Object.fromEntries(
                          codesForThisTerm.map((code) => [code, courseInfos[iYear][code]])
                        );
                        return (
                          <TermBox
                            key={key}
                            name={key}
                            courseInfos={courseInfos[iYear]}
                            validateInfos={validations.courses_state}
                            termCourseInfos={courseInfoForThisTerm}
                            termCourseCodes={codesForThisTerm}
                            draggingCourseCode={!draggingCourse ? undefined : draggingCourse}
                          />
                        );
                      })}
                    </React.Fragment>
                  );
                })}
                <UnplannedColumn
                  dragging={!!draggingCourse}
                  courseInfos={Object.fromEntries(
                    planner.unplanned.map((code) => [code, courseInfos[LIVE_YEAR][code]])
                  )}
                  validateInfos={validations.courses_state}
                />
              </S.PlannerGridWrapper>
            </S.PlannerContainer>
          </DragDropContext>
        )}
        {/* </Suspense> */}
      </S.ContainerWrapper>
    </PageTemplate>
  );
};

export default TermPlanner;
