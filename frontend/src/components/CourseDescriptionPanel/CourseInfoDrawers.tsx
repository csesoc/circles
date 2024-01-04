import React from 'react';
import { useQuery } from 'react-query';
import { Course, CoursesUnlockedWhenTaken } from 'types/api';
import { CourseList } from 'types/courses';
import { badCourses, badValidations } from 'types/userResponse';
import { validateTermPlanner } from 'utils/api/plannerApi';
import { getUserCourses } from 'utils/api/userApi';
import Collapsible from 'components/Collapsible';
import CourseTag from 'components/CourseTag';
import PrerequisiteTree from 'components/PrerequisiteTree';
import { inDev } from 'config/constants';

type CourseInfoDrawersProps = {
  course: Course;
  pathFrom?: CourseList;
  unlocked?: CoursesUnlockedWhenTaken;
  onCourseClick?: (code: string) => void;
};

const CourseInfoDrawers = ({
  course,
  onCourseClick,
  pathFrom = [],
  unlocked
}: CourseInfoDrawersProps) => {
  const courses = useQuery('courses', getUserCourses).data || badCourses;

  const pathFromInPlanner = pathFrom.filter((courseCode) =>
    Object.keys(courses).includes(courseCode)
  );
  const pathFromNotInPlanner = pathFrom.filter(
    (courseCode) => !Object.keys(courses).includes(courseCode)
  );
  const inPlanner = courses[course.code];
  const validateQuery = useQuery('validate', validateTermPlanner);
  const validations = validateQuery.data ?? badValidations;
  const isUnlocked = validations.courses_state[course.code];
  return (
    <div>
      <Collapsible title="Overview">
        {/* eslint-disable-next-line react/no-danger */}
        <p dangerouslySetInnerHTML={{ __html: course?.description || 'None' }} />
      </Collapsible>
      <Collapsible title="Requirements">
        {/* eslint-disable-next-line react/no-danger */}
        <p dangerouslySetInnerHTML={{ __html: course?.raw_requirements || 'None' }} />
      </Collapsible>
      <Collapsible title="Course Prerequisites">
        {!!pathFrom.length && !isUnlocked ? (
          <>
            <p>
              These courses in your planner have helped unlocked this course:
              {!pathFromInPlanner.length && ' None'}
            </p>
            {!!pathFromInPlanner.length && (
              <p>
                {pathFromInPlanner.map((code) => (
                  <CourseTag key={code} onCourseClick={onCourseClick} name={code} />
                ))}
              </p>
            )}
            <p>
              You may need to complete these courses to unlock this course:
              {!pathFromNotInPlanner.length && ' None'}
            </p>
            {!!pathFromNotInPlanner.length && (
              <p>
                {pathFromNotInPlanner.map((code) => (
                  <CourseTag key={code} onCourseClick={onCourseClick} name={code} />
                ))}
              </p>
            )}
          </>
        ) : (
          <p>
            {isUnlocked
              ? 'You have already unlocked this course.'
              : 'This course does not have any prerequisite that needs to be met.'}
          </p>
        )}
      </Collapsible>
      <Collapsible title="Courses unlocked after doing this course">
        {!!unlocked?.direct_unlock?.length && !inPlanner ? (
          <>
            <p>These courses are directly unlocked after completing this course:</p>
            <p>
              {unlocked.direct_unlock.map((code) => (
                <CourseTag key={code} name={code} onCourseClick={onCourseClick} />
              ))}
            </p>
          </>
        ) : (
          <p>
            {inPlanner
              ? "This course have already been added to your planner and hence can't unlock any more courses."
              : 'No courses will be unlocked after completing this course.'}
          </p>
        )}
      </Collapsible>
      <Collapsible title="Courses indirectly unlocked after doing this course" initiallyCollapsed>
        {!!unlocked?.indirect_unlock?.length && !inPlanner ? (
          <>
            <p>These courses are indirectly unlocked after completing this course:</p>
            <p>
              {unlocked.indirect_unlock.map((code) => (
                <CourseTag key={code} name={code} onCourseClick={onCourseClick} />
              ))}
            </p>
          </>
        ) : (
          <p>
            {inPlanner
              ? "This course have already been added to your planner and hence can't unlock any more courses."
              : 'No courses will be indirectly unlocked after completing this course.'}
          </p>
        )}
      </Collapsible>
      {inDev && (
        <Collapsible title="Prerequisite Visualisation">
          <PrerequisiteTree courseCode={course.code} onCourseClick={onCourseClick} />
        </Collapsible>
      )}
    </div>
  );
};

export default CourseInfoDrawers;
