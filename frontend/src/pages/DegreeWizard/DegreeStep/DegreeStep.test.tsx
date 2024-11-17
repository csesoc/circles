import React from 'react';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { renderWithProviders } from 'test/testUtil';
import { vi } from 'vitest';
import * as hooks from 'hooks';
import Steps from '../common/steps';
import DegreeStep from './DegreeStep';

const axiosMock = new MockAdapter(axios);
axiosMock.onGet('/programs/getPrograms').reply(200, {
  programs: {
    3778: 'Computer Science'
  }
});

const incrementStepMock = vi.fn();
const setDegreeInfoMock = vi.fn();

describe('DegreeStep', () => {
  const useDispatchMock = vi.spyOn(hooks, 'useAppDispatch');

  beforeEach(() => {
    useDispatchMock.mockClear();
    vi.clearAllMocks();
  });

  it('should render', () => {
    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    expect(screen.getByText('What are you studying?')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search Degree')).toBeInTheDocument();
  });

  it('should dispatch correct props and call incrementStep after selecting degree', async () => {
    const dummyDispatch = vi.fn();
    useDispatchMock.mockReturnValue(dummyDispatch);

    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    expect(screen.getByPlaceholderText('Search Degree')).toBeInTheDocument();
    userEvent.type(screen.getByPlaceholderText('Search Degree'), 'comp');
    await userEvent.click(await screen.findByText('3778 Computer Science'));
    expect(dummyDispatch).toBeCalledWith({
      payload: {
        programCode: '3778',
        programName: 'Computer Science'
      },
      type: 'degree/setProgram'
    });
    expect(incrementStepMock).toHaveBeenCalledWith(Steps.SPECS);
  });

  it('should show no degree options on mount', async () => {
    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    expect(screen.queryByText('Computer Science')).not.toBeInTheDocument();
  });

  it('should search degree based on program code', async () => {
    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    userEvent.type(screen.getByPlaceholderText('Search Degree'), '3778');
    expect(await screen.findByText('3778 Computer Science')).toBeInTheDocument();
  });

  it('should search degree based on program name', async () => {
    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    userEvent.type(screen.getByPlaceholderText('Search Degree'), 'Computer Science');
    expect(await screen.findByText('3778 Computer Science')).toBeInTheDocument();
  });

  it('should search degree case insensitively', async () => {
    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    userEvent.type(screen.getByPlaceholderText('Search Degree'), 'computer science');
    expect(await screen.findByText('3778 Computer Science')).toBeInTheDocument();
  });

  it('should not show degree options if no match', async () => {
    renderWithProviders(
      <DegreeStep incrementStep={incrementStepMock} setDegreeInfo={setDegreeInfoMock} />
    );
    userEvent.type(screen.getByPlaceholderText('Search Degree'), 'Economics');
    expect(screen.queryByTestId('antd-degree-menu')).not.toBeInTheDocument();
  });
});
