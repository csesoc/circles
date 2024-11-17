import React from 'react';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from 'test/testUtil';
import openNotification from 'utils/openNotification';
import { vi } from 'vitest';
import * as hooks from 'hooks';
import SpecialisationStep from './SpecialisationStep';

const mockDegreeInfo = {
  programCode: '3778',
  startYear: undefined,
  endYear: undefined,
  specs: []
};

const incrementStepMock = vi.fn();
const setDegreeInfoMock = vi.fn();

describe('SpecialisationStep', () => {
  const useDispatchMock = vi.spyOn(hooks, 'useAppDispatch');

  beforeEach(() => {
    useDispatchMock.mockClear();
    vi.clearAllMocks();
  });

  it('should render', async () => {
    await renderWithProviders(
      <SpecialisationStep
        incrementStep={incrementStepMock}
        type="majors"
        degreeInfo={mockDegreeInfo}
        setDegreeInfo={setDegreeInfoMock}
      />
    );
    expect(screen.queryByText('Next')).not.toBeInTheDocument();
    expect(screen.getByText('What are your majors?')).toBeInTheDocument();
    expect(await screen.findByText('Majors for Computer Science')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Note: COMPA1 is the default stream, and will be used if no other stream is selected.'
      )
    ).toBeInTheDocument();
    expect(screen.getByText('COMPA1 Computer Science')).toBeInTheDocument();
    expect(screen.getByText('COMPD1 Computer Science (Database Systems)')).toBeInTheDocument();
    expect(screen.getByText('COMPE1 Computer Science (eCommerce Systems)')).toBeInTheDocument();
    expect(
      screen.getByText('COMPI1 Computer Science (Artificial Intelligence)')
    ).toBeInTheDocument();
    expect(screen.getByText('COMPN1 Computer Science (Computer Networks)')).toBeInTheDocument();
    expect(screen.getByText('COMPS1 Computer Science (Embedded Systems)')).toBeInTheDocument();
    expect(screen.getByText('COMPY1 Computer Science (Security Engineering)')).toBeInTheDocument();
    expect(screen.getByText('COMPJ1 Computer Science (Programming Languages)')).toBeInTheDocument();
  });

  it('should set degree info when adding an item', async () => {
    const dummyDispatch = vi.fn();
    useDispatchMock.mockReturnValue(dummyDispatch);

    await renderWithProviders(
      <SpecialisationStep
        incrementStep={incrementStepMock}
        type="majors"
        degreeInfo={mockDegreeInfo}
        setDegreeInfo={setDegreeInfoMock}
      />
    );
    await userEvent.click(await screen.findByText('COMPA1 Computer Science'));
    expect(setDegreeInfoMock).toBeCalled();
  });

  it('should display "Next" button when on current step and call incrementStep', async () => {
    await renderWithProviders(
      <SpecialisationStep
        incrementStep={incrementStepMock}
        currStep
        type="majors"
        degreeInfo={mockDegreeInfo}
        setDegreeInfo={setDegreeInfoMock}
      />
    );
    await userEvent.click(await screen.findByText('COMPA1 Computer Science'));
    await userEvent.click(await screen.findByText('Next'));
  });

  it('should show error notification when "Next" button without selecting a spec', async () => {
    await renderWithProviders(
      <SpecialisationStep
        incrementStep={incrementStepMock}
        currStep
        type="majors"
        degreeInfo={mockDegreeInfo}
        setDegreeInfo={setDegreeInfoMock}
      />
    );
    await userEvent.click(await screen.findByText('Next'));
    expect(openNotification).toBeCalledWith({
      message: 'Select a major for Computer Science',
      type: 'error'
    });
  });
});
