import React, { useState } from 'react';
import additionalOptionsGifDark from 'assets/TermPlannerHelp/additional-options-dark.gif';
import additionalOptionsPicDark from 'assets/TermPlannerHelp/additional-options-dark.jpg';
import additionalOptionsGifLight from 'assets/TermPlannerHelp/additional-options-light.gif';
import additionalOptionsPicLight from 'assets/TermPlannerHelp/additional-options-light.jpg';
import dragAndDropGifDark from 'assets/TermPlannerHelp/drag-and-drop-dark.gif';
import dragAndDropPicDark from 'assets/TermPlannerHelp/drag-and-drop-dark.jpg';
import dragAndDropGifLight from 'assets/TermPlannerHelp/drag-and-drop-light.gif';
import dragAndDropPicLight from 'assets/TermPlannerHelp/drag-and-drop-light.jpg';
import hideYearGifDark from 'assets/TermPlannerHelp/hide-year-dark.gif';
import hideYearPicDark from 'assets/TermPlannerHelp/hide-year-dark.jpg';
import hideYearGifLight from 'assets/TermPlannerHelp/hide-year-light.gif';
import hideYearPicLight from 'assets/TermPlannerHelp/hide-year-light.jpg';
import unscheduleGifDark from 'assets/TermPlannerHelp/unschedule-dark.gif';
import unschedulePicDark from 'assets/TermPlannerHelp/unschedule-dark.jpg';
import unscheduleGifLight from 'assets/TermPlannerHelp/unschedule-light.gif';
import unschedulePicLight from 'assets/TermPlannerHelp/unschedule-light.jpg';
import useSettings from 'hooks/useSettings';
import CS from '../common/styles';
import S from './styles';

type HelpStepProps = {
  title: string;
  gif: string;
  pic: string;
  altText: string;
};

const HelpStep = ({ title, gif, pic, altText }: HelpStepProps) => {
  const [playing, setPlaying] = useState(false);

  return (
    <div>
      <CS.PopupEntry>
        <CS.MenuText>{title}</CS.MenuText>
      </CS.PopupEntry>
      <S.HelpGif
        onMouseEnter={() => setPlaying(true)}
        onMouseLeave={() => setPlaying(false)}
        src={playing ? gif : pic}
        alt={altText}
      />
    </div>
  );
};

const HelpMenu = () => {
  const { theme } = useSettings();
  const helpSteps = [
    {
      title: '1. Drag and Drop Courses',
      pic: theme === 'light' ? dragAndDropPicLight : dragAndDropPicDark,
      gif: theme === 'light' ? dragAndDropGifLight : dragAndDropGifDark,
      altText: 'drag and drop walkthrough'
    },
    {
      title: '2. Right Click Courses for More Actions',
      pic: theme === 'light' ? unschedulePicLight : unschedulePicDark,
      gif: theme === 'light' ? unscheduleGifLight : unscheduleGifDark,
      altText: 'context menu walkthrough'
    },
    {
      title: '3. Hide Year',
      pic: theme === 'light' ? hideYearPicLight : hideYearPicDark,
      gif: theme === 'light' ? hideYearGifLight : hideYearGifDark,
      altText: 'hide year walkthrough'
    },
    {
      title: '4. Additional Features',
      pic: theme === 'light' ? additionalOptionsPicLight : additionalOptionsPicDark,
      gif: theme === 'light' ? additionalOptionsGifLight : additionalOptionsGifDark,
      altText: 'additional options walkthrough'
    }
  ];

  return (
    <S.HelpMenuWrapper>
      <S.HeaderWrapper>
        <CS.MenuHeader>Term Planner Tips (Hover to Play)</CS.MenuHeader>
        <CS.MenuDivider />
      </S.HeaderWrapper>
      {helpSteps.map(({ title, pic, gif, altText }) => (
        <HelpStep key={title} title={title} gif={gif} pic={pic} altText={altText} />
      ))}
    </S.HelpMenuWrapper>
  );
};

export default HelpMenu;
