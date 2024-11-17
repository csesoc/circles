import React from 'react';
import * as reactRouterDom from 'react-router-dom';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from 'test/testUtil';
import openNotification from 'utils/openNotification';
import { vi } from 'vitest';
import * as hooks from 'hooks';
import StartBrowsingStep from './StartBrowsingStep';

const mockDegreeInfo = {
  programCode: '3778',
  startYear: 2020,
  endYear: 2024,
  specs: ['COMPA1']
};

describe('StartBrowsingStep', () => {
  const useDispatchMock = vi.spyOn(hooks, 'useAppDispatch');
  const useNavigateMock = vi.spyOn(reactRouterDom, 'useNavigate');

  beforeEach(() => {
    useDispatchMock.mockClear();
    useNavigateMock.mockClear();
    vi.clearAllMocks();
  });

  it('should render', async () => {
    await renderWithProviders(<StartBrowsingStep degreeInfo={mockDegreeInfo} />);
    expect(screen.getByText('Start browsing courses!')).toBeInTheDocument();
  });

  it('should call openNotification when program code is not provided', async () => {
    const degreeInfo = { ...mockDegreeInfo };
    degreeInfo.programCode = '';
    await renderWithProviders(<StartBrowsingStep degreeInfo={degreeInfo} />);
    await userEvent.click(screen.getByText('Start browsing courses!'));
    expect(openNotification).toBeCalledWith({
      message: 'Please select a degree',
      type: 'error'
    });
  });

  it('should call openNotification when a specialisation is not provided', async () => {
    const degreeInfo = { ...mockDegreeInfo };
    degreeInfo.specs = [];
    await renderWithProviders(<StartBrowsingStep degreeInfo={degreeInfo} />);
    await userEvent.click(screen.getByText('Start browsing courses!'));
    expect(openNotification).toBeCalledWith({
      message: 'Please select a specialisation',
      type: 'error'
    });
  });

  it('should navigate to course selector', async () => {
    const dummyNavigate = vi.fn();
    useNavigateMock.mockReturnValue(dummyNavigate);
    await renderWithProviders(<StartBrowsingStep degreeInfo={mockDegreeInfo} />);
    await userEvent.click(screen.getByText('Start browsing courses!'));
    await React.act(async () => {
      await vi.waitFor(() => expect(dummyNavigate).toBeCalledWith('/course-selector'));
    });
  });
});
