import React, { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { animated, useSpring } from '@react-spring/web';
import type { MenuProps } from 'antd';
import { Button, Typography } from 'antd';
import axios from 'axios';
import { Specialisations } from 'types/api';
import type { RootState } from 'config/store';
import { addSpecialisation, removeSpecialisation } from 'reducers/degreeSlice';
import springProps from '../common/spring';
import Steps from '../common/steps';
import CS from '../common/styles';
import S from './styles';

const { Title } = Typography;

type Props = {
  incrementStep: (stepTo?: Steps) => void
  currStep: boolean
  type: string
};

type Specialisation = {
  [spec: string]: {
    specs: Record<string, string>
    notes: string
  }
};

const SpecialisationStep = ({ incrementStep, currStep, type }: Props) => {
  const props = useSpring(springProps);
  const dispatch = useDispatch();
  const { programCode, specs } = useSelector((store: RootState) => store.degree);
  const [options, setOptions] = useState<Specialisation>({ someProgramName: { specs: { major: 'major data' }, notes: 'a note' } });

  const fetchAllSpecialisations = useCallback(async () => {
    try {
      const res = await axios.get<Specialisations>(`/specialisations/getSpecialisations/${programCode}/${type}`);
      setOptions(res.data.spec);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Error at getSteps', e);
    }
  }, [programCode, type]);

  useEffect(() => {
    if (programCode !== '') fetchAllSpecialisations();
  }, [fetchAllSpecialisations, programCode, type]);

  const menuItems: MenuProps['items'] = Object.keys(options).map((program, index) => ({
    label: `${type.replace(/^\w/, (c) => c.toUpperCase())} for ${program}`,
    key: index,
    children:
      options[program].notes
        ? [{
          label: `Note: ${options[program].notes}`,
          type: 'group',
          children: Object.keys(options[program].specs).sort().map((spec) => ({
            label: `${spec} ${options[program].specs[spec]}`,
            key: `${index}-${spec}`,
          })),
        }]
        : Object.keys(options[program].specs).sort().map((spec) => ({
          label: `${spec} ${options[program].specs[spec]}`,
          key: `${index}-${spec}`,
        })),
  }));

  return (
    <CS.StepContentWrapper id={type}>
      <animated.div style={props}>
        <CS.StepHeadingWrapper>
          <Title level={4} className="text">
            What are your {type}?
          </Title>
          {currStep && (
          <Button type="primary" onClick={() => incrementStep()}>
            Next
          </Button>
          )}
        </CS.StepHeadingWrapper>
        <S.Menu
          onSelect={(e) => dispatch(addSpecialisation(e.key))}
          onDeselect={(e) => dispatch(removeSpecialisation(e.key))}
          selectedKeys={specs}
          defaultOpenKeys={['0']}
          mode="inline"
          style={{
            gap: '10px',
            display: 'flex',
            flexDirection: 'column',
          }}
          items={menuItems}
        />
      </animated.div>
    </CS.StepContentWrapper>
  );
};

export default SpecialisationStep;
