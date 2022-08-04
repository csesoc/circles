import styled, { keyframes } from "styled-components";

const PageWrapper = styled.div`
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
`;

const pulse = keyframes`
  0% {
    box-shadow: 0 0 0 0px rgba(84, 72, 91, 0.2);
  }
  100% {
    box-shadow: 0 0 0 40px rgba(17, 3, 52, 0);
  }
`;

const LoadingLogo = styled.img`
  width: 200px;
  border-radius: 50%;
  animation: ${pulse} 1.5s infinite;
`;

export default { PageWrapper, LoadingLogo };
