import React, { useEffect, useState, useMemo, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Select, Spin } from "antd";
import axios from "axios";
import { courseTabActions } from "../../actions/courseTabActions";
import { useDebounce } from "../../hooks/useDebounce";
import { prepareUserPayload } from "./helper";

export default function SearchCourse() {
  const [value, setValue] = useState(null);
  const debouncedSearchTerm = useDebounce(value, 200);
  const [courses, setCourses] = React.useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();

  const planner = useSelector((state) => state.planner);
  const degree = useSelector((state) => state.degree);

  useEffect(() => {
    // if debounced term changes , call API
    if (debouncedSearchTerm)
      search(debouncedSearchTerm, setCourses, setIsLoading, degree, planner);
  }, [debouncedSearchTerm]);

  const handleSelect = (courseCode) => {
    setValue(null);
    dispatch(courseTabActions("ADD_TAB", courseCode));
  };

  const handleSearch = (courseCode) => {
    setValue(courseCode);
    setCourses([]);
    setIsLoading(true);
  };

  return (
    <Select
      showSearch
      placeholder="Search for a course..."
      filterOption={false}
      size="large"
      options={courses}
      value={value}
      // open attribute - close search dropdown when there is no input value or 
      // when a course has been selected
      open={!!value}
      onSearch={handleSearch}
      onSelect={handleSelect}
      notFoundContent={isLoading && value && <Spin size="small" />}
      style={{ width: "30rem", marginRight: "0.5rem" }}
    />
  );
}

export const search = async (query, setCourses, setIsLoading, degree, planner) => {
  try {
    const res = await axios.post(
      `/courses/searchCourse/${query}`,
      JSON.stringify(prepareUserPayload(degree, planner))
    );
    setCourses(
      Object.keys(res.data).map((course) => ({
        label: `${course}: ${res.data[course]}`,
        value: course,
      }))
    );
  } catch (err) {
    console.log(err);
    return [];
  }
  setIsLoading(false);
};
