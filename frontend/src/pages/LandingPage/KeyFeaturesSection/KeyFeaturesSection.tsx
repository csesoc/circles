import React from 'react';
import PageContainer from 'styles/PageContainer';
import blobBgSrc from 'assets/LandingPage/blobFeaturesBackground.svg';
import dragIconSrc from 'assets/LandingPage/dragIcon.png';
import flagIconSrc from 'assets/LandingPage/flagIcon.png';
import padlockIconSrc from 'assets/LandingPage/padlockIcon.png';
import S from './styles';

const KeyFeaturesSection = () => {
  return (
    <PageContainer>
      <S.FeatureTitle>Introducing our features</S.FeatureTitle>
      <S.CardsSection>
        <S.BlobBackground src={blobBgSrc} alt="Key Features Wave Background" />
        <S.Card>
          <S.IconContainer color="#eae5ed">
            <img src={dragIconSrc} alt="" width={50} height={50} />
          </S.IconContainer>
          <S.FeatureSubtitle $startColor="#cabade" $endColor="#9e88ba">
            Drag N&apos; Drop
          </S.FeatureSubtitle>
          <S.Divider color="#c3b3c9" />
          <S.Content>
            Drag and drop functionality to make planning an intuitive and easy process
          </S.Content>
        </S.Card>
        <S.Card>
          <S.IconContainer color="#eddafc">
            <img src={flagIconSrc} alt="" width={50} height={50} />
          </S.IconContainer>
          <S.FeatureSubtitle $startColor="#9b5dea" $endColor="#dbe2fc">
            Track progress
          </S.FeatureSubtitle>
          <S.Divider color="#f2ccff" />
          <S.Content>
            Plan ahead with our progression tracker, and track how far you&apos;ve gone in your
            degree
          </S.Content>
        </S.Card>
        <S.Card>
          <S.IconContainer color="#d4ffdc">
            <img src={padlockIconSrc} alt="" width={50} height={50} />
          </S.IconContainer>
          <S.FeatureSubtitle $startColor="#9fecae" $endColor="#93d392">
            Prereq Validation
          </S.FeatureSubtitle>
          <S.Divider color="#a3ebb1" />
          <S.Content>
            Verify you meet all the pre-requisites required to take any given course
          </S.Content>
        </S.Card>
      </S.CardsSection>
    </PageContainer>
  );
};

export default KeyFeaturesSection;
