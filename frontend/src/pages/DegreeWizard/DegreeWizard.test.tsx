import React from 'react';
import * as reactRouterDom from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from 'test/testUtil';
import { getUserDegree } from 'utils/api/userApi';
import { vi } from 'vitest';
import DegreeWizard from './DegreeWizard';

describe('DegreeWizard', () => {
  const useNavigateMock = vi.spyOn(reactRouterDom, 'useNavigate');

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render', async () => {
    await renderWithProviders(<DegreeWizard />);
    expect(screen.getByText('Welcome to Circles!')).toBeInTheDocument();
  });

  it('test degree wizard user flow', async () => {
    const dummyNavigate = vi.fn();
    useNavigateMock.mockReturnValue(dummyNavigate);

    await renderWithProviders(<DegreeWizard />);
    expect(screen.getByText('Welcome to Circles!')).toBeInTheDocument();

    // select years
    await waitFor(() => expect(screen.getByTestId('antd-rangepicker')).toBeInTheDocument(), {
      timeout: 5000
    });
    await React.act(async () => {
      await userEvent.click(screen.getByTestId('antd-rangepicker'));
    });
    await React.act(async () => {
      await userEvent.click(screen.getByText('2020'));
      await userEvent.click(screen.getByText('2022'));
    });
    await React.act(async () => {
      // select degree
      await waitFor(
        () => expect(screen.getByPlaceholderText('Search Degree')).toBeInTheDocument(),
        { timeout: 5000 }
      );
      userEvent.type(screen.getByPlaceholderText('Search Degree'), 'comp');
      await userEvent.click(await screen.findByText('3778 Computer Science'));
    });

    // select majors
    await waitFor(() =>
      expect(screen.getByText('Majors for Computer Science')).toBeInTheDocument()
    );
    await userEvent.click(screen.getByText('COMPA1 Computer Science'));
    await userEvent.click(screen.getByText('Next'));

    // select minors
    await waitFor(() =>
      expect(screen.getByText('Minors for Computer Science')).toBeInTheDocument()
    );
    await userEvent.click(screen.getByText('Skip'));

    // finish degree wizard
    await userEvent.click(screen.getByText('Start browsing courses!'));

    // check final states
    // TODO: FIGURE OUT TOKEN HERE
    expect(await getUserDegree('')).toEqual({
      programCode: '3778',
      programName: 'Computer Science',
      specs: ['COMPA1']
    });
    expect(dummyNavigate).toBeCalledWith('/course-selector');
  });
});
