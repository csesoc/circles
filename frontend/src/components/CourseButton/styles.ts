import { Button } from 'antd';
import styled, { css } from 'styled-components';

const CourseButton = styled(Button)<{ $planned?: boolean }>`
  border-radius: 10px;
  border: 1px solid ${({ theme }) => theme.purpleLight};
  display: flex;
  align-items: center;
  justify-content: center;
  width: 270px;
  height: 80px;
  white-space: normal;

  ${({ $planned, theme }) =>
    !$planned &&
    css`
      background-color: ${theme.courseButton.backgroundColor};
      color: #9254de !important;

      &:hover {
        background-color: ${theme.courseButton.hoverBackgroundColor} !important;
      }
    `}
`;

export default { CourseButton };
