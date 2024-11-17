import React, { useState } from 'react';
import { Typography } from 'antd';
import S from './styles';

const { Title } = Typography;

type Props = {
  initiallyCollapsed?: boolean;
  title: string | React.ReactNode;
  children: React.ReactNode;
  headerStyle?: React.CSSProperties;
};

const Collapsible = ({ initiallyCollapsed = false, title, children, headerStyle = {} }: Props) => {
  const [isCollapsed, setIsCollapsed] = useState(initiallyCollapsed);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div>
      <S.CollapsibleHeader onClick={toggleCollapse} style={headerStyle}>
        <S.CollapseButton $collapsed={isCollapsed} />
        {typeof title === 'string' ? (
          <Title level={3} className="text">
            {title}
          </Title>
        ) : (
          title
        )}
      </S.CollapsibleHeader>
      <S.CollapsibleContent $collapsed={isCollapsed}>{children}</S.CollapsibleContent>
    </div>
  );
};

export default Collapsible;
