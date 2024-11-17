import styled from 'styled-components';

const Wrapper = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const IconsWrapper = styled.div`
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 5px;
`;

const CourseTitleWrapper = styled.div<{ $selected?: boolean; $locked?: boolean }>`
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  color: ${({ theme }) => theme.text};

  font-weight: ${({ $selected, $locked }) => {
    if ($locked) return '100';
    if ($selected) return '700';
    return 'normal';
  }};
`;

export default {
  Wrapper,
  IconsWrapper,
  CourseTitleWrapper
};
