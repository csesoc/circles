import React from 'react';
import { Typography } from 'antd';
import step1Dark from 'assets/GraphicalSelectorHelp/step1-dark.jpg';
import step1Light from 'assets/GraphicalSelectorHelp/step1-light.jpg';
import step2Dark from 'assets/GraphicalSelectorHelp/step2-dark.jpg';
import step2Light from 'assets/GraphicalSelectorHelp/step2-light.jpg';
import step3Dark from 'assets/GraphicalSelectorHelp/step3-dark.jpg';
import step3Light from 'assets/GraphicalSelectorHelp/step3-light.jpg';
import step4Dark from 'assets/GraphicalSelectorHelp/step4-dark.jpg';
import step4Light from 'assets/GraphicalSelectorHelp/step4-light.jpg';
import step5Dark from 'assets/GraphicalSelectorHelp/step5-dark.jpg';
import step5Light from 'assets/GraphicalSelectorHelp/step5-light.jpg';
import useSettings from 'hooks/useSettings';
import CS from '../common/styles';
import S from './styles';

const { Title } = Typography;

const HowToUse = () => {
  const { theme } = useSettings();

  const step = (num: number) => {
    const pics = {
      light: [step1Light, step2Light, step3Light, step4Light, step5Light],
      dark: [step1Dark, step2Dark, step3Dark, step4Dark, step5Dark]
    };
    return theme === 'light' ? pics.light[num - 1] : pics.dark[num - 1];
  };

  return (
    <S.Wrapper>
      <S.TitleWrapper>
        <Title level={2} className="text">
          How to use the Graphical Selector
        </Title>
      </S.TitleWrapper>

      <S.ContentsWrapper>
        <div>
          <CS.TextWrapper> 1. Navigate the graph to find available courses. </CS.TextWrapper>
        </div>
        <S.ImageStep src={step(1)} alt="How to find a course infographic." />
        <div>
          <CS.TextWrapper> 2. Courses can be planned, unlocked or locked. </CS.TextWrapper>
        </div>
        <S.ImageStep src={step(2)} alt="Icons for planned, unlocked or locked courses." />
        <div>
          <CS.TextWrapper> 3. Use the search bar to bring up the courses. </CS.TextWrapper>
        </div>
        <S.ImageStep src={step(3)} alt="How to use the search bar infographic." />
        <div>
          <CS.TextWrapper> 4. Hover over a course to see related courses. </CS.TextWrapper>
        </div>
        <S.ImageStep src={step(4)} alt="How to quickly view related courses." />
        <div>
          <CS.TextWrapper> 5. Click the course to view the course information! </CS.TextWrapper>
        </div>
        <S.ImageStep src={step(5)} alt="Where to click to view course information infographic." />
      </S.ContentsWrapper>
    </S.Wrapper>
  );
};

export default HowToUse;
