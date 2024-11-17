import React, { Suspense } from 'react';
import { useContextMenu } from 'react-contexify';
import { Tooltip as ReactTooltip } from 'react-tooltip';
import { InfoCircleOutlined, PieChartOutlined, WarningOutlined } from '@ant-design/icons';
import { Typography } from 'antd';
import { useTheme } from 'styled-components';
import { Course } from 'types/api';
import { CourseTime } from 'types/courses';
import { CoursesResponse, PlannerResponse, ValidateResponse } from 'types/userResponse';
import { courseHasOffering } from 'utils/getAllCourseOfferings';
import getMostRecentPastTerm from 'utils/getMostRecentPastTerm';
import Spinner from 'components/Spinner';
import useMediaQuery from 'hooks/useMediaQuery';
import useSettings from 'hooks/useSettings';
import ContextMenu from '../ContextMenu';
import S from './styles';

type Props = {
  planner: PlannerResponse;
  courses: CoursesResponse;
  validate?: ValidateResponse;
  courseInfo: Course;
  index: number;
  time?: CourseTime;
};

const Draggable = React.lazy(() =>
  import('react-beautiful-dnd').then((plot) => ({ default: plot.Draggable }))
);

const DraggableCourse = ({ planner, validate, courses, courseInfo, index, time }: Props) => {
  const { isSummerEnabled } = planner;
  const { showMarks, showPastWarnings } = useSettings();
  const theme = useTheme();
  const { Text } = Typography;

  const courseIsPastTerm = (t: CourseTime): boolean => {
    const mostRecentPastTerm = getMostRecentPastTerm(planner.startYear);
    const courseYear = parseInt(t.year, 10) - planner.startYear + 1;
    const courseTerm = parseInt(t.term.slice(1), 10);
    return (
      courseYear < mostRecentPastTerm.Y ||
      (courseYear === mostRecentPastTerm.Y && courseTerm <= mostRecentPastTerm.T)
    );
  };

  // If the user has asked to ignore warnings for past terms, check if the course is in a past term
  const ignoreWarnings = time && !showPastWarnings && courseIsPastTerm(time);

  // prereqs are populated in CourseDescription.jsx via course.raw_requirements
  const { title, code } = courseInfo;
  // TODO: Change the backend so that naming is universally in camelCase so we don't have to do this
  const { is_legacy: isLegacy, handbook_note: handbookNote } = courseInfo;
  const {
    is_accurate: isAccurate,
    unlocked: isUnlocked,
    warnings: warningMessage
  } = validate || {
    is_accurate: true,
    warnings: [],
    unlocked: true,
    handbook_note: ''
  };

  const hasOffering = time ? courseHasOffering(courseInfo, time.term) : true;

  const contextMenu = useContextMenu({
    id: `${code}-context`
  });

  const BEwarnings = handbookNote || warningMessage.length !== 0;

  const isTermLocked = time ? planner.lockedTerms[`${time.year}${time.term}`] ?? false : false;

  const isSmall = useMediaQuery('(max-width: 1400px)');
  // TODO: Fix these boolean checks for warnings
  const shouldHaveWarning =
    !ignoreWarnings && (isLegacy || !isUnlocked || BEwarnings || !isAccurate || !hasOffering);
  const errorIsInformational =
    shouldHaveWarning &&
    isUnlocked &&
    warningMessage.length === 0 &&
    !isLegacy &&
    isAccurate &&
    hasOffering;

  const handleContextMenu = (e: React.MouseEvent) => {
    if (!isTermLocked) contextMenu.show({ event: e });
  };

  const stripExtraParenthesis = (warning: string): string => {
    if (warning[0] !== '(' || warning[warning.length - 1] !== ')') {
      return warning;
    }
    let openParenCount = 0;
    // If first open brace is ever fully closed, we don't want to strip them out
    for (let i = 0; i < warning.length - 1; i += 1) {
      if (warning[i] === '(') {
        openParenCount += 1;
      } else if (warning[i] === ')') {
        openParenCount -= 1;
      }
      if (openParenCount <= 0) {
        return warning;
      }
    }
    return stripExtraParenthesis(warning.slice(1, warning.length - 1));
  };

  return (
    <>
      <Suspense fallback={<Spinner text="Loading Course..." />}>
        <Draggable
          isDragDisabled={isTermLocked}
          draggableId={`${code}${time?.term ?? 'unplanned'}`}
          index={index}
        >
          {(provided) => (
            <S.CourseWrapper
              $summerEnabled={isSummerEnabled}
              $isSmall={isSmall}
              $dragDisabled={isTermLocked}
              $warningsDisabled={isTermLocked && !isUnlocked}
              $isWarning={!ignoreWarnings && (!isUnlocked || !hasOffering)}
              {...provided.draggableProps}
              {...provided.dragHandleProps}
              ref={provided.innerRef}
              style={provided.draggableProps.style}
              data-tip
              data-for={code}
              id={code}
              onContextMenu={handleContextMenu}
            >
              {!isTermLocked &&
                shouldHaveWarning &&
                (errorIsInformational ? (
                  <InfoCircleOutlined style={{ color: theme.infoOutlined.color }} />
                ) : (
                  <WarningOutlined
                    style={{ fontSize: '16px', color: theme.warningOutlined.color }}
                  />
                ))}
              {courses[code].ignoreFromProgression && (
                <PieChartOutlined style={{ color: theme.infoOutlined.color }} />
              )}
              <S.CourseLabel>
                {isSmall ? (
                  <Text className="text">{code}</Text>
                ) : (
                  <div>
                    <Text className="text">
                      <strong>{code}: </strong>
                      {title}
                    </Text>
                  </div>
                )}
                {showMarks && (
                  <div>
                    <Text strong className="text">
                      Mark:&nbsp;
                    </Text>
                    <Text className="text">
                      {/*
                          Marks can be strings (i.e. HD, CR) or a number (i.e. 90, 85).
                          Mark can be 0.
                        */}
                      {courses[code]?.mark || courses[code]?.mark === 0
                        ? courses[code].mark
                        : 'N/A'}
                    </Text>
                  </div>
                )}
              </S.CourseLabel>
            </S.CourseWrapper>
          )}
        </Draggable>
      </Suspense>
      <ContextMenu
        code={code}
        ignoreFromProgression={courses[code].ignoreFromProgression}
        plannedFor={courses[code].plannedFor}
      />
      {/* display prereq tooltip for all courses. However, if a term is marked as complete
        and the course has no warning, then disable the tooltip */}
      {isSmall && (
        <ReactTooltip anchorSelect={`#${code}`} place="top" style={{ zIndex: 10 }}>
          {title}
        </ReactTooltip>
      )}
      {!isTermLocked && shouldHaveWarning && (
        <ReactTooltip anchorSelect={`#${code}`} place="bottom" style={{ zIndex: 10 }}>
          {isLegacy ? (
            'This course is discontinued. If an equivalent course is currently being offered, please pick that instead.'
          ) : !hasOffering ? (
            'The course is not offered in this term.'
          ) : warningMessage.length !== 0 ? (
            stripExtraParenthesis(warningMessage.join('\n'))
          ) : (
            // eslint-disable-next-line react/no-danger -- TODO: we really should remove this when we figure out better formatting strings
            <div dangerouslySetInnerHTML={{ __html: handbookNote }} />
          )}
          {/* TODO: Fix fullstops. example: "48 UoC required in all courses you have 36 This course will not be included ..."
           */}
          {!isAccurate ? ' The course info may be inaccurate.' : ''}
          {courses[code].ignoreFromProgression
            ? ' This course will not be included in your progression.'
            : ''}
        </ReactTooltip>
      )}
    </>
  );
};

export default DraggableCourse;
