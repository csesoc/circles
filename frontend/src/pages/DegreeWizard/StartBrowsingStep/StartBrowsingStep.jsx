import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import {
  Button, notification,
} from "antd";
import { setIsComplete } from "reducers/degreeSlice";
import CS from "../common/styles";
import S from "./styles";

const openNotification = (msg) => {
  const args = {
    message: msg,
    duration: 2,
    className: "text helpNotif",
    placement: "bottomRight",
  };
  notification.error(args);
};

const StartBrowsingStep = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { programCode, specs } = useSelector((state) => state.degree);

  const handleSaveUserSettings = () => {
    if (programCode === "") {
      openNotification("Please select a degree");
    } else if (!specs.length) {
      openNotification("Please select a specialisation");
    } else {
      dispatch(setIsComplete(true));
      navigate("/course-selector");
    }
  };

  return (
    <CS.StepContentWrapper id="start browsing">
      <S.StartBrowsingWrapper>
        <Button type="primary" onClick={handleSaveUserSettings}>
          Start browsing courses!
        </Button>
      </S.StartBrowsingWrapper>
    </CS.StepContentWrapper>
  );
};

export default StartBrowsingStep;
