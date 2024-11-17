import type { Arrow } from '@antv/g6';

const plannedNode = {
  size: 70,
  style: {
    fill: '#9254de',
    stroke: '#9254de',
    cursor: 'pointer',
    lineWidth: 1
  },
  labelCfg: {
    style: {
      fill: '#fff',
      fontFamily: 'Arial',
      cursor: 'pointer'
    }
  }
};

const lockedNode = (theme: string) => ({
  style: {
    fill: theme === 'light' ? '#fff' : '#000',
    stroke: theme === 'light' ? '#9254de' : '#d7b7fd',
    lineWidth: 1
  },
  labelCfg: {
    style: {
      fill: theme === 'light' ? '#9254de' : '#d7b7fd'
    }
  }
});

const unlockedNode = (theme: string) => ({
  style: {
    fill: theme === 'light' ? '#fbefff' : '#381f56',
    stroke: theme === 'light' ? '#9254de' : '#d7b7fd',
    lineWidth: 1
  },
  labelCfg: {
    style: {
      fill: theme === 'light' ? '#9254de' : '#d7b7fd'
    }
  }
});

const prereqNode = (theme: string) => ({
  style: {
    stroke: theme === 'light' ? '#000' : '#fff',
    lineWidth: 2
  }
});

const sameNode = (courseCode: string) => ({
  id: courseCode,
  label: courseCode
});

const nodeStateStyles = {
  hover: {
    fill: '#b37feb',
    stroke: '#b37feb'
  },
  click: {
    fill: '#b37feb',
    stroke: '#b37feb'
  }
};

const plannedLabel = {
  labelCfg: {
    style: {
      fill: '#fff'
    }
  }
};

const lockedLabel = (theme: string) => ({
  labelCfg: {
    style: {
      fill: theme === 'light' ? '#9254de' : '#d7b7fd'
    }
  }
});

const nodeLabelHoverStyle = (courseCode: string) => ({
  ...sameNode(courseCode),
  ...plannedLabel
});

const nodeLabelUnhoverStyle = (courseCode: string, isPlanned: boolean, theme: string) => {
  if (isPlanned) {
    return {
      ...sameNode(courseCode),
      ...plannedLabel
    };
  }
  return {
    ...sameNode(courseCode),
    ...lockedLabel(theme)
  };
};

const arrowColor = (theme: string) => ({
  default: theme === 'light' ? '#e0e0e0' : '#4a4a4a',
  outHover: theme === 'light' ? '#999' : '#aaa',
  inHover: theme === 'light' ? '#000' : '#fff'
});

const defaultEdge = (arrow: typeof Arrow, theme: string) => ({
  style: {
    endArrow: {
      path: arrow.triangle(5, 5, 30),
      fill: arrowColor(theme).default,
      d: 25
    },
    stroke: arrowColor(theme).default
  }
});

const edgeOutHoverStyle = (arrow: typeof Arrow, theme: string, id: string) => ({
  id,
  style: {
    endArrow: {
      path: arrow.triangle(5, 5, 30),
      fill: arrowColor(theme).outHover,
      d: 25
    },
    stroke: arrowColor(theme).outHover,
    opacity: 1
  }
});

const edgeInHoverStyle = (arrow: typeof Arrow, theme: string, id: string) => ({
  id,
  style: {
    endArrow: {
      path: arrow.triangle(5, 5, 30),
      fill: arrowColor(theme).inHover,
      d: 25
    },
    stroke: arrowColor(theme).inHover,
    opacity: 1
  }
});

const edgeUnhoverStyle = (arrow: typeof Arrow, theme: string, id: string) => {
  return {
    id,
    ...defaultEdge(arrow, theme)
  };
};

const mapNodeStyle = (
  courseCode: string,
  isPlanned: boolean,
  isUnlocked: boolean,
  theme: string
) => {
  if (isPlanned) return { ...sameNode(courseCode), ...plannedNode };
  if (isUnlocked) return { ...sameNode(courseCode), ...unlockedNode(theme) };
  return { ...sameNode(courseCode), ...lockedNode(theme) };
};

const mapNodePrereq = (courseCode: string, theme: string) => {
  return {
    ...sameNode(courseCode),
    ...prereqNode(theme)
  };
};

const mapNodeOpacity = (courseCode: string, opacity: number) => {
  return {
    ...sameNode(courseCode),
    style: {
      opacity
    },
    labelCfg: {
      style: {
        opacity
      }
    }
  };
};

// Changes opacity but also changes edge to default style due to endArrow styling
const mapEdgeOpacity = (arrow: typeof Arrow, theme: string, id: string, opacity: number) => ({
  id,
  style: {
    opacity,
    endArrow: {
      path: arrow.triangle(5, 5, 30),
      fill: arrowColor(theme).default,
      opacity,
      d: 25
    }
  }
});

export {
  defaultEdge,
  edgeInHoverStyle,
  edgeOutHoverStyle,
  edgeUnhoverStyle,
  mapEdgeOpacity,
  mapNodeOpacity,
  mapNodePrereq,
  mapNodeStyle,
  nodeLabelHoverStyle,
  nodeLabelUnhoverStyle,
  nodeStateStyles,
  plannedNode
};
