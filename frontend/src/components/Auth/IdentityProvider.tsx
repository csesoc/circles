import React, { useCallback, useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { refreshTokens } from 'utils/api/authApi';
import PageLoading from 'components/PageLoading';
import { useAppDispatch, useAppSelector } from 'hooks';
import { selectIdentity, unsetIdentity, updateIdentityWithAPIRes } from 'reducers/identitySlice';

const IdentityProvider = () => {
  const dispatch = useAppDispatch();
  const { expiresAt, userId } = useAppSelector(selectIdentity) ?? {};
  const [initialLoad, setInitialLoad] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  const updateToken = useCallback(async () => {
    try {
      const newIdentity = await refreshTokens();
      if (newIdentity.uid !== userId) {
        // only clear if its a new user id, although this shouldnt really happen...
        // TODO-OLLI(pm): dont actually need to clear entire queryClient, just user storage
        queryClient.clear();
      }

      dispatch(updateIdentityWithAPIRes(newIdentity));
    } catch (e) {
      if (isAxiosError(e) && e.response?.status === 401) {
        // TODO-OLLI(pm): maybe make this a interceptor for all 401 requests
        queryClient.clear();

        dispatch(unsetIdentity());
      } else {
        throw e;
      }
    }
  }, [dispatch, queryClient, userId]);

  useEffect(() => {
    const initialRefresh = async () => {
      if (expiresAt === undefined || expiresAt * 1000 <= Date.now()) {
        // we can enter the IdentityProvider from a page that already setup an identity (LoginSuccess)
        // thus we don't have to do the initial refresh if token isn't yet expired. (let the token boundaries check validity)
        await updateToken();
      }

      setIsLoading(false);
    };

    if (initialLoad) {
      setInitialLoad(false);
      initialRefresh();
    }
  }, [updateToken, initialLoad, expiresAt]);

  useEffect(() => {
    // silent refresh, don't set loading
    if (expiresAt === undefined) {
      return () => {};
    }

    const refreshPeriod = Math.floor((expiresAt * 1000 - Date.now()) * 0.9);
    const timeout = setTimeout(updateToken, Math.max(refreshPeriod, 60000));

    return () => clearTimeout(timeout);
  }, [updateToken, expiresAt]);

  return isLoading ? <PageLoading /> : <Outlet />;
};

export default IdentityProvider;
