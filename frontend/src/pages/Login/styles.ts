import styled, { css } from 'styled-components';

const LoginContainer = styled.div`
  width: 100%;
  height: 100vh;
  background-color: ${({ theme }) => theme.loginSplash?.backgroundColor};
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Wrapper = styled.div`
  display: flex;
  height: 80vh;
  width: 80vw;
  @media (max-width: 1440px) {
    width: 95vw;
  }
`;

const Left = styled.div`
  flex: 0.9;
  width: 100%;
  height: 100%;
  ${({ theme }) =>
    theme.loginSplash &&
    css`
      background-color: ${theme.loginSplash.svgColor};
    `}
  padding: 50px;
  border-radius: 15px 0px 0px 15px;
`;

const SplashArt = styled.img`
  width: 100%;
  height: 100%;
`;

const Right = styled.div`
  position: relative;
  flex: 1;
  width: 100%;
  background-color: ${({ theme }) => theme.body};
  border-radius: 0px 15px 15px 0px;
`;

const Login = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 5rem;
  h2 {
    align-self: flex-start;
    font-size: 2rem;
    font-weight: 700;
    color: ${({ theme }) => theme.text};
  }
  p {
    align-self: flex-start;
    font-weight: 500;
    color: ${({ theme }) => theme.text};
  }
`;

const LoginButton = styled.button`
  background: linear-gradient(90deg, #b47cfb 32.03%, #8d48f6 87.53%, #8037f4 106.41%);
  border: none;
  width: 70%;
  height: 70px;
  color: #fff;
  font-weight: 700;
  font-size: 20px;
  margin: 20px;
  cursor: pointer;
  transition: all 0.3s;
  &:hover {
    ${({ theme }) =>
      theme.loginSplash &&
      css`
        background: linear-gradient(270deg, #b47cfb 32.03%, #8d48f6 87.53%, #8037f4 106.41%);
      `}
  }
  &:active {
    ${({ theme }) =>
      theme.loginSplash &&
      css`
        transform: translateY(5%);
      `}
  }
  @media (max-width: 1200px) {
    width: 100%;
  }
`;

const GuestButton = styled.button`
  background: transparent;
  border: linear-gradient(90deg, #b47cfb 32.03%, #8d48f6 87.53%, #8037f4 106.41%);
  width: 70%;
  height: 70px;
  color: ${({ theme }) => theme.text};
  font-weight: 700;
  font-size: 20px;
  margin: 20px;
  cursor: pointer;
  transition: all 0.3s;
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  &:hover {
    ${({ theme }) =>
      theme.loginSplash &&
      css`
        background-color: #191b1b;
      `}
    color: #fff;
  }
  &:active {
    ${({ theme }) =>
      theme.loginSplash &&
      css`
        transform: translateY(5%);
      `}
  }
  @media (max-width: 1200px) {
    width: 100%;
  }
`;

const Back = styled.img`
  position: absolute;
  top: 10%;
  left: 10%;
  width: 10%;
  @media (max-width: 1600px) {
    width: 12%;
  }
`;

export default {
  Left,
  LoginContainer,
  LoginButton,
  GuestButton,
  SplashArt,
  Wrapper,
  Login,
  Right,
  Back
};
