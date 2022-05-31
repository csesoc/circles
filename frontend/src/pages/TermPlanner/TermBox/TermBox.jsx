import React, { useEffect, useState } from "react";
import { Droppable } from "react-beautiful-dnd";
import { useSelector, useDispatch } from "react-redux";
import { Badge } from "antd";
import { LockFilled, UnlockFilled } from "@ant-design/icons";
import DraggableCourse from "../DraggableCourse";
import { toggleTermComplete } from "../../../reducers/plannerSlice";
import "./index.less";

const TermBox = ({
  name, coursesList, termsOffered, isDragging,
}) => {
  const term = name.match(/T[0-3]/)[0];

  const { isSummerEnabled, completedTerms, courses } = useSelector((state) => state.planner);
  const [totalUOC, setTotalUOC] = useState(0);
  const dispatch = useDispatch();
  const handleCompleteTerm = () => {
    dispatch(toggleTermComplete(name));
  };

  useEffect(() => {
    setTotalUOC(0);
    let count = 0;
    const key = Object.keys(courses);
    key.forEach((i) => {
      if (coursesList.includes(i)) {
        count += courses[i].UOC;
        console.log(i, " ", count);
        setTotalUOC(count);
      }
    });
  }, [coursesList]);

  const isCompleted = !!completedTerms[name];

  const isOffered = termsOffered.includes(term) && !isCompleted;

  return (
    <Droppable droppableId={name} isDropDisabled={isCompleted}>
      {(provided) => (
        <Badge color="#9254de" count={`${totalUOC} UOC`} offset={isSummerEnabled ? [-20, 250] : [-14, 260]}>
          <Badge
            count={(
              <div className={`termCheckboxContainer ${isCompleted && "checkedTerm"}`}>
                {(
                  !isCompleted
                    ? (
                      <UnlockFilled
                        className="termCheckbox"
                        onClick={handleCompleteTerm}
                      />
                    ) : (
                      <LockFilled
                        className="termCheckbox"
                        onClick={handleCompleteTerm}
                      />
                    )
                )}
              </div>
            )}
            offset={isSummerEnabled ? [-13, 13] : [-22, 22]}
          >
            <ul
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`termBox ${isOffered && isDragging && "droppable "
              } ${isSummerEnabled && "summerTermBox"} `}
            >
              {coursesList.map((code, index) => (
                <DraggableCourse key={code} code={code} index={index} />
              ))}
              {provided.placeholder}
            </ul>
          </Badge>
        </Badge>
      )}
    </Droppable>
  );
};

export default TermBox;
