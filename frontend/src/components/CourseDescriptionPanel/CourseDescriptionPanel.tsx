import React from 'react';
import { useLocation } from 'react-router-dom';
import { Typography } from 'antd';
import { CoursesResponse } from 'types/userResponse';
import {
  useCourseInfoQuery,
  useCoursePrereqsQuery,
  useCourseTimetableQuery
} from 'utils/apiHooks/static';
import { useUserCoursesUnlockedWhenTaken } from 'utils/apiHooks/user';
import getEnrolmentCapacity from 'utils/getEnrolmentCapacity';
import {
  LoadingCourseDescriptionPanel,
  LoadingCourseDescriptionPanelSidebar
} from 'components/LoadingSkeleton';
import PlannerButton from 'components/PlannerButton';
import CourseAttributes from './CourseAttributes';
import CourseInfoDrawers from './CourseInfoDrawers';
import S from './styles';

const { Title, Text } = Typography;

type CourseDescriptionPanelProps = {
  className?: string;
  courseCode: string;
  onCourseClick?: (code: string) => void;
  courses?: CoursesResponse;
};

const CourseDescriptionPanel = ({
  className,
  courseCode,
  onCourseClick,
  courses
}: CourseDescriptionPanelProps) => {
  const { pathname } = useLocation();
  const sidebar = pathname === '/course-selector';

  const coursesUnlockedQuery = useUserCoursesUnlockedWhenTaken({}, courseCode);

  const courseQuery = useCourseInfoQuery({}, courseCode);
  const coursePrereqsQuery = useCoursePrereqsQuery({}, courseCode);
  const courseCapacityQuery = useCourseTimetableQuery(
    { queryOptions: { select: getEnrolmentCapacity, retry: 1, enabled: sidebar } }, // retry only once because we have bad error handling
    courseCode
  );

  const loadingWrapper = (
    <S.Wrapper $sidebar={sidebar}>
      {!sidebar ? <LoadingCourseDescriptionPanelSidebar /> : <LoadingCourseDescriptionPanel />}
    </S.Wrapper>
  );

  if (
    courseQuery.isPending ||
    coursePrereqsQuery.isPending ||
    (sidebar && courseCapacityQuery.isPending)
  )
    return loadingWrapper;

  const course = courseQuery.data;
  const coursesPathFrom = coursePrereqsQuery.data?.courses;
  const courseCapacity = courseCapacityQuery.data;

  // course wasn't fetchable (fatal; should do proper error handling instead of indefinitely loading)
  if (!course) return loadingWrapper;
  return (
    <S.Wrapper $sidebar={sidebar} className={className}>
      <S.MainWrapper>
        <S.TitleWrapper $sidebar={sidebar}>
          <div>
            <Title level={2} className="text">
              {courseCode} - {course.title}
            </Title>
          </div>
          <PlannerButton
            course={course}
            isAddedInPlanner={courses !== undefined && courses[course.code] !== undefined}
          />
        </S.TitleWrapper>
        {/* TODO: Style this better? */}
        {course.is_legacy && (
          <Text strong>
            NOTE: this course is discontinued - if a current course exists, pick that instead
          </Text>
        )}

        {!sidebar && (
          <div style={{ flexBasis: '25%' }}>
            <CourseAttributes course={course} />
          </div>
        )}

        <CourseInfoDrawers
          course={course}
          pathFrom={coursesPathFrom}
          unlocked={coursesUnlockedQuery.data}
          onCourseClick={onCourseClick}
        />
      </S.MainWrapper>

      {sidebar && (
        <S.SidebarWrapper>
          <CourseAttributes course={course} courseCapacity={courseCapacity} />
        </S.SidebarWrapper>
      )}
    </S.Wrapper>
  );
};

export default React.memo(CourseDescriptionPanel);
