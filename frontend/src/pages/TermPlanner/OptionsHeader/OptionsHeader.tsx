/* eslint-disable import/no-extraneous-dependencies */
import React from 'react';
import { FaRegCalendarTimes } from 'react-icons/fa';
import {
  DownloadOutlined,
  EyeFilled,
  QuestionCircleOutlined,
  SettingFilled,
  UploadOutlined,
  WarningFilled
} from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import Tippy from '@tippyjs/react';
import { Popconfirm, Switch, Tooltip } from 'antd';
import { unscheduleAll } from 'utils/api/plannerApi';
import useUserPlanner from 'utils/apiHooks/useUserPlanner';
import useSettings from 'hooks/useSettings';
import useToken from 'hooks/useToken';
import ExportPlannerMenu from '../ExportPlannerMenu';
import HelpMenu from '../HelpMenu/HelpMenu';
import ImportPlannerMenu from '../ImportPlannerMenu';
import SettingsMenu from '../SettingsMenu';
import { isPlannerEmpty } from '../utils';
import S from './styles';
// Used for tippy stylings
import 'tippy.js/dist/tippy.css';
import 'tippy.js/themes/light.css';

const OptionsHeader = () => {
  const token = useToken();
  const queryClient = useQueryClient();

  const plannerQuery = useUserPlanner();
  const planner = plannerQuery.data;

  const {
    theme,
    showMarks,
    showPastWarnings,
    hiddenYears,
    toggleShowMarks,
    toggleShowPastWarnings,
    showYears
  } = useSettings();
  const iconStyles = {
    fontSize: '20px',
    color: theme === 'light' ? '#323739' : '#f1f1f1'
  };

  const unscheduleAllMutation = useMutation({
    mutationFn: () => unscheduleAll(token),
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
    },
    onError: (err) => {
      // eslint-disable-next-line no-console
      console.error('Error at unscheduleAllMutation: ', err);
    }
  });

  const handleUnscheduleAll = async () => {
    unscheduleAllMutation.mutate();
  };

  return (
    <S.OptionsHeaderWrapper>
      <S.OptionSection>
        <Tippy
          content={<SettingsMenu planner={planner} />}
          moveTransition="transform 0.2s ease-out"
          interactive
          trigger="click"
          theme={theme}
          zIndex={1}
          placement="bottom-start"
          disabled={!planner}
        >
          <div>
            <Tooltip title="Settings">
              <S.OptionButton>
                <SettingFilled style={iconStyles} />
              </S.OptionButton>
            </Tooltip>
          </div>
        </Tippy>
        <Tippy
          content={<ExportPlannerMenu />}
          moveTransition="transform 0.2s ease-out"
          interactive
          trigger="click"
          theme={theme}
          zIndex={1}
          placement="bottom-start"
        >
          <div>
            <Tooltip title="Export">
              <S.OptionButton>
                <DownloadOutlined style={iconStyles} />
              </S.OptionButton>
            </Tooltip>
          </div>
        </Tippy>
        <Tippy
          content={<ImportPlannerMenu />}
          moveTransition="transform 0.2s ease-out"
          interactive
          trigger="click"
          theme={theme}
          zIndex={1}
          placement="bottom-start"
        >
          <div>
            <Tooltip title="Import">
              <S.OptionButton>
                <UploadOutlined style={iconStyles} />
              </S.OptionButton>
            </Tooltip>
          </div>
        </Tippy>

        {planner && !isPlannerEmpty(planner) && (
          <Tooltip title="Unplan all courses">
            <Popconfirm
              placement="bottomRight"
              title="Are you sure you want to unplan all your courses?"
              onConfirm={handleUnscheduleAll}
              style={{ width: '200px' }}
              okText="Yes"
              cancelText="No"
              overlayClassName="popconfirm-unplan"
            >
              <S.OptionButton>
                <FaRegCalendarTimes style={iconStyles} />
              </S.OptionButton>
            </Popconfirm>
          </Tooltip>
        )}
        {hiddenYears.length > 0 && (
          <Tooltip title="Show all hidden years">
            <S.OptionButton onClick={() => showYears()}>
              <EyeFilled style={iconStyles} />
            </S.OptionButton>
          </Tooltip>
        )}
        <Tooltip title="Toggle warnings for previous terms">
          <S.OptionButton onClick={() => toggleShowPastWarnings()}>
            <WarningFilled
              style={{
                ...iconStyles,
                ...(showPastWarnings && { color: theme === 'light' ? '#9254de' : '#c198ef' })
              }}
            />
          </S.OptionButton>
        </Tooltip>
      </S.OptionSection>

      <S.OptionSection>
        <S.ShowMarks>
          <S.TextShowMarks>Show Marks</S.TextShowMarks>
          <Switch defaultChecked={showMarks} onChange={() => toggleShowMarks()} />
        </S.ShowMarks>
        <Tippy
          content={<HelpMenu />}
          moveTransition="transform 0.2s ease-out"
          interactive
          trigger="click"
          theme={theme}
          maxWidth="80vh"
          placement="bottom-start"
        >
          <div>
            <Tooltip title="Help">
              <S.OptionButton>
                <QuestionCircleOutlined style={iconStyles} />
              </S.OptionButton>
            </Tooltip>
          </div>
        </Tippy>
      </S.OptionSection>
    </S.OptionsHeaderWrapper>
  );
};

export default OptionsHeader;
