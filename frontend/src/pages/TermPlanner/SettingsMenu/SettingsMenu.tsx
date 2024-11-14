import React, { Suspense } from 'react';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { DatePicker, Modal, Select, Switch } from 'antd';
import dayjs from 'dayjs';
import { PlannerResponse } from 'types/userResponse';
import {
  useToggleSummerTermMutation,
  useUpdateDegreeLengthMutation,
  useUpdateStartYearMutation
} from 'utils/apiHooks/user';
import Spinner from 'components/Spinner';
import useSettings from 'hooks/useSettings';
import CS from '../common/styles';

type Props = {
  planner?: PlannerResponse;
};

const SettingsMenu = ({ planner }: Props) => {
  const { Option } = Select;
  const { theme } = useSettings();

  function willUnplanCourses(numYears: number) {
    if (!planner) return false;

    if (numYears < planner.years.length) {
      for (let i = numYears; i < planner.years.length; i++) {
        if (Object.values(planner.years[i]).flat().length > 0) return true;
      }
    }

    return false;
  }

  const updateStartYearMutation = useUpdateStartYearMutation();

  const handleUpdateStartYear = async (_: unknown, dateString: string | string[]) => {
    if (dateString && typeof dateString === 'string') {
      updateStartYearMutation.mutate(dateString);
    } else {
      // eslint-disable-next-line no-console
      console.error('Error updating start year. Invalid date string:', dateString);
    }
  };

  const updateDegreeLengthMutation = useUpdateDegreeLengthMutation();

  const handleUpdateDegreeLength = async (value: number) => {
    if (willUnplanCourses(value)) {
      Modal.confirm({
        title: 'Unplanned Courses',
        content:
          'Changing the degree length will unplan courses. Are you sure you want to continue?',
        onOk: () => updateDegreeLengthMutation.mutate(value)
      });
    } else {
      updateDegreeLengthMutation.mutate(value);
    }
  };

  const summerToggleMutation = useToggleSummerTermMutation();

  const handleSummerToggle = async () => {
    summerToggleMutation.mutate();
  };

  const years = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  // The settings menu *should* be disabled a layer up if there is no planner
  if (!planner) {
    return null;
  }

  return (
    <CS.MenuPopup>
      <CS.MenuHeader>Settings</CS.MenuHeader>
      <CS.MenuDivider />
      <CS.PopupEntry>
        <CS.MenuText>Summer Term</CS.MenuText>
        <Switch
          defaultChecked={planner.isSummerEnabled}
          onChange={handleSummerToggle}
          checkedChildren={<CheckOutlined />}
          unCheckedChildren={<CloseOutlined />}
        />
      </CS.PopupEntry>
      <CS.PopupEntry className="settings-start-year-popup">
        <CS.MenuText>Start Year</CS.MenuText>
        <Suspense fallback={<Spinner text="Loading Year Selector..." />}>
          <DatePicker
            onChange={handleUpdateStartYear}
            picker="year"
            style={{ width: 105 }}
            value={dayjs().year(planner.startYear)}
            minDate={dayjs('2019')}
            maxDate={dayjs().add(7, 'year')}
          />
        </Suspense>
      </CS.PopupEntry>
      <CS.PopupEntry className="settings-degree-length-popup">
        <CS.MenuText>Degree Length</CS.MenuText>
        <Select
          value={planner.years.length}
          style={{ width: 70 }}
          dropdownStyle={{
            backgroundColor: theme === 'light' ? '#fff' : '#444249',
            color: theme === 'light' ? '#444249' : '#fff'
          }}
          onChange={handleUpdateDegreeLength}
          className="settings-degree-length-popup"
        >
          {years.map((num) => (
            <Option key={num} value={num} className="settings-degree-length-popup">
              {num}
            </Option>
          ))}
        </Select>
      </CS.PopupEntry>
    </CS.MenuPopup>
  );
};

export default SettingsMenu;
