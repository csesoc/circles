import React, { useState } from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import { Menu, Layout, Typography } from "antd";
import { useSelector } from "react-redux";
import ThemeToggle from "./components/ThemeToggle";
import CourseSelector from "./pages/CourseSelector/main";
import DegreeSelector from "./pages/DegreeSelector/main";
import ProgressionChecker from "./pages/ProgressionChecker/main";
import TermPlanner from "./pages/TermPlanner/main";
import circlesLogo from "./images/circlesLogo.svg";
import "./App.less";

const { Header, Content } = Layout;

function App() {
  const [current, setCurrent] = useState("progression");
  const userDegree = useSelector(store => store.degree);
  const handleClick = (e) => {
    setCurrent(e.key);
  };

  const { Title } = Typography;
  return (
    <Router>
        <Header className="header">
          <div className="logo">
            <img alt="circles-logo" src={circlesLogo} width="40" height="40" />
            <Title level={3} style={titleStyles}>
              Circles
            </Title>
          </div>
          <div className='header-content'>
            { userDegree !== null && ( 
              <Menu
                theme="dark"
                onClick={handleClick}
                selectedKeys={[current]}
                mode="horizontal"
                style={menuStyles}
                >
                  <Menu.Item key="course">
                    <span>Course Selector</span>
                    <Link to="/course-selector" />
                  </Menu.Item>
                  <Menu.Item key="progression">
                    <span>Progression Checker</span>
                    <Link to="/progression-checker"></Link>
                  </Menu.Item>
                  <Menu.Item key="planner">
                    <span>Term Planner</span>
                    <Link to="/term-planner" />
                  </Menu.Item>
              </Menu>
            )} 
            <ThemeToggle />
          </div>
        </Header>
      <Content className="content">
        <Switch>
          <Route exact path="/">
            <DegreeSelector />
            {/* Change to term planner if user session active */}
          </Route>
          <Route path="/course-selector">
            <CourseSelector />
          </Route>
          <Route path="/term-planner">
            <TermPlanner />
          </Route>
          <Route path="/degree-selector">
            <DegreeSelector />
          </Route>
          <Route path="/progression-checker">
            <ProgressionChecker />
          </Route>
        </Switch>
      </Content>
    </Router>
  );
}

const menuStyles = {
  backgroundColor: "inherit",
  marginLeft: "auto",
  marginRight: "2em",
};

const titleStyles = {
  marginLeft: "0.3em",
  marginBottom: "0",
};

export default App;