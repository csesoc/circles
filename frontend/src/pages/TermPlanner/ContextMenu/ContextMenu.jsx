import React, { useState } from "react";
import { Item, Menu, theme } from "react-contexify";
import { FaRegCalendarTimes } from "react-icons/fa";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { DeleteFilled, EditFilled, InfoCircleFilled } from "@ant-design/icons";
import EditMarkModal from "components/EditMarkModal";
import { addTab } from "reducers/courseTabsSlice";
import { removeCourse, unschedule } from "reducers/plannerSlice";
import "react-contexify/dist/ReactContexify.css";

const ContextMenu = ({ code, plannedFor }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleDelete = () => {
    dispatch(removeCourse(code));
  };

  const handleUnschedule = () => {
    dispatch(unschedule({
      destIndex: null,
      code,
    }));
  };
  const id = `${code}-context`;

  const handleInfo = () => {
    navigate("/course-selector");
    dispatch(addTab(code));
  };

  const [isEditMarkVisible, setIsEditMarkVisible] = useState(false);

  const showEditMark = () => {
    setIsEditMarkVisible(true);
  };

  const iconStyle = {
    fontSize: "14px",
    marginRight: "5px",
  };

  return (
    <>
      <Menu id={id} theme={theme.dark}>
        {plannedFor && (
          <Item onClick={handleUnschedule}>
            <FaRegCalendarTimes style={iconStyle} /> Unschedule
          </Item>
        )}
        <Item onClick={handleDelete}>
          <DeleteFilled style={iconStyle} /> Delete from Planner
        </Item>
        <Item onClick={showEditMark}>
          <EditFilled style={iconStyle} /> Edit mark
        </Item>
        <Item onClick={handleInfo}>
          <InfoCircleFilled style={iconStyle} /> View Info
        </Item>
      </Menu>
      <EditMarkModal
        code={code}
        isVisible={isEditMarkVisible}
        setIsVisible={setIsEditMarkVisible}
      />
    </>
  );
};

export default ContextMenu;
