import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { getAllCourses } from '../../actions/updateCourses';
import { Menu } from 'antd';

const { SubMenu } = Menu;

export default function CourseMenu(props) {
  const history = useHistory();
  const dispatch = useDispatch();
  // const courses = useSelector(state => state.updateCourses.courses);
  const [core, setCore] = useState([]);
  const [electives, setElectives] = useState([]);
  const [genEd, setGenEd] = useState([]);

  // useEffect(() => {
  //   console.log('COURSE MENU');
  //   dispatch(getAllCourses());
  // }, []);

  useEffect(() => {
    setCore([]);
    setElectives([]);
    setGenEd([]);
    let currCore = [...core];
    let currElec = [...electives];
    let currGenEd = [...genEd];
    for (const course in props.courses) {
      if (props.courses[course].type === 'core') {
        currCore.push(course);
      } else if (props.courses[course].type === 'elective') {
        currElec.push(course);
      } else if (props.courses[course].type === 'gened') {
        currGenEd.push(course);
      }
    };
    setCore(currCore);
    setElectives(currElec);
    setGenEd(currGenEd);
  }, [props.courses]);

  const handleClick = e => {
    console.log('click ', e);
  };

  const goToCourse = (id) => {
    history.push(`/course-selector/${id}`);
  }

  return (
    <Menu
      onClick={handleClick}
      style={{ width: '70%' }}
      defaultSelectedKeys={['1']}
      defaultOpenKeys={['sub1']}
      mode="inline"
    >
      <SubMenu key="sub1" /* icon={<MailOutlined />} */ title="Recently Viewed">

      </SubMenu>
      <SubMenu key="sub2" /* icon={<AppstoreOutlined />} */ title="Core">
        {
          core.map((course) => {
            return (
              <Menu.Item key={ course } onClick={ () => goToCourse(course) }>{ course }</Menu.Item>
            )
          })
        }
      </SubMenu>
      <SubMenu key="sub4" /* icon={<SettingOutlined />} */ title="Electives">
        {
          electives.map((course) => {
            return (
              <Menu.Item key={ course } onClick={ () => goToCourse(course) }>{ course }</Menu.Item>
            )
          })
        }
      </SubMenu>
      <SubMenu key="sub5" /* icon={<SettingOutlined />} */ title="General Education">
        {
          genEd.map((course) => {
            return (
              <Menu.Item key={ course } onClick={ () => goToCourse(course) }>{ course }</Menu.Item>
            )
          })
        }
      </SubMenu>
    </Menu>
  );
}