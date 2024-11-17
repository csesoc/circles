import React, { PropsWithChildren } from 'react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { vi } from 'vitest';
import axios from 'config/axios';
import { RootState, setupStore } from 'config/store';
import { lightTheme } from 'config/theme';
import '@testing-library/jest-dom';
// This type interface extends the default options for render from RTL, as well
// as allows the user to specify other things such as initialState, store.
interface ExtendedRenderOptions extends Omit<RenderOptions, 'queries'> {
  preloadedState?: RootState;
}

// eslint-disable-next-line import/prefer-default-export
export const renderWithProviders = async (
  ui: React.ReactElement,
  {
    preloadedState = {
      courseTabs: {
        tabs: [], // list of course codes i.e. ['COMP1511', 'COMP1521']
        active: 0 // index of the active tab in the tabs array
      },
      settings: {
        theme: 'dark',
        showLockedCourses: false,
        showPastWarnings: false
      },
      identity: null
    },
    ...renderOptions
  }: ExtendedRenderOptions = {}
) => {
  const queryClient = new QueryClient();
  await axios.post('user/reset');
  const store = setupStore(preloadedState);
  vi.mock('redux-persist', async (importOriginal) => {
    const mod = await importOriginal<typeof import('redux-persist')>();
    return {
      ...mod,
      getStoredState: async () => ({
        settings: {
          theme: 'dark',
          showLockedCourses: true,
          showPastWarnings: true,
          token: 'token' // force token to be dummy
        }
      })
    };
  });

  const Wrapper = ({ children }: PropsWithChildren) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ThemeProvider theme={lightTheme}>
          <Provider store={store}>{children}</Provider>
        </ThemeProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );

  // Return an object with the store and all of RTL's query functions
  return render(ui, { wrapper: Wrapper, ...renderOptions });
};
