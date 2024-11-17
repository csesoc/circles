import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from 'redux';
import storage from 'redux-persist/lib/storage';
import courseTabsReducer from 'reducers/courseTabsSlice';
import identityReducer from 'reducers/identitySlice';
import settingsReducer from 'reducers/settingsSlice';
import persistMigrate, { persistVersion } from './migrations';

export const rootReducer = combineReducers({
  courseTabs: courseTabsReducer,
  settings: settingsReducer,
  identity: identityReducer
});

export const setupStore = (preloadedState?: RootState) =>
  configureStore({
    reducer: rootReducer,
    preloadedState
  });

export const persistConfig = {
  key: 'root',
  version: persistVersion,
  storage,
  whitelist: ['settings'],
  migrate: persistMigrate
};

export type RootState = ReturnType<typeof rootReducer>;
export type AppStore = ReturnType<typeof setupStore>;
export type AppDispatch = AppStore['dispatch'];
