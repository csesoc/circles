import React from 'react';
import useSettings from 'hooks/useSettings';
import S from './styles';

type Props = {
  progress: number;
};

const ProgressBar = ({ progress }: Props) => {
  const { theme } = useSettings();
  const trailColor = theme === 'light' ? '#f5f5f5' : '#444249';

  let bgColor = '#3cb371';
  if (progress >= 75) {
    bgColor = '#fe6f5e';
  } else if (progress >= 45) {
    bgColor = '#ffa500';
  }

  return <S.Progress strokeColor={bgColor} percent={progress} trailColor={trailColor} />;
};
export default ProgressBar;
