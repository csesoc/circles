import styled, { css } from 'styled-components';

const getAnimationState = (openState: boolean | undefined) => {
  // hasnt been opened or closed yet, is closed
  if (openState === undefined)
    return css`
      right: -30rem;
    `;

  // to be opened or closed
  return openState
    ? css`
        animation-name: animation_opening;
      `
    : css`
        animation-name: animation_closing;
      `;
};

const Wrapper = styled.div<{ $open?: boolean }>`
  position: absolute;
  height: 85%;
  width: 30rem;

  top: 5rem;

  background-color: ${({ theme }) => theme.sidebarDrawer.backgroundColor};
  border-radius: 10px 0 0 10px;
  filter: drop-shadow(-2px 2px 4px rgba(0, 0, 0, 0.3));

  animation-duration: 0.7s;
  animation-fill-mode: forwards;
  ${({ $open }) => getAnimationState($open)}

  @keyframes animation_opening {
    from {
      right: -30rem;
    }
    to {
      right: 0;
    }
  }

  @keyframes animation_closing {
    from {
      right: 0;
    }
    to {
      right: -30rem;
    }
  }
`;

const ChildrenWrapper = styled.div`
  width: 100%;
  height: 100%;
  padding: 12px 20px;
  background-color: ${({ theme }) => theme.sidebarDrawer.backgroundColor};

  overflow-y: auto;
  overflow-x: hidden;
`;

const ButtonWrapper = styled.div`
  height: 40%;
  width: 2rem;

  position: absolute;
  left: -2rem;
  top: 30%;

  border-radius: 10px 0 0 10px;
  cursor: pointer;

  display: flex;
  justify-content: center;
  align-items: center;

  background-color: ${({ theme }) => theme.sidebarDrawer.backgroundColor};
  color: ${({ theme }) => theme.text};
  border-color: ${({ theme }) => theme.sidebarDrawer.borderColor};
  &:hover {
    background-color: ${({ theme }) => theme.sidebarDrawer.hoverBackgroundColor};
  }
  &:focus {
    background-color: ${({ theme }) => theme.sidebarDrawer.hoverBackgroundColor};
  }
`;

const SVGWrapper = styled.svg`
  width: 12px;
  height: 48px;
`;

const SVGLine = styled.line`
  stroke-linecap: round;
  stroke-width: 2px;
  stroke: #aaa;
`;

export default {
  Wrapper,
  ChildrenWrapper,
  ButtonWrapper,
  SVGLine,
  SVGWrapper
};
