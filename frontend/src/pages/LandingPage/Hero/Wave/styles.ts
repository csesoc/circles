import styled, { css, keyframes } from 'styled-components';
import waveBackground from 'assets/LandingPage/waveBackground.svg';
import waveForeground from 'assets/LandingPage/waveForeground.svg';

const waveAnimation = keyframes`
  0%, {margin-left: 0;}
  100% {margin-left: -1600px;}
`;

const waveSwell = keyframes`
  0%, 100% {
    transform: translate3d(0,-30px,0);
  }
  50% {
    transform: translate3d(0,5px,0);
  }
`;

const waveStyle = css`
  animation-fill-mode: backwards;
  width: 6400px;
  height: 916px;
  background-size: cover;
  position: absolute;
`;

const WaveForeground = styled.div`
  ${waveStyle}
  background: url(${waveForeground}) repeat-x;
  animation:
    ${waveAnimation} 13s cubic-bezier(0.36, 0.45, 0.63, 0.53) -0.125s infinite,
    ${waveSwell} 5s ease -1.25s infinite;
  @media (min-width: 1024px) {
    top: -38vh;
  }
  @media (min-width: 1440px) {
    top: -22vh;
  }
  @media (min-width: 1980px) {
    top: -10px;
  }
`;

const WaveBackground = styled.div`
  ${waveStyle}
  background: url(${waveBackground}) repeat-x;
  animation: ${waveAnimation} 13s cubic-bezier(0.36, 0.45, 0.63, 0.53) infinite;
  transform: translate3d(0, 0, 0);
  @media (min-width: 1024px) {
    top: -42vh;
  }
  @media (min-width: 1440px) {
    top: -25vh;
  }
  @media (min-width: 1980px) {
    top: -12px;
  }
`;

const WaveWrapper = styled.div`
  width: 100%;
  max-width: 100%;
  height: 1000px;
  position: absolute;
  z-index: -99;
  overflow-x: hidden;
`;

export default {
  WaveForeground,
  WaveBackground,
  WaveWrapper
};
