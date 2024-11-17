import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { logout } from 'utils/api/authApi';
import PageLoading from 'components/PageLoading';
import { useAppDispatch, useAppSelector } from 'hooks';
import { selectToken, unsetIdentity } from 'reducers/identitySlice';

const Logout = () => {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  const token = useAppSelector(selectToken);
  const navigate = useNavigate();

  useEffect(() => {
    const performLogout = async () => {
      try {
        if (token !== undefined) {
          await logout(token);
        }
      } catch (e) {
        // NOTE: this is ok, can happen if logged out on other tab before
        // eslint-disable-next-line no-console
        console.error(e);
      } finally {
        queryClient.clear();
        dispatch(unsetIdentity());

        // use window.location.replace over navigate to try delete all data/effects
        // this is very important for the refresh timeouts
        window.location.replace('/');
      }
    };

    performLogout();
  }, [token, dispatch, queryClient, navigate]);

  return <PageLoading />;
};

export default Logout;
