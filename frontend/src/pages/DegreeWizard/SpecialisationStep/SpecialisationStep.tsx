import React from 'react';
import { animated, useSpring } from '@react-spring/web';
import { Button, Select, Typography } from 'antd';
import { DegreeWizardPayload } from 'types/degreeWizard';
import { useSpecsForProgramQuery } from 'utils/apiHooks/static';
import openNotification from 'utils/openNotification';
import Spinner from 'components/Spinner';
import springProps from '../common/spring';
import Steps from '../common/steps';
import CS from '../common/styles';

const { Title } = Typography;

type SetState<T> = React.Dispatch<React.SetStateAction<T>>;

type Props = {
  incrementStep: (stepTo?: Steps) => void;
  currStep?: boolean;
  type: string;
  degreeInfo: DegreeWizardPayload;
  setDegreeInfo: SetState<DegreeWizardPayload>;
};

const SpecialisationStep = ({
  incrementStep,
  currStep,
  type,
  degreeInfo,
  setDegreeInfo
}: Props) => {
  const props = useSpring(springProps);

  const handleAddSpecialisation = (specialisation: string) => {
    setDegreeInfo((prev) => ({
      ...prev,
      specs: [...prev.specs, specialisation]
    }));
  };

  const handleRemoveSpecialisation = (specialisation: string) => {
    setDegreeInfo((prev) => ({
      ...prev,
      specs: prev.specs.filter((spec) => spec !== specialisation)
    }));
  };

  const specsQuery = useSpecsForProgramQuery(
    {
      queryOptions: { select: (data) => data.spec, enabled: degreeInfo.programCode !== '' }
    },
    degreeInfo.programCode,
    type
  );
  const options = specsQuery.data;

  type SelectGroup = {
    label: string;
    note: string | undefined;
    children: {
      label: string;
      value: string;
    }[];
  };

  const selectGroups: SelectGroup[] | undefined = options
    ? Object.keys(options).map((program) => ({
        label: `${type.replace(/^\w/, (c) => c.toUpperCase())} for ${program}`,
        note: options[program].notes,
        children: Object.keys(options[program].specs)
          .sort()
          .map((spec) => ({
            label: `${spec} ${options[program].specs[spec]}`,
            value: spec
          }))
      }))
    : undefined;

  // check if step is optional and can be skipped
  let optionalStep = true;
  if (options) {
    Object.keys(options).forEach((specKey) => {
      const { is_optional: isOptional, specs: optionSpecs } = options[specKey];
      if (!isOptional || degreeInfo.specs.some((spec) => Object.keys(optionSpecs).includes(spec))) {
        optionalStep = false;
      }
    });
  }

  const handleOnNextClick = () => {
    if (!options) return;
    let missingSpec = '';
    Object.keys(options).forEach((specKey) => {
      const { is_optional: isOptional, specs: optionSpecs } = options[specKey];
      if (
        !isOptional &&
        !degreeInfo.specs.some((spec) => Object.keys(optionSpecs).includes(spec)) &&
        !missingSpec
      ) {
        missingSpec = specKey;
      }
    });
    if (missingSpec) {
      openNotification({
        type: 'error',
        message: `Select a ${type.substring(0, type.length - 1)} for ${missingSpec}`
      });
    } else incrementStep();
  };

  return (
    <CS.StepContentWrapper id={type}>
      <animated.div style={props}>
        <CS.StepHeadingWrapper>
          <Title level={4} className="text">
            What are your {type}?
          </Title>
          {currStep && (
            <Button type="primary" onClick={handleOnNextClick}>
              {optionalStep ? 'Skip' : 'Next'}
            </Button>
          )}
        </CS.StepHeadingWrapper>
        {selectGroups ? (
          selectGroups.map((group) => (
            <animated.div style={{ ...props, marginBottom: '1rem' }} key={group.label}>
              <Title level={5}>{group.label}</Title>
              {group.note && <p>{group.note}</p>}
              <Select
                disabled={specsQuery.isLoading}
                mode="multiple"
                style={{ width: '100%' }}
                allowClear
                placeholder={`Select ${type.substring(0, type.length - 1)}s`}
                defaultValue={[]}
                options={group.children}
                onSelect={(value) => handleAddSpecialisation(value)}
                onDeselect={(value) => handleRemoveSpecialisation(value)}
                onClear={() => {
                  group.children.forEach((child) => handleRemoveSpecialisation(child.value));
                }}
              />
            </animated.div>
          ))
        ) : (
          <Spinner text={`Loading ${type}...`} />
        )}
      </animated.div>
    </CS.StepContentWrapper>
  );
};

export default SpecialisationStep;
