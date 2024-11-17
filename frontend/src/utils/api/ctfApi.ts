import axios from 'axios';
import { withAuthorization } from './authApi';

export type CtfResult = {
  valid: boolean;
  failed: number;
  passed: Array<string>;
  message: string;
  flags: Array<string>;
};

// lol
export const validateCtf = async (token: string): Promise<CtfResult> => {
  const res = await axios.post<CtfResult>(
    '/ctf/validateCtf/',
    {},
    { headers: withAuthorization(token) }
  );

  return res.data;
};
