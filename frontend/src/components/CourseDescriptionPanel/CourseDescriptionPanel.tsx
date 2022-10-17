import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { Typography } from 'antd';
import axios from 'axios';
import { Course, CoursePathFrom, CoursesUnlockedWhenTaken } from 'types/api';
import { CourseTimetable, EnrolmentCapacityData } from 'types/courseCapacity';
import { CourseList } from 'types/courses';
import getEnrolmentCapacity from 'utils/getEnrolmentCapacity';
import prepareUserPayload from 'utils/prepareUserPayload';
import {
  LoadingCourseDescriptionPanel,
  LoadingCourseDescriptionPanelSidebar
} from 'components/LoadingSkeleton';
import PlannerButton from 'components/PlannerButton';
import { TIMETABLE_API_URL } from 'config/constants';
import type { RootState } from 'config/store';
import CourseAttributes from './CourseAttributes';
import CourseInfoDrawers from './CourseInfoDrawers';
import S from './styles';

const { Title, Text } = Typography;

type CourseDescriptionPanelProps = {
  courseCode: string;
  onCourseClick?: (code: string) => void;
};

const CourseDescriptionPanel = ({ courseCode, onCourseClick }: CourseDescriptionPanelProps) => {
  const { degree, planner } = useSelector((state: RootState) => state);

  const { pathname } = useLocation();
  const showAttributesSidebar = !!(pathname === '/course-selector');

  const [isLoading, setIsLoading] = useState(false);
  const [course, setCourse] = useState<Course>();
  const [coursesPathFrom, setCoursesPathFrom] = useState<CourseList>();
  const [coursesUnlocked, setCoursesUnlocked] = useState<CoursesUnlockedWhenTaken>();
  const [courseCapacity, setCourseCapacity] = useState<EnrolmentCapacityData>();

  function unwrap<T>(res: PromiseSettledResult<T>): T | undefined {
    if (res.status === 'rejected') {
      // eslint-disable-next-line no-console
      console.error('Rejected request at unwrap', res.reason);
      return undefined;
    }
    return res.value;
  }

  useEffect(() => {
    // if the course code changes, force a reload
    setIsLoading(true);
  }, [courseCode]);

  useEffect(() => {
    const getCourseInfo = async () => {
      try {
        const results = await Promise.allSettled([
          axios.get<Course>(`/courses/getCourse/${courseCode}`),
          axios.get<CoursePathFrom>(`/courses/getPathFrom/${courseCode}`),
          axios.post<CoursesUnlockedWhenTaken>(
            `/courses/coursesUnlockedWhenTaken/${courseCode}`,
            JSON.stringify(prepareUserPayload(degree, planner))
          ),
          axios.get<CourseTimetable>(`${TIMETABLE_API_URL}/${courseCode}`)
        ]);

        const [courseRes, pathFromRes, unlockedRes, courseCapRes] = results;

        setCourse(unwrap(courseRes)?.data);
        setCoursesPathFrom(unwrap(pathFromRes)?.data.courses);
        setCoursesUnlocked(unwrap(unlockedRes)?.data);
        setCourseCapacity(getEnrolmentCapacity(unwrap(courseCapRes)?.data));
        setIsLoading(false);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Error at getCourse', e);
      }
    };

    if (isLoading) {
      // gets the associated info for a course
      getCourseInfo();
    }
  }, [courseCode, degree, isLoading, planner]);

  if (isLoading || !course) {
    // either still loading or the course wasn't fetchable (fatal)
    return (
      <S.Wrapper showAttributesSidebar={showAttributesSidebar}>
        {!showAttributesSidebar ? (
          <LoadingCourseDescriptionPanelSidebar />
        ) : (
          <LoadingCourseDescriptionPanel />
        )}
      </S.Wrapper>
    );
  }

  return (
    <S.Wrapper showAttributesSidebar={showAttributesSidebar}>
      <S.MainWrapper>
        <S.TitleWrapper showAttributesSidebar={showAttributesSidebar}>
          <div>
            <Title level={2} className="text">
              {courseCode} - {course.title}
            </Title>
          </div>
          <PlannerButton course={course} />
        </S.TitleWrapper>
        {/* TODO: Style this better? */}
        {course.is_legacy && (
          <Text strong>
            NOTE: this course is discontinued - if a current course exists, pick that instead
          </Text>
        )}

        {!showAttributesSidebar && (
          <div style={{ flexBasis: '25%' }}>
            <CourseAttributes course={course} />
          </div>
        )}

        <CourseInfoDrawers
          course={course}
          pathFrom={coursesPathFrom}
          unlocked={coursesUnlocked}
          onCourseClick={onCourseClick}
        />
      </S.MainWrapper>

      {showAttributesSidebar && (
        <S.SidebarWrapper>
          <CourseAttributes course={course} courseCapacity={courseCapacity} />
        </S.SidebarWrapper>
      )}
    </S.Wrapper>
  );
};

export default CourseDescriptionPanel;
