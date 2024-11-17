import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRightOutlined } from '@ant-design/icons';
import { Space } from 'antd';
import devsocLogo from 'assets/devsocLogo.svg';
import easySubTitle from 'assets/LandingPage/easySubtitle.svg';
import S from './styles';

type Props = {
  startLocation: string;
};

const HeroContent = ({ startLocation }: Props) => {
  return (
    <S.HeroContent>
      <S.HeroTitle animate={{ x: [-60, 10, 0] }} transition={{ duration: 1, ease: 'easeInOut' }}>
        Degree planning made <S.HeroSubTitle src={easySubTitle} alt="Hero Subtitle" />
      </S.HeroTitle>
      <Link to={startLocation}>
        <S.HeroCTA
          initial={{ scale: 0.0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 10 }}
          whileHover={{ scale: 1.1 }}
        >
          GET STARTED <Space size="large" />
          <ArrowRightOutlined style={{ strokeWidth: '5rem', stroke: '#9453e6' }} />
        </S.HeroCTA>
      </Link>
      <S.DevSocLogo
        src={devsocLogo}
        alt="DevSoc Logo"
        initial={{ opacity: 0, scale: 0.5, x: 100 }}
        animate={{ opacity: 1, scale: 1, x: 0 }}
        transition={{ duration: 1 }}
      />
    </S.HeroContent>
  );
};

export default HeroContent;
