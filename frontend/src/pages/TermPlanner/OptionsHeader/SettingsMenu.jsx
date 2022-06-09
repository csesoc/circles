import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { CheckOutlined, CloseOutlined } from "@ant-design/icons";
import {
  DatePicker, Divider,
  Select, Switch, Typography,
} from "antd";
import moment from "moment";
import { toggleSummer, updateDegreeLength, updateStartYear } from "reducers/plannerSlice";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/light.css";
import "./index.less";

const SettingsMenu = () => {
  const { Title } = Typography;
  const { Option } = Select;
  const { isSummerEnabled, numYears, startYear } = useSelector((state) => state.planner);

  const dispatch = useDispatch();

  function handleUpdateStartYear(date, dateString) {
    if (dateString) {
      dispatch(updateStartYear(dateString));
    }
  }

  function handleUpdateDegreeLength(value) {
    dispatch(updateDegreeLength(value));
  }

  function handleSummerToggle() {
    dispatch(toggleSummer());
  }

  const years = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  return (
    <div className="settingsMenu">
      <div className="settingsTitleContainer">
        <Title level={2} strong className="text settingsTitle">
          Settings
        </Title>
        <Divider className="settingsDivider" />
      </div>
      <div className="settingsEntry">
        <Title level={3} className="text settingsSubtitle">
          Summer Term
        </Title>
        <Switch
          defaultChecked={isSummerEnabled}
          onChange={handleSummerToggle}
          checkedChildren={<CheckOutlined />}
          unCheckedChildren={<CloseOutlined />}
        />
      </div>
      <div className="settingsEntry">
        <Title level={3} className="text settingsSubtitle">
          Start Year
        </Title>
        <DatePicker
          onChange={handleUpdateStartYear}
          picker="year"
          style={{ width: 105 }}
          value={moment(startYear, "YYYY")}
        />
      </div>
      <div className="settingsEntry">
        <Title level={3} className="text settingsSubtitle">
          Degree Length
        </Title>
        <Select
          value={numYears}
          style={{ width: 70 }}
          onChange={handleUpdateDegreeLength}
        >
          {years.map((num) => (
            <Option key={num} value={num}>{num}</Option>
          ))}
        </Select>
      </div>
    </div>
  );
};

export default SettingsMenu;
