import React, { Suspense, useEffect, useRef, useState } from 'react';
import type { DraggingStyle } from 'react-beautiful-dnd';
import { useDispatch, useSelector } from 'react-redux';
import { CloseOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { useTheme } from 'styled-components';
import Spinner from 'components/Spinner';
import type { RootState } from 'config/store';
import useIntersectionObserver from 'hooks/useIntersectionObserver';
import { removeTab, setActiveTab } from 'reducers/courseTabsSlice';
import S from './styles';

const Draggable = React.lazy(() =>
  import('react-beautiful-dnd').then((plot) => ({ default: plot.Draggable }))
);

type Props = {
  tabName: string;
  index: number;
};

const DraggableTab = ({ tabName, index }: Props) => {
  const [scrolledTo, setScrolledTo] = useState(false);
  const dispatch = useDispatch();
  const ref = useRef<HTMLDivElement | null>(null);
  const tabInView = useIntersectionObserver(ref);
  const { active } = useSelector((state: RootState) => state.courseTabs);
  const theme = useTheme();

  const getDraggableStyle = (style: DraggingStyle) => {
    // lock x axis when dragging
    if (style?.transform) {
      return {
        ...style,
        // style.transform = transform(Xpx, Ypx) - splitting string to only get the X position
        // and lock the Y position when dragging
        transform: `${style.transform.split(',')[0]}, 0px)`
      };
    }
    return style;
  };

  useEffect(() => {
    if (active === index && !scrolledTo && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth' });
      setScrolledTo(true);
    }
    setScrolledTo(false);
  }, [active, tabInView, index, scrolledTo]);

  const handleOnClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // stop propagation for above tab onclick event
    dispatch(removeTab(index));
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLElement>) => {
    const MIDDLE_CLICK_BTN = 1;
    if (e.button === MIDDLE_CLICK_BTN) {
      dispatch(removeTab(index));
    }
  };

  return (
    <Suspense fallback={<Spinner text="Loading..." />}>
      <Draggable key={tabName} draggableId={tabName} index={index}>
        {(draggableProvided) => (
          <S.DraggableTabWrapper
            role="tab"
            $active={index === active}
            onClick={() => dispatch(setActiveTab(index))}
            ref={(r) => {
              ref.current = r;
              draggableProvided.innerRef(r);
            }}
            {...draggableProvided.draggableProps}
            {...draggableProvided.dragHandleProps}
            style={getDraggableStyle(draggableProvided.draggableProps.style as DraggingStyle)}
            onMouseUp={handleMouseUp}
          >
            <S.TabNameWrapper>{tabName}</S.TabNameWrapper>
            <Button
              type="text"
              size="small"
              icon={<CloseOutlined style={{ fontSize: '12px', color: theme.text }} />}
              onClick={handleOnClick}
            />
          </S.DraggableTabWrapper>
        )}
      </Draggable>
    </Suspense>
  );
};

export default DraggableTab;
