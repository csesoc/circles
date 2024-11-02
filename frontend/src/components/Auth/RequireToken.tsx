import React, { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { isAxiosError } from 'axios';
import { useUserSetupState } from 'utils/apiHooks/user';
import openNotification from 'utils/openNotification';
import PageLoading from 'components/PageLoading';
import { useAppSelector } from 'hooks';
import { selectIdentity } from 'reducers/identitySlice';

type Props = {
  needSetup?: boolean;
};

const RequireToken = ({ needSetup }: Props) => {
  const { token } = useAppSelector(selectIdentity) ?? {};

  const {
    isPending,
    data: isSetup,
    error
  } = useUserSetupState({
    allowUnsetToken: true,
    queryOptions: { refetchOnWindowFocus: 'always' }
  });
  // TODO-OLLI(pm): multitab support is hard

  useEffect(() => {
    // TODO-OLLI(pm): wont need this when we get new notification hook
    if (token === undefined || !!error) {
      openNotification({
        type: 'error',
        message: 'Error',
        description: 'You must be logged in before visiting this page 🙂'
      });
    } else if (isSetup === false && !!needSetup) {
      openNotification({
        type: 'warning',
        message: 'Warning',
        description: 'You must setup your degree before visiting this page 🙂'
      });
    }
  }, [token, isSetup, error, needSetup]);

  if (token === undefined) {
    return <Navigate to="/login" />;
  }

  if (error) {
    // must be a 401 axios error, even though it should be auto refreshing, so likely session died for other reasons and couldnt notice it...
    // something like a logout from another tab
    // TODO-OLLI(pm): do we want to do better handling here like redirect, clear cache and unset? maybe redirect to logout when that is robust
    // TODO-OLLI(pm): especially this could just lead to infinite reloading if backend bugs and never gives good session token
    // ideal solution: make all other querys and mutations have proper error handling,
    // and then this component only really helps with redirect, and doesn't handle the 401 errors (since they shouldn't really happen)
    if (isAxiosError(error) && error.response?.status === 401) {
      window.location.reload();
    } else {
      throw error; // NOTE: not using `throwOnError` from reactQuery, since this seems to override `retryOnMount`
    }
  }

  if (isPending || isSetup === undefined) {
    return <PageLoading />;
  }

  if (!isSetup && !!needSetup) {
    return <Navigate to="/degree-wizard" />;
  }

  return <Outlet />;
};

export default RequireToken;
