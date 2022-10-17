import React from 'react';
import { useSelector } from 'react-redux';
import { scroller } from 'react-scroll';
import { ArrowDownOutlined } from '@ant-design/icons';
import { useSpring } from '@react-spring/web';
import { Button, Typography } from 'antd';
import { ProgramStructure } from 'types/structure';
import getNumTerms from 'utils/getNumTerms';
import LiquidProgressChart from 'components/LiquidProgressChart';
import { LoadingDashboard } from 'components/LoadingSkeleton';
import SpecialisationCard from 'components/SpecialisationCard';
import type { RootState } from 'config/store';
import FreeElectivesCard from './FreeElectivesCard';
import S from './styles';

type StoreUOC = {
  [groupKey: string]: {
    total: number;
    curr: number;
  };
};

type Props = {
  isLoading: boolean;
  structure: ProgramStructure;
  totalUOC: number;
  freeElectivesUOC: number;
};

const Dashboard = ({ isLoading, structure, totalUOC, freeElectivesUOC }: Props) => {
  const { Title } = Typography;
  const currYear = new Date().getFullYear();

  const props = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    reset: true,
    config: { tension: 80, friction: 60 }
  });

  const { courses } = useSelector((state: RootState) => state.planner);
  const { programCode, programName } = useSelector((state: RootState) => state.degree);

  let completedUOC = 0;
  Object.keys(courses).forEach((courseCode) => {
    if (courses[courseCode]?.plannedFor) {
      completedUOC +=
        courses[courseCode].UOC *
        getNumTerms(courses[courseCode].UOC, courses[courseCode].isMultiterm);
    }
  });

  const storeUOC: StoreUOC = {};

  // Example groups: Major, Minor, General, Rules
  Object.keys(structure).forEach((group) => {
    storeUOC[group] = {
      total: 0,
      curr: 0
    };

    // Example subgroup: Core Courses, Computing Electives
    Object.keys(structure[group].content).forEach((subgroup) => {
      storeUOC[group].total += structure[group].content[subgroup].UOC;
      const subgroupStructure = structure[group].content[subgroup];

      const isRule = subgroupStructure.type && subgroupStructure.type.includes('rule');

      if (subgroupStructure.courses && !isRule) {
        let currUOC = 0;
        // only consider disciplinary component courses
        Object.keys(subgroupStructure.courses).forEach((courseCode) => {
          if (courses[courseCode]?.plannedFor && currUOC < subgroupStructure.UOC) {
            const courseUOC =
              courses[courseCode].UOC *
              getNumTerms(courses[courseCode].UOC, courses[courseCode].isMultiterm);
            storeUOC[group].curr += courseUOC;
            currUOC += courseUOC;
          }
        });
      }
    });
  });

  const handleClick = () => {
    scroller.scrollTo('divider', {
      duration: 1500,
      smooth: true
    });
  };

  return (
    <S.Wrapper>
      {isLoading ? (
        <LoadingDashboard />
      ) : (
        <S.ContentWrapper style={props}>
          <LiquidProgressChart completedUOC={completedUOC} totalUOC={totalUOC} />
          <a
            href={`https://www.handbook.unsw.edu.au/undergraduate/programs/${currYear}/${programCode}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Title className="text">
              {programCode} - {programName}
            </Title>
          </a>
          <S.CardsWrapper>
            {Object.entries(structure)
              .filter(([group]) => group !== 'Rules')
              .map(([group, specialisation]) => (
                <SpecialisationCard
                  key={group}
                  type={group}
                  totalUOC={storeUOC[group].total}
                  currUOC={storeUOC[group].curr}
                  specTitle={specialisation.name}
                />
              ))}
            <FreeElectivesCard uoc={freeElectivesUOC} />
          </S.CardsWrapper>
          <Button
            type="primary"
            shape="circle"
            icon={<ArrowDownOutlined />}
            onClick={handleClick}
          />
        </S.ContentWrapper>
      )}
    </S.Wrapper>
  );
};

export default Dashboard;
