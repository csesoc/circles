import React, { useState } from 'react';
import { Item, Menu } from 'react-contexify';
import { FaRegCalendarTimes } from 'react-icons/fa';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  DeleteFilled,
  EditFilled,
  InfoCircleFilled,
  PieChartFilled,
  PieChartOutlined,
  StarOutlined
} from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { UnscheduleCourse } from 'types/planner';
import { toggleIgnoreFromProgression, unscheduleCourse } from 'utils/api/plannerApi';
import { useRemoveCourseMutation } from 'utils/apiHooks/user';
import EditMarkModal from 'components/EditMarkModal';
import useToken from 'hooks/useToken';
import { addTab } from 'reducers/courseTabsSlice';
import 'react-contexify/ReactContexify.css';

type Props = {
  code: string;
  plannedFor: string | null;
  ignoreFromProgression: boolean;
};

const ContextMenu = ({ code, plannedFor, ignoreFromProgression }: Props) => {
  const token = useToken();

  const queryClient = useQueryClient();
  const [openModal, setOpenModal] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const showEditMark = () => setOpenModal(true);
  const handleUnschedule = useMutation({
    mutationFn: (data: UnscheduleCourse) => unscheduleCourse(token, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['planner']
      });
      queryClient.invalidateQueries({
        queryKey: ['courses']
      });
      queryClient.invalidateQueries({
        queryKey: ['validate']
      });
    }
  });

  const handleDelete = useRemoveCourseMutation();

  const handleInfo = () => {
    navigate('/course-selector');
    dispatch(addTab(code));
  };
  const ignoreFromProgressionMutation = useMutation({
    mutationFn: (courseId: string) => toggleIgnoreFromProgression(token, courseId),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ['courses']
      })
  });
  const handleToggleProgression = () => {
    ignoreFromProgressionMutation.mutate(code);
  };

  const handleUnilective = () => {
    window.open(`https://unilectives.devsoc.app/course/${code}`, '_blank');
  };

  const iconStyle = {
    fontSize: '14px',
    marginRight: '5px'
  };

  return (
    <>
      <Menu id={`${code}-context`} theme="dark">
        {plannedFor && (
          <Item
            onClick={() =>
              handleUnschedule.mutate({
                courseCode: code
              })
            }
          >
            <FaRegCalendarTimes style={iconStyle} /> Unschedule
          </Item>
        )}
        <Item onClick={() => handleDelete.mutate(code)}>
          <DeleteFilled style={iconStyle} /> Delete from Planner
        </Item>
        <Item onClick={showEditMark}>
          <EditFilled style={iconStyle} /> Edit mark
        </Item>
        {ignoreFromProgression ? (
          <Item onClick={handleToggleProgression}>
            <PieChartFilled style={iconStyle} /> Acknowledge Progression
          </Item>
        ) : (
          <Item onClick={handleToggleProgression}>
            <PieChartOutlined style={iconStyle} /> Ignore Progression
          </Item>
        )}
        <Item onClick={handleInfo}>
          <InfoCircleFilled style={iconStyle} /> View Info
        </Item>
        <Item onClick={handleUnilective}>
          <StarOutlined style={iconStyle} /> View on unilectives
        </Item>
      </Menu>
      <EditMarkModal code={code} open={openModal} onCancel={() => setOpenModal(false)} />
    </>
  );
};

export default ContextMenu;
