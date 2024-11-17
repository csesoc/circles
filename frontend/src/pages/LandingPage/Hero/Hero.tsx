import React from 'react';
import PageContainer from 'styles/PageContainer';
import svgDots from 'assets/LandingPage/dots.svg';
import HeroContent from './HeroContent';
import HeroHeader from './HeroHeader';
import LogoFloat from './LogoFloat';
import S from './styles';
import Wave from './Wave';

type Props = {
  startLocation: string;
};

const Hero = ({ startLocation }: Props) => (
  <S.HeroSection>
    <Wave />
    <PageContainer>
      <HeroHeader />
      <S.ContentWrapper>
        <S.HeaderDots
          src={svgDots}
          alt="Svg Dots"
          animate={{ x: 0, opacity: 1 }}
          initial={{ x: -30, opacity: 0 }}
        />
        <HeroContent startLocation={startLocation} />
        <LogoFloat />
      </S.ContentWrapper>
    </PageContainer>
  </S.HeroSection>
);

export default Hero;
