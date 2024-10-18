import { useCallback } from 'react';
import { QueryClient, useQuery, useQueryClient } from '@tanstack/react-query';
import { SettingsResponse } from 'types/userResponse';
import { getUserSettings } from 'utils/api/userApi';
import {
  useHideYearMutation,
  useShowYearsMutation,
  useToggleMarksMutation
} from 'utils/apiHooks/user';
import { useAppDispatch, useAppSelector } from 'hooks';
import {
  toggleLockedCourses as toggleLocked,
  toggleShowPastWarnings as togglePastWarnings,
  toggleTheme
} from 'reducers/settingsSlice';
import useToken from './useToken';

type Theme = 'light' | 'dark';

export interface LocalSettings {
  theme: Theme;
  showLockedCourses: boolean;
  showPastWarnings: boolean;
}

export interface Settings extends LocalSettings, SettingsResponse {
  mutateTheme: (theme: Theme) => void;
  toggleShowMarks: () => void;
  hideYear: (yearIndex: number) => void;
  showYears: () => void;
  toggleLockedCourses: () => void;
  toggleShowPastWarnings: () => void;
}

const defaultUserSettings = {
  showMarks: false,
  hiddenYears: []
};

function useSettings(queryClient?: QueryClient): Settings {
  const localSettings = useAppSelector((state) => state.settings);
  const dispatch = useAppDispatch();

  const token = useToken({ allowUnset: true });
  const realQueryClient = useQueryClient(queryClient);
  const settingsQuery = useQuery(
    {
      queryKey: ['settings'],
      queryFn: () => getUserSettings(token!),
      placeholderData: defaultUserSettings,
      enabled: !!token
    },
    queryClient
  );
  const userSettings = settingsQuery.data ?? defaultUserSettings;

  const showMarksMutation = useToggleMarksMutation({
    allowUnsetToken: true,
    queryClient: realQueryClient
  });

  const hideYearMutation = useHideYearMutation({
    allowUnsetToken: true,
    queryClient: realQueryClient
  });

  const showYearsMutation = useShowYearsMutation({
    allowUnsetToken: true,
    queryClient: realQueryClient
  });

  const mutateTheme = useCallback((theme: Theme) => dispatch(toggleTheme(theme)), [dispatch]);
  const toggleLockedCourses = useCallback(() => dispatch(toggleLocked()), [dispatch]);
  const toggleShowPastWarnings = useCallback(() => dispatch(togglePastWarnings()), [dispatch]);
  const toggleShowMarks = showMarksMutation.mutate;
  const hideYear = hideYearMutation.mutate;
  const showYears = showYearsMutation.mutate;

  return {
    // Do not use the spread operator here, as it doesn't update after the mutation
    theme: localSettings.theme,
    showLockedCourses: localSettings.showLockedCourses,
    showPastWarnings: localSettings.showPastWarnings,
    showMarks: userSettings.showMarks,
    hiddenYears: userSettings.hiddenYears,
    mutateTheme,
    toggleShowMarks,
    hideYear,
    showYears,
    toggleLockedCourses,
    toggleShowPastWarnings
  };
}

export default useSettings;
