import React from "react";
import { FaRegCalendarTimes } from "react-icons/fa";
import { useDispatch, useSelector } from "react-redux";
import {
  DownloadOutlined, EyeFilled, QuestionCircleOutlined, SettingFilled, WarningFilled,
} from "@ant-design/icons";
import Tippy from "@tippyjs/react";
import { Popconfirm, Switch, Tooltip } from "antd";
import { unhideAllYears, unscheduleAll } from "reducers/plannerSlice";
import { toggleShowMarks, toggleShowWarnings } from "reducers/settingsSlice";
import ExportPlannerMenu from "../ExportPlannerMenu";
import HelpMenu from "../HelpMenu/HelpMenu";
import SettingsMenu from "../SettingsMenu";
import { isPlannerEmpty } from "../utils";
import S from "./styles";

const OptionsHeader = ({ plannerRef }) => {
  const { theme } = useSelector((state) => state.settings);
  const { areYearsHidden, years } = useSelector((state) => state.planner);
  const { showMarks, showWarnings } = useSelector((state) => state.settings);
  const dispatch = useDispatch();

  const iconStyles = {
    fontSize: "20px",
    color: "#323739",
  };

  return (
    <S.OptionsHeaderWrapper>
      <S.OptionSection>
        <Tippy
          content={<SettingsMenu />}
          moveTransition="transform 0.2s ease-out"
          interactive
          trigger="click"
          theme={theme}
          zIndex={1}
          placement="bottom-start"
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
          content={<ExportPlannerMenu plannerRef={plannerRef} />}
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

        {!isPlannerEmpty(years) && (
          <Tooltip title="Unplan all courses">
            <Popconfirm
              placement="bottomRight"
              title="Are you sure you want to unplan all your courses?"
              onConfirm={() => dispatch(unscheduleAll())}
              style={{ width: "200px" }}
              okText="Yes"
              cancelText="No"
            >
              <S.OptionButton>
                <FaRegCalendarTimes style={iconStyles} />
              </S.OptionButton>
            </Popconfirm>
          </Tooltip>
        )}

        {areYearsHidden && (
          <Tooltip title="Show all hidden years">
            <S.OptionButton onClick={() => dispatch(unhideAllYears())}>
              <EyeFilled style={iconStyles} />
            </S.OptionButton>
          </Tooltip>
        )}
        <Tooltip title="Toggle warnings for previous terms">
          <S.OptionButton onClick={() => dispatch(toggleShowWarnings())}>
            <WarningFilled style={{ ...iconStyles, ...(showWarnings && { color: "#9254de" }) }} />
          </S.OptionButton>
        </Tooltip>
      </S.OptionSection>

      <S.OptionSection>
        <div>
          <Switch
            defaultChecked={showMarks}
            onChange={() => dispatch(toggleShowMarks())}
            checkedChildren="marks shown"
            unCheckedChildren="marks hidden"
          />
        </div>
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
