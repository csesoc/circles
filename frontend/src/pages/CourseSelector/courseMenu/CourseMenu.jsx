import React from "react";
import axios from "axios";
import { useSelector, useDispatch } from "react-redux";
import { Menu } from "antd";
import { courseTabActions } from "../../../actions/courseTabActions";
import { setStructure } from "../../../actions/setStructure";
import { Loading } from "./Loading";
import "./CourseMenu.less";
import { setCourses } from "../../../actions/updateCourses";

const { SubMenu } = Menu;

const MenuItem = ({ courseCode }) => {
  const dispatch = useDispatch();
  const handleClick = () => {
    dispatch(courseTabActions("ADD_TAB", courseCode));
  };
  return (
    <Menu.Item className="text" key={courseCode} onClick={handleClick}>
      {courseCode}
    </Menu.Item>
  );
};

export default function CourseMenu() {
  const dispatch = useDispatch();
  const structure = useSelector((state) => state.structure);
  const { active, tabs } = useSelector((state) => state.tabs);
  let id = tabs[active];

  // Exception tabs
  if (id === "explore" || id === "search") id = null;

  const [coursesState, setCoursesState] = React.useState({});

  const fetchProgression = async () => {
    // Local Development Testing
    // const res = await axios.get("http://localhost:3000/structure.json");
    // console.log(res.data);
    const res1 = await axios.get(
      "http://localhost:8000/api/getStructure/3778/COMPA1"
    );
    // console.log(res1);
    // Uncomment when DB is working
    // const coreData = await axios.get(`http://localhost:8000/api/getCoreCourses/${programCode}/${specialisation}/${minor}`);
    dispatch(setStructure(res1.data.structure));

    try {
      const res = await axios.post(
        `http://localhost:8000/api/getAllUnlocked/`,
        JSON.stringify(payload),
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      setCoursesState(res.data.courses_state);
    } catch (err) {
      console.log(err);
    }
  };
  React.useEffect(() => {
    fetchProgression();
  }, []);

  return (
    <div className="cs-menu-root">
      {structure === null ? (
        <Loading />
      ) : (
        <>
          <Menu
            className={"text"}
            onClick={() => {}}
            // style={{ width: '100%'}}
            defaultSelectedKeys={[]}
            selectedKeys={[]}
            defaultOpenKeys={[[...Object.keys(structure)][0]]}
            mode="inline"
          >
            {[...Object.keys(structure)].map((category) => (
              // Major, Minor, GeneralX
              <SubMenu key={category} title={category}>
                {/* Business core, Flexible core etc */}
                {Object.keys(structure[category]).map((subCategory) => {
                  // let regex = courses.join("|");
                  // for (const course in courses_state) {
                  //   if (course.match(regex)) {
                  //     console.log(course);
                  //   }
                  // }
                  if (typeof structure[category][subCategory] !== "string") {
                    const subCourses = Object.keys(
                      structure[category][subCategory].courses
                    );
                    const regex = subCourses.join("|");
                    return (
                      <Menu.ItemGroup key={subCategory} title={subCategory}>
                        {Object.keys(coursesState).map((courseCode) => {
                          if (courseCode.match(regex))
                            return <MenuItem courseCode={courseCode} />;
                        })}
                      </Menu.ItemGroup>
                    );
                  }
                })}
              </SubMenu>
            ))}
          </Menu>
        </>
      )}
    </div>
  );
}

const payload = {
  program: "3778",
  specialisations: ["COMPA1"],
  courses: {},
  year: 0,
};
