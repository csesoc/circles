import React from "react";
import {
  Button, notification,
} from "antd";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import "./steps.less";
import { setIsComplete } from "../../../reducers/degreeSlice";

// import {
//   updateDegreeLength, updateStartYear, setProgram, addMajor, removeMajor, setMinor,
// } from "../../../reducers/plannerSlice";

const openNotification = (msg) => {
  const args = {
    message: msg,
    duration: 2,
    className: "text helpNotif",
    placement: "topRight",
  };
  notification.error(args);
};

const StartBrowsingStep = () => {
  const navigate = useNavigate();
  const degree = useSelector((state) => state.degree);

  const saveUserSettings = () => {
    // const dispatch = useDispatch(); // switch final degree change to true
    if (degree.programCode === "") {
      openNotification("Please select a degree");
    } else if (!degree.majors.length && !degree.minors.length) {
      openNotification("Please select a specialisation");
    } else {
      navigate("/course-selector");
      const dispatch = useDispatch();
      dispatch(setIsComplete(true));
    }
  };

  return (
    <div className="steps-root-container">
      <div className="steps-start-browsing-container">
        <Button
          className="steps-next-btn"
          type="primary"
          onClick={saveUserSettings}
        >
          Start browsing courses!
        </Button>
      </div>
    </div>
  );
};

export default StartBrowsingStep;
