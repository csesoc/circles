import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import useUserCourses from 'utils/apiHooks/useUserCourses';
import useUserDegree from 'utils/apiHooks/useUserDegree';
import openNotification from 'utils/openNotification';
import infographic from 'assets/infographicFontIndependent.svg';
import CourseDescriptionPanel from 'components/CourseDescriptionPanel';
import PageTemplate from 'components/PageTemplate';
import type { RootState } from 'config/store';
import { addTab } from 'reducers/courseTabsSlice';
import CourseBanner from './CourseBanner';
import CourseMenu from './CourseMenu';
import CourseTabs from './CourseTabs';
import S from './styles';

const CourseSelector = () => {
  const coursesQuery = useUserCourses();

  const degreeQuery = useUserDegree();

  const [showedNotif, setShowedNotif] = useState(false);
  useEffect(() => {
    if (coursesQuery.isSuccess && !showedNotif && !Object.keys(coursesQuery.data).length) {
      openNotification({
        type: 'info',
        message: 'How do I see more sidebar courses?',
        description:
          'Courses are shown as you meet the requirements to take them. Any course can also be selected via the search bar.'
      });
      setShowedNotif(true);
    }
  }, [showedNotif, coursesQuery.isSuccess, coursesQuery.data]);

  const { active, tabs } = useSelector((state: RootState) => state.courseTabs);

  const dispatch = useDispatch();

  const courseCode = tabs[active];

  const divRef = useRef<null | HTMLDivElement>(null);
  const [menuOffset, setMenuOffset] = useState<number | undefined>(undefined);
  useEffect(() => {
    const minMenuWidth = 100;
    const maxMenuWidth = (60 * window.innerWidth) / 100;
    const resizerDiv = divRef.current as HTMLDivElement;
    const setNewWidth = (clientX: number) => {
      if (clientX > minMenuWidth && clientX < maxMenuWidth) {
        resizerDiv.style.left = `${clientX}px`;
        setMenuOffset(clientX);
      }
    };
    const handleResize = (ev: globalThis.MouseEvent) => {
      setNewWidth(ev.clientX);
    };
    const endResize = (ev: MouseEvent) => {
      setNewWidth(ev.clientX);
      window.removeEventListener('mousemove', handleResize);
      window.removeEventListener('mouseup', endResize); // remove myself
    };
    const startResize = (ev: MouseEvent) => {
      ev.preventDefault(); // stops highlighting text
      window.addEventListener('mousemove', handleResize);
      window.addEventListener('mouseup', endResize);
    };
    resizerDiv?.addEventListener('mousedown', startResize);
    return () => resizerDiv?.removeEventListener('mousedown', startResize);
  }, []);

  const onCourseClick = useCallback((code: string) => dispatch(addTab(code)), [dispatch]);

  return (
    <PageTemplate>
      <S.ContainerWrapper>
        <CourseBanner courses={coursesQuery.data} />
        <CourseTabs />
        <S.ContentWrapper $offset={menuOffset}>
          <CourseMenu courses={coursesQuery.data} degree={degreeQuery.data} />
          <S.ContentResizer ref={divRef} $offset={menuOffset} />
          {courseCode ? (
            <div style={{ overflow: 'auto' }}>
              <CourseDescriptionPanel
                courseCode={courseCode}
                courses={coursesQuery.data}
                onCourseClick={onCourseClick}
              />
            </div>
          ) : (
            <S.InfographicContainer>
              <img src={infographic} alt="How to use Circles infographic" />
            </S.InfographicContainer>
          )}
        </S.ContentWrapper>
      </S.ContainerWrapper>
    </PageTemplate>
  );
};

export default CourseSelector;
