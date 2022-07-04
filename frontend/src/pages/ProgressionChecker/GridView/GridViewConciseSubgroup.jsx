import React from "react";
import { Empty, Typography } from "antd";
import Collapsible from "components/Collapsible";
import CourseBadge from "./CourseBadge";

const GridViewConciseSubgroup = ({ uoc, subgroupKey, subgroupEntries }) => {
  const { Title } = Typography;

  const planned = subgroupEntries.filter((c) => (c.unplanned || c.past || c.past === false));
  const unplanned = subgroupEntries.filter((c) => (!(c.unplanned || c.past || c.past === false)));

  // convert lists to components
  const plannedGroup = (
    <div className="courseGroup">
      {planned.map((course) => (<CourseBadge course={course} key={course.key} />))}
    </div>
  );
  const unplannedGroup = (
    <div className="courseGroup">
      {unplanned.map((course) => (<CourseBadge course={course} key={course.key} />))}
    </div>
  );

  return (
    <div key={subgroupKey} className="subCategory">
      <Title level={2}>{subgroupKey}</Title>
      <Title level={3}>
        {uoc} UOC of the following courses
      </Title>
      <Collapsible
        title={<Title level={4}>Courses you have planned</Title>}
        headerStyle={{ border: "none" }}
        initiallyCollapsed={planned.length === 0}
      >
        {planned.length > 0 ? plannedGroup : <Empty description="Nothing to see here! 👀" image={Empty.PRESENTED_IMAGE_SIMPLE} />}
      </Collapsible>
      <Collapsible
        title={<Title level={4}>Choose from the following</Title>}
        headerStyle={{ border: "none" }}
        initiallyCollapsed={unplanned.length > 8 || unplanned.length === 0}
      >
        {unplanned.length > 0 ? unplannedGroup : <Empty description="Nothing to see here! 👀" image={Empty.PRESENTED_IMAGE_SIMPLE} />}
      </Collapsible>
      <br />
    </div>
  );
};

export default GridViewConciseSubgroup;
