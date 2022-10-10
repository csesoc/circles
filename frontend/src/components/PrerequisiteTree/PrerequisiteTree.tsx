import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { Item, TreeGraph, TreeGraphData } from '@antv/g6';
import axios from 'axios';
import { CourseChildren, CoursePathFrom } from 'types/api';
import { CourseList } from 'types/courses';
import Spinner from 'components/Spinner';
import type { RootState } from 'config/store';
import { addTab } from 'reducers/courseTabsSlice';
import GRAPH_STYLE from './config';
import TREE_CONSTANTS from './constants';
import S from './styles';
import { bringEdgeLabelsToFront, calcHeight, handleNodeData, updateEdges } from './utils';

type Props = {
  courseCode: string;
};

const PrerequisiteTree = ({ courseCode }: Props) => {
  const [loading, setLoading] = useState(true);
  const [graph, setGraph] = useState<TreeGraph | null>(null);
  const [courseUnlocks, setCourseUnlocks] = useState<CourseList>([]);
  const [coursesRequires, setCoursesRequires] = useState<CourseList>([]);
  const dispatch = useDispatch();
  const ref = useRef<HTMLDivElement | null>(null);
  const { degree, planner } = useSelector((state: RootState) => state);

  useEffect(() => {
    /* GRAPH IMPLEMENTATION */
    const generateTreeGraph = async (graphData: TreeGraphData) => {
      const container = ref.current;
      if (!container) return;
      const { TreeGraph } = await import('@antv/g6');

      const treeGraphInstance = new TreeGraph({
        container,
        width: container.scrollWidth,
        height: container.scrollHeight,
        fitView: true,
        layout: GRAPH_STYLE.graphLayout,
        defaultNode: GRAPH_STYLE.defaultNode,
        defaultEdge: GRAPH_STYLE.defaultEdge
      });

      setGraph(treeGraphInstance);

      treeGraphInstance.data(graphData);

      updateEdges(treeGraphInstance, graphData);

      treeGraphInstance.render();

      bringEdgeLabelsToFront(treeGraphInstance);

      treeGraphInstance.on('node:click', (event) => {
        // open new course tab
        const node = event.item as Item;
        dispatch(addTab(node.getModel().label as string));
      });
    };

    // NOTE: This is for hot reloading in development as new graph will instantiate every time
    const updateTreeGraph = (graphData: TreeGraphData) => {
      if (!graph) return;
      graph.changeData(graphData);
      bringEdgeLabelsToFront(graph);
    };

    /* REQUESTS */
    const getCourseUnlocks = async (code: string) => {
      try {
        const res = await axios.get<CourseChildren>(`/courses/courseChildren/${code}`);
        return res.data.courses;
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Error at getCourseUnlocks', e);
        return [];
      }
    };

    const getCoursePrereqs = async (code: string) => {
      try {
        const res = await axios.get<CoursePathFrom>(`/courses/getPathFrom/${code}`);
        return res.data.courses;
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Error at getCoursePrereqs', e);
        return [];
      }
    };

    /* MAIN */
    const setupGraph = async (c: string) => {
      setLoading(true);

      const unlocks = await getCourseUnlocks(c);
      if (unlocks) setCourseUnlocks(unlocks);
      const prereqs = await getCoursePrereqs(c);
      if (prereqs) setCoursesRequires(prereqs);

      // create graph data
      const graphData = {
        id: 'root',
        label: courseCode,
        children: prereqs
          ?.map((child) => handleNodeData(child, TREE_CONSTANTS.PREREQ))
          .concat(unlocks?.map((child) => handleNodeData(child, TREE_CONSTANTS.UNLOCKS)))
      };

      // render graph
      if (!graph && graphData.children.length !== 0) {
        generateTreeGraph(graphData);
      } else {
        // NOTE: This is for hot reloading in development as new graph will instantiate every time
        updateTreeGraph(graphData);
      }
      setLoading(false);
    };
    if (courseCode) setupGraph(courseCode);
  }, [courseCode, degree, dispatch, graph, planner]);

  return (
    <S.PrereqTreeContainer ref={ref} height={calcHeight(coursesRequires, courseUnlocks)}>
      {loading && <Spinner text="Loading tree..." />}
      {!loading && !graph?.getNodes && (
        <p> No prerequisite visualisation is needed for this course </p>
      )}
    </S.PrereqTreeContainer>
  );
};

export default PrerequisiteTree;
