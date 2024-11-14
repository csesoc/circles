import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';
import { IdentityResponse } from 'utils/api/authApi';

export type CompleteIdentity = {
  token: string;
  userId: string;
  expiresAt: number;
};

// Either we have the entire identity or no properties at all...
type IdentitySliceState = CompleteIdentity | null;

export const initialIdentityState: IdentitySliceState = null;

const identitySlice = createSlice({
  name: 'identity',
  initialState: initialIdentityState as IdentitySliceState, // make sure it infers the correct type
  selectors: {
    selectToken: (state) => state?.token,
    selectIdentity: (state) => state
  },
  reducers: {
    updateIdentity: (state, action: PayloadAction<CompleteIdentity>) => ({
      expiresAt: action.payload.expiresAt,
      token: action.payload.token,
      userId: action.payload.userId
    }),
    updateIdentityWithAPIRes: (state, action: PayloadAction<IdentityResponse>) => ({
      expiresAt: action.payload.exp,
      token: action.payload.session_token,
      userId: action.payload.uid
    }),
    unsetIdentity: () => initialIdentityState
  }
});

export const { updateIdentity, updateIdentityWithAPIRes, unsetIdentity } = identitySlice.actions;
export const { selectToken, selectIdentity } = identitySlice.selectors;

export default identitySlice.reducer;
