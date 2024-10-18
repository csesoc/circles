import React from 'react';
import { Modal } from 'antd';
import { useResetDegreeMutation } from 'utils/apiHooks/user';
import { useAppDispatch } from 'hooks';
import useToken from 'hooks/useToken';
import { resetTabs } from 'reducers/courseTabsSlice';

type Props = {
  open?: boolean;
  onOk?: () => void; // runs after resetting the data
  onCancel?: () => void;
};

// has no internal "open" state since it becomes difficult to juggle with external buttons
const ResetModal = ({ open, onOk, onCancel }: Props) => {
  const dispatch = useAppDispatch();
  const token = useToken({ allowUnset: true }); // NOTE: must allow unset since this is used in ErrorBoundary itself

  const resetDegreeMutation = useResetDegreeMutation({ allowUnsetToken: true });
  const handleResetDegree = () => {
    if (token !== undefined) {
      resetDegreeMutation.mutate();
    }
  };

  const handleOk = async () => {
    handleResetDegree();
    dispatch(resetTabs());
    onOk?.();
  };

  return (
    <Modal
      title="Reset Planner?"
      open={open ?? false}
      closable={false}
      onOk={handleOk}
      okText="Reset Data"
      okButtonProps={{ type: 'primary', danger: true }}
      onCancel={onCancel}
      cancelText="Go to Course Selector"
    >
      <div>
        You can navigate to the Degree Wizard to reset your data. By clicking Ok, Your existing data
        will be permanently removed.
      </div>
    </Modal>
  );
};

export default ResetModal;
