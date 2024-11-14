import React from 'react';
import { useLocation } from 'react-router-dom';
import { Progress, Rate, Typography } from 'antd';
import { useTheme } from 'styled-components';
import { Course } from 'types/api';
import { EnrolmentCapacityData } from 'types/courseCapacity';
import { useCourseRatingQuery } from 'utils/apiHooks/static';
import getMostRecentPastTerm from 'utils/getMostRecentPastTerm';
import ProgressBar from 'components/ProgressBar';
import TermTag from 'components/TermTag';
import { CURR_YEAR, TERM } from 'config/constants';
import S from './styles';

const { Title, Text } = Typography;

const termMapping: Record<number, string> = {
  0: 'Summer',
  1: 'Term%201',
  2: 'Term%202',
  3: 'Term%203'
};

type CourseAttributesProps = {
  course: Course;
  courseCapacity?: EnrolmentCapacityData;
};

const CourseAttributes = ({ course, courseCapacity }: CourseAttributesProps) => {
  const { pathname } = useLocation();
  const sidebar = pathname === '/course-selector';
  const theme = useTheme();

  const ratingQuery = useCourseRatingQuery({}, course.code);
  const rating = ratingQuery.data;

  const { study_level: studyLevel, terms, campus, code, school, UOC } = course;

  const currentTerm = getMostRecentPastTerm(CURR_YEAR).T;

  const recentTermNumber = terms?.length ? parseInt(terms[0].slice(1), 10) : currentTerm;

  const yearCourseAvaliable = recentTermNumber > currentTerm ? CURR_YEAR - 1 : CURR_YEAR;

  const updatedTerm = recentTermNumber > currentTerm ? recentTermNumber : currentTerm;

  const teachingPeriod = updatedTerm > 0 ? `T${updatedTerm}` : 'U0';

  const termMod = termMapping[updatedTerm];

  const termTags = terms?.length
    ? terms.map((term) => {
        const termNo = term.slice(1);
        return <TermTag key={term} name={term === 'T0' ? 'Summer' : `Term ${termNo}`} />;
      })
    : 'None';

  if (!sidebar) {
    return (
      <div>
        <S.TermWrapper>{termTags !== 'None' && termTags}</S.TermWrapper>
        <S.AttributesWrapperConcise>
          <S.AttributeConcise>
            <div>
              <Text>{studyLevel}</Text>
            </div>
            <div>
              <Text>{campus}</Text>
            </div>
          </S.AttributeConcise>
          <S.AttributeConcise>
            <Text>{school}</Text>
          </S.AttributeConcise>
          <S.AttributeConcise>
            <div>
              <Text strong>{UOC} UOC</Text>
            </div>
            <div>
              <Text>View Handbook</Text>
            </div>
          </S.AttributeConcise>
        </S.AttributesWrapperConcise>
      </div>
    );
  }

  // course selector attribute view
  const courseAttributesData = course
    ? [
        {
          title: 'Offering Terms',
          content: termTags
        },
        {
          title: 'UNSW Handbook',
          content: studyLevel ? (
            <S.Link
              href={`https://www.handbook.unsw.edu.au/${studyLevel.toLowerCase()}/courses/${CURR_YEAR}/${code}/`}
              target="_blank"
              rel="noreferrer"
            >
              View {code} in handbook
            </S.Link>
          ) : null
        },
        {
          title: 'UNSW Course Outline',
          content: studyLevel ? (
            <S.Link
              href={`https://www.unsw.edu.au/course-outlines/course-outline#year=${yearCourseAvaliable}&term=${termMod}&deliveryMode=Multimodal&deliveryFormat=Standard&teachingPeriod=${teachingPeriod}&deliveryLocation=Kensington&courseCode=${code}&activityGroupId=1`}
              target="_blank"
              rel="noreferrer"
            >
              View {code} in Course Outline
            </S.Link>
          ) : null
        },
        {
          title: 'School',
          content: school
        },
        {
          title: 'Study Level',
          content: studyLevel
        },
        {
          title: 'Campus',
          content: campus
        },
        {
          title: 'Course Capacity',
          content:
            courseCapacity && Object.keys(courseCapacity).length ? (
              <>
                <div>
                  {courseCapacity.capacity} Students for {TERM}
                </div>
                <ProgressBar
                  progress={
                    Math.round((courseCapacity.enrolments / courseCapacity.capacity) * 1000) / 10
                  }
                />
              </>
            ) : (
              <p>No data available</p>
            )
        },
        {
          title: 'Units of Credit',
          content: UOC
        },
        {
          title: 'Unilectives Rating',
          content: rating ? (
            <>
              <S.RatingWrapper>
                <S.DialWrapper>
                  <Progress
                    type="dashboard"
                    percent={rating.enjoyability ? (rating.enjoyability / 5) * 100 : 0}
                    format={() =>
                      `${rating.enjoyability ? rating.enjoyability.toFixed(1) : '?'} / 5`
                    }
                    strokeColor={theme.purplePrimary}
                    size={65}
                  />
                  <S.DialLabel>Enjoyability</S.DialLabel>
                </S.DialWrapper>
                <S.DialWrapper>
                  <Progress
                    type="dashboard"
                    percent={rating.usefulness ? (rating.usefulness / 5) * 100 : 0}
                    format={() => `${rating.usefulness ? rating.usefulness.toFixed(1) : '?'} / 5`}
                    strokeColor={theme.purplePrimary}
                    size={65}
                  />
                  <S.DialLabel>Usefulness</S.DialLabel>
                </S.DialWrapper>
                <S.DialWrapper>
                  <Progress
                    type="dashboard"
                    percent={rating.manageability ? (rating.manageability / 5) * 100 : 0}
                    format={() =>
                      `${rating.manageability ? rating.manageability.toFixed(1) : '?'} / 5`
                    }
                    strokeColor={theme.purplePrimary}
                    size={65}
                  />
                  <S.DialLabel>Manageability</S.DialLabel>
                </S.DialWrapper>
              </S.RatingWrapper>
              <div style={{ textAlign: 'center' }}>
                <Rate disabled value={rating.overallRating ? rating.overallRating : 0} allowHalf />
                <p>Overall</p>
              </div>
              <S.Link
                href={`https://unilectives.devsoc.app/course/${code}/`}
                target="_blank"
                rel="noreferrer"
              >
                View full reviews on Unilectives
              </S.Link>
            </>
          ) : (
            <p>N/A</p>
          )
        }
      ]
    : [];

  return (
    <>
      {courseAttributesData.map(
        ({ title, content }) =>
          content && (
            <S.AttributeWrapper key={`course-attribute-${title}`}>
              <Title level={3} className="text">
                {title}
              </Title>
              <S.AttributeText>{content}</S.AttributeText>
            </S.AttributeWrapper>
          )
      )}
    </>
  );
};

export default CourseAttributes;
