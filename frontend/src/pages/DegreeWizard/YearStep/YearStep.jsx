import React from "react";
import { useDispatch } from "react-redux";
import { animated, useSpring } from "@react-spring/web";
import { DatePicker, Typography } from "antd";
import { updateDegreeLength, updateStartYear } from "reducers/plannerSlice";
import springProps from "../common/spring";
import STEPS from "../common/steps";
import CS from "../common/styles";

const { Title } = Typography;
const { RangePicker } = DatePicker;

const YearStep = ({ incrementStep }) => {
  const props = useSpring(springProps);
  const dispatch = useDispatch();

  const handleYearChange = (_, [startYear, endYear]) => {
    const numYears = endYear - startYear + 1;
    dispatch(updateDegreeLength(numYears));
    dispatch(updateStartYear(startYear));

    if (startYear && endYear) incrementStep(STEPS.DEGREE);
  };

  return (
    <CS.StepContentWrapper id="year">
      <animated.div style={props}>
        <Title level={4} className="text">
          What years do you start and finish?
        </Title>
        <RangePicker
          picker="year"
          size="large"
          onChange={handleYearChange}
          style={{
            width: "100%",
          }}
        />
      </animated.div>
    </CS.StepContentWrapper>
  );
};

export default YearStep;
