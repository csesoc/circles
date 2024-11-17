import React from 'react';
import { PlusOutlined, StopOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { Course } from 'types/api';
import { useAddToUnplannedMutation, useRemoveCourseMutation } from 'utils/apiHooks/user';
import S from './styles';

interface PlannerButtonProps {
  course: Course;
  isAddedInPlanner: boolean;
}

const PlannerButton = ({ course, isAddedInPlanner }: PlannerButtonProps) => {
  const removeCourseMutation = useRemoveCourseMutation();
  const addToUnplannedMutation = useAddToUnplannedMutation();

  const mutation = isAddedInPlanner ? removeCourseMutation : addToUnplannedMutation;

  const handleClick = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    mutation.mutate(course.code);
  };

  return isAddedInPlanner ? (
    <S.Button loading={mutation.isPending} onClick={handleClick} icon={<StopOutlined />}>
      {!mutation.isPending ? 'Remove from planner' : 'Removing from planner'}
    </S.Button>
  ) : (
    <Button
      loading={mutation.isPending}
      onClick={handleClick}
      icon={<PlusOutlined />}
      type="primary"
    >
      {!mutation.isPending ? 'Add to planner' : 'Adding to planner'}
    </Button>
  );
};

export default PlannerButton;
