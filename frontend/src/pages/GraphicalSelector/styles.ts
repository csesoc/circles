import styled, { css } from 'styled-components';
import CourseDescriptionPanelComp from 'components/CourseDescriptionPanel';

const Wrapper = styled.div<{ $fullscreen: boolean }>`
  height: calc(100vh - var(--navbar-height));
  display: flex;
  gap: 20px;

  ${({ $fullscreen }) =>
    !$fullscreen &&
    css`
      padding: 25px;
    `}
`;

const GraphWrapper = styled.div<{ $fullscreen: boolean }>`
  height: 100%;
  width: 100%;
  overflow: hidden;
  flex: 5;
  position: relative;

  ${({ $fullscreen }) =>
    !$fullscreen &&
    css`
      border-radius: 20px;
      border: ${({ theme }) => theme.graph.borderColor} solid 1px;
    `}
`;

const SidebarWrapper = styled.div`
  border-radius: 20px;
  border: ${({ theme }) => theme.graph.borderColor} solid 1px;
  padding: 10px;
  flex: 2;
  overflow-y: auto;
  background-color: ${({ theme }) => theme.graph.backgroundColor};
`;

const SearchBarWrapper = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
`;

const CourseDescriptionPanel = styled(CourseDescriptionPanelComp)`
  & h3.ant-typography {
    font-size: 20px !important;
  }

  & h2.ant-typography {
    font-size: 26px !important;
  }
`;

const SpinnerWraper = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
`;

export default {
  CourseDescriptionPanel,
  Wrapper,
  GraphWrapper,
  SidebarWrapper,
  SearchBarWrapper,
  SpinnerWraper
};
