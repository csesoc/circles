import { useQuery } from '@tanstack/react-query';
import { getUserPlanner } from 'utils/api/userApi';
import useIdentity from 'hooks/useIdentity';

const useUserPlanner = (allowTokenUnset?: boolean) => {
  const { userId, token } = useIdentity(allowTokenUnset === true) ?? {};

  const degreeQuery = useQuery({
    queryKey: ['user', userId!, 'planner'],
    queryFn: () => getUserPlanner(token!),
    enabled: token !== undefined
  });

  return degreeQuery;
};

export default useUserPlanner;
