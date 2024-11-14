import { useAppSelector } from 'hooks';
import { CompleteIdentity, selectIdentity } from 'reducers/identitySlice';

function useIdentity(allowUnset?: false): CompleteIdentity;
function useIdentity(allowUnset: true): CompleteIdentity | null;
function useIdentity(allowUnset: boolean): CompleteIdentity | null;

function useIdentity(allowUnset?: boolean): CompleteIdentity | null {
  const identity = useAppSelector(selectIdentity);

  if (identity === null && allowUnset !== true) {
    throw TypeError(`useIdentity: allowUnset was false and identity was null.`);
  }

  return identity;
}

export default useIdentity;
