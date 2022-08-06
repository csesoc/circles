import type { Dispatch, SetStateAction } from 'react';
import React from 'react';
import CourseBadge from '../CourseBadge';
import { GridSubgroupCourse } from '../GridView/types';
import S from './styles';

type Props = {
  title: string
  courses: GridSubgroupCourse[]
  modalVisible: boolean
  setModalVisible: Dispatch<SetStateAction<boolean>>
};

const CourseListModal = ({
  title, courses, modalVisible, setModalVisible,
}: Props) => (
  <S.CourseModal
    title={(
      <S.ModalHeader>
        <S.ModalTitle level={2}>Course List</S.ModalTitle>
        <S.ModalTitle level={3}>{title}</S.ModalTitle>
        <S.Instruction>See your possible courses:</S.Instruction>
      </S.ModalHeader>
        )}
    width="625px"
    visible={modalVisible}
    onCancel={() => setModalVisible(false)}
    footer={null}
  >
    <S.CourseList>
      {courses.map((course) => (<CourseBadge course={course} key={course.key} />))}
    </S.CourseList>
  </S.CourseModal>
);

export default CourseListModal;
