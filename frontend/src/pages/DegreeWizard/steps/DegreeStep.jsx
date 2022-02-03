import React, { useEffect } from "react";
import axios from "axios";
import { Menu, Typography, Button } from "antd";
import { degreeActions } from "../../../actions/degreeActions";
import { Link } from "react-scroll";
import { useDispatch, useSelector } from "react-redux";
import "./steps.less";

const { Title } = Typography;
export const DegreeStep = ({ isYearsSet }) => {
  const dispatch = useDispatch();
  const programCode = useSelector((store) => store.degree.programCode);
  const [input, setInput] = React.useState("");
  const [options, setOptions] = React.useState(null);

  const fetchAllDegrees = async () => {
    // const res = await axios.get("http://localhost:8000/programs/getPrograms");
    // setOptions(res.data["programs"]);
    setOptions({
      3778: "Computer Science",
      3502: "Commerce",
      3970: "Science",
      3543: "Economics",
    });
    // setIsLoading(false);
  };

  useEffect(() => {
    // setTimeout(fetchDegree, 2000);  // testing skeleton
    fetchAllDegrees();
  }, []);

  const handleDegreeChange = (e) => {
    setInput(options[e.key]);
    dispatch(
      degreeActions("SET_PROGRAM", {
        programCode: e.key,
        programName: options[e.key],
      })
    );
  };

  return (
    <div className="steps-root-container-first">
      <Title level={3} className="text">
        What are you studying?
      </Title>
      <input
        className="steps-search-input"
        type="text"
        value={input}
        placeholder="Search Degree"
        onChange={(e) => setInput(e.target.value)}
      />
      {input !== "" && options && (
        <Menu
          className="degree-search-results"
          onClick={handleDegreeChange}
          selectedKeys={programCode && [programCode]}
          mode="inline"
        >
          {Object.keys(options).map((key) => (
            <Menu.Item className="text" key={key}>
              {key} &nbsp; {options[key]}
            </Menu.Item>
          ))}
        </Menu>
      )}

      {programCode && (
        <Link to={"Specialisation"} smooth={true} duration={1000}>
          <Button className="steps-next-btn-first" type="primary">
            Next
          </Button>
        </Link>
      )}
    </div>
  );
};
