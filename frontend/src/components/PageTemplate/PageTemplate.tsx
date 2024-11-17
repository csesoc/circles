import React from 'react';
import { Helmet } from 'react-helmet';
import FeedbackButton from 'components/FeedbackButton';
import Header from 'components/Header';

type Props = {
  children: React.ReactNode;
  showHeader?: boolean;
  showBugButton?: boolean;
};

const PageTemplate = ({ children, showHeader = true, showBugButton = true }: Props) => (
  <>
    <Helmet>
      <title>Circles</title>
      <meta name="description" content="Circles UNSW Degree Planner" />
      <meta
        name="keywords"
        content="circles, unsw, csesoc, devsoc, degree, planner, course, plan"
      />
    </Helmet>
    {showHeader && <Header />}
    <div>
      {children}
      {showBugButton && <FeedbackButton />}
    </div>
  </>
);

export default PageTemplate;
