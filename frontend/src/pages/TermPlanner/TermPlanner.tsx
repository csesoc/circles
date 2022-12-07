import React, { Suspense, useEffect, useRef, useState } from 'react';
import type { OnDragEndResponder, OnDragStartResponder } from 'react-beautiful-dnd';
import { useDispatch, useSelector } from 'react-redux';
import { Badge } from 'antd';
import axios from 'axios';
import { ValidateTermPlanner } from 'types/api';
import { Term } from 'types/planner';
import getAllCourseOfferings from 'utils/getAllCourseOfferings';
import openNotification from 'utils/openNotification';
import prepareCoursesForValidationPayload from 'utils/prepareCoursesForValidationPayload';
import PageTemplate from 'components/PageTemplate';
import Spinner from 'components/Spinner';
import type { RootState } from 'config/store';
import {
  moveCourse,
  setPlannedCourseToTerm,
  setUnplannedCourseToTerm,
  toggleWarnings,
  unschedule,
  updateLegacyOfferings
} from 'reducers/plannerSlice';
import { GridItem } from './common/styles';
import HideYearTooltip from './HideYearTooltip';
import OptionsHeader from './OptionsHeader';
import S from './styles';
import TermBox from './TermBox';
import UnplannedColumn from './UnplannedColumn';
import { checkMultitermInBounds, isPlannerEmpty } from './utils';

const DragDropContext = React.lazy(() =>
  import('react-beautiful-dnd').then((plot) => ({ default: plot.DragDropContext }))
);

const TermPlanner = () => {
  const { showWarnings } = useSelector((state: RootState) => state.settings);
  const planner = useSelector((state: RootState) => state.planner);
  const degree = useSelector((state: RootState) => state.degree);

  const [draggingCourse, setDraggingCourse] = useState('');
  const [checkYearMultiTerm, setCheckYearMultiTerm] = useState('');
  const [multiCourse, setMultiCourse] = useState('');

  const dispatch = useDispatch();

  // needed for useEffect deps as it does not deep compare arrays well enough :c
  // also only want it to update on new/removed course codes
  const courses = Object.keys(planner.courses).sort().join('');

  useEffect(() => {
    // update the legacy term offered
    const updateOfferingsData = async () => {
      const years: string[] = [];
      for (let i = 0; i < planner.numYears; i++) {
        years.push((planner.startYear + i).toString());
      }

      // get the outdated legacy offerings
      const outdated = Object.entries(planner.courses)
        .filter(([, course]) => {
          const oldOfferings = course.legacyOfferings;
          // no legacy offering data, or doesn't include the wanted years
          return !oldOfferings || years.filter((y) => !(y in oldOfferings)).length > 0;
        })
        .map(([code]) => code);

      // update them
      const data = await getAllCourseOfferings(outdated, years);
      Object.entries(data).forEach(([code, offerings]) => {
        dispatch(updateLegacyOfferings({ code, offerings }));
      });
    };

    updateOfferingsData();

    // disabled planner.courses as part of useEffect dep to avoid api double calling
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courses, dispatch, planner.numYears, planner.startYear]);

  const payload = JSON.stringify(prepareCoursesForValidationPayload(planner, degree, showWarnings));
  const plannerEmpty = isPlannerEmpty(planner.years);
  useEffect(() => {
    const validateTermPlanner = async () => {
      try {
        const res = await axios.post<ValidateTermPlanner>('/planner/validateTermPlanner/', payload);
        dispatch(toggleWarnings(res.data.courses_state));
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Error at validateTermPlanner', err);
      }
    };

    if (plannerEmpty) {
      openNotification({
        type: 'info',
        message: 'Your terms are looking a little empty',
        description:
          'Add courses from the course selector to the term planner and drag courses from the unplanned column'
      });
    }
    validateTermPlanner();
  }, [payload, showWarnings, plannerEmpty, dispatch]);

  const currYear = new Date().getFullYear();

  /* Ref used for exporting planner to image */
  const plannerPicRef = useRef<HTMLDivElement>(null);

  const handleOnDragStart: OnDragStartResponder = (result) => {
    const course = result.draggableId.slice(0, 8);
    setDraggingCourse(course);
    if (planner.courses[course].isMultiterm) {
      setCheckYearMultiTerm(result.source.droppableId);
      setMultiCourse(course);
    }
  };

  const handleOnDragEnd: OnDragEndResponder = (result) => {
    setDraggingCourse('');
    setCheckYearMultiTerm('');
    setMultiCourse('');
    const { destination, source, draggableId: draggableIdUnique } = result;
    // draggableIdUnique contains course code + term (e.g. COMP151120T1)
    // draggableId only contains the course code (e.g. COMP1511)
    const draggableId = draggableIdUnique.slice(0, 8);

    if (!destination) return; // drag outside container

    if (destination.droppableId !== 'unplanned') {
      // Check if multiterm course extends below bottom row of term planner
      if (
        planner.courses[draggableId].isMultiterm &&
        !checkMultitermInBounds({
          destRow: Number(destination.droppableId.match(/[0-9]{4}/)?.[0]) - planner.startYear,
          destTerm: destination.droppableId.match(/T[0-3]/)?.[0] as Term,
          srcTerm: source.droppableId as Term,
          course: planner.courses[draggableId],
          isSummerTerm: planner.isSummerEnabled,
          numYears: planner.numYears
        })
      ) {
        openNotification({
          type: 'warning',
          message: 'Course would extend outside of the term planner',
          description: `Keep ${draggableId} inside the calendar by moving it to a different term instead`
        });
        return;
      }

      // === moving course to unplanned doesn't require term logic ===
      if (destination.droppableId !== source.droppableId) {
        dispatch(
          moveCourse({
            course: draggableId,
            destTerm: destination.droppableId,
            srcTerm: source.droppableId
          })
        );
      }
    }

    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      // drag to same place
      return;
    }

    const destIndex = destination.index;

    if (destination.droppableId === 'unplanned') {
      // === move course to unplanned ===
      dispatch(
        unschedule({
          destIndex,
          code: draggableId
        })
      );
      return;
    }

    const destYear = Number(destination.droppableId.match(/[0-9]{4}/)?.[0]);
    const destTerm = destination.droppableId.match(/T[0-3]/)?.[0] as Term;
    const destRow = destYear - planner.startYear;

    if (source.droppableId === 'unplanned') {
      // === move unplanned course to term ===
      dispatch(
        setUnplannedCourseToTerm({
          destRow,
          destTerm,
          destIndex,
          course: draggableId
        })
      );
    } else {
      // === move between terms ===
      const srcYear = parseInt(source.droppableId.match(/[0-9]{4}/)?.[0] as string, 10);
      const srcTerm = source.droppableId.match(/T[0-3]/)?.[0] as Term;
      const srcRow = srcYear - planner.startYear;
      const srcIndex = source.index;
      dispatch(
        setPlannedCourseToTerm({
          srcRow,
          srcTerm,
          srcIndex,
          destRow,
          destTerm,
          destIndex,
          course: draggableId
        })
      );
    }
  };

  return (
    <PageTemplate>
      <OptionsHeader plannerRef={plannerPicRef} />
      <S.ContainerWrapper>
        <Suspense fallback={<Spinner text="Loading Table..." />}>
          <DragDropContext onDragEnd={handleOnDragEnd} onDragStart={handleOnDragStart}>
            <S.PlannerContainer>
              <S.PlannerGridWrapper summerEnabled={planner.isSummerEnabled} ref={plannerPicRef}>
                <GridItem /> {/* Empty grid item for the year */}
                {planner.isSummerEnabled && <GridItem>Summer</GridItem>}
                <GridItem>Term 1</GridItem>
                <GridItem>Term 2</GridItem>
                <GridItem>Term 3</GridItem>
                {planner.years.map((year, index) => {
                  const iYear = planner.startYear + index;
                  let yearUOC = 0;
                  Object.keys(year).forEach((termKey) => {
                    Object.keys(planner.courses).forEach((courseCode) => {
                      if (year[termKey as Term].includes(courseCode)) {
                        yearUOC += planner.courses[courseCode].UOC;
                      }
                    });
                  });
                  if (planner.hidden[iYear]) return null;
                  return (
                    <React.Fragment key={iYear}>
                      <S.YearGridBox>
                        <S.YearWrapper>
                          <S.YearText currYear={currYear === iYear}>{iYear}</S.YearText>
                          <HideYearTooltip year={iYear} />
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
                        return (
                          <TermBox
                            key={key}
                            name={key}
                            coursesList={year[term as Term]}
                            draggingCourse={!draggingCourse ? undefined : draggingCourse}
                            currMultiCourseDrag={checkYearMultiTerm === key ? multiCourse : ''}
                          />
                        );
                      })}
                    </React.Fragment>
                  );
                })}
                <UnplannedColumn dragging={!!draggingCourse} />
              </S.PlannerGridWrapper>
            </S.PlannerContainer>
          </DragDropContext>
        </Suspense>
      </S.ContainerWrapper>
    </PageTemplate>
  );
};

export default TermPlanner;
