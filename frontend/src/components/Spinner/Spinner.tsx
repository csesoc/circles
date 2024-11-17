import React from 'react';
import { LoadingOutlined } from '@ant-design/icons';
import { Spin } from 'antd';
import S from './styles';

type Props = {
  text: string;
  size?: 'small' | 'large';
};

const Spinner = ({ text, size = 'large' }: Props) => {
  // Small Spinner
  if (size === 'small') {
    return (
      <S.SmallWrapper className="loading-spinner">
        <Spin indicator={<LoadingOutlined spin />} size="small" />
        <p>{text}</p>
      </S.SmallWrapper>
    );
  }
  return (
    <S.LargeWrapper className="loading-spinner">
      <Spin indicator={<LoadingOutlined spin />} size="large" />
      <p>{text}</p>
    </S.LargeWrapper>
  );
};

export default Spinner;
