import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { EyeInvisibleFilled } from "@ant-design/icons";
import { notification, Tooltip } from "antd";
import { hideYear } from "reducers/plannerSlice";

const HideYearTooltip = ({ year }) => {
  const { hidden, numYears } = useSelector((state) => state.planner);
  const dispatch = useDispatch();

  const showCannotHideAllYearsNotification = () => {
    notification.open({
      type: "error",
      message: "Something's not right",
      description: "You cannot hide all years in your term planner",
      duration: 2,
      placement: "bottomRight",
    });
  };

  const handleHideYear = () => {
    const numHidden = Object.values(hidden).filter((h) => h).length;
    if (numHidden === numYears - 1) showCannotHideAllYearsNotification();
    else {
      dispatch(hideYear(year));
    }
  };

  return (
    <Tooltip title="Hide year">
      {/* TODO: Hacky way to have className for YearWrapper styling */}
      <div role="button" className="year-tooltip" onClick={handleHideYear}>
        <EyeInvisibleFilled />
      </div>
    </Tooltip>
  );
};

export default HideYearTooltip;
