import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Menu } from 'antd';
import { courseOptionsActions } from '../../actions/courseOptionsActions';
import { courseTabActions } from '../../actions/courseTabActions';
import axios from 'axios';
import './CourseMenu.less';

const { SubMenu } = Menu;

const MenuItem = ({courseCode}) => {
  const dispatch = useDispatch();
  const handleClick = () => {
      dispatch(courseTabActions("ADD_TAB", courseCode));
  }
  return (
    <Menu.Item className='text' key={courseCode} onClick={handleClick}>
      { courseCode }
    </Menu.Item>
  )
}

export default function CourseMenu() {
  const dispatch = useDispatch();
  const { active, tabs } = useSelector(state => state.tabs);
  let id = tabs[active];
  // Exception tabs
  if (id === 'explore' || id === 'search') id = null;
  const courseOptions = useSelector(store => store.courseOptions);

  useEffect(() => {
    getCourseOptions();
  }, []);

  const getCourseOptions = async () => {
    const res = await axios.get('http://localhost:3000/courseOptions.json');
    let core = [];
    let electives = [];
    let genEds = [];
    res.data.courseOptions.map(course => {
      let type = course[Object.keys(course)[0]].type;
      if (type === 'core') {
        core.push(course);
      } else if (type === 'elective') {
        electives.push(course);
      } else if (type === 'gened') {
        genEds.push(course);
      }
    });
    dispatch(courseOptionsActions('SET_RECENTLY_VIEWED_COURSES', res.data.recentlyViewed));
    dispatch(courseOptionsActions('SET_CORE_COURSES', core));
    dispatch(courseOptionsActions('SET_ELECTIVE_COURSES', electives));
    dispatch(courseOptionsActions('SET_GENED_COURSES', genEds));
  }

  const handleClick = e => {
    console.log('click ', e);
  };

  return (
    <div className='cs-menu-root'>
      {
        courseOptions.recentlyViewed && courseOptions.core && courseOptions.electives && courseOptions.genEds &&
        <Menu
          className={'text'}
          onClick={handleClick}
          style={{ width: '100%'}}
          defaultSelectedKeys={[id ? id : courseOptions.core[0]]}
          selectedKeys={[]}
          defaultOpenKeys={['recently-viewed', 'core', 'electives']}
          mode="inline"
        >
          <SubMenu className={"text"} key="recently-viewed" title="Recently Viewed">
            { courseOptions.recentlyViewed.length === 0
              ? <Menu.Item key={'empty-recently-viewed'} disabled> No courses here (ㆆ_ㆆ) </Menu.Item>
              : courseOptions.recentlyViewed.map(course => <MenuItem courseCode={course}/>) 
            }
          </SubMenu>
          <SubMenu  className={"text"} key="core" title="Core">
            { courseOptions.core.length === 0
              ? <Menu.Item key={'empty-core'} disabled> No courses here (ㆆ_ㆆ) </Menu.Item>
              : courseOptions.core.map(course => <MenuItem courseCode={Object.keys(course)[0]}/>) 
            }
          </SubMenu>
          <SubMenu className={"text"} key="electives" title="Electives">
            { courseOptions.electives.length === 0
              ? <Menu.Item key={'empty-electives'} disabled> No courses here (ㆆ_ㆆ) </Menu.Item>
              : courseOptions.electives.map(course => <MenuItem courseCode={Object.keys(course)[0]}/>) 
            }
          </SubMenu>
          <SubMenu  className={"text"} key="general-education" title="General Education">
            { courseOptions.genEds.length === 0
              ? <Menu.Item key={'empty-general-education'} disabled> No courses here (ㆆ_ㆆ) </Menu.Item>
              : courseOptions.genEds.map(course => <MenuItem courseCode={Object.keys(course)[0]}/>) 
            }
          </SubMenu>
        </Menu>
      }
    </div>
  );
}