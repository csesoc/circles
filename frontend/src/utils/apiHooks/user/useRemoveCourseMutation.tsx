import { useMutation, useQueryClient } from '@tanstack/react-query';
import { removeCourse } from 'utils/api/plannerApi';
import useToken from 'hooks/useToken';

const useRemoveCourseMutation = () => {
  const token = useToken();

  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (courseCode: string) => removeCourse(token, courseCode),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['user', 'planner']
      });
    }
  });

  return mutation;
};

export default useRemoveCourseMutation;
