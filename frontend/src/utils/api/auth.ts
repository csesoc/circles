import axios from 'axios';

export enum TokenStatus {
  UNSET = 'unset',
  EXPIRED = 'expired',
  NOTSETUP = 'notsetup',
  SETUP = 'setup'
}

interface OldIdentityPayload {
  session_token: string;
}

export type IdentityResponse = {
  session_token: string;
  exp: number;
  uid: string;
};

export const guestLogin = async (): Promise<IdentityResponse> => {
  const res = await axios.post<IdentityResponse>(
    '/auth/guest_login',
    {},
    { withCredentials: true }
  );

  return res.data;
};

export const logout = async (token: string): Promise<void> => {
  await axios.delete<void>('/auth/logout', {
    withCredentials: true,
    headers: { Authorization: `Bearer ${token}` }
  });
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars, no-unused-vars
export const checkTokenStatus = async (token: string | undefined): Promise<TokenStatus> => {
  if (token === undefined) {
    return TokenStatus.UNSET;
  }

  const res = await axios.get<TokenStatus>('/auth/tokenUserState', {
    headers: { Authorization: `Bearer ${token}` }
  });

  return res.data;
};

export const exchangeAuthCode = async (
  query_params: Record<string, string>
): Promise<OldIdentityPayload> => {
  console.log(`exchanging`);
  const res = await axios.post<OldIdentityPayload>(
    '/auth/login',
    { query_params },
    { withCredentials: true }
  );
  console.log('exchange result:', res);
  return res.data;
};

export const refreshTokens = async (): Promise<IdentityResponse> => {
  // NOTE: will raise a 401 if could not refresh
  console.log('-- refreshing tokens');
  const res = await axios.post<IdentityResponse>('/auth/refresh', {}, { withCredentials: true });

  return res.data;
};
