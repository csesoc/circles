import React from "react";
import { Helmet } from "react-helmet";
import FeedbackButton from "components/FeedbackButton";
import Header from "components/Header";

const PageTemplate = ({ children, showHeader = true }) => (
  <>
    <Helmet>
      <title>Circles</title>
      <meta
        name="description"
        content="Circles UNSW Degree Planner"
      />
      <meta
        name="keywords"
        content="circles, unsw, csesoc, degree, planner, course, plan"
      />
    </Helmet>
    {showHeader && <Header />}
    <div>
      {children}
      <FeedbackButton />
    </div>
  </>
);

export default PageTemplate;
