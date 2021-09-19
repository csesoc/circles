import React from 'react';
import { useSelector } from 'react-redux';
import CourseMenu from './courseMenu/CourseMenu';
import CourseDescription from './courseDescription/CourseDescription';
import { CourseTabs } from './CourseTabs';
import SearchCourse from './SearchCourse';
import './main.less';

export default function CourseSelector() {
  const degree = useSelector(state => state.degree);
  return (
      <div className='cs-root'>
        <div className='cs-top-cont'>
          <div className='cs-degree-cont'>
            <h1 className='text'>{ degree.code } - { degree.name }</h1>
            <SearchCourse />
          </div>
        </div>
          <CourseTabs/>
        <div className='cs-bottom-cont'>
          <CourseMenu/>
          <CourseDescription />
        </div>
      </div>
  );
}