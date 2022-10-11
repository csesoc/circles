import type { Arrow } from '@antv/g6';

const defaultNode = {
  size: 70,
  style: {
    fill: '#9254de',
    stroke: '#9254de',
    cursor: 'pointer'
  },
  labelCfg: {
    style: {
      fill: '#fff',
      fontFamily: 'Arial',
      cursor: 'pointer'
    }
  }
};

const defaultEdge = (arrow: typeof Arrow) => ({
  style: {
    endArrow: {
      path: arrow.triangle(5, 5, 30),
      fill: '#e0e0e0',
      d: 25
    }
  }
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

const unplannedNodeAdditionalStyle = (courseCode: string) => ({
  id: courseCode,
  label: courseCode,
  style: {
    fill: '#fff',
    stroke: '#9254de'
  },
  labelCfg: {
    style: {
      fill: '#9254de'
    }
  }
});

export default {
  defaultNode,
  defaultEdge,
  nodeStateStyles,
  unplannedNodeAdditionalStyle
};
