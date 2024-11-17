import React from 'react';
import { Link } from 'react-scroll';
import { Tooltip as ReactTooltip } from 'react-tooltip';
import { purple } from '@ant-design/colors';
import { Progress, Typography } from 'antd';
import useSettings from 'hooks/useSettings';
import S from './styles';

type Props = {
  type: string;
  totalUOC: number;
  currUOC: number;
  specTitle: string;
};

const SpecialisationCard = ({ type, totalUOC, currUOC, specTitle }: Props) => {
  const { Title, Text } = Typography;
  const progress = Math.min(Math.round((currUOC / totalUOC) * 100), 100);

  const { theme } = useSettings();
  const trailColor = theme === 'light' ? '#fff' : '#444249';

  return (
    <Link to={type} smooth duration={2000}>
      <S.Card hoverable bordered={false} id={`#${specTitle || type}SpecCard`}>
        <Title className="text" level={5}>
          {specTitle || type}
        </Title>
        <Text style={{ color: '#737372' }}>{type.charAt(0).toUpperCase() + type.slice(1)}</Text>
        <div data-tip data-for={`card-${type}`}>
          <Progress
            percent={progress}
            trailColor={trailColor}
            showInfo={false}
            strokeColor={{ '0%': purple[3], '100%': purple[4] }}
          />
        </div>
      </S.Card>
      <ReactTooltip
        id={`card-${type}`}
        anchorSelect={`#${specTitle || type}SpecCard`}
        place="bottom"
        variant={theme === 'dark' ? 'light' : 'dark'}
      >
        <S.TooltipText>
          <div>{progress}%</div>
          <div>
            ({currUOC} / {totalUOC} UOC)
          </div>
        </S.TooltipText>
      </ReactTooltip>
    </Link>
  );
};

export default SpecialisationCard;
