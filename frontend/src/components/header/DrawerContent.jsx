import React from "react";
// import { IoMdMoon, IoIosSunny } from "react-icons/io";
// import { toggleTheme } from "../../actions/toggleTheme";
// import { useSelector, useDispatch } from 'react-redux';
import { BugOutlined } from "@ant-design/icons";
import { Menu } from "antd";
import { useNavigate } from "react-router";

export const DrawerContent = ({ onCloseDrawer }) => {
  // const theme = useSelector(state => state.theme);
  const FORM_LINK = "https://github.com/csesoc/Circles/issues?q=is%3Aissue+is%3Aopen";
  const navigate = useNavigate();
  // const dispatch = useDispatch();
  const handlePush = (url) => {
    navigate(url);
    onCloseDrawer();
  };
  const openFeedbackLink = () => {
    window.open(FORM_LINK, "_blank");
    onCloseDrawer();
  };
  // const handleThemeToggle = () => {
  //     dispatch(toggleTheme(theme === "light" ? "dark" : "light"));
  //     onCloseDrawer();
  // }
  return (
    <Menu mode="vertical" style={{ marginTop: "2em" }}>
      <Menu.Item key="1" onClick={() => handlePush("/course-selector")}>
        Course Selector
      </Menu.Item>
      <Menu.Item key="3" onClick={() => handlePush("/term-planner")}>
        Term Planner
      </Menu.Item>
      {/* <Menu.Item key="2" onClick={() => handlePush("/progression-checker")}>
        Progression Checker
      </Menu.Item> */}
      <Menu.Item key="4" icon={<BugOutlined />} onClick={openFeedbackLink}>
        Report a bug
      </Menu.Item>
      {/* <Menu.ItemGroup key="customisation" title="Customisation">
                <Menu.Item key="4" 
                    onClick={() => handleThemeToggle()}
                    icon={theme === "light" ? <IoMdMoon/> : <IoIosSunny/> }
                >
                    Change to {theme === "light" ? "dark" : "light"} theme
                </Menu.Item>
            </Menu.ItemGroup> */}
    </Menu>
  );
};
