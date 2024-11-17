import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';

type Theme = 'light' | 'dark';

type SettingsSliceState = {
  theme: Theme;
  showLockedCourses: boolean;
  showPastWarnings: boolean;
};

export const initialSettingsState: SettingsSliceState = {
  theme: 'light',
  showLockedCourses: false,
  showPastWarnings: true
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState: initialSettingsState,
  reducers: {
    resetSettings: () => initialSettingsState,
    toggleTheme: (state, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
    },
    toggleLockedCourses: (state) => {
      state.showLockedCourses = !state.showLockedCourses;
    },
    toggleShowPastWarnings: (state) => {
      state.showPastWarnings = !state.showPastWarnings;
    }
  }
});

export const { resetSettings, toggleTheme, toggleLockedCourses, toggleShowPastWarnings } =
  settingsSlice.actions;

export default settingsSlice.reducer;
