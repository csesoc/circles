import React from 'react';
import { EyeInvisibleFilled } from '@ant-design/icons';
import { Tooltip } from 'antd';
import { badPlanner, PlannerResponse } from 'types/userResponse';
import { useUserPlanner } from 'utils/apiHooks/user';
import openNotification from 'utils/openNotification';
import useSettings from 'hooks/useSettings';

type Props = {
  year: number;
};

const HideYearTooltip = ({ year }: Props) => {
  const { hiddenYears, hideYear } = useSettings();

  const plannerQuery = useUserPlanner();
  const planner: PlannerResponse = plannerQuery.data ?? badPlanner;
  const numYears = planner.years.length;

  const handleHideYear = () => {
    if (hiddenYears.length === numYears - 1) {
      openNotification({
        type: 'error',
        message: "Something's not right",
        description: 'You cannot hide all years in your term planner'
      });
    } else {
      hideYear(year);
    }
  };

  return (
    <Tooltip title="Hide year">
      {/* TODO: Hacky way to have className for YearWrapper styling */}
      <div role="button" className="year-tooltip" onClick={handleHideYear} aria-label="Hide year">
        <EyeInvisibleFilled />
      </div>
    </Tooltip>
  );
};

export default HideYearTooltip;
