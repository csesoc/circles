import React from 'react';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from 'test/testUtil';
import { getUserPlanner } from 'utils/api/userApi';
import { vi } from 'vitest';
import CourseSelector from './CourseSelector';

vi.mock('components/DraggableTab', () => ({
  default: ({ tabName }: { tabName: string }) => <div>{tabName}</div>
}));

describe('CourseSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render', async () => {
    await renderWithProviders(<CourseSelector />);
    expect(screen.getByText('3778 - Computer Science')).toBeInTheDocument();
    expect(await screen.findByText('Major - COMPA1 - Computer Science')).toBeInTheDocument();
    expect(await screen.findByText('Core Courses')).toBeInTheDocument();
    expect(await screen.findByText('COMP1511: Programming Fundamentals')).toBeInTheDocument();
  });

  it('should toggle locked courses', async () => {
    await renderWithProviders(<CourseSelector />);
    expect(await screen.findByText('COMP1511: Programming Fundamentals')).toBeInTheDocument();
    expect(screen.queryByText('COMP2521: Data Structures and Algorithms')).not.toBeInTheDocument();
    await userEvent.click(screen.getByTestId('show-all-courses'));
    expect(screen.getByText('COMP2521: Data Structures and Algorithms')).toBeInTheDocument();
  });

  it('should be able to quick add and remove a course from the course menu', async () => {
    await renderWithProviders(<CourseSelector />);
    expect(await screen.findByText('COMP1511: Programming Fundamentals')).toBeInTheDocument();
    await userEvent.click(screen.getByTestId('quick-add-cart-button'));
    // TODO: idk how to get token into here...
    let planner = await getUserPlanner('');
    expect(planner.unplanned).toEqual(['COMP1511']);
    planner = await getUserPlanner('');
    await userEvent.click(screen.getByTestId('quick-remove-cart-button'));
    expect(planner.unplanned).toEqual([]);
  });
});
