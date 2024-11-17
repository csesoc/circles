import { motion } from 'framer-motion';
import styled from 'styled-components';

const HeroContent = styled.div`
  display: flex;
  flex-direction: column;
  @media (max-width: 1024px) {
    align-items: center;
  }
`;

const HeroTitle = motion(styled.h1`
  color: #fff;
  line-height: 1.2;
  font-size: 70px;
  font-weight: 650;
`);

const HeroSubTitle = styled.img`
  width: 160px;
  margin-top: -6px;
  margin-left: -8px;
`;

const HeroCTA = motion(styled.button`
  border-radius: 50px;
  background-color: #fff;
  border: none;
  width: 250px;
  height: 3.5rem;
  cursor: pointer;
  margin-bottom: 2.5rem;
  font-weight: 700;
  font-size: 1rem;
  color: #9453e6;
`);

const DevSocLogo = motion(styled.img`
  width: 160px;
`);

export default {
  DevSocLogo,
  HeroContent,
  HeroCTA,
  HeroSubTitle,
  HeroTitle
};
