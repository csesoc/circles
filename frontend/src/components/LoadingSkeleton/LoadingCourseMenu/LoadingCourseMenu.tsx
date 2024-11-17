import React, { Fragment } from 'react';
import { Skeleton } from 'antd';
import S from './styles';

const LoadingCourseMenu = () => (
  <S.SkeletonWrapper>
    {[...Array(5).keys()].map((i) => (
      <Fragment key={i}>
        <Skeleton.Input style={{ width: '100%', height: 40, margin: '1rem 0' }} active />
        <Skeleton.Input style={{ width: '85%', height: 35, margin: '1rem 0' }} active />
        <Skeleton.Input style={{ width: '75%', height: 25, margin: '1rem 0' }} active />
        <Skeleton.Input style={{ width: '75%', height: 25, margin: '1rem 0' }} active />
      </Fragment>
    ))}
  </S.SkeletonWrapper>
);

export default LoadingCourseMenu;
