import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { CSELogin } from 'utils/api/authApi';
import { getUserIsSetup } from 'utils/api/userApi';
import PageLoading from 'components/PageLoading';
import { unsetIdentity, updateIdentityWithAPIRes } from 'reducers/identitySlice';

const LoginSuccess = () => {
  const dispatch = useDispatch();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [query] = useSearchParams();

  useEffect(() => {
    const exchangeCode = async () => {
      try {
        const identity = await CSELogin(Object.fromEntries(query.entries()));

        dispatch(updateIdentityWithAPIRes(identity));
        const userIsSetup = await queryClient.fetchQuery({
          queryKey: ['isSetup'], // TODO-OLLI(pm): fix this key
          queryFn: () => getUserIsSetup(identity.session_token)
        });

        navigate(userIsSetup ? '/course-selector' : '/degree-wizard', { replace: true });
      } catch (e) {
        dispatch(unsetIdentity());
        queryClient.clear();

        throw e;
      }
    };

    queryClient.clear(); // TODO-OLLI(pm): only need to clear user stuff
    exchangeCode();
  }, [query, dispatch, navigate, queryClient]);

  return <PageLoading />;
};

export default LoginSuccess;
