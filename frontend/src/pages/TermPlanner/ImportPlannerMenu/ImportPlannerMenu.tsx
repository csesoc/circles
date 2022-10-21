import React, { useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { LoadingOutlined } from '@ant-design/icons';
import { Button, Spin } from 'antd';
import axios from 'axios';
import { Course } from 'types/api';
import { JSONPlanner, PlannerCourse, Term } from 'types/planner';
import openNotification from 'utils/openNotification';
import type { RootState } from 'config/store';
import {
  addToUnplanned,
  moveCourse,
  setUnplannedCourseToTerm,
  toggleSummer,
  updateDegreeLength,
  updateStartYear
} from 'reducers/plannerSlice';
import CS from '../common/styles';
import S from './styles';

const ImportPlannerMenu = () => {
  const planner = useSelector((state: RootState) => state.planner);
  const inputRef = useRef<HTMLInputElement>(null);
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  const upload = () => {
    inputRef.current?.click();
  };

  const uploadedJSONFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files === null) {
      return;
    }

    if (e.target.files[0].type !== 'application/json') {
      openNotification({
        type: 'error',
        message: 'Import file needs to be JSON.',
        description: 'The uploaded file is not of type JSON.'
      });
      e.target.value = '';
      return;
    }

    const plannedCourses: string[] = [];
    planner.years.forEach((year) => {
      Object.values(year).forEach((termKey) => {
        termKey.forEach((code) => {
          plannedCourses.push(code);
        });
      });
    });

    setLoading(true);
    const reader = new FileReader();
    reader.readAsText(e.target.files[0], 'UTF-8');
    reader.onload = (ev) => {
      if (ev.target !== null) {
        const content = ev.target.result;
        e.target.value = '';

        try {
          const fileInJson = JSON.parse(content as string) as JSONPlanner;
          if (
            !Object.prototype.hasOwnProperty.call(fileInJson, 'startYear') ||
            !Object.prototype.hasOwnProperty.call(fileInJson, 'numYears') ||
            !Object.prototype.hasOwnProperty.call(fileInJson, 'isSummerEnabled') ||
            !Object.prototype.hasOwnProperty.call(fileInJson, 'years') ||
            !Object.prototype.hasOwnProperty.call(fileInJson, 'version')
          ) {
            openNotification({
              type: 'error',
              message: 'Invalid structure of the JSON file',
              description: 'The structure of the JSON file is not valid.'
            });
            return;
          }
          dispatch(updateDegreeLength(fileInJson.numYears));
          dispatch(updateStartYear(fileInJson.startYear));
          if (planner.isSummerEnabled !== fileInJson.isSummerEnabled) {
            dispatch(toggleSummer());
          }
          fileInJson.years.forEach((year, yearIndex) => {
            Object.entries(year).forEach(([term, termCourses]) => {
              termCourses.forEach(async (code, index) => {
                const { data: course } = await axios.get<Course>(`/courses/getCourse/${code}`);
                const courseData: PlannerCourse = {
                  title: course.title,
                  termsOffered: course.terms,
                  UOC: course.UOC,
                  plannedFor: null,
                  prereqs: course.raw_requirements,
                  isLegacy: course.is_legacy,
                  isUnlocked: true,
                  warnings: [],
                  handbookNote: course.handbook_note,
                  isAccurate: course.is_accurate,
                  isMultiterm: course.is_multiterm,
                  supressed: false,
                  mark: undefined
                };

                if (plannedCourses.indexOf(course.code) === -1) {
                  plannedCourses.push(course.code);
                  dispatch(addToUnplanned({ courseCode: course.code, courseData }));
                  const destYear = Number(yearIndex) + Number(planner.startYear);
                  const destTerm = term as Term;
                  const destRow = destYear - planner.startYear;
                  const destIndex = index;
                  dispatch(
                    moveCourse({
                      course: code,
                      destTerm: `${destYear}${destTerm}`,
                      srcTerm: 'unplanned'
                    })
                  );
                  dispatch(
                    setUnplannedCourseToTerm({
                      destRow,
                      destTerm,
                      destIndex,
                      course: code
                    })
                  );
                }
              });
            });
          });
          setLoading(false);
        } catch (err) {
          setLoading(false);
          // eslint-disable-next-line no-console
          console.error('Error at uploadedJSONFile', err);
          openNotification({
            type: 'error',
            message: 'Invalid JSON format',
            description: 'An error occured when parsing the JSON file'
          });
          return;
        }

        openNotification({
          type: 'success',
          message: 'JSON Imported',
          description: 'Planner has been successfully imported.'
        });
      }
    };
  };

  const spinIcon = <LoadingOutlined style={{ fontSize: 28 }} spin />;

  return (
    <S.Wrapper style={{ width: '240px' }}>
      <CS.MenuHeader>Import</CS.MenuHeader>
      <CS.MenuDivider />
      <div>Import an existing planner if you have exported it previously as a JSON file.</div>
      <div>If you currently have courses planned, it may be merged with the imported planner.</div>
      <>
        <div style={{ display: 'flex' }}>
          <Button style={{ width: '150px', margin: '5px' }} onClick={upload}>
            Upload a planner
          </Button>
          {loading && <Spin indicator={spinIcon} />}
        </div>
        <input type="file" style={{ display: 'none' }} ref={inputRef} onChange={uploadedJSONFile} />
      </>
    </S.Wrapper>
  );
};

export default ImportPlannerMenu;
