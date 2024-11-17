/* eslint-disable jsx-a11y/no-static-element-interactions */
/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from 'antd';
import { importUser as importUserApi } from 'utils/api/userApi';
import { importUser, UserJson } from 'utils/export';
import openNotification from 'utils/openNotification';
import useToken from 'hooks/useToken';
import { resetTabs } from 'reducers/courseTabsSlice';
import { resetSettings } from 'reducers/settingsSlice';

type Props = {
  open?: boolean;
  onOk?: () => void; // runs after resetting the data
  onCancel?: () => void;
};

function migrationErrorNotification() {
  openNotification({
    type: 'error',
    message: 'Migration failed',
    description:
      'An error occurred whilst migrating your data. Either try again, reset your data, or download your data and attempt to import it again/contact DevSoc for help.'
  });
}

const MigrationModal = ({ open, onOk, onCancel }: Props) => {
  const dispatch = useDispatch();
  const token = useToken();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const importUserMutation = useMutation({
    mutationFn: (user: UserJson) => importUserApi(token, user),
    onSuccess: () => {
      localStorage.removeItem('oldUser');
      queryClient.resetQueries();
      navigate('/course-selector');
      onOk?.();
    },
    onError: () => {
      migrationErrorNotification();
    }
  });

  const clearOldUser = () => {
    localStorage.removeItem('oldUser');
    dispatch(resetSettings());
    dispatch(resetTabs());
    onCancel?.();
  };

  const handleMigration = async () => {
    try {
      const user = importUser(JSON.parse(localStorage.getItem('oldUser')!) as JSON);
      importUserMutation.mutate(user);
    } catch (error) {
      migrationErrorNotification();
    }
  };

  const download = () => {
    const blob = new Blob([localStorage.getItem('oldUser')!], { type: 'application/json' });
    const jsonObjectUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = jsonObjectUrl;
    const date = new Date();
    a.download = `circles-planner-export-${date.toISOString()}.json`;
    a.click();
  };

  return (
    <Modal
      title="Local Circles Data Detected (Pre Nov 2024)"
      open={open ?? false}
      closable={false}
      onOk={handleMigration}
      okButtonProps={{ type: 'primary' }}
      okText="Migrate Old Data"
      onCancel={clearOldUser}
      cancelText="Clear Old Data"
      cancelButtonProps={{ type: 'primary', danger: true }}
      mask
      maskClosable={false}
      keyboard={false}
    >
      <div>
        <p>
          As you may have noticed, Circles moved to a login system in 2024 Term 3. We&apos;ve
          detected an old planner saved locally, and can attempt to migrate it for you. You can also{' '}
          <a onClick={download}>download</a> it for importing later.
        </p>
        <p>
          If you&apos;re signed in as a guest, you may wish to <a href="/logout">logout</a> and sign
          in with your zID to save your data in the long term.
        </p>
      </div>
    </Modal>
  );
};

export default MigrationModal;
