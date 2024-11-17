import styled, { css } from 'styled-components';

const DraggableTabWrapper = styled.div<{ $active: boolean }>`
  height: 100%;
  border-radius: 10px 0 0 0;
  background-color: ${({ theme }) => theme.draggableTab.backgroundColor};
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  padding: 6px 6px 6px 16px;
  margin-left: 2px;
  border: 1px solid ${({ theme }) => theme.draggableTab.borderColor};
  color: ${({ theme }) => theme.text};

  ${({ $active, theme }) =>
    $active &&
    css`
      background-color: ${theme.body};
      border-bottom-color: ${theme.body};
      color: #9254de;
      font-weight: 700;
    `}
`;

const TabNameWrapper = styled.span`
  &:hover {
    color: #9254de;
    cursor: pointer;
  }
`;

export default { DraggableTabWrapper, TabNameWrapper };
