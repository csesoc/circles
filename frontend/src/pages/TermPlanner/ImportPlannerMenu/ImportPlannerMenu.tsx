import React, { useRef, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';
import { Spin } from 'antd';
import { useImportUserMutation } from 'utils/apiHooks/user';
import { importUser, UserJson } from 'utils/export';
import openNotification from 'utils/openNotification';
import CS from '../common/styles';
import S from './styles';

const ImportPlannerMenu = () => {
  const importUserMutation = useImportUserMutation();

  const handleImport = (user: UserJson) => {
    importUserMutation.mutate(user);
  };

  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);

  const upload = () => {
    inputRef.current?.click();
  };

  const uploadedJSONFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files === null) {
      return;
    }

    if (e.target.files[0].type !== 'application/json') {
      openNotification({
        type: 'error',
        message: 'Import file needs to be JSON.',
        description: 'The uploaded file is not of type JSON.'
      });
      e.target.value = '';
      return;
    }

    setLoading(true);
    const reader = new FileReader();
    reader.readAsText(e.target.files[0], 'UTF-8');
    reader.onload = async (ev) => {
      if (ev.target === null) {
        return;
      }

      const content = ev.target.result;
      e.target.value = '';

      try {
        const fileInJson = JSON.parse(content as string) as JSON;
        const user = importUser(fileInJson);
        handleImport(user);
        setLoading(false);
      } catch (err) {
        setLoading(false);
        // eslint-disable-next-line no-console
        console.error('Error at uploadedJSONFile', err);
        openNotification({
          type: 'error',
          message: 'Invalid JSON format',
          description: 'An error occured when parsing the JSON file'
        });
        return;
      }

      openNotification({
        type: 'success',
        message: 'JSON Imported',
        description: 'Planner has been successfully imported.'
      });
    };
  };

  const spinIcon = <LoadingOutlined style={{ fontSize: 28 }} spin />;

  return (
    <S.Wrapper style={{ width: '240px' }}>
      <CS.MenuHeader>Import</CS.MenuHeader>
      <CS.MenuDivider />
      <div>Import an existing planner if you have exported it previously as a JSON file.</div>
      <div>If you currently have courses planned, it may be merged with the imported planner.</div>
      <>
        <div style={{ display: 'flex' }}>
          <CS.Button style={{ width: '150px', margin: '5px' }} onClick={upload}>
            Upload a planner
          </CS.Button>
          {loading && <Spin indicator={spinIcon} />}
        </div>
        <input type="file" style={{ display: 'none' }} ref={inputRef} onChange={uploadedJSONFile} />
      </>
    </S.Wrapper>
  );
};

export default ImportPlannerMenu;
