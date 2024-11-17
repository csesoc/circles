import React from 'react';
import { IoIosSunny, IoMdMoon } from 'react-icons/io';
import { Switch } from 'antd';
import useSettings from 'hooks/useSettings';

const ThemeToggle = () => {
  const { theme, mutateTheme } = useSettings();

  const toggleStyle = {
    backgroundColor: theme === 'light' ? '#b37feb' : '#722ed1'
  };

  return (
    <Switch
      checkedChildren={<IoMdMoon />}
      unCheckedChildren={<IoIosSunny />}
      defaultChecked={theme === 'dark'}
      onChange={() => mutateTheme(theme === 'light' ? 'dark' : 'light')}
      style={toggleStyle}
    />
  );
};

export default ThemeToggle;
