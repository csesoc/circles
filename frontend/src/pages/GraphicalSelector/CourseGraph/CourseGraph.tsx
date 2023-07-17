import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useQuery } from 'react-query';
import {
  ExpandAltOutlined,
  ShrinkOutlined,
  ZoomInOutlined,
  ZoomOutOutlined
} from '@ant-design/icons';
import type { Graph, GraphOptions, INode, Item } from '@antv/g6';
import { Button, Switch } from 'antd';
import { CourseEdge, CoursesAllUnlocked, GraphPayload } from 'types/api';
import { CoursesResponse, DegreeResponse } from 'types/userResponse';
import { useDebouncedCallback } from 'use-debounce';
import { getProgramGraph } from 'utils/api/programsApi';
import { getUserCourses, getUserDegree, getUsersUnlockedCourses } from 'utils/api/userApi';
import Spinner from 'components/Spinner';
import { useAppWindowSize } from 'hooks';
import { ZOOM_IN_RATIO, ZOOM_OUT_RATIO } from '../constants';
import { defaultEdge, defaultNode, mapNodeStyle, nodeStateStyles } from './graph';
import S from './styles';

type Props = {
  onNodeClick: (node: INode) => void;
  handleToggleFullscreen: () => void;
  fullscreen: boolean;
  focused?: string;
};

// TODO: dont use these
const DUMMYDEGREE: DegreeResponse = {
  isComplete: false,
  programCode: '3778',
  specs: ['COMPA1']
};
const DUMMYGRAPH: GraphPayload = { courses: [], edges: [] };
const DUMMYCOURSES: CoursesResponse = {};

const CourseGraph = ({ onNodeClick, handleToggleFullscreen, fullscreen, focused }: Props) => {
  const windowSize = useAppWindowSize();

  const graphRef = useRef<Graph | null>(null);
  const [loading, setLoading] = useState(true);
  const [showingUnlockedCourses, setShowingUnlockedCourses] = useState(false);

  const containerRef = useRef<HTMLDivElement | null>(null);

  const degreeQuery = useQuery('degree', getUserDegree);
  const degree: DegreeResponse = degreeQuery.isSuccess ? degreeQuery.data : DUMMYDEGREE;

  // TODO: combine the 'courses' like queries
  const coursesUnlockedQuery = useQuery('unlockedCourses', getUsersUnlockedCourses);
  const coursesUnlocked: CoursesAllUnlocked | undefined = coursesUnlockedQuery.data;

  const coursesQuery = useQuery('courses', getUserCourses);
  const selectedCourses = coursesQuery.isSuccess ? coursesQuery.data : DUMMYCOURSES;

  const programGraphQuery = useQuery({
    queryKey: 'graph',
    queryFn: () => getProgramGraph(degree.programCode, degree.specs),
    enabled: degreeQuery.isSuccess
  });
  const programGraph: GraphPayload = programGraphQuery.isSuccess
    ? programGraphQuery.data
    : DUMMYGRAPH;

  // TODO: make a non success handler
  const queriesSuccess =
    degreeQuery.isSuccess &&
    coursesQuery.isSuccess &&
    coursesUnlockedQuery.isSuccess &&
    programGraphQuery.isSuccess;

  const { programCode, specs } = degree;

  useEffect(() => {
    // courses is a list of course codes
    const initialiseGraph = async (courses: string[], courseEdges: CourseEdge[]) => {
      const container = containerRef.current;
      if (!container) return;

      const { Graph, Arrow } = await import('@antv/g6');

      const graphArgs: GraphOptions = {
        container,
        width: container.scrollWidth,
        height: container.scrollHeight,
        linkCenter: true,
        modes: {
          default: ['drag-canvas', 'zoom-canvas']
        },
        layout: {
          type: 'gForce',
          linkDistance: 500,
          nodeStrength: 2500,
          preventOverlap: true,
          onLayoutEnd: () => {
            setLoading(false);
          }
        },
        animate: true, // Boolean, whether to activate the animation when global changes happen
        animateCfg: {
          duration: 500, // Number, the duration of one animation
          easing: 'easeQuadInOut' // String, the easing function
        },
        defaultNode,
        defaultEdge: defaultEdge(Arrow),
        nodeStateStyles
      };

      graphRef.current = new Graph(graphArgs);

      const data = {
        nodes: courses.map((c) => mapNodeStyle(c, selectedCourses)),
        edges: courseEdges
      };

      graphRef.current.data(data);
      graphRef.current.render();

      graphRef.current.on('node:click', async (ev) => {
        // Clicking a node loads up course description for the course and set active
        // tab to course info
        onNodeClick(ev.item as INode);
      });

      graphRef.current.on('node:mouseenter', async (ev) => {
        const node = ev.item as Item;
        graphRef.current?.setItemState(node, 'hover', true);
      });

      graphRef.current.on('node:mouseleave', async (ev) => {
        const node = ev.item as Item;
        graphRef.current?.clearItemStates(node, 'hover');
      });
    };

    // setup the graph
    if (!graphRef.current && queriesSuccess) {
      const { edges, courses } = programGraph;
      if (courses.length !== 0 && edges.length !== 0) initialiseGraph(courses, edges);
    }
  }, [onNodeClick, queriesSuccess, selectedCourses, programCode, specs, programGraph]);

  const showAllCourses = () => {
    if (!graphRef.current) return;
    graphRef.current.getNodes().forEach((n) => n.show());
    graphRef.current.getEdges().forEach((e) => e.show());
  };

  const showUnlockedCourses = useCallback(async () => {
    if (!graphRef.current || !coursesUnlocked) return;

    const coursesStates = coursesUnlocked.courses_state;
    graphRef.current.getNodes().forEach((n) => {
      const id = n.getID();
      if (coursesStates[id]?.unlocked) {
        n.show();
        n.getOutEdges().forEach((e) => {
          if (coursesStates[e.getTarget().getID()]?.unlocked) e.show();
        });
      } else {
        n.hide();
        n.getEdges().forEach((e) => e.hide());
      }
    });
  }, [coursesUnlocked]);

  const handleZoomIn = () => {
    const viewportCenter = graphRef.current?.getViewPortCenterPoint();
    graphRef.current?.zoom(ZOOM_IN_RATIO, viewportCenter, true, {
      easing: 'easeQuadIn',
      duration: 200
    });
  };

  const handleZoomOut = () => {
    const viewportCenter = graphRef.current?.getViewPortCenterPoint();
    graphRef.current?.zoom(ZOOM_OUT_RATIO, viewportCenter, true, {
      easing: 'easeQuadOut',
      duration: 200
    });
  };

  // focus the focussed course
  useEffect(() => {
    if (focused) {
      graphRef.current?.focusItem(focused);
    }
  }, [focused]);

  // handle resizing
  const resizeGraph = useCallback(() => {
    const graph = graphRef.current;
    const container = containerRef.current;
    if (!graph || graph.get('destroyed')) return;
    if (!container || !container.scrollWidth || !container.scrollHeight) return;
    graph.changeSize(container.scrollWidth, container.scrollHeight);
  }, []);
  const resizeGraphDebounce = useDebouncedCallback(resizeGraph, 20, { maxWait: 20 });

  useEffect(() => {
    // resize on window size change
    resizeGraphDebounce();
  }, [windowSize, resizeGraphDebounce]);

  useEffect(() => {
    // resize instantly for fullscreening
    resizeGraph();
  }, [fullscreen, resizeGraph]);

  useEffect(() => {
    if (showingUnlockedCourses) showUnlockedCourses();
    else showAllCourses();
  }, [coursesQuery.dataUpdatedAt, showUnlockedCourses, showingUnlockedCourses]);

  return (
    <S.Wrapper ref={containerRef}>
      {loading ? (
        <S.SpinnerWrapper>
          <Spinner text="Loading graph..." />
        </S.SpinnerWrapper>
      ) : (
        <S.ToolsWrapper>
          Show All Courses
          <Switch
            checked={!showingUnlockedCourses}
            onChange={() => setShowingUnlockedCourses((prevState) => !prevState)}
          />
          <Button onClick={handleZoomIn} icon={<ZoomInOutlined />} />
          <Button onClick={handleZoomOut} icon={<ZoomOutOutlined />} />
          <Button
            onClick={handleToggleFullscreen}
            icon={fullscreen ? <ShrinkOutlined /> : <ExpandAltOutlined />}
          />
        </S.ToolsWrapper>
      )}
    </S.Wrapper>
  );
};

export default CourseGraph;
