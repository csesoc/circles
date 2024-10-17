import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Typography } from 'antd';
import { CoursesResponse } from 'types/userResponse';
import { fetchAllDegrees } from 'utils/api/programsApi';
import { useUserDegree } from 'utils/apiHooks/user';
import CourseSearchBar from 'components/CourseSearchBar';
import { useAppDispatch } from 'hooks';
import { addTab } from 'reducers/courseTabsSlice';
import S from './styles';

const { Title } = Typography;

type CourseBannerProps = {
  courses?: CoursesResponse;
};

const CourseBanner = ({ courses }: CourseBannerProps) => {
  const dispatch = useAppDispatch();

  const degreeQuery = useUserDegree();
  const allPrograms = useQuery({
    queryKey: ['programs'],
    queryFn: fetchAllDegrees
  });

  const getUserProgramTitle = (): string => {
    if (degreeQuery.data?.programCode) {
      return allPrograms.data?.programs[degreeQuery.data?.programCode] || '';
    }
    return '';
  };

  return (
    <S.BannerWrapper>
      <Title level={2} className="text">
        {degreeQuery.data?.programCode} - {getUserProgramTitle()}
      </Title>
      <CourseSearchBar
        onSelectCallback={(courseCode) => dispatch(addTab(courseCode))}
        userCourses={courses}
      />
    </S.BannerWrapper>
  );
};

export default CourseBanner;
