import React, { Suspense } from 'react';
import { LockFilled, UnlockFilled } from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Badge } from 'antd';
import { useTheme } from 'styled-components';
import { Course } from 'types/api';
import { CourseTime } from 'types/courses';
import { Term } from 'types/planner';
import { ValidateResponse } from 'types/userResponse';
import { toggleLockTerm } from 'utils/api/plannerApi';
import { useUserCourses, useUserPlanner } from 'utils/apiHooks/user';
import { courseHasOffering } from 'utils/getAllCourseOfferings';
import Spinner from 'components/Spinner';
import useMediaQuery from 'hooks/useMediaQuery';
import useToken from 'hooks/useToken';
import DraggableCourse from '../DraggableCourse';
import S from './styles';

const Droppable = React.lazy(() =>
  import('react-beautiful-dnd').then((plot) => ({ default: plot.Droppable }))
);

type Props = {
  name: string; // Ideally replace this with a proper term type later
  courseInfos: Record<string, Course>; // All courses in planner
  validateInfos: Record<string, ValidateResponse>; // All courses in planner
  termCourseInfos: Record<string, Course>; // All courses in term
  termCourseCodes: string[]; // Course codes in the current term
  draggingCourseCode?: string;
};

const TermBox = ({
  name,
  courseInfos,
  validateInfos,
  termCourseInfos,
  termCourseCodes,
  draggingCourseCode
}: Props) => {
  const token = useToken();
  const year = name.slice(0, 4);
  const term = name.match(/T[0-3]/)?.[0] as Term;
  const theme = useTheme();
  const queryClient = useQueryClient();

  const plannerQuery = useUserPlanner();

  const toggleLockTermMutation = useMutation({
    mutationFn: () => toggleLockTerm(token, year, term),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['planner']
      });
    },
    onError: (err) => {
      // eslint-disable-next-line no-console
      console.error('Error at toggleLockTermMutation: ', err);
    }
  });

  const coursesQuery = useUserCourses();
  const isSmall = useMediaQuery('(max-width: 1400px)');

  if (!coursesQuery.data || !plannerQuery.data) {
    return <div>loading page...</div>;
  }
  const planner = plannerQuery.data;
  const { isSummerEnabled } = planner;
  const courses = coursesQuery.data;

  const handleToggleLockTerm = async () => {
    toggleLockTermMutation.mutate();
  };

  const termUOC = termCourseCodes.reduce((acc, code) => acc + termCourseInfos[code].UOC, 0);

  const isLocked: boolean = planner.lockedTerms[`${year}${term}`] ?? false;
  const offeredInTerm =
    !!draggingCourseCode && courseHasOffering(courseInfos[draggingCourseCode], term);
  const isOffered = offeredInTerm && !isLocked;

  const iconStyle = {
    fontSize: '12px',
    color: theme.termCheckbox.color
  };

  const uocBadgeStyle = {
    backgroundColor: theme.uocBadge.backgroundColor,
    boxShadow: 'none'
  };
  return (
    <Suspense fallback={<Spinner text="Loading Term..." />}>
      <Droppable droppableId={name} isDropDisabled={isLocked}>
        {(provided) => (
          <Badge
            count={
              <S.TermCheckboxWrapper $checked={isLocked}>
                {!isLocked ? (
                  <UnlockFilled style={iconStyle} onClick={handleToggleLockTerm} />
                ) : (
                  <LockFilled style={iconStyle} onClick={handleToggleLockTerm} />
                )}
              </S.TermCheckboxWrapper>
            }
            offset={isSummerEnabled ? [-13, 13] : [-22, 22]}
            styles={{ root: { width: 'unset' } }}
          >
            <S.TermBoxWrapper
              $droppable={isOffered && !!draggingCourseCode}
              $summerEnabled={isSummerEnabled}
              $isSmall={isSmall}
              ref={provided.innerRef}
              {...provided.droppableProps}
            >
              {Object.values(termCourseInfos).map((info, index) => {
                return (
                  <DraggableCourse
                    key={`${info.title || ''}${term}`}
                    planner={planner}
                    courses={courses}
                    validate={validateInfos[info.code]}
                    courseInfo={info}
                    index={index}
                    time={{ year, term } as CourseTime}
                  />
                );
              })}
              {provided.placeholder}
              <S.UOCBadgeWrapper>
                <Badge
                  style={uocBadgeStyle}
                  size="small"
                  count={`${termUOC} UOC`}
                  offset={[0, 0]}
                />
              </S.UOCBadgeWrapper>
            </S.TermBoxWrapper>
          </Badge>
        )}
      </Droppable>
    </Suspense>
  );
};

export default TermBox;
