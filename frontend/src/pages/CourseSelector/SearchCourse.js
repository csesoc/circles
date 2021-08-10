import React, { useEffect, useState, useMemo, useRef } from 'react';
import { useHistory } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Select, Spin } from 'antd';
import debounce from 'lodash/debounce';
import { courseOptionsActions } from '../../actions/courseOptionsActions';
import { getCourseById } from './courseProvider';
// import { getAllCourses } from '../../actions/updateCourses';

const { Option } = Select;

export default function SearchCourse(props) {
  const dispatch = useDispatch();
  const history = useHistory();
  // const courses = useSelector(state => state.updateCourses.courses);

  // useEffect(() => {
  //   console.log('SEARCH COURSE');
  //   dispatch(getAllCourses());
  // }, []);

  function onChange(value, { data }) {
    dispatch(courseOptionsActions('APPEND_COURSE', {
      [value]: {
        title: data.name,
        type: data.type,
        termsOffered: data.terms,
        prereq: data.prereq
      }
    }));
    console.log(`selected ${value}`, data);
    history.push(`/course-selector/${value}`);
  }
  
  function onBlur() {
    console.log('blur');
  }
  
  function onFocus() {
    console.log('focus');
  }
  
  function onSearch(val) {
    console.log('search:', val);
  }

  return (
    <Select
      showSearch
      className="text"
      style={{ width: '20rem', marginRight: '0.5rem' }}
      placeholder="Find a course"
      optionFilterProp="children"
      onChange={onChange}
      onFocus={onFocus}
      onBlur={onBlur}
      onSearch={onSearch}
      filterOption={(input, option) =>
        option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
      }
    >
      {
        Object.keys(props.courses).map(course => {
          return (
            <Option className={"text"} value={ course } data={ props.courses[course] }>{ course }</Option>
          )
        })
      }
    </Select>
  );
}

// const DebounceSelect = ({ fetchOptions, debounceTimeout = 800, ...props }) => {
//   const [fetching, setFetching] = useState(false);
//   const [options, setOptions] = useState([]);
//   const fetchRef = useRef(0);

//   const debounceFetcher = useMemo(() => {
//     const loadOptions = (value) => {
//       fetchRef.current += 1;
//       const fetchId = fetchRef.current;
//       setOptions([]);
//       setFetching(true);
//       fetchOptions(value).then((newOptions) => {
//         if (fetchId !== fetchRef.current) {
//           // for fetch callback order
//           return;
//         }

//         setOptions(newOptions);
//         setFetching(false);
//       });
//     };

//     return debounce(loadOptions, debounceTimeout);
//   }, [fetchOptions, debounceTimeout]);
//   return (
//     <Select
//       labelInValue
//       filterOption={false}
//       onSearch={debounceFetcher}
//       notFoundContent={fetching ? <Spin size="small" /> : null}
//       {...props}
//       options={options}
//     />
//   );
// } // Usage of DebounceSelect



// export default function SearchCourse(props) {
//   const [value, setValue] = useState([]);

//   const dispatch = useDispatch();
//   // const courses = useSelector(state => state.updateCourses.courses);

//   // useEffect(() => {
//   //   dispatch(getAllCourses());
//   // }, []);

//   async function fetchUserList(username) {
//     // console.log('fetching user', username);
//     // return fetch('https://randomuser.me/api/?results=5')
//     //   .then((response) => response.json())
//     //   .then((body) =>
//     //     body.results.map((user) => ({
//     //       label: `${user.name.first} ${user.name.last}`,
//     //       value: user.login.username,
//     //     })),
//     //   );
//     return Object.keys(props.courses).map(course => ({
//       label: course,
//       value: course
//     }));
//   }

//   return (
//     <DebounceSelect
//       mode="multiple"
//       value={value}
//       placeholder="Search a course"
//       fetchOptions={fetchUserList}
//       onChange={(newValue) => {
//         setValue(newValue);
//       }}
//       style={{ width: '20rem', marginRight: '0.5rem' }}
//     />
//   );
// }