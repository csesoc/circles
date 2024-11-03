import React, { useEffect, useRef, useState } from 'react';
import type { Item, TreeGraph, TreeGraphData } from '@antv/g6';
import { useCourseChildrenQuery, useCoursePrereqsQuery } from 'utils/apiHooks/static';
import Spinner from 'components/Spinner';
import GRAPH_STYLE from './config';
import TREE_CONSTANTS from './constants';
import S from './styles';
import { bringEdgeLabelsToFront, calcHeight, handleNodeData, updateEdges } from './utils';

type Props = {
  courseCode: string;
  onCourseClick?: (code: string) => void;
};

const PrerequisiteTree = ({ courseCode, onCourseClick }: Props) => {
  const [initGraph, setInitGraph] = useState(true);
  const graphRef = useRef<TreeGraph | null>(null);
  const ref = useRef<HTMLDivElement | null>(null);

  const childrenQuery = useCourseChildrenQuery(
    { queryOptions: { select: (data) => data.courses } },
    courseCode
  );

  const prereqsQuery = useCoursePrereqsQuery(
    { queryOptions: { select: (data) => data.courses } },
    courseCode
  );

  useEffect(() => {
    // if the course code changes, force a reload (REQUIRED)
    setInitGraph(true);
  }, [courseCode]);

  useEffect(() => {
    /* GRAPH IMPLEMENTATION */
    const generateTreeGraph = async (graphData: TreeGraphData) => {
      const container = ref.current;
      if (!container) return;
      const { TreeGraph } = await import('@antv/g6');

      graphRef.current = new TreeGraph({
        container,
        width: container.scrollWidth,
        height: container.scrollHeight,
        fitView: true,
        layout: GRAPH_STYLE.graphLayout,
        defaultNode: GRAPH_STYLE.defaultNode,
        defaultEdge: GRAPH_STYLE.defaultEdge
      });

      graphRef.current.data(graphData);

      updateEdges(graphRef.current, graphData);

      graphRef.current.render();

      bringEdgeLabelsToFront(graphRef.current);

      graphRef.current.on('node:click', (event) => {
        // open new course tab
        const node = event.item as Item;
        if (onCourseClick) onCourseClick(node.getModel().label as string);
      });

      setInitGraph(false);
    };

    const updateTreeGraph = (graphData: TreeGraphData) => {
      // TODO: fix sizing change here (will need to use graph.changeSize with the scroll height/width)
      // Doing so has weird interactions where it grows in width each update,
      // which gets influenced by the margins from here and Collapsible, and by the loading spinner size (= 142px)
      if (!graphRef.current) return;
      graphRef.current.changeData(graphData);
      bringEdgeLabelsToFront(graphRef.current);

      setInitGraph(false);
    };

    if (initGraph && !childrenQuery.isPending && !prereqsQuery.isPending) {
      const unlocks = childrenQuery.data ?? [];
      const prereqs = prereqsQuery.data ?? [];
      const graphData = {
        id: 'root',
        label: courseCode,
        children: prereqs
          .map((child) => handleNodeData(child, TREE_CONSTANTS.PREREQ))
          .concat(unlocks.map((child) => handleNodeData(child, TREE_CONSTANTS.UNLOCKS)))
      };

      if (!graphRef.current && graphData.children.length !== 0) {
        generateTreeGraph(graphData);
      } else {
        // NOTE: This is for hot reloading in development as new graph will instantiate every time
        updateTreeGraph(graphData);
      }
    }
  }, [
    courseCode,
    initGraph,
    onCourseClick,
    childrenQuery.data,
    prereqsQuery.data,
    childrenQuery.isPending,
    prereqsQuery.isPending
  ]);

  const loading = initGraph || childrenQuery.isPending || prereqsQuery.isPending;
  const height = calcHeight(prereqsQuery.data ?? [], childrenQuery.data ?? []);

  return (
    <S.PrereqTreeContainer ref={ref} $height={height}>
      {loading && <Spinner text="Loading tree..." />}
      {!loading && graphRef.current && graphRef.current.getEdges().length === 0 && (
        <p> No prerequisite visualisation is needed for this course </p>
      )}
    </S.PrereqTreeContainer>
  );
};

export default PrerequisiteTree;
