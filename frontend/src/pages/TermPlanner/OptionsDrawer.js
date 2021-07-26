import React, { useEffect } from "react";
import { plannerActions } from "../../actions/plannerActions";
import { Typography, Drawer, Collapse, Alert } from "antd";
import { Droppable } from "react-beautiful-dnd";
import DraggableCourse from "./DraggableCourse";
import { CloseOutlined } from "@ant-design/icons";
import { useSelector, useDispatch } from "react-redux";

const OptionsDrawer = ({ visible, setVisible }) => {
  const { Title } = Typography;
  const { Panel } = Collapse;

  const theme = useSelector((state) => state.theme);
  const { courses, unplanned, sortedUnplanned } = useSelector((state) => {
    return state.planner;
  });

  const dispatch = useDispatch();

  useEffect(() => {
    // get unplanned array and store the sorted version
    dispatch(
      plannerActions("SET_SORTED_UNPLANNED", sortUnplanned(unplanned, courses))
    );
  }, []);

  return (
    <Drawer
      placement="left"
      onClose={() => setVisible(false)}
      closeIcon={
        <CloseOutlined style={{ color: theme === "dark" && "white" }} />
      }
      visible={visible}
      getContainer={false}
      bodyStyle={{
        background: theme === "dark" ? "#151718" : "white",
      }}
      width="25em"
      mask={false}
    >
      <Title class="text">Options</Title>
      <Title level={2} class="text">
        Unplanned Courses
      </Title>
      {Object.keys(sortedUnplanned).length === 0 ? (
        <Alert
          message="Oops!" // might need to change this
          description="It looks like you haven't added any courses to your term planner. Please do so in the course selector."
          type="warning"
          showIcon
          className="alert"
        />
      ) : (
        <Collapse className="collapse" ghost={theme === "dark"}>
          {Object.keys(sortedUnplanned).map((type, index) => (
            <Panel header={type} key={index}>
              <Droppable droppableId={type} isDropDisabled={true}>
                {(provided) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className="panel"
                  >
                    {sortedUnplanned[type].map((code, index) => (
                      <DraggableCourse code={code} index={index} key={code} />
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </Panel>
          ))}
        </Collapse>
      )}
    </Drawer>
  );
};

// create separate array for each type
// e.g. courseTypes = { Core: ["COMP1511", "COMP2521"], Elective: ["COMP6881"] }
const sortUnplanned = (unplanned, courses) => {
  if (unplanned == null) return {};
  let courseTypes = {};
  unplanned.forEach((code) => {
    const type = courses.get(code)["type"];
    if (!courseTypes.hasOwnProperty(type)) {
      courseTypes[type] = [code];
    } else {
      courseTypes[type].push(code);
    }
  });
  return courseTypes;
};

export default OptionsDrawer;
