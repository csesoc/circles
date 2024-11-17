import React from 'react';
import { BugOutlined } from '@ant-design/icons';
import { Tooltip } from 'antd';
import { FEEDBACK_LINK } from 'config/constants';
import useMediaQuery from 'hooks/useMediaQuery';
import useSettings from 'hooks/useSettings';
import S from './styles';

const FeedbackButton = () => {
  // Feedback form
  const isTablet = useMediaQuery('(max-width: 1000px)');
  const openFeedbackLink = () => {
    window.open(FEEDBACK_LINK, '_blank');
  };

  const { theme } = useSettings();

  // Move this to the drawer if the screen is too small
  return isTablet ? null : (
    <S.FeedbackBtnWrapper>
      <Tooltip title="Report a bug!">
        <S.Button
          shape="circle"
          icon={<BugOutlined style={{ color: theme === 'light' ? '#323739' : '#f1f1f1' }} />}
          size="large"
          onClick={() => openFeedbackLink()}
        />
      </Tooltip>
    </S.FeedbackBtnWrapper>
  );
};

export default FeedbackButton;
