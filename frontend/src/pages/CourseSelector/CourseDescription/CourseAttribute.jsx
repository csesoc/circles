import React from "react";
import { Typography } from "antd";

const { Title, Text } = Typography;

const CourseAttribute = ({ title, content }) => (
  <div className="cs-course-attr">
    <Title level={3} className="text">
      {title}
    </Title>
    <Text className="text">{content}</Text>
  </div>
);

export default CourseAttribute;
