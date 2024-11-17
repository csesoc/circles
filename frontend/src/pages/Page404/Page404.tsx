import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from 'antd';
import circlesLogo from 'assets/circlesLogo.svg';
import PageTemplate from 'components/PageTemplate';
import S from './syles';

const Page404 = () => {
  const navigate = useNavigate();

  return (
    <PageTemplate showHeader={false}>
      <S.PageWrapper>
        <S.GridCircleWrapper>
          <S.LogoBox>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox $alt>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox $alt>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox $alt>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox $alt>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox $alt>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox $alt>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
          <S.LogoBox>
            <img alt="circles-logo" src={circlesLogo} width="200" height="200" />
          </S.LogoBox>
        </S.GridCircleWrapper>
      </S.PageWrapper>
      <S.TextWrapper>
        <S.Title404>404</S.Title404>
        <S.Text404>PAGE NOT FOUND</S.Text404>
        <Button type="primary" size="large" onClick={() => navigate('/')}>
          Go Back Home
        </Button>
      </S.TextWrapper>
    </PageTemplate>
  );
};

export default Page404;
