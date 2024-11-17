import React from 'react';
import { notification } from 'antd';
import { ArgsProps } from 'antd/lib/notification';

type IconType = ArgsProps['type'];

type Props = {
  type: IconType;
  message?: string;
  description?: React.ReactNode;
  duration?: number;
  icon?: React.ReactNode;
};

const openNotification = ({ type = 'info', message, description, duration = 5, icon }: Props) => {
  notification.open({
    type,
    message,
    description,
    duration,
    placement: 'bottomRight',
    icon
  });
};

export default openNotification;
