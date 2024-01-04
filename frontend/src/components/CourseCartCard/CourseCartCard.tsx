import React from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { DeleteOutlined } from '@ant-design/icons';
import { Button, Popconfirm, Tooltip, Typography } from 'antd';
import { removeCourse } from 'utils/api/plannerApi';
import { addTab } from 'reducers/courseTabsSlice';
import S from './styles';

const { Text } = Typography;

type Props = {
  code: string;
  title: string;
};

const CourseCartCard = ({ code, title }: Props) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleClick = () => {
    navigate('/course-selector');
    dispatch(addTab(code));
  };

  const remove = useMutation(removeCourse, {
    onSuccess: () => {
      queryClient.invalidateQueries('courses');
      queryClient.invalidateQueries('planner');
    }
  });

  return (
    <S.CourseCardWrapper>
      <div role="menuitem" onClick={handleClick}>
        <Text className="text" strong>
          {code}:&nbsp;
        </Text>
        <Text className="text">{title}</Text>
      </div>
      <Popconfirm
        placement="bottomRight"
        title="Remove this course from your planner?"
        onConfirm={() => () => remove.mutate(code)}
        style={{ width: '200px' }}
        okText="Yes"
        cancelText="No"
      >
        <Tooltip title={`Remove ${code}`}>
          <Button danger size="small" shape="circle" icon={<DeleteOutlined />} />
        </Tooltip>
      </Popconfirm>
    </S.CourseCardWrapper>
  );
};

export default CourseCartCard;
