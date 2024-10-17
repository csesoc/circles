import { useQuery } from '@tanstack/react-query';
import { getUserDegree } from 'utils/api/userApi';
import useIdentity from 'hooks/useIdentity';

const useUserDegree = (allowTokenUnset?: boolean) => {
  const { userId, token } = useIdentity(allowTokenUnset === true) ?? {};

  const degreeQuery = useQuery({
    queryKey: ['user', userId!, 'degree'],
    queryFn: () => getUserDegree(token!),
    enabled: token !== undefined
  });

  return degreeQuery;
};

export default useUserDegree;
