import React from 'react';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from 'test/testUtil';
import { vi } from 'vitest';
import * as hooks from 'hooks';
import ResetModal from './ResetModal';

describe('ResetModal', () => {
  const useDispatchMock = vi.spyOn(hooks, 'useAppDispatch');

  beforeEach(() => {
    useDispatchMock.mockClear();
    vi.clearAllMocks();
  });

  it('should render', async () => {
    await renderWithProviders(<ResetModal />);
    expect(screen.queryByText('Reset Planner?')).not.toBeInTheDocument();
  });

  // it('should show modal when degree wizard is complete', async () => {
  //   await renderWithProviders(<ResetModal open />);
  //   // TODO: idk what to do with token here
  //   await setIsComplete('', true);
  //   expect(screen.getByText('Reset Planner?')).toBeInTheDocument();
  // });

  // it('should reset state when reset button is clicked', async () => {
  //   const dummyDispatch = vi.fn();
  //   useDispatchMock.mockReturnValue(dummyDispatch);

  //   await renderWithProviders(<ResetModal open />);
  //   // TODO: idk what to do with token here
  //   await setIsComplete('', true);
  //   await userEvent.click(screen.getByText('Reset'));
  //   expect(dummyDispatch.mock.calls).toEqual([
  //     [{ payload: undefined, type: 'courseTabs/resetTabs' }]
  //   ]);
  // });

  it('should call the OnCancel callback when the Go Back button is clicked', async () => {
    const dummyOnCancel = vi.fn();

    await renderWithProviders(<ResetModal open onCancel={dummyOnCancel} />);
    await userEvent.click(screen.getByText('Go back'));
    expect(dummyOnCancel).toBeCalled();
  });

  it('should call the OnOk callback when the Reset button is clicked', async () => {
    const dummyOnOk = vi.fn();

    await renderWithProviders(<ResetModal open onOk={dummyOnOk} />);
    await userEvent.click(screen.getByText('Reset'));
    expect(dummyOnOk).toBeCalled();
  });
});
