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

    const gotoCourses = () => {
      window.location.href = '/course-selector';
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
          <h1>An error has occurred. You should never see this...</h1>
          <S.TextBody>
            <p>
              Unfortunately, due to a bug in Circles, an error has occurred. If you want to help us
              fix this bug, please let us know! We would greatly appreciate it!
            </p>
            <p>
              Fill in this form&nbsp;
              <a href={FEEDBACK_LINK} target="_blank" rel="noreferrer">
                here
              </a>
              &nbsp;to inform us how the error occurred! Please also include brief description on
              the steps that led up to the error and a copy of the error messages seen below.
            </p>
            <p>
              If you are seeing this page often, try to reset your data by clicking the &apos;Reset
              Data&apos; button. Otherwise, you can return back to planning your future degree!
            </p>
            <Space wrap>
              <Button onClick={gotoCourses} type="primary">
                Return to Circles
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
