import styled from 'styled-components';

const ContainerWrapper = styled.div`
  padding: 2rem;
  max-width: 1500px;
  margin: auto;
`;

const Subtitle = styled.div`
  font-size: 16px;
  font-weight: 300;
`;

const HorizontalLine = styled.hr`
  margin-top: 30px;
  margin-bottom: 20px;
  border-color: rgb(251, 251, 251);
`;

const StepsWrapper = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const HeaderWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

export default {
  ContainerWrapper,
  HorizontalLine,
  Subtitle,
  StepsWrapper,
  HeaderWrapper
};
