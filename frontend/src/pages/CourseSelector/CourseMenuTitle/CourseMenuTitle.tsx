import React from 'react';
import { LockOutlined, WarningOutlined } from '@ant-design/icons';
import { Tooltip } from 'antd';
import { useTheme } from 'styled-components';
import QuickAddCartButton from 'components/QuickAddCartButton';
import useMediaQuery from 'hooks/useMediaQuery';
import S from './styles';

type Props = {
  courseCode: string;
  runMutate?: (courseId: string) => void;
  selected?: boolean;
  accurate?: boolean;
  unlocked?: boolean;
  title: string;
};

const CourseMenuTitle = ({ courseCode, runMutate, selected, accurate, unlocked, title }: Props) => {
  const isSmall = useMediaQuery('(max-width: 1400px)');
  const theme = useTheme();
  const locked = !unlocked;

  return (
    <S.Wrapper>
      {isSmall ? (
        <Tooltip title={title} placement="topLeft">
          <S.CourseTitleWrapper $selected={selected} $locked={locked}>
            {courseCode}
          </S.CourseTitleWrapper>
        </Tooltip>
      ) : (
        <S.CourseTitleWrapper $selected={selected} $locked={locked}>
          {courseCode}: {title}
        </S.CourseTitleWrapper>
      )}
      <S.IconsWrapper>
        {!accurate && (
          <Tooltip
            placement="top"
            title="We couldn't parse the requirement for this course. Please manually check if you have the correct prerequisites to unlock it."
          >
            <WarningOutlined
              data-testid="antd-warning-icon"
              style={{
                color: '#DC9930',
                fontSize: '16px'
              }}
            />
          </Tooltip>
        )}
        {!unlocked && (
          <LockOutlined
            data-testid="antd-lock-icon"
            style={{ fontSize: '12px', color: theme.text }}
          />
        )}
        <QuickAddCartButton runMutate={runMutate} courseCode={courseCode} planned={selected} />
      </S.IconsWrapper>
    </S.Wrapper>
  );
};

export default CourseMenuTitle;
