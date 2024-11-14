import React, { useState } from 'react';
import { Button, message } from 'antd';
import { Grade } from 'types/planner';
import { useUpdateMarkMutation } from 'utils/apiHooks/user';
import S from './styles';

type Props = {
  code: string;
  open: boolean;
  onCancel: () => void;
};

const EditMarkModal = ({ code, open, onCancel }: Props) => {
  const [markValue, setMarkValue] = useState<string | number | undefined>();

  const letterGrades: Grade[] = ['SY', 'FL', 'PS', 'CR', 'DN', 'HD'];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    if (typeof value === 'number') setMarkValue(Number(value));
    setMarkValue(value);
  };

  const updateMarkMutation = useUpdateMarkMutation();

  const handleUpdateMark = () => {
    if (!Number.isNaN(parseInt(markValue as string, 10))) {
      if (Number(markValue) >= 0 && Number(markValue) <= 100) {
        updateMarkMutation.mutate({ course: code, mark: Number(markValue) });
      } else {
        // number is not in range
        message.error('Not a valid mark. Enter a mark between 0 and 100.');
      }
    } else if (letterGrades.includes(markValue as Grade)) {
      // mark is a letter grade
      updateMarkMutation.mutate({ course: code, mark: markValue as Grade });
    } else if (markValue === '' || markValue === undefined) {
      updateMarkMutation.mutate({ course: code, mark: null });
    } else {
      message.error('Could not update mark. Please enter a valid mark or letter grade');
    }
  };

  return (
    <S.Modal
      title={`Edit mark for ${code}`}
      open={open}
      onOk={handleUpdateMark}
      onCancel={onCancel}
      width="350px"
    >
      <S.EditMarkWrapper>
        <S.Input
          value={markValue}
          onChange={handleInputChange}
          onPressEnter={handleUpdateMark}
          placeholder="Enter Mark"
        />
        <S.LetterGradeWrapper>
          {letterGrades.map((letterGrade) => (
            <Button
              key={letterGrade}
              onClick={() => updateMarkMutation.mutate({ course: code, mark: letterGrade })}
            >
              {letterGrade}
            </Button>
          ))}
        </S.LetterGradeWrapper>
      </S.EditMarkWrapper>
    </S.Modal>
  );
};

export default EditMarkModal;
