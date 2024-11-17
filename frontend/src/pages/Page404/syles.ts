import styled from 'styled-components';

const PageWrapper = styled.div`
  background-color: black;
  opacity: 0.1;
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100%;
  overflow: hidden;
`;

const GridCircleWrapper = styled.div`
  display: grid;
  grid-template-columns: auto auto auto auto;
  background-image: linear-gradient(to right, #ff512f, #f09819);
  padding: 10px;
  height: 100%;
  width: 100%;
`;

const LogoBox = styled.div<{ $alt?: boolean }>`
  margin: 10px;
  margin-right: 50px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: ${({ $alt }) => ($alt ? 'transform: rotate(10deg)' : 'rotate(350deg)')};
`;

const TextWrapper = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  margin-right: -50%;
  display: flex;
  align-items: center;
  flex-direction: column;
`;

const Title404 = styled.div`
  font-size: 6rem;
  color: #808080;
  font-weight: 600;
  height: 120px;
`;

const Text404 = styled.div`
  font-size: 1.5rem;
  color: #808080;
  margin: 5px;
  font-weight: 500;
`;

export default {
  PageWrapper,
  GridCircleWrapper,
  LogoBox,
  TextWrapper,
  Text404,
  Title404
};
