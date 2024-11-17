import React from 'react';
import { getUser } from 'utils/api/userApi';
import { exportUser } from 'utils/export';
import useToken from 'hooks/useToken';
import CS from '../common/styles';
import S from './styles';

const ExportPlannerMenu = () => {
  const token = useToken();

  const download = async () => {
    getUser(token)
      .then((user) => {
        const exported = exportUser(user);
        const blob = new Blob([JSON.stringify(exported)], { type: 'application/json' });
        const jsonObjectUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = jsonObjectUrl;
        const date = new Date();
        a.download = `circles-planner-export-${date.toISOString()}.json`;
        a.click();
      })
      .catch((err) => {
        // eslint-disable-next-line no-console
        console.error('Error at exportPlannerMenu: ', err);
      });
  };

  return (
    <S.Wrapper style={{ width: '240px' }}>
      <CS.MenuHeader>Export</CS.MenuHeader>
      <CS.MenuDivider />
      <div>Export your planner and settings as JSON. Can be re-imported later.</div>
      <CS.Button onClick={download}> Download </CS.Button>
    </S.Wrapper>
  );
};

export default ExportPlannerMenu;
