import React, { useState } from 'react';
import { animated, useSpring } from '@react-spring/web';
import { Select, Typography } from 'antd';
import { fuzzy } from 'fast-fuzzy';
import { DegreeWizardPayload } from 'types/degreeWizard';
import { useAllDegreesQuery } from 'utils/apiHooks/static';
import springProps from '../common/spring';
import Steps from '../common/steps';
import CS from '../common/styles';

const { Title } = Typography;

type SetState<T> = React.Dispatch<React.SetStateAction<T>>;

type Props = {
  incrementStep: (stepTo?: Steps) => void;
  setDegreeInfo: SetState<DegreeWizardPayload>;
};

const DegreeStep = ({ incrementStep, setDegreeInfo }: Props) => {
  const allDegreesQuery = useAllDegreesQuery({
    queryOptions: {
      select: (data) =>
        Object.keys(data.programs).map((code) => ({
          label: `${code} ${data.programs[code]}`,
          value: `${code} ${data.programs[code]}`
        }))
    }
  });
  const allDegrees = allDegreesQuery.data ?? [];

  const onDegreeChange = async (key: string) => {
    setDegreeInfo((prev) => ({
      ...prev,
      // key is of format `${programCode} - ${title}`; Need to extract code
      programCode: key.slice(0, 4),
      specs: []
    }));
    if (key) incrementStep(Steps.SPECS);
  };

  const props = useSpring(springProps);

  const [items, setItems] = useState<{ label: string; value: string }[]>([]);

  const searchDegree = (newInput: string) => {
    // List all degrees if input is empty
    if (newInput === '') {
      setItems(allDegrees);
      return;
    }

    // score is a number between 0 and 1 where 1 is a perfect match
    const fuzzedDegrees = allDegrees
      .map((item) => {
        return {
          score: fuzzy(newInput, item.label),
          ...item
        };
      })
      .filter((pair) => pair.score > 0.5);

    // Shorter name with greater or equal score means better match
    fuzzedDegrees.sort((a, b) => {
      if (a.score > b.score) return -1;
      if (a.score < b.score) return 1;
      if (a.label.length < b.label.length) return -1;
      if (a.label.length > b.label.length) return 1;
      return 0;
    });

    setItems(fuzzedDegrees);
  };

  return (
    <CS.StepContentWrapper id="degree">
      <animated.div style={props}>
        <Title level={4} className="text">
          What are you studying?
        </Title>
        <Select
          disabled={allDegreesQuery.isPending}
          size="large"
          showSearch
          optionFilterProp="label"
          placeholder="Search Degree"
          style={{ width: '100%' }}
          onSelect={onDegreeChange}
          options={items}
          filterOption={false}
          onSearch={searchDegree}
          // items should be initialised with all degrees
          onClick={() => searchDegree('')}
        />
      </animated.div>
    </CS.StepContentWrapper>
  );
};

export default DegreeStep;
