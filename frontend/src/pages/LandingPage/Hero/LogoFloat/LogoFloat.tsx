import React from 'react';
import circlesLogo from 'assets/circlesLogo.svg';
import S from './styles';

const LogoFloat = () => (
  <S.Wrapper>
    <S.Bubble2
      animate={{
        y: 80,
        opacity: [0, 1, 0],
        x: [-50, -55, -35, 0]
      }}
      initial={{ y: 170 }}
      transition={{
        duration: 5,
        delay: 2.5,
        repeat: Infinity,
        repeatDelay: 2
      }}
    />
    <S.Bubble
      animate={{
        y: 70,
        opacity: [0, 1, 0],
        x: [140, 180, 160, 115]
      }}
      initial={{ y: 210, x: 140 }}
      transition={{
        duration: 7,
        delay: 2,
        repeat: Infinity
      }}
    />
    <S.LandingLogo
      src={circlesLogo}
      alt="Circles Logo"
      animate={{ y: 40 }}
      initial={{ y: -20 }}
      transition={{
        duration: 2,
        delay: 0.3,
        ease: 'easeInOut',
        repeat: Infinity,
        repeatType: 'reverse'
      }}
    />
  </S.Wrapper>
);

export default LogoFloat;
