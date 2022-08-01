/* eslint-disable react/destructuring-assignment */
import React from "react";
import { Button } from "antd";
import { FEEDBACK_LINK } from "config/constants";
import S from "./styles";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // eslint-disable-next-line no-console
    console.log({ error, errorInfo });
    this.setState({ errorInfo });
  }

  render() {
    const { hasError, error, errorInfo } = this.state;

    const handleClick = () => {
      localStorage.clear();
      window.location = "/degree-wizard";
    };

    if (hasError) {
      // You can render any custom fallback UI
      return (
        <S.Container>
          <h1>An error has occurred. You should never see this...</h1>
          <S.TextBody>
            <p>
              Unfortunately, due to a bug in Circles, an error has occurred.
              If you want to help us fix this bug, please let us know! We would
              greatly appreciate it!
            </p>
            <p>
              Fill in this form <a href={FEEDBACK_LINK} target="_blank" rel="noreferrer">here</a> to inform us how
              the error occurred! Please also include brief description on the steps that led
              up to the error and a copy of the error messages seen below.
            </p>
            <Button onClick={handleClick} type="primary">Return to Circles</Button>
          </S.TextBody>
          <h3>Error</h3>
          <p>{JSON.stringify(error, Object.getOwnPropertyNames(error))}</p>
          <h3>Error Info</h3>
          <p>{errorInfo?.componentStack.toString()}</p>
        </S.Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
