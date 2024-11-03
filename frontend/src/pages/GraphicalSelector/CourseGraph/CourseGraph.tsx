import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ExpandAltOutlined,
  ShrinkOutlined,
  ZoomInOutlined,
  ZoomOutOutlined
} from '@ant-design/icons';
import type { Graph, GraphOptions, IG6GraphEvent, INode, Item } from '@antv/g6';
import { Switch } from 'antd';
import { CourseEdge } from 'types/api';
import { useDebouncedCallback } from 'use-debounce';
import { useProgramGraphQuery } from 'utils/apiHooks/static';
import {
  useUserAllUnlocked,
  useUserCourses,
  useUserDegree,
  useUserPlanner
} from 'utils/apiHooks/user';
import { unwrapQuery } from 'utils/queryUtils';
import Spinner from 'components/Spinner';
import { useAppWindowSize } from 'hooks';
import useSettings from 'hooks/useSettings';
import { ZOOM_IN_RATIO, ZOOM_OUT_RATIO } from '../constants';
import {
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
} from './graph';
import S from './styles';

type Props = {
  onNodeClick: (node: INode) => void;
  handleToggleFullscreen: () => void;
  fullscreen: boolean;
  focused?: string;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
};

interface CoursePrerequisite {
  [key: string]: string[];
}

const CourseGraph = ({
  onNodeClick,
  handleToggleFullscreen,
  fullscreen,
  focused,
  loading,
  setLoading
}: Props) => {
  const degreeQuery = useUserDegree();
  const plannerQuery = useUserPlanner();
  const coursesQuery = useUserCourses();

  const windowSize = useAppWindowSize();
  const { theme } = useSettings();
  const previousTheme = useRef<typeof theme>(theme);

  const graphRef = useRef<Graph | null>(null);
  const initialisingStart = useRef(false); // prevents multiple graphs being loaded
  const initialisingEnd = useRef(false); // unhide graph after loading complete
  const [prerequisites, setPrerequisites] = useState<CoursePrerequisite>({});

  const containerRef = useRef<HTMLDivElement | null>(null);
  const [showingUnlockedCourses, setShowingUnlockedCourses] = useState(false);

  const programGraphQuery = useProgramGraphQuery(
    {
      queryOptions: { enabled: !degreeQuery.isPending && degreeQuery.data && degreeQuery.isSuccess }
    },
    // TODO-olli: this is ugly, but we will need some interesting type rules to allow this otherwise
    degreeQuery.data?.programCode ?? '',
    degreeQuery.data?.specs ?? []
  );

  const coursesStateQuery = useUserAllUnlocked();
  const coursesStatePrevLastUpdated = useRef<number>(0); // used to repaint on invalidation

  const queriesSuccess =
    degreeQuery.isSuccess && coursesQuery.isSuccess && programGraphQuery.isSuccess;

  const isCoursePrerequisite = useCallback(
    (target: string, neighbour: string) => {
      const prereqs = prerequisites[target] || [];
      return prereqs.includes(neighbour);
    },
    [prerequisites]
  );

  const addNeighbourStyles = useCallback(
    async (nodeItem: Item) => {
      const node = nodeItem as INode;
      const neighbours = node.getNeighbors();
      const opacity = theme === 'light' ? 0.3 : 0.4;
      const { Arrow } = await import('@antv/g6');

      // Every other node and edge becomes less visible
      graphRef.current?.getNodes().forEach((n) => {
        graphRef.current?.updateItem(n as Item, mapNodeOpacity(n.getID(), opacity));
        n.getEdges().forEach((e) => {
          graphRef.current?.updateItem(e, mapEdgeOpacity(Arrow, theme, e.getID(), opacity));
        });
        n.toBack();
      });
      // Highlight node's edges
      node.getOutEdges().forEach((e) => {
        graphRef.current?.updateItem(e, edgeOutHoverStyle(Arrow, theme, e.getID()));
        e.toFront();
      });
      node.getInEdges().forEach((e) => {
        graphRef.current?.updateItem(e, edgeInHoverStyle(Arrow, theme, e.getID()));
        e.toFront();
      });
      // Target node and neighbouring nodes remain visible
      node.toFront();
      graphRef.current?.updateItem(node as Item, mapNodeOpacity(node.getID(), 1));
      neighbours.forEach((n) => {
        graphRef.current?.updateItem(n as Item, mapNodeOpacity(n.getID(), 1));
        n.toFront();
        const courseId = n.getID();
        if (isCoursePrerequisite(node.getID(), courseId)) {
          graphRef.current?.updateItem(n as Item, mapNodePrereq(courseId, theme));
        }
      });
    },
    [isCoursePrerequisite, theme]
  );

  const removeNeighbourStyles = useCallback(
    async (nodeItem: Item) => {
      const node = nodeItem as INode;
      const edges = node.getEdges();
      const { Arrow } = await import('@antv/g6');
      const courses = unwrapQuery(coursesQuery.data);
      const coursesStates = unwrapQuery(coursesStateQuery.data?.courses_state);

      edges.forEach((e) => {
        graphRef.current?.updateItem(e, edgeUnhoverStyle(Arrow, theme, e.getID()));
      });
      graphRef.current?.getNodes().forEach((n) => {
        const courseId = n.getID();
        graphRef.current?.updateItem(
          n as Item,
          mapNodeStyle(courseId, courseId in courses, !!coursesStates[courseId]?.unlocked, theme)
        );
        graphRef.current?.updateItem(n as Item, mapNodeOpacity(courseId, 1));
        n.toFront();
      });
      graphRef.current?.getEdges().forEach((e) => {
        graphRef.current?.updateItem(e, mapEdgeOpacity(Arrow, theme, e.getID(), 1));
      });
    },
    [coursesQuery.data, coursesStateQuery.data?.courses_state, theme]
  );

  // On hover: add styles
  const addHoverStyles = useCallback(
    (ev: IG6GraphEvent) => {
      const node = ev.item as Item;
      graphRef.current?.setItemState(node, 'hover', true);
      graphRef.current?.updateItem(node, nodeLabelHoverStyle(node.getID()));
      addNeighbourStyles(node);
      graphRef.current?.paint();
    },
    [addNeighbourStyles]
  );

  // On hover: remove styles
  const addUnhoverStyles = useCallback(
    (ev: IG6GraphEvent) => {
      const courses = unwrapQuery(coursesQuery.data);
      const node = ev.item as Item;
      graphRef.current?.clearItemStates(node, 'hover');
      graphRef.current?.updateItem(
        node,
        nodeLabelUnhoverStyle(node.getID(), node.getID() in courses, theme)
      );
      removeNeighbourStyles(node);
      graphRef.current?.paint();
    },
    [coursesQuery.data, removeNeighbourStyles, theme]
  );

  // Without re-render, update styling for: each node, hovering state and edges
  const repaintCanvas = useCallback(async () => {
    const nodes = graphRef.current?.getNodes();
    const courses = unwrapQuery(coursesQuery.data);
    const coursesStates = coursesStateQuery.data?.courses_state ?? {};

    nodes?.map((n) =>
      graphRef.current?.updateItem(
        n,
        mapNodeStyle(n.getID(), n.getID() in courses, !!coursesStates[n.getID()]?.unlocked, theme)
      )
    );

    graphRef.current?.off('node:mouseenter');
    graphRef.current?.off('node:mouseleave');
    graphRef.current?.on('node:mouseenter', async (ev) => {
      addHoverStyles(ev);
    });
    graphRef.current?.on('node:mouseleave', async (ev) => {
      addUnhoverStyles(ev);
    });

    const { Arrow } = await import('@antv/g6');
    const edges = graphRef.current?.getEdges();
    edges?.map((e) => graphRef.current?.updateItem(e, defaultEdge(Arrow, theme)));
    graphRef.current?.paint();
  }, [
    addHoverStyles,
    addUnhoverStyles,
    coursesQuery.data,
    coursesStateQuery.data?.courses_state,
    theme
  ]);

  useEffect(() => {
    // Store a hashmap for performance reasons when highlighting nodes
    const makePrerequisitesMap = (edges: CourseEdge[] | undefined) => {
      const prereqs: CoursePrerequisite = prerequisites;
      edges?.forEach((e) => {
        if (!prereqs[e.target]) {
          prereqs[e.target] = [e.source];
        } else {
          prereqs[e.target].push(e.source);
        }
      });
      setPrerequisites(prereqs);
    };

    const initialiseGraph = async () => {
      const container = containerRef.current;
      if (!container) return;
      const courses = unwrapQuery(coursesQuery.data);
      const programs = unwrapQuery(programGraphQuery.data);
      const coursesStates = unwrapQuery(coursesStateQuery.data?.courses_state);

      makePrerequisitesMap(programs?.edges);
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
            initialisingEnd.current = true;
            setLoading(false);
          }
        },
        animate: true, // Boolean, whether to activate the animation when global changes happen
        animateCfg: {
          duration: 500, // Number, the duration of one animation
          easing: 'easeQuadInOut' // String, the easing function
        },
        groupByTypes: false,
        defaultNode: plannedNode,
        defaultEdge: defaultEdge(Arrow, theme),
        nodeStateStyles
      };
      graphRef.current = new Graph(graphArgs);
      const data = {
        nodes: programs.courses?.map((c) =>
          mapNodeStyle(c, c in courses, !!coursesStates[c]?.unlocked, theme)
        ),
        edges: programs.edges
      };

      // Hide graph until it's finished loaded, due to incomplete initial graph generation
      graphRef.current.data(data);
      graphRef.current.render();
      graphRef.current.getNodes().forEach((n) => n.hide());
      graphRef.current.getEdges().forEach((e) => e.hide());

      graphRef.current.on('node:click', async (ev) => {
        // Clicking a node loads up course description for the course and set active
        // tab to course info
        onNodeClick(ev.item as INode);
      });

      graphRef.current.on('node:mouseenter', async (ev) => {
        addHoverStyles(ev);
      });

      graphRef.current.on('node:mouseleave', async (ev) => {
        addUnhoverStyles(ev);
      });
    };

    const setupGraph = async () => {
      try {
        if (
          !degreeQuery.data ||
          !coursesQuery.data ||
          !plannerQuery.data ||
          !programGraphQuery.data ||
          !coursesStateQuery.data
        )
          return;
        initialisingStart.current = true;
        initialiseGraph();
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Error at setupGraph', e);
      }
    };

    if (!initialisingStart.current) setupGraph();
  }, [
    onNodeClick,
    degreeQuery,
    theme,
    prerequisites,
    setLoading,
    coursesQuery.data,
    plannerQuery.data,
    programGraphQuery.data,
    coursesStateQuery.data,
    addHoverStyles,
    addUnhoverStyles,
    repaintCanvas
  ]);

  useEffect(() => {
    // Change theme without re-render
    if (previousTheme.current !== theme) {
      previousTheme.current = theme;
      repaintCanvas();
    }
  }, [repaintCanvas, theme]);

  useEffect(() => {
    // update unlocked courses without re-render
    if (
      coursesStatePrevLastUpdated.current !== 0 &&
      coursesStatePrevLastUpdated.current !== coursesStateQuery.dataUpdatedAt
    ) {
      repaintCanvas();
    }
    coursesStatePrevLastUpdated.current = coursesStateQuery.dataUpdatedAt;
  }, [repaintCanvas, coursesStateQuery.dataUpdatedAt]);

  // Show all nodes and edges once graph is initially loaded
  useEffect(() => {
    if (initialisingEnd.current) {
      graphRef.current?.getNodes().forEach((n) => n.show());
      graphRef.current?.getEdges().forEach((e) => e.show());
      initialisingEnd.current = false;
    }
  }, [loading]);

  const showAllCourses = () => {
    if (!graphRef.current) return;
    graphRef.current.getNodes().forEach((n) => n.show());
    graphRef.current.getEdges().forEach((e) => e.show());
  };

  const showUnlockedCourses = useCallback(async () => {
    if (!graphRef.current) return;
    const coursesStates = coursesStateQuery.data?.courses_state ?? {};

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
  }, [coursesStateQuery.data]);

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
    if (!queriesSuccess) return;
    if (showingUnlockedCourses) showUnlockedCourses();
    else showAllCourses();
  }, [showUnlockedCourses, showingUnlockedCourses, queriesSuccess]);

  return (
    <S.Wrapper ref={containerRef}>
      {loading || !queriesSuccess ? (
        <S.SpinnerWrapper className="spinner-wrapper">
          <Spinner text="Loading graph..." />
        </S.SpinnerWrapper>
      ) : (
        <S.ToolsWrapper>
          Show All Courses
          <Switch
            checked={!showingUnlockedCourses}
            onChange={() => setShowingUnlockedCourses((prevState) => !prevState)}
          />
          <S.Button onClick={handleZoomIn} icon={<ZoomInOutlined />} />
          <S.Button onClick={handleZoomOut} icon={<ZoomOutOutlined />} />
          <S.Button
            onClick={handleToggleFullscreen}
            icon={fullscreen ? <ShrinkOutlined /> : <ExpandAltOutlined />}
          />
        </S.ToolsWrapper>
      )}
    </S.Wrapper>
  );
};

export default CourseGraph;
