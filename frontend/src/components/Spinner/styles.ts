import styled from 'styled-components';

const SmallWrapper = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 1px;

  p {
    font-size: 0.5rem;
    margin: 0;
    padding: 0;
  }
`;

const LargeWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 15px;

  p {
    margin: 0;
    padding: 0;
  }
`;

export default { SmallWrapper, LargeWrapper };
