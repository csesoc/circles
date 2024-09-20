import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from 'antd';
import { DegreeWizardPayload } from 'types/degreeWizard';
import { setupDegreeWizard } from 'utils/api/degreeApi';
import useNotification from 'hooks/useNotification';
import useToken from 'hooks/useToken';
import CS from '../common/styles';
import S from './styles';

type Props = {
  degreeInfo: DegreeWizardPayload;
};

const StartBrowsingStep = ({ degreeInfo }: Props) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const token = useToken();

  const degreeSetupErrorNotif = useNotification('degree-setup-error-notification');

  const setupDegreeMutation = useMutation({
    mutationFn: (wizard: DegreeWizardPayload) => setupDegreeWizard(token, wizard),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['degree']
      });
      queryClient.invalidateQueries({
        queryKey: ['planner']
      });
      queryClient.invalidateQueries({
        queryKey: ['courses']
      });
      queryClient.clear();
      navigate('/course-selector');
    },
    onError: (err) => {
      degreeSetupErrorNotif({
        type: 'error',
        message: 'Error setting up degree, ensure your specialisations are valid.'
      });
      // eslint-disable-next-line no-console
      console.error('Error at resetDegreeMutation: ', err);
    }
  });

  const handleSetupDegree = () => {
    setupDegreeMutation.mutate(degreeInfo);
  };

  const selectDegreeErrorNotif = useNotification('select-degree-error-notification');
  const selectSpecErrorNotif = useNotification('select-spec-error-notification');

  const handleSaveUserSettings = async () => {
    // TODO: Are these checks necessary?
    if (!degreeInfo.programCode) {
      selectDegreeErrorNotif({
        type: 'error',
        message: 'Please select a degree'
      });
    } else if (!degreeInfo.specs.length) {
      selectSpecErrorNotif({
        type: 'error',
        message: 'Please select a specialisation'
      });
    } else {
      handleSetupDegree();
    }
  };

  return (
    <CS.StepContentWrapper id="start browsing">
      <S.StartBrowsingWrapper>
        <Button type="primary" onClick={handleSaveUserSettings}>
          Start browsing courses!
        </Button>
      </S.StartBrowsingWrapper>
    </CS.StepContentWrapper>
  );
};

export default StartBrowsingStep;
