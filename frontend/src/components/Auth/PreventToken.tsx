import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { isAxiosError } from 'axios';
import { useUserSetupState } from 'utils/apiHooks/user';
import PageLoading from 'components/PageLoading';
import { useAppSelector } from 'hooks';
import { selectToken } from 'reducers/identitySlice';

const PreventToken = () => {
  const token = useAppSelector(selectToken);

  const {
    isPending,
    data: isSetup,
    error
  } = useUserSetupState({
    allowUnsetToken: true,
    queryOptions: { refetchOnWindowFocus: 'always' }
  });

  if (token === undefined) {
    // good
    return <Outlet />;
  }

  if (error) {
    // TODO-OLLI(pm): check RequireToken for relevant comments
    if (isAxiosError(error) && error.response?.status === 401) {
      window.location.reload();
    } else {
      throw error;
    }
  }

  if (isPending || isSetup === undefined) {
    return <PageLoading />;
  }

  return <Navigate to={isSetup ? '/course-selector' : '/degree-wizard'} />;
};

export default PreventToken;

// can't just check if token is undefined since
// - we dispatch the token update and then navigate inside guestLogin
// - but the before the navigate, this component rerenders
// - meaning that we get the notification and navigate, before the login navigates
// solution?
// - useQuery to add some delay (actually needed since we dont know where we want to go)
// - dont navigate in container, rely on this navigate and remove the notification
// - perform the actual fetch dispatch on a different page and guestLogin just navigates there
// -.. move guestLogin into a thunk, and .then chain the navigate? not sure if this works
// -/- move to a data router and then we have access to the useNavigation...
// - combine the PreventToken into the login page, and then no parent to rerender
