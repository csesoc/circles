import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Skeleton, Table, Typography } from "antd";
import { getFormattedPlannerCourses } from "../utils";

const TableView = ({ isLoading, structure }) => {
  const { Title } = Typography;
  const [tableLayout, setTableLayout] = useState({});
  const { years, startYear, courses } = useSelector((store) => store.planner);

  const generateTableStructure = (plannedCourses) => {
    const newTableLayout = {};

    // Example groups: Major, Minor, General, Rules
    Object.keys(structure).forEach((group) => {
      newTableLayout[group] = {};
      // Example subgroup: Core Courses, Computing Electives
      Object.keys(structure[group]).forEach((subgroup) => {
        const subgroupStructure = structure[group][subgroup];

        newTableLayout[group][subgroup] = [];

        // only consider disciplinary component courses
        Object.keys(subgroupStructure.courses).forEach((courseCode) => {
          if (courseCode in plannedCourses) {
            newTableLayout[group][subgroup].push({
              key: courseCode,
              title: plannedCourses[courseCode].title,
              UOC: plannedCourses[courseCode].UOC,
              termPlanned: plannedCourses[courseCode].termPlanned,
            });
            newTableLayout[group][subgroup].sort(
              (a, b) => a.termPlanned.localeCompare(b.termPlanned),
            );
          }
        });
      });
    });

    return newTableLayout;
  };

  useEffect(() => {
    const plannerCourses = getFormattedPlannerCourses(years, startYear, courses);
    const tableStructure = generateTableStructure(plannerCourses);
    setTableLayout(tableStructure);
  }, [isLoading, structure, years, startYear, courses]);

  const columns = [
    {
      title: "Course Code",
      dataIndex: "key",
      key: "key",
    },
    {
      title: "Course Name",
      dataIndex: "title",
      key: "title",
    },
    {
      title: "UOC",
      dataIndex: "UOC",
      key: "UOC",
    },
    {
      title: "Term Planned",
      dataIndex: "termPlanned",
      key: "termPlanned",
    },
  ];

  return (
    <div>
      {isLoading ? (
        <Skeleton />
      ) : (
        <>
          {Object.entries(tableLayout).map(([group, groupEntry]) => (
            <div key={group}>
              <Title level={1}>{structure[group].name ? `${group} - ${structure[group].name}` : group}</Title>
              {Object.entries(groupEntry).map(([subGroup, subGroupEntry]) => (
                <div key={subGroup}>
                  <Title level={2}>{subGroup}</Title>
                  <Table
                    dataSource={subGroupEntry}
                    columns={columns}
                    pagination={{ position: ["none", "none"] }}
                  />
                  <br />
                </div>
              ))}
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default TableView;
