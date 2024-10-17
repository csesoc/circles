import { useQuery } from '@tanstack/react-query';
import { getUserCourses } from 'utils/api/userApi';
import useIdentity from 'hooks/useIdentity';

const useUserCourses = (allowTokenUnset?: boolean) => {
  const { userId, token } = useIdentity(allowTokenUnset === true) ?? {};

  const coursesQuery = useQuery({
    queryKey: ['user', userId!, 'planner', 'courses'],
    queryFn: () => getUserCourses(token!),
    enabled: token !== undefined
  });

  return coursesQuery;
};

export default useUserCourses;
