import { RightOutlined } from '@ant-design/icons';
import styled, { css } from 'styled-components';

const CollapsibleHeader = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  vertical-align: bottom;
  border-bottom: ${({ theme }) => theme.courseDescription.paddingColor} solid 1px; //grey-5
  margin-top: 10px;
  margin-bottom: 7px;
  transition: 250ms;

  &:hover {
    cursor: pointer;
    color: ${({ theme }) => theme.purplePrimary};
    transition: 250ms;
  }
`;

const CollapseButton = styled(RightOutlined)<{ $collapsed: boolean }>`
  margin-bottom: 10px;
  padding: 10px;
  transition: 200ms;
  transform: rotate(90deg);
  color: ${({ theme }) => theme.collapseBtnIcon.color};

  ${({ $collapsed }) =>
    $collapsed &&
    css`
      transform: rotate(0);
    `}
`;

const CollapsibleContent = styled.div<{ $collapsed: boolean }>(
  ({ $collapsed }) => css`
    width: 100%;
    margin: 10px;
    max-height: ${$collapsed ? 0 : 4000}px;
    transition: max-height 0.4s ease-in-out;
    overflow: hidden;
  `
);

export default { CollapsibleHeader, CollapsibleContent, CollapseButton };
