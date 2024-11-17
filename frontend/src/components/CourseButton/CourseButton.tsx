import React from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { addTab } from 'reducers/courseTabsSlice';
import S from './styles';

type Props = {
  courseCode: string;
  title: string;
  planned?: boolean;
};

const CourseButton = ({ courseCode, title, planned }: Props) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleCourseLink = (e: React.MouseEvent<HTMLElement>): void => {
    e.stopPropagation();
    navigate('/course-selector');
    dispatch(addTab(courseCode));
  };

  return (
    <S.CourseButton $planned={planned} type="primary" onClick={handleCourseLink}>
      {courseCode}: {title}
    </S.CourseButton>
  );
};

export default CourseButton;
