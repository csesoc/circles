import React from 'react';
import { Link } from 'react-router-dom';
import circlesLogo from 'assets/circlesLogo.svg';
import S from './styles';

const HeroHeader = () => (
  <S.Header animate={{ y: 0 }} initial={{ y: -40 }} transition={{ duration: 0.5, ease: 'easeOut' }}>
    <Link to="/">
      <S.LogoWrapper>
        <S.HeaderLogo src={circlesLogo} alt="Circles Logo" />
        <S.HeaderTitle>Circles</S.HeaderTitle>
      </S.LogoWrapper>
    </Link>
  </S.Header>
);

export default HeroHeader;
