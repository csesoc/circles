import React from 'react';
import { BugOutlined } from '@ant-design/icons';
import { Button, Tooltip } from 'antd';
import { FEEDBACK_LINK } from 'config/constants';
import useMediaQuery from 'hooks/useMediaQuery';
import S from './styles';

const FeedbackButton = () => {
  // Feedback form
  const isTablet = useMediaQuery('(max-width: 1000px)');
  const openFeedbackLink = () => {
    window.open(FEEDBACK_LINK, '_blank');
  };

  // Move this to the drawer if the screen is too small
  return isTablet ? null : (
    <S.FeedbackBtnWrapper>
      <Tooltip title="Report a bug!">
        <Button
          shape="circle"
          icon={<BugOutlined />}
          size="large"
          onClick={() => openFeedbackLink()}
        />
      </Tooltip>
    </S.FeedbackBtnWrapper>
  );
};

export default FeedbackButton;
