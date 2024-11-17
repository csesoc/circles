import React from 'react';
import { Typography } from 'antd';
import styled from 'styled-components';
import { CtfResult, validateCtf as validateCtfRequest } from 'utils/api/ctfApi';
import useToken from 'hooks/useToken';
import CS from '../common/styles';
import S from './styles';

const { Text, Title } = Typography;

const TextBlock = styled(Text)`
  display: block;
  padding: 1em;
  color: ${({ theme }) => theme.graph.tabTextColor};
`;

const loadingResult: CtfResult = {
  valid: false,
  failed: 0,
  passed: [],
  message: 'Loading...',
  flags: []
};

const ModalTitle = styled(Title)`
  margin: 0 !important;
  color: ${({ theme }) => theme.text} !important;
`;

// TODO: hide this behind a feature flag?
const ValidateCtfButton = () => {
  const [open, setOpen] = React.useState(false);
  const [result, setResult] = React.useState(loadingResult);
  const token = useToken();

  const validateCtf = async () => {
    setOpen(true);
    const res = await validateCtfRequest(token);
    setResult(res);
  };

  return (
    <>
      <CS.Button onClick={validateCtf}>Validate CTF</CS.Button>
      <S.Modal
        title="Validate CTF"
        open={open}
        onOk={() => setOpen(false)}
        onCancel={() => setOpen(false)}
        width="60%"
      >
        <ModalTitle level={4}>Passed Challenges</ModalTitle>
        <TextBlock>
          <ol>
            {result.passed.map((challenge) => (
              <li key={challenge}>
                <TextBlock>{challenge}</TextBlock>
              </li>
            ))}
          </ol>
        </TextBlock>

        <ModalTitle level={4}>Unlocked Flags</ModalTitle>
        <TextBlock>
          <ol>
            {result.flags.length > 0 &&
              result.flags.map((flag) => (
                <li key={flag}>
                  <TextBlock>{flag}</TextBlock>
                </li>
              ))}
          </ol>
        </TextBlock>

        <ModalTitle level={4}>
          {result.valid ? (
            <Text type="success">{result.message}</Text>
          ) : (
            <Text type="warning">Next: {result.message}</Text>
          )}
        </ModalTitle>
      </S.Modal>
    </>
  );
};

export default ValidateCtfButton;
