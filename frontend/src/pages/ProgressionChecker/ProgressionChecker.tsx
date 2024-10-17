import React, { useEffect, useState } from 'react';
import {
  BorderlessTableOutlined,
  EyeFilled,
  EyeInvisibleOutlined,
  TableOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Button, Divider, Typography } from 'antd';
import {
  ProgressionAdditionalCourses,
  ProgressionViewStructure,
  Views,
  ViewSubgroup,
  ViewSubgroupCourse
} from 'types/progressionViews';
import { ProgramStructure } from 'types/structure';
import { badCourses, badPlanner } from 'types/userResponse';
import { getProgramStructure } from 'utils/api/programsApi';
import { useUserCourses, useUserDegree, useUserPlanner } from 'utils/apiHooks/user';
import getNumTerms from 'utils/getNumTerms';
import openNotification from 'utils/openNotification';
import Collapsible from 'components/Collapsible';
import PageTemplate from 'components/PageTemplate';
import { MAX_COURSES_OVERFLOW } from 'config/constants';
import Dashboard from './Dashboard';
import GenericCoursesSection from './GenericCoursesSection';
import GridView from './GridView';
import S from './styles';
import TableView from './TableView';

const { Title } = Typography;

const ProgressionChecker = () => {
  const plannerQuery = useUserPlanner();
  const planner = plannerQuery.data ?? badPlanner;
  const { unplanned } = planner;

  const degreeQuery = useUserDegree();
  const degree = degreeQuery.data;

  const structureQuery = useQuery({
    queryKey: ['structure', degree?.programCode, degree?.specs],
    queryFn: () => getProgramStructure(degree!.programCode, degree!.specs),
    enabled: degree !== undefined
  });
  const structure: ProgramStructure = structureQuery.data?.structure ?? {};
  const uoc = structureQuery.data?.uoc ?? 0;

  useEffect(() => {
    openNotification({
      type: 'info',
      message: 'Disclaimer',
      description:
        "This progression check is intended to outline the courses required by your degree and may not be 100% accurate. Please refer to UNSW's official progression check and handbook for further accuracy."
    });
  }, []);

  const [view, setView] = useState(Views.GRID_CONCISE);
  const coursesQuery = useUserCourses();
  const courses = coursesQuery.data ?? badCourses;

  const countedCourses: string[] = [];
  const newViewLayout: ProgressionViewStructure = {};

  // keeps track of courses which overflows a subgroup UOC requirements
  // these courses are appended as 'Additional Electives'
  const overflowCourses: ProgressionAdditionalCourses = {};

  const ignoredCourses: ProgressionAdditionalCourses = {};

  const generateViewStructure = () => {
    // Example groups: Major, Minor, General, Rules
    Object.keys(structure).forEach((group) => {
      newViewLayout[group] = {};

      // Example subgroup: Core Courses, Computing Electives
      Object.keys(structure[group].content)
        .sort()
        .forEach((subgroup) => {
          const subgroupStructure = structure[group].content[subgroup];

          const isRule = subgroupStructure.type.includes('rule');
          const isGenEd = subgroupStructure.type.includes('gened');
          const isElectives = subgroupStructure.type.includes('electives');

          newViewLayout[group][subgroup] = {
            // section types with gened or rule/elective substring can have their
            // courses hidden as a modal
            isCoursesOverflow:
              isGenEd ||
              isRule ||
              isElectives ||
              Object.keys(subgroupStructure.courses).length > MAX_COURSES_OVERFLOW,
            courses: []
          };

          let currUOC = 0;

          // only consider disciplinary component courses
          Object.keys(subgroupStructure.courses).forEach((courseCode) => {
            if (courses[courseCode]?.ignoreFromProgression) return;

            const isDoubleCounted =
              countedCourses.includes(courseCode) &&
              !/Core/.test(subgroup) &&
              !group.includes('Rules');

            // flag when a course is overcounted (i.e. if a subgroup UOC requirement is filled) but
            // additional courses can be considered to count to the subgroup progression
            // only exception is Rules where it should display all courses
            const isOverCounted =
              !!courses[courseCode]?.plannedFor && currUOC > subgroupStructure.UOC && !isRule;

            const course: ViewSubgroupCourse = {
              courseCode,
              title: subgroupStructure.courses[courseCode],
              UOC: courses[courseCode]?.uoc ?? 0,
              plannedFor: courses[courseCode]?.plannedFor ?? '',
              isUnplanned: unplanned.includes(courseCode),
              isMultiterm: !!courses[courseCode]?.isMultiterm,
              isDoubleCounted,
              isOverCounted
            };

            newViewLayout[group][subgroup].courses.push(course);
            if (
              courses[courseCode]?.plannedFor &&
              !isOverCounted &&
              !countedCourses.includes(courseCode)
            ) {
              countedCourses.push(courseCode);
            }

            // adjust overflow courses
            if (!isRule) {
              if (!isOverCounted && overflowCourses[course.courseCode]) {
                // case where a course will be counted in a subgroup UOC requirement
                // delete the entry
                delete overflowCourses[course.courseCode];
              } else if (isOverCounted && !isDoubleCounted) {
                // check if course should be displayed as 'Additional Electives'
                // Double counted courses should not show as 'Additional Electives'
                // as we are counting double counted courses in the subgroup progression
                overflowCourses[course.courseCode] = {
                  ...course,
                  isDoubleCounted: false,
                  isOverCounted: false
                };
              }
            }

            currUOC +=
              (courses[courseCode]?.uoc ?? 0) *
              getNumTerms(courses[courseCode]?.uoc, !!courses[courseCode]?.isMultiterm);
          });

          newViewLayout[group][subgroup].courses.sort((a, b) =>
            a.courseCode.localeCompare(b.courseCode)
          );
        });
    });

    const programCourseList = Object.values(structure).flatMap((specialisation) =>
      Object.values(specialisation.content)
        .filter((spec) => typeof spec === 'object' && spec.courses && !spec.type.includes('rule'))
        .flatMap((spec) => Object.keys(spec.courses))
    );
    Object.keys(courses).forEach((courseCode) => {
      const course = {
        courseCode,
        title: courses[courseCode]?.title,
        UOC: courses[courseCode]?.uoc,
        plannedFor: courses[courseCode]?.plannedFor ?? '',
        isUnplanned: unplanned.includes(courseCode),
        isMultiterm: courses[courseCode]?.isMultiterm,
        isDoubleCounted: false,
        isOverCounted: false
      };
      if (courses[courseCode]?.plannedFor && courses[courseCode]?.ignoreFromProgression) {
        ignoredCourses[courseCode] = course;
      } else if (
        !programCourseList.includes(courseCode) &&
        courses[courseCode]?.plannedFor &&
        !courses[courseCode]?.ignoreFromProgression
      ) {
        overflowCourses[courseCode] = course;
      }
    });
    return newViewLayout;
  };

  const viewStructure = generateViewStructure();

  const sortSubgroups = (item1: [string, ViewSubgroup], item2: [string, ViewSubgroup]) => {
    if (/Core/.test(item1[0]) && !/Core/.test(item2[0])) {
      return -1;
    }

    if (/Core/.test(item2[0]) && !/Core/.test(item1[0])) {
      return 1;
    }

    return item1[0] > item2[0] ? 1 : -1;
  };

  return (
    <PageTemplate>
      <S.Wrapper>
        <Dashboard
          isLoading={structureQuery.isPending}
          structure={structure}
          totalUOC={uoc}
          freeElectivesUOC={Object.values(overflowCourses).reduce((acc, curr) => acc + curr.UOC, 0)}
        />
        <div id="divider">
          <Divider />
        </div>
        <S.ProgressionViewContainer>
          <S.ViewSwitcherWrapper>
            {view === Views.GRID || view === Views.GRID_CONCISE ? (
              <>
                <Button
                  type="primary"
                  icon={view === Views.GRID ? <EyeInvisibleOutlined /> : <EyeFilled />}
                  onClick={() => setView(view === Views.GRID ? Views.GRID_CONCISE : Views.GRID)}
                >
                  {view === Views.GRID ? 'Display Concise Mode' : 'Display Full Mode'}
                </Button>
                <Button
                  type="primary"
                  icon={<TableOutlined />}
                  onClick={() => setView(Views.TABLE)}
                >
                  Display Table View
                </Button>
              </>
            ) : (
              <Button
                type="primary"
                icon={<BorderlessTableOutlined />}
                onClick={() => setView(Views.GRID)}
              >
                Display Grid View
              </Button>
            )}
          </S.ViewSwitcherWrapper>
          {Object.entries(viewStructure).map(([group, groupEntry]) => (
            <Collapsible
              title={
                <Title level={1} className="text" id={group}>
                  {structure[group].name ? `${group} - ${structure[group].name}` : group}
                </Title>
              }
              key={group}
              initiallyCollapsed={group === 'Rules'}
            >
              {Object.entries(groupEntry)
                .sort(sortSubgroups)
                .map(([subgroup, subgroupEntry]) =>
                  view === Views.TABLE ? (
                    <TableView
                      uoc={structure[group].content[subgroup].UOC}
                      subgroupTitle={subgroup}
                      notes={structure[group].content[subgroup].notes}
                      showNotes={group === 'Rules'}
                      type={structure[group].content[subgroup].type}
                      courses={subgroupEntry.courses}
                    />
                  ) : (
                    <GridView
                      uoc={structure[group].content[subgroup].UOC}
                      subgroupTitle={subgroup}
                      notes={structure[group].content[subgroup].notes}
                      showNotes={group === 'Rules'}
                      type={structure[group].content[subgroup].type}
                      courses={subgroupEntry.courses}
                      isCoursesOverflow={subgroupEntry.isCoursesOverflow}
                      isConcise={view === Views.GRID_CONCISE}
                    />
                  )
                )}
            </Collapsible>
          ))}
          <GenericCoursesSection
            courses={Object.values(overflowCourses)}
            view={view}
            title="Free Electives"
            subheading="additional courses planned"
            description="These courses may or may not be counted to your program. Please manually verify your progression with this information."
          />
          <GenericCoursesSection
            courses={Object.values(ignoredCourses)}
            view={view}
            title="Progression Ignored"
            subheading="courses ignored from your progression"
            description="These courses have been manually ignored from the progression count. You can undo this from the Term Planner page if you wish."
          />
        </S.ProgressionViewContainer>
      </S.Wrapper>
    </PageTemplate>
  );
};

export default ProgressionChecker;
