import styled, { css } from 'styled-components';
import { Droppable, GridItem } from '../common/styles';

const UnplannedContainer = styled.div<{ $summerEnabled: boolean }>`
  grid-row-start: 1;
  grid-row-end: span 10;
  grid-column-start: ${({ $summerEnabled }) => ($summerEnabled ? 6 : 5)};
  display: flex;
  flex-direction: column;
  place-self: stretch;
  min-width: 18em;
  align-items: center;
`;

const UnplannedTitle = styled(GridItem)`
  position: absolute;
  font-weight: 500;
  // sum of heights from the top of the page for where the unplanned header should be
  top: calc(
    var(--navbar-height) + var(--option-header-height) + var(--tp-main-container-padding) +
      var(--tp-planner-container-margin)
  );
`;

type UnplannedBoxProps = {
  $droppable: boolean;
  $summerEnabled: boolean;
  $isSmall: boolean;
};

const UnplannedBox = styled.ul<UnplannedBoxProps>`
  position: absolute;
  overflow-y: auto;
  overflow-x: hidden;
  // sum of heights from the top of the page for where the unplanned box should be
  top: calc(
    var(--navbar-height) + var(--option-header-height) + var(--tp-main-container-padding) +
      var(--tp-planner-container-margin) + var(--tp-term-box-margin) + var(--tp-grid-item-font-size)
  );
  // height of box should be the remaining viewport excluding the top and a bottom gap matching the other term boxes
  height: calc(
    100vh -
      (
        var(--navbar-height) + var(--option-header-height) + var(--tp-main-container-padding) + 3 *
          var(--tp-planner-container-margin) + 2 * var(--tp-term-box-margin) +
          var(--tp-grid-item-font-size)
      )
  );
  min-width: 20em;
  max-width: 20em;
  margin: 1em;
  border: 1.5px solid #9254de;
  border-radius: 15px;
  padding: 15px;
  transition: 200ms ease-out;
  &::-webkit-scrollbar-button {
    display: block;
    background-color: transparent;
  }
  &::-webkit-scrollbar-track-piece {
    background-color: #fff;
  }

  ${({ $droppable }) => $droppable && Droppable}

  ${({ $summerEnabled }) =>
    $summerEnabled &&
    css`
      // sum of heights from the top of the page for where the unplanned header should be
      // for summer term
      height: calc(
        100vh -
          (
            var(--navbar-height) + var(--option-header-height) + var(--tp-main-container-padding) +
              3 * var(--tp-planner-container-margin) + 2 * var(--tp-summer-term-box-margin) +
              var(--tp-grid-item-font-size)
          )
      );
      min-width: 17em;
      max-width: 17em;
      margin: 0.5em;
      padding-top: 0.5em;
    `}

  ${({ $isSmall }) =>
    $isSmall &&
    css`
      border-radius: 1em;
      min-width: 12em;
    `}

  ${({ $isSmall, $summerEnabled }) =>
    $isSmall &&
    $summerEnabled &&
    css`
      border-radius: 1em;
      min-width: 13em;
    `}
`;

export default { UnplannedContainer, UnplannedBox, UnplannedTitle };
