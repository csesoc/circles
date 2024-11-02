import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { scroller } from 'react-scroll';
import { useQuery } from '@tanstack/react-query';
import { Button, Typography } from 'antd';
import { DegreeWizardPayload } from 'types/degreeWizard';
import { getSpecialisationTypes } from 'utils/api/specsApi';
import { useResetDegreeMutation, useUserSetupState } from 'utils/apiHooks/user';
import openNotification from 'utils/openNotification';
import MigrationModal from 'components/MigrationModal';
import PageTemplate from 'components/PageTemplate';
import ResetModal from 'components/ResetModal';
import Steps from './common/steps';
import DegreeStep from './DegreeStep';
import SpecialisationStep from './SpecialisationStep';
import StartBrowsingStep from './StartBrowsingStep';
import S from './styles';
import YearStep from './YearStep';

const { Title } = Typography;

const DEFAULT_SPEC_TYPES = ['majors', 'honours', 'minors'];

const DegreeWizard = () => {
  const [currStep, setCurrStep] = useState(Steps.YEAR);

  const [degreeInfo, setDegreeInfo] = useState<DegreeWizardPayload>({
    programCode: '',
    startYear: undefined,
    endYear: undefined,
    specs: []
  });

  const { programCode } = degreeInfo;
  const isSetup = useUserSetupState().data;
  const navigate = useNavigate();

  const specTypesQuery = useQuery({
    queryKey: ['specialisations', 'types', programCode],
    queryFn: () => getSpecialisationTypes(programCode),
    select: (data) => data.types,
    enabled: programCode !== ''
  });
  const specs = specTypesQuery.data ?? DEFAULT_SPEC_TYPES;
  const stepList = ['year', 'degree'].concat(specs).concat(['start browsing']);

  const resetDegree = useResetDegreeMutation();

  useEffect(() => {
    openNotification({
      type: 'info',
      message: 'Disclaimer',
      description:
        'Currently, Circles can only support some degrees and undergrad courses. If you find any errors, feel free to report a bug!'
    });
  }, []);

  const incrementStep = (stepTo?: Steps) => {
    const step = stepTo ? stepList[stepTo] : stepList[currStep + 1];
    // if spec, then that's chillll
    if (stepTo === Steps.SPECS) {
      setCurrStep(stepTo);
      // no step or its more than curr step
      // then we go forwards a state?????????????
      // not spec, or its null, :(
      // not defined HOWEVER (this may falsely trigger when stepTo is 0)
    } else if (!stepTo || stepTo > currStep) {
      setCurrStep((prevState) => prevState + 1);
    }
    // we can increment a step IF it moves forwards

    setTimeout(() => {
      scroller.scrollTo(step, {
        duration: 1500,
        smooth: true
      });
    }, 100);
  };

  const handleLogout = () => {
    navigate('/logout');
  };

  const [migrationNeeded, setMigrationNeeded] = useState(localStorage.getItem('oldUser') !== null);

  return (
    <PageTemplate showHeader={false} showBugButton={false}>
      <S.ContainerWrapper>
        <MigrationModal
          open={migrationNeeded}
          onOk={() => setMigrationNeeded(false)}
          onCancel={() => setMigrationNeeded(false)}
        />
        <ResetModal
          open={isSetup && !migrationNeeded}
          onCancel={() => navigate('/course-selector')}
          onOk={() => resetDegree.mutate()}
        />
        <Title className="text">Welcome to Circles!</Title>
        <S.HeaderWrapper>
          <S.Subtitle>
            Let’s start by setting up your UNSW degree, so you can make a plan that suits you.
          </S.Subtitle>
          <Button danger onClick={handleLogout}>
            Logout
          </Button>
        </S.HeaderWrapper>
        <S.HorizontalLine />
        <S.StepsWrapper>
          <YearStep incrementStep={incrementStep} setDegreeInfo={setDegreeInfo} />
          {currStep >= Steps.DEGREE && (
            <DegreeStep incrementStep={incrementStep} setDegreeInfo={setDegreeInfo} />
          )}
          {specs.map(
            (stepName, index) =>
              currStep - Steps.SPECS >= index && (
                <SpecialisationStep
                  incrementStep={incrementStep}
                  currStep={currStep - Steps.SPECS === index}
                  type={stepName}
                  degreeInfo={degreeInfo}
                  setDegreeInfo={setDegreeInfo}
                />
              )
          )}
          {currStep >= Steps.DONE && <StartBrowsingStep degreeInfo={degreeInfo} />}
        </S.StepsWrapper>
      </S.ContainerWrapper>
    </PageTemplate>
  );
};
export default DegreeWizard;
