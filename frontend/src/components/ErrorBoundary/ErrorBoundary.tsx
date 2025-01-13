import React, { ErrorInfo } from 'react';
import { Button, Space } from 'antd';
import ResetModal from 'components/ResetModal';
import { FEEDBACK_LINK } from 'config/constants';
import S from './styles';

type Props = {
  children?: React.ReactNode;
};

type State = {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  modalOpen: boolean;
};

class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null, modalOpen: false };
  }

  static getDerivedStateFromError(error: Error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error({ error, errorInfo });
    this.setState({ errorInfo });
  }

  render() {
    const { hasError, error, errorInfo, modalOpen } = this.state;
    const { children } = this.props;

    const gotoDegrees = () => {
      window.location.href = '/degree-wizard';
    };

    const gotoLanding = () => {
      window.location.href = '/';
    };

    const gotologout = () => {
      window.location.href = '/logout';
    };

    const openModal = () => {
      this.setState({ modalOpen: true });
    };

    const closeModal = () => {
      this.setState({ modalOpen: false });
    };

    if (hasError) {
      // You can render any custom fallback UI
      return (
        <S.Container>
          <ResetModal open={modalOpen} onOk={gotoDegrees} onCancel={closeModal} />
          <h1>An error has occurred, please try the following steps:</h1>
          <S.TextBody>
            <p>
              1. Try refreshing the current page. If the issue persists, consider the options below:
            </p>
            <p>
              2. Send us a screenshot of this page along with a brief description of what you were
              doing when the error occurred by filling out this form&nbsp;
              <a href={FEEDBACK_LINK} target="_blank" rel="noreferrer">
                here
              </a>
              .
            </p>
            {/* <p>
              Fill in this form&nbsp;
              <a href={FEEDBACK_LINK} target="_blank" rel="noreferrer">
                here
              </a>
              &nbsp;to inform us how the error occurred! Please also include brief description on
              the steps that led up to the error and a copy of the error messages seen below.
            </p> */}
            <Space wrap>
              <Button onClick={gotoLanding} type="primary">
                Return to Circles
              </Button>
              <Button onClick={gotologout} type="primary">
                Logout
              </Button>
              <Button onClick={openModal} type="primary" danger>
                Reset Data
              </Button>
            </Space>
          </S.TextBody>
          <h3>Error</h3>
          <p>{JSON.stringify(error, Object.getOwnPropertyNames(error))}</p>
          <h3>Error Info</h3>
          <p>{errorInfo?.componentStack?.toString()}</p>
        </S.Container>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
