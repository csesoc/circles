import React from "react";
import { Tooltip, Popconfirm } from "antd";
import { useSelector, useDispatch } from "react-redux";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/light.css";
import { FaRegCalendarTimes } from "react-icons/fa";
import {
  DownloadOutlined, EyeFilled, QuestionCircleOutlined, SettingFilled,
} from "@ant-design/icons";
import SaveMenu from "./SaveMenu";
import SettingsMenu from "./SettingsMenu";
import HelpMenu from "./HelpMenu";
import { unhideAllYears, unscheduleAll } from "../../../reducers/plannerSlice";
import "./index.less";

const OptionsHeader = ({ plannerRef, isAllEmpty }) => {
  const theme = useSelector((state) => state.theme);
  const { areYearsHidden } = useSelector((state) => state.planner);
  const { years } = useSelector((state) => state.planner);
  const dispatch = useDispatch();

  return (
    <div className="options-header">
      <div className="left-buttons">
        <Tippy
          content={<SettingsMenu />}
          moveTransition="transform 0.2s ease-out"
          interactive
          trigger="click"
          theme={theme === "light" ? "light" : "dark"}
          zIndex={1}
          placement="bottom-start"
        >
          <div>
            <Tooltip title="Settings">
              <button type="button" className="settings-button">
                <SettingFilled className="settings-icon" />
              </button>
            </Tooltip>
          </div>
        </Tippy>

        {theme === "light" && (
          <Tippy
            content={<SaveMenu plannerRef={plannerRef} />}
            moveTransition="transform 0.2s ease-out"
            interactive
            trigger="click"
            theme={theme === "light" ? "light" : "dark"}
            zIndex={1}
            placement="bottom-start"
          >
            <div>
              <Tooltip title="Export">
                <button type="button" className="settings-button">
                  <DownloadOutlined className="settings-icon" />
                </button>
              </Tooltip>
            </div>
          </Tippy>
        )}

        {!isAllEmpty(years) && (
          <Popconfirm
            placement="bottomRight"
            title="Are you sure you want to unplan all your courses?"
            onConfirm={() => dispatch(unscheduleAll())}
            style={{ width: "200px" }}
            okText="Yes"
            cancelText="No"
          >
            <Tooltip title="Unplan all courses">
              <button type="button" className="settings-button">
                <FaRegCalendarTimes className="settings-icon" />
              </button>
            </Tooltip>
          </Popconfirm>
        )}

        {areYearsHidden && (
          <Tooltip title="Show all hidden years">
            <button type="button" className="settings-button" onClick={() => dispatch(unhideAllYears())}>
              <EyeFilled className="settings-icon" />
            </button>
          </Tooltip>
        )}
      </div>

      <Tippy
        content={<HelpMenu />}
        moveTransition="transform 0.2s ease-out"
        interactive
        trigger="click"
        theme={theme === "light" ? "light" : "dark"}
        zIndex={1}
        maxWidth="80vh"
        placement="bottom-start"
      >
        <div>
          <Tooltip title="Help">
            <button type="button" className="settings-button help-button">
              <QuestionCircleOutlined className="settings-icon" />
            </button>
          </Tooltip>
        </div>
      </Tippy>
    </div>
  );
};

export default OptionsHeader;
