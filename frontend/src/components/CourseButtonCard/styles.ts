import { Button } from 'antd';
import styled, { css } from 'styled-components';

const CourseWrapper = styled.div`
  display: block;
  align-items: center;
`;

const CourseCode = styled.p`
  margin: 0 !important;
  font-size: 11px;
  font-weight: 400;
  text-align: left;
`;

const CourseTitle = styled.p`
  margin: 0 !important;
  font-size: 14px;
  font-weight: 500;
  text-align: left;

  text-overflow: ellipsis;
  overflow: hidden;

  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
`;

const CourseButtonCard = styled(Button)<{ $planned?: boolean }>`
  border-radius: 10px;
  border-width: 1px;
  width: 270px;
  height: 80px;
  white-space: break-spaces;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 5px;

  ${({ $planned }) =>
    !$planned &&
    css`
      background: #fafafa;
      border-color: #dcdcdc;
      color: #000000 !important;

      &:hover {
        background-color: #f9f9f9;
      }
    `}
`;

export default {
  CourseWrapper,
  CourseCode,
  CourseTitle,
  CourseButtonCard
};
