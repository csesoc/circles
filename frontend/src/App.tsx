import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { NotificationOutlined } from '@ant-design/icons';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App as AntdApp, ConfigProvider, theme as antdTheme } from 'antd';
import { ThemeProvider } from 'styled-components';
import openNotification from 'utils/openNotification';
import IdentityProvider from 'components/Auth/IdentityProvider';
import PreventToken from 'components/Auth/PreventToken';
import RequireToken from 'components/Auth/RequireToken';
import ErrorBoundary from 'components/ErrorBoundary';
import PageLoading from 'components/PageLoading';
import { inDev } from 'config/constants';
import { darkTheme, GlobalStyles, lightTheme } from 'config/theme';
import useSettings from 'hooks/useSettings';
import Login from 'pages/Login';
import LoginSuccess from 'pages/LoginSuccess';
import Logout from 'pages/Logout';
import './config/axios';
// stylesheets for antd library
import 'antd/dist/reset.css';

// Lazy load in pages
const LandingPage = React.lazy(() => import('./pages/LandingPage'));
const CourseSelector = React.lazy(() => import('./pages/CourseSelector'));
const DegreeWizard = React.lazy(() => import('./pages/DegreeWizard'));
const GraphicalSelector = React.lazy(() => import('./pages/GraphicalSelector'));
const Page404 = React.lazy(() => import('./pages/Page404'));
const ProgressionChecker = React.lazy(() => import('./pages/ProgressionChecker'));
const TermPlanner = React.lazy(() => import('./pages/TermPlanner'));

const App = () => {
  const [queryClient] = React.useState(
    () => new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false } } })
  );

  const { theme } = useSettings(queryClient);

  useEffect(() => {
    // using local storage since I don't want to risk invalidating the redux state right now
    const cooldownMs = 1000 * 60 * 60 * 24 * 7; // every 7 days
    const lastSeen = localStorage.getItem('last-seen-contribution');
    if (lastSeen !== null && Date.now() - parseInt(lastSeen, 10) < cooldownMs) return;

    localStorage.setItem('last-seen-contribution', Date.now().toString());

    openNotification({
      type: 'info',
      message: 'Want to contribute?',
      description: (
        <>
          Found a bug or have feedback? Open an issue on{' '}
          <a
            href="https://github.com/devsoc-unsw/circles/issues"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>{' '}
          or share your thoughts on{' '}
          <a href="https://discord.gg/u9p34WUTcs" target="_blank" rel="noopener noreferrer">
            Discord
          </a>
          !
          <br />
          <br />
          Feeling brave? You can even fix it yourself by submitting a{' '}
          <a
            href="https://github.com/devsoc-unsw/circles/pulls"
            target="_blank"
            rel="noopener noreferrer"
          >
            pull request
          </a>
          !
          <br />
          <br />
          Let&apos;s make <strong>Circles</strong> even better, together! &#128156;
        </>
      ),
      duration: 20,
      icon: <NotificationOutlined style={{ color: lightTheme.purplePrimary }} />
    });
  }, []);

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#9254de'
        },
        algorithm: theme === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm
      }}
    >
      <AntdApp>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme === 'light' ? lightTheme : darkTheme}>
            <GlobalStyles />
            <ErrorBoundary>
              <Suspense fallback={<PageLoading />}>
                <Router>
                  <Routes>
                    <Route element={<IdentityProvider />}>
                      <Route path="/" element={<LandingPage />} />
                      <Route element={<PreventToken />}>
                        <Route path="/login" element={<Login />} />
                      </Route>
                      <Route element={<RequireToken />}>
                        <Route path="/degree-wizard" element={<DegreeWizard />} />
                      </Route>
                      <Route element={<RequireToken needSetup />}>
                        <Route path="/course-selector" element={<CourseSelector />} />
                        {inDev && (
                          <Route path="/graphical-selector" element={<GraphicalSelector />} />
                        )}
                        <Route path="/term-planner" element={<TermPlanner />} />
                        <Route path="/progression-checker" element={<ProgressionChecker />} />
                      </Route>
                      <Route path="/logout" element={<Logout />} />
                    </Route>
                    <Route path="/login/success/:provider" element={<LoginSuccess />} />
                    <Route path="*" element={<Page404 />} />
                  </Routes>
                </Router>
              </Suspense>
            </ErrorBoundary>
          </ThemeProvider>
        </QueryClientProvider>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;
