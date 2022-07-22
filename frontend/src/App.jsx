import React, { useState } from "react";
import { useSelector } from "react-redux";
import {
  BrowserRouter as Router, Route,
  Routes,
} from "react-router-dom";
import { ThemeProvider } from "styled-components";
import { darkTheme, GlobalStyles, lightTheme } from "config/theme";
import PageLoading from "./components/PageLoading";
import CourseSelector from "./pages/CourseSelector";
import DegreeWizard from "./pages/DegreeWizard";
import GraphicalSelector from "./pages/GraphicalSelector";
import Page404 from "./pages/Page404";
import ProgressionChecker from "./pages/ProgressionChecker";
import TermPlanner from "./pages/TermPlanner";
import "./App.less";
import "./config/axios";
// stylesheets for antd library
import "antd/dist/antd.less";

const App = () => {
  const [loading, setLoading] = useState(true);
  const { theme } = useSelector((state) => state.settings);

  return (
    <ThemeProvider theme={theme === "light" ? lightTheme : darkTheme}>
      <GlobalStyles />
      <Router>
        {loading ? (
          <PageLoading setLoading={setLoading} />
        ) : (
          <Routes>
            <Route path="/degree-wizard" element={<DegreeWizard />} />
            <Route path="/course-selector" element={<CourseSelector />} />
            <Route path="/graphical-selector" element={<GraphicalSelector />} />
            <Route path="/term-planner" element={<TermPlanner />} />
            <Route path="/progression-checker" element={<ProgressionChecker />} />
            <Route path="*" element={<Page404 />} />
          </Routes>
        )}
      </Router>
    </ThemeProvider>
  );
};

export default App;
