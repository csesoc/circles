import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { guestLogin as guestLoginRequest, initiateCSEAuth } from 'utils/api/authApi';
import openNotification from 'utils/openNotification';
import BackButton from 'assets/back.svg';
import SplashArt from 'assets/splashart.svg';
import PageTemplate from 'components/PageTemplate';
import { useAppDispatch } from 'hooks';
import { updateIdentityWithAPIRes } from 'reducers/identitySlice';
import S from './styles';

const Login = () => {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();

  // TODO-OLLI(pm): what if a user has two tabs open, logs in with one and then logs in with other??
  // similarly with logout and other authentication events
  // https://www.reddit.com/r/howdidtheycodeit/comments/wj9c65/you_signed_in_with_another_tab_or_window_reload/
  // ideas:
  // - broadcastchannel for all auth events
  // - a special cookie/localstorage state to indicate that we are already logged in
  // - onFocus
  // - quick api call before login, although this is probs BAD
  // -- can just check if a refresh token is given at the login routes
  const guestLogin = useCallback(async () => {
    let res;
    try {
      res = await guestLoginRequest();
    } catch (_) {
      openNotification({
        type: 'error',
        message: "Can't log in",
        description:
          'If you attempted to continue as guest, you may have hit a timeout. Either log in with your zID or wait until the timeout has cleared. Otherwise, there may be an issue with your user.'
      });
      return;
    }

    queryClient.clear();
    dispatch(updateIdentityWithAPIRes(res));
    // NOTE: rely on the PreventToken to do the redirecting
  }, [dispatch, queryClient]);

  return (
    <PageTemplate showHeader={false}>
      <S.LoginContainer>
        <S.Wrapper>
          <S.Left>
            <S.SplashArt src={SplashArt} />
          </S.Left>
          <S.Right>
            <S.Login>
              <Link to="/">
                <S.Back src={BackButton} />
              </Link>
              <h2>Login to Circles</h2>
              <p>For current UNSW Students</p>
              <S.LoginButton onClick={initiateCSEAuth}>Login with zID</S.LoginButton>
              <S.GuestButton onClick={guestLogin}>Continue as guest</S.GuestButton>
            </S.Login>
          </S.Right>
        </S.Wrapper>
      </S.LoginContainer>
    </PageTemplate>
  );
};

export default Login;
