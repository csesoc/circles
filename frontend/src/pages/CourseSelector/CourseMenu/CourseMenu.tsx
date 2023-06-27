/* eslint-disable */
import React, { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { MenuProps } from 'antd';
import axios from 'axios';
import { CoursesAllUnlocked, Structure } from 'types/api';
import { CourseUnitsStructure, MenuDataStructure, MenuDataSubgroup } from 'types/courseMenu';
import { CourseValidation } from 'types/courses';
import { ProgramStructure } from 'types/structure';
import getNumTerms from 'utils/getNumTerms';
import prepareUserPayload from 'utils/prepareUserPayload';
import { LoadingCourseMenu } from 'components/LoadingSkeleton';
import { MAX_COURSES_OVERFLOW } from 'config/constants';
import type { RootState } from 'config/store';
import { setCourses } from 'reducers/coursesSlice';
import { addTab } from 'reducers/courseTabsSlice';
import CourseMenuTitle from '../CourseMenuTitle';
import S from './styles';
import { getUserDegree, getUserPlanner } from 'utils/api/userApi';
import { useQuery, useQueryClient } from 'react-query';
import { DegreeResponse, PlannerResponse } from 'types/userResponse';
import { errLogger } from 'utils/queryUtils';

type SubgroupTitleProps = {
  title: string;
  currUOC: number;
  totalUOC: number;
};

const SubgroupTitle = ({ title, currUOC, totalUOC }: SubgroupTitleProps) => (
  <S.SubgroupHeader>
    <S.LabelTitle>{title}</S.LabelTitle>
    <S.UOCBadge>
      {currUOC} / {totalUOC}
    </S.UOCBadge>
  </S.SubgroupHeader>
);


const getEverything = async () => {
  const degreePromise = getUserDegree();
  const plannerPromise = getUserPlanner();
  const structurePromise = degreePromise.then(async ({ programCode, specs }) => {
    const res = await axios.get<Structure>(
      `/programs/getStructure/${programCode}/${specs.join('+')}`
    );
    return res.data.structure;
  });
  const coursesStatePromise = Promise.all([degreePromise, plannerPromise]).then(async ([degree, planner]) => {
    const res = await axios.post<CoursesAllUnlocked>(
      '/courses/getAllUnlocked/',
      JSON.stringify(prepareUserPayload(degree, planner))
    );
    return res.data.courses_state;
  });
  return Promise.all([plannerPromise, structurePromise, coursesStatePromise]);
};

const CourseMenu = () => {
  const dispatch = useDispatch();
  const [menuData, setMenuData] = useState<MenuDataStructure>({});
  const [coursesUnits, setCoursesUnits] = useState<CourseUnitsStructure | null>(null);

  const { showLockedCourses } = useSelector((state: RootState) => state.settings);

  const [pageLoaded, setPageLoaded] = useState(false);

  const generateMenuData = useCallback((planner: PlannerResponse, structure: ProgramStructure, courses: Record<string, CourseValidation>) => {
    const newMenu: MenuDataStructure = {};
    const newCoursesUnits: CourseUnitsStructure = {};
    // Example groups: Major, Minor, General, Rules
    Object.keys(structure).forEach((group) => {
      // Do not include 'Rules' group in sidebar or any other groups that do not
      // have subgroups
      if (group === 'Rules' || !Object.keys(structure[group].content).length) return;
      newMenu[group] = {};
      newCoursesUnits[group] = {};
      // Example subgroup: Core Courses, Computing Electives
      Object.keys(structure[group].content).forEach((subgroup) => {
        const subgroupStructure = structure[group].content[subgroup];
        newCoursesUnits[group][subgroup] = {
          total: subgroupStructure.UOC,
          curr: 0
        };
        newMenu[group][subgroup] = [];
        if (subgroupStructure.courses && !subgroupStructure.type.includes('rule')) {
          // only consider disciplinary component courses
          Object.keys(subgroupStructure.courses).forEach((courseCode) => {
            // suppress gen ed courses if it has not been added to the planner
            if (subgroupStructure.type === 'gened' && !planner.courses[courseCode]) return;
            newMenu[group][subgroup].push({
              courseCode,
              title: subgroupStructure.courses[courseCode],
              unlocked: !!courses[courseCode]?.unlocked,
              accuracy: courses[courseCode] ? courses[courseCode].is_accurate : true
            });
            // add UOC to curr
            if (planner.courses[courseCode]) {
              const anyCourse = planner.courses[courseCode] as any; // while types get unfucked
              newCoursesUnits[group][subgroup].curr +=
                anyCourse.UOC *
                getNumTerms(
                  anyCourse.UOC,
                  anyCourse.isMultiterm
                );
            }
          });
        }
      });
    });
    setMenuData(newMenu);
    setCoursesUnits(newCoursesUnits);
    setPageLoaded(true);
  }, []);

  const everythingQuery = useQuery(['degree', 'planner', 'programStructure'], getEverything, {
    onError: errLogger("getEverything"),
    onSuccess: (data) => {
      if (!Object.keys(data[1]).length) return;
      // should maybe be delted later or something
      dispatch(setCourses(data[2]));
      generateMenuData(...data);

    }
  });

  const sortSubgroups = (
    item1: [string, MenuDataSubgroup[]],
    item2: [string, MenuDataSubgroup[]]
  ) => {
    if (/Core/.test(item1[0]) && !/Core/.test(item2[0])) {
      return -1;
    }

    if (/Core/.test(item2[0]) && !/Core/.test(item1[0])) {
      return 1;
    }

    return item1[0] > item2[0] ? 1 : -1;
  };

  const sortCourses = (item1: MenuDataSubgroup, item2: MenuDataSubgroup) =>
    item1.courseCode > item2.courseCode ? 1 : -1;

  const defaultOpenKeys = [Object.keys(menuData)[0]];

  let menuItems: MenuProps['items'];
  if (everythingQuery.isSuccess) {
    const [planner, structure, _] = everythingQuery.data;
    menuItems = Object.entries(menuData).map(([groupKey, groupEntry]) => ({
      label: structure[groupKey].name ? `${groupKey} - ${structure[groupKey].name}` : groupKey,
      key: groupKey,
      children: Object.entries(groupEntry)
        .sort(sortSubgroups)
        .map(([subgroupKey, subGroupEntry]) => {
          const currUOC = coursesUnits ? coursesUnits[groupKey][subgroupKey].curr : 0;
          const totalUOC = coursesUnits ? coursesUnits[groupKey][subgroupKey].total : 0;
          if (subGroupEntry.length <= MAX_COURSES_OVERFLOW) defaultOpenKeys.push(subgroupKey);
          return {
            label: <SubgroupTitle title={subgroupKey} currUOC={currUOC} totalUOC={totalUOC} />,
            key: subgroupKey,
            disabled: !subGroupEntry.length, // disable submenu if there are no courses
            // check if there are courses to show collapsible submenu
            children: subGroupEntry.length
              ? subGroupEntry
                .sort(sortCourses)
                .filter(
                  (course) =>
                    course.unlocked || planner.courses[course.courseCode] || showLockedCourses
                )
                .map((course) => ({
                  label: (
                    <CourseMenuTitle
                      courseCode={course.courseCode}
                      title={course.title}
                      selected={planner.courses[course.courseCode] !== undefined || planner.unplanned.includes(course.courseCode)}
                      accurate={course.accuracy}
                      unlocked={course.unlocked}
                    />
                  ),
                  // key is course code + groupKey + subgroupKey to differentiate as unique
                  // course items in menu
                  key: `${course.courseCode}-${groupKey}-${subgroupKey}`
                }))
              : null
          };
        })
    }));
  }

  const handleClick = ({ key }: { key: string }) => {
    // course code is first 8 chars due to the key being course code + group + subGroup
    // to differentiate duplicate courses in different groups/subgroups
    const courseCode = key.slice(0, 8);
    dispatch(addTab(courseCode));
  };

  return (
    <S.SidebarWrapper>
      {pageLoaded ? (
        <S.Menu
          defaultSelectedKeys={[]}
          defaultOpenKeys={defaultOpenKeys}
          items={menuItems}
          mode="inline"
          onClick={handleClick}
        />
      ) : (
        <LoadingCourseMenu />
      )}
    </S.SidebarWrapper>
  );
};

export default CourseMenu;
