import { createGlobalStyle, DefaultTheme } from 'styled-components';

export const GlobalStyles = createGlobalStyle`
  html {
    font-size: 16px;
  }

  html,
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    background: ${({ theme }) => theme.body};
    color: ${({ theme }) => theme.text};

    --navbar-height: 70px;
    --option-header-height: 65px;

    --cs-top-cont-height: 23%;
    --cs-tabs-cont-height: 40px;
    --cs-bottom-cont-height: calc(100% - var(--cs-top-cont-height) - var(--cs-tabs-cont-height));

    --tp-main-container-padding: 10px;
    --tp-grid-item-font-size: 1.5rem;
    --tp-planner-container-margin: 15px;
    --tp-term-box-margin: 1em;
    --tp-summer-term-box-margin: 0.5em;
  }

  .text {
    color: ${({ theme }) => theme.text} !important;
  }

  p {
    font-size: 0.9rem;
  }

  .ant-menu:not(.ant-menu-horizontal) .ant-menu-item-selected {
    background-color: ${({ theme }) => theme.courseMenu?.backgroundColor} !important;
  }
  // Fixes white padding in dark mode in CourseMenu
  .ant-menu-root {
    border-right-color: ${({ theme }) => theme.courseMenu?.borderColor} !important; 
  }

  .ant-notification-notice,
  .ant-notification-notice-message,
  .ant-notification-notice-close-x,
  .ant-modal-content,
  .ant-modal-header,
  .ant-modal-close-x,
  .ant-modal-title {
    background-color: ${({ theme }) => theme.body};
    color: ${({ theme }) => theme.text} !important;
  }

  // Antd Select customisation - Course Searchbar
  .ant-select-dropdown.ant-select-dropdown-placement-bottomLeft {
    background-color: ${({ theme }) => theme.searchBar.backgroundColor} !important;
    box-shadow: ${({ theme }) => theme.searchBar.boxShadow} !important; 
  }
  .ant-spin-dot-item {
    background-color: ${({ theme }) => theme.searchBar.spinBackgroundColor} !important;
  }
  .course-search-bar .ant-select-selector {
    background-color: ${({ theme }) => theme.searchBar.backgroundColor} !important;
    border-color: ${({ theme }) => theme.searchBar.borderColor} !important;
    color: ${({ theme }) => theme.text};
  }
  .rc-virtual-list .ant-select-item-option {
    background-color: ${({ theme }) => theme.searchBar.backgroundColor} !important;
    color: ${({ theme }) => theme.text} !important;
  }
  .rc-virtual-list .ant-select-item-option:hover {
    background-color: ${({ theme }) => theme.searchBar.hoverBackgroundColor} !important;
  }

  // Antd Select customisation - TermPlanner SettingsMenu
  .settings-degree-length-popup .ant-select-selector {
    background-color: ${({ theme }) => theme.settingsMenuSelect.selectBackgroundColor} !important;
    border-color: ${({ theme }) => theme.settingsMenuSelect.selectBorderColor} !important;
    color: ${({ theme }) => theme.text};
  }
  .settings-degree-length-popup .ant-select-arrow {
    color: ${({ theme }) => theme.settingsMenuSelect.selectArrowColor};
  }
  .settings-degree-length-popup.ant-select-item-option {
    background-color: ${({ theme }) => theme.settingsMenuSelect.optionBackgroundColor} !important;
    color: ${({ theme }) => theme.settingsMenuSelect.optionTextColor} !important;
  }
  .settings-degree-length-popup.ant-select-item-option-selected {
    background-color: ${({ theme }) =>
      theme.settingsMenuSelect.optionHoverBackgroundColor} !important;
    color: ${({ theme }) => theme.settingsMenuSelect.optionTextColor} !important;
  }
  .settings-degree-length-popup.ant-select-item-option:hover {
    background-color: ${({ theme }) =>
      theme.settingsMenuSelect.optionHoverBackgroundColor} !important;
  }

  // Antd DatePicker customisation
  .ant-picker {
    background-color: ${({ theme }) => theme.datePicker.inputBackgroundColor};
    border-color: ${({ theme }) => theme.datePicker.inputBorderColor};
  }
  .ant-picker-input input {
    color: ${({ theme }) => theme.text};
  }
  .anticon-calendar svg {
    fill: ${({ theme }) => theme.datePicker.calendarSvgFill};
  }
  .ant-picker-clear svg {
    fill: ${({ theme }) => theme.datePicker.clearSvgFill};
  }
  .ant-picker-clear {
    background-color: ${({ theme }) => theme.datePicker.clearBackgroundColor};
  }
  .ant-picker-header, .ant-picker-body {
    background-color: ${({ theme }) => theme.datePicker.bodyBackgroundColor};
  }
  .ant-picker-header, .ant-picker-panel {
    border-color: ${({ theme }) => theme.datePicker.inputBorderColor};
  }
  .ant-picker-header-super-prev-btn, .ant-picker-header-super-next-btn {
    color: ${({ theme }) => theme.datePicker.arrowColor} !important;
  }
  .ant-picker-decade-btn {
    color: ${({ theme }) => theme.text} !important;
  }
  .ant-picker-cell-end, .ant-picker-cell-start {
    color: ${({ theme }) => theme.datePicker.cellNotInViewColor};
  }
  .ant-picker-cell-in-view {
    color: ${({ theme }) => theme.text} !important;
  }
  .ant-picker-cell:hover {
    .ant-picker-cell-inner {
      background-color: ${({ theme }) => theme.datePicker.yearHoverBackgroundColor} !important;
    }
  }
  .ant-picker-cell-selected.ant-picker-cell:hover {
    .ant-picker-cell-inner {
      background-color: #9154DE !important;
    }
  }

  // Antd popconfirm customisation
  .popconfirm-unplan .ant-popover-inner,
  .popconfirm-unplan .ant-popover-arrow-content:before {
    background-color: ${({ theme }) => theme.popconfirm.backgroundColor};
  }
  .popconfirm-unplan .ant-popover-message-title {
    color: ${({ theme }) => theme.text};
  }
  .popconfirm-unplan .ant-popover-buttons .ant-btn-default{
    background-color: ${({ theme }) => theme.optionsHeader.buttonBackgroundColor};
    color: ${({ theme }) => theme.text};
    border-color: ${({ theme }) => theme.optionsHeader.borderAlternativeColor};
    &:hover {
      background-color: ${({ theme }) => theme.optionsHeader.buttonHoverAlternativeColor};
    }  
  }

  // Antd Tabs customisation
  .graph-sidebar .ant-tabs-tab,
  .graph-sidebar-fullscreen .ant-tabs-tab {
    color: ${({ theme }) => theme.graph.tabColor};
  }
  .graph-sidebar .ant-tabs-nav::before, 
  .graph-sidebar-fullscreen .ant-tabs-nav::before {
    border-color: ${({ theme }) => theme.graph.tabBottomBorderColor};
  }
  .graph-sidebar .ant-typography.text,
  .graph-sidebar .ant-typography,
  .graph-sidebar-fullscreen .ant-typography.text,
  .graph-sidebar-fullscreen .ant-typography {
    color: ${({ theme }) => theme.graph.tabTextColor};
  }
  .graph-sidebar .ant-tabs-nav-wrap-ping-left::before,
  .graph-sidebar .ant-tabs-nav-wrap-ping-left::after,
  .graph-sidebar .ant-tabs-nav-wrap-ping-right::before,
  .graph-sidebar .ant-tabs-nav-wrap-ping-right::after,
  .graph-sidebar-fullscreen .ant-tabs-nav-wrap-ping-left::before,
  .graph-sidebar-fullscreen .ant-tabs-nav-wrap-ping-left::after,
  .graph-sidebar-fullscreen .ant-tabs-nav-wrap-ping-right::before,
  .graph-sidebar-fullscreen .ant-tabs-nav-wrap-ping-right::after {
    box-shadow: ${({ theme }) => theme.graph?.tabBoxShadow} !important;
  }

  // .spinner-wrapper .anticon anticon-loading anticon-spin ant-spin-dot {
  .spinner-wrapper .ant-spin-dot {
    color: ${({ theme }) => theme.graph.loadingIcon};
  }

  .loading-spinner p {
    color: ${({ theme }) => theme.text};
    text-shadow:
      0.07em 0 ${({ theme }) => theme.graph.loadingText},
      0 0.07em ${({ theme }) => theme.graph.loadingText},
      -0.07em 0 ${({ theme }) => theme.graph.loadingText},
      0 -0.07em ${({ theme }) => theme.graph.loadingText};
  }

  // Scrollbar settings
  /* width */
  ::-webkit-scrollbar {
    width: 12px;                 /* width of the entire scrollbar */
  }

  ::-webkit-scrollbar-track {    /* color of the tracking area */
    background: ${({ theme }) => theme.scrollbar.trackingAreaColor};        
  }

  ::-webkit-scrollbar-thumb {
    /* color of the scroll thumb */
    background-color:  ${({ theme }) => theme.scrollbar.scrollbarColor};
    /* roundness of the scroll thumb */
    border-radius: 20px;
    /* creates padding around scroll thumb */
    border: 3px solid ${({ theme }) => theme.scrollbar.scollbarBorderColor}; 
  }
`;

const lightBaseColors = {
  purplePrimary: '#9254de', // purple-5
  purpleLight: '#efdbff', // purple-2
  purpleDark: '#531dab' // purple-7
};

const darkBaseColors = {
  purplePrimary: '#9254de', // purple-5 from light theme
  purpleLight: '#51258f', // purple-2
  purpleDark: '#854eca' // purple-7
};

export const lightTheme: DefaultTheme = {
  ...lightBaseColors,
  body: '#ffffff',
  text: '#323739',
  scrollbar: {
    trackingAreaColor: '#fAfAfA',
    scrollbarColor: '#c2c2c2',
    scollbarBorderColor: '#fAfAfA'
  },
  droppable: {
    backgroundColor: '#e8fef2'
  },
  plannerCartCard: {
    backgroundColorHover: '#f4f4f4'
  },
  plannerCartMenu: {
    backgroundColor: '#ffffff'
  },
  draggableTab: {
    backgroundColor: '#fafafa',
    borderColor: '#f0f0f0'
  },

  degreeCard: {
    backgroundColor: '#f0f0f0'
  },
  draggableCourse: {
    backgroundColor: '#d9d9d9',
    warningBackgroundColor: '#ffe8c3',
    dragDisabledBackgroundColor: '#eee',
    iconColor: '#fff'
  },
  termCheckbox: {
    color: '#fff'
  },
  warningOutlined: {
    color: '#DC9930'
  },
  termBoxWrapper: {
    borderColor: '#d9d9d9'
  },
  optionsHeader: {
    borderColor: '#d9d9d9',
    borderAlternativeColor: '#cecece',
    buttonBorderColor: '#cecece',
    buttonBackgroundColor: '#fff',
    buttonHoverColor: '#e3e3e3',
    buttonHoverAlternativeColor: '#fff'
  },
  editMark: {
    backgroundColor: '#fff',
    color: '#323739',
    borderColor: '#d9d9d9',
    borderColorHeader: '#ededed',
    backgroundColorHover: '#fff'
  },
  settingsMenuSelect: {
    selectBackgroundColor: '#fff',
    selectBorderColor: '#d9d9d9',
    selectArrowColor: '#d9d9d9',
    optionBackgroundColor: '#fff',
    optionTextColor: '#000',
    optionHoverBackgroundColor: '#f5f5f5'
  },
  datePicker: {
    inputBackgroundColor: '#fff',
    inputBorderColor: '#d9d9d9',
    calendarSvgFill: '#d9d9d9',
    clearSvgFill: '#d9d9d9',
    clearBackgroundColor: '#fff',
    bodyBackgroundColor: '#fff',
    arrowColor: '#d9d9d9',
    yearHoverBackgroundColor: '#f5f5f5',
    cellNotInViewColor: '#b8b8b8'
  },
  popconfirm: {
    backgroundColor: '#fff'
  },
  infoOutlined: {
    color: '#000'
  },
  uocBadge: {
    backgroundColor: '#9254de'
  },
  courseButton: {
    backgroundColor: '#fff',
    hoverBackgroundColor: '#F9F9F9'
  },
  courseMenu: {
    backgroundColor: '#f8f0ff',
    borderColor: '#f0f0f0',
    hrefColor: '#9254de',
    hrefHoverColor: '#c9aaef'
  },
  searchBar: {
    spinBackgroundColor: '#9254de',
    backgroundColor: '#fff',
    boxShadow: '0 3px 6px -4px #0000001f, 0 6px 16px #00000014, 0 9px 28px 8px #0000000d',
    borderColor: '#d9d9d9',
    hoverBackgroundColor: '#f5f5f5'
  },
  courseDescription: {
    paddingColor: '#d9d9d9'
  },
  collapseBtnIcon: {
    color: '#000'
  },
  quickAddRemoveBtn: {
    addBackgroundColor: '#fafafa',
    removeBackgroundColor: '#fafafa',
    addBorderColor: '#d9d9d9'
  },
  graph: {
    backgroundColor: '#fff',
    borderColor: '#c2c2c2',
    tabColor: '#666',
    tabBottomBorderColor: '#f0f0f0',
    tabTextColor: '#000',
    loadingText: '#fff'
  },
  sidebarDrawer: {
    backgroundColor: '#fff',
    borderColor: '#cecece',
    hoverBackgroundColor: '#fff'
  },
  genericButton: {
    backgroundColor: '#fff',
    borderColor: '#cecece',
    hoverBackgroundColor: '#fff'
  },
  bugIcon: {
    backgroundColor: '#fff',
    borderColor: '#d9d9d9',
    hoverBackgroundColor: '#fff'
  },
  loginSplash: {
    svgColor: '#9453e6',
    backgroundColor: '#f8f8f9'
  }
};

export const darkTheme: DefaultTheme = {
  ...darkBaseColors,
  body: '#1d1f20',
  text: '#f1f1f1',
  scrollbar: {
    trackingAreaColor: '#1d1f20',
    scrollbarColor: '#666c7a',
    scollbarBorderColor: '#1d1f20'
  },
  droppable: {
    backgroundColor: '#373A36'
  },
  plannerCartCard: {
    backgroundColorHover: '#292a2b'
  },
  plannerCartMenu: {
    backgroundColor: '#1D1F20'
  },
  courseTag: {
    backgroundColor: '#444'
  },

  draggableTab: {
    backgroundColor: '#1d1f20',
    borderColor: '#1d1f20'
  },

  courseSidebar: {
    menuSubColor: '#262626' // gray-10
  },

  degreeCard: {
    backgroundColor: '#131415'
  },
  draggableCourse: {
    backgroundColor: '#121212',
    warningBackgroundColor: '#ab6a03',
    dragDisabledBackgroundColor: '#2b2b2b',
    iconColor: '#fff'
  },
  termCheckbox: {
    color: '#000'
  },
  warningOutlined: {
    color: '#fff'
  },
  termBoxWrapper: {
    borderColor: '#4d4b4a'
  },
  optionsHeader: {
    borderColor: '#4d4b4a',
    borderAlternativeColor: '#7b7481',
    buttonBorderColor: '#5f5a64',
    buttonBackgroundColor: '#444249',
    buttonHoverColor: '#6d6772',
    buttonHoverAlternativeColor: '#343239'
  },
  editMark: {
    backgroundColor: '#2c2b2f',
    color: '#f1f1f1',
    borderColor: '#444249',
    borderColorHeader: '#444249',
    backgroundColorHover: '#1c1b1f'
  },
  settingsMenuSelect: {
    selectBackgroundColor: '#444249',
    selectBorderColor: '#5f5a64',
    selectArrowColor: '#cecece',
    optionBackgroundColor: '#444249',
    optionTextColor: '#fff',
    optionHoverBackgroundColor: '#6d6772'
  },
  datePicker: {
    inputBackgroundColor: '#444249',
    inputBorderColor: '#5f5a64',
    calendarSvgFill: '#cecece',
    clearSvgFill: '#cecece',
    clearBackgroundColor: '#444249',
    bodyBackgroundColor: '#444249',
    arrowColor: '#d9d9d9',
    yearHoverBackgroundColor: '#6d6772',
    cellNotInViewColor: '#8a8a8a'
  },
  popconfirm: {
    backgroundColor: '#444249'
  },
  infoOutlined: {
    color: '#fff'
  },
  uocBadge: {
    backgroundColor: '#51258f'
  },
  courseButton: {
    backgroundColor: '#17191A',
    hoverBackgroundColor: '#1e2021'
  },
  courseMenu: {
    backgroundColor: darkBaseColors.purpleLight,
    borderColor: '#333',
    hrefColor: '#b384ea',
    hrefHoverColor: '#c9aaef'
  },
  searchBar: {
    spinBackgroundColor: '#b384ea',
    backgroundColor: '#262626',
    boxShadow: '0 3px 20px -10px #ffffe0, 0 5px 0px -10px #ffffeb, 0 10px 20px -25px #fffff2',
    borderColor: '#5f5a64',
    hoverBackgroundColor: '#6d6772'
  },
  courseDescription: {
    paddingColor: '#444249'
  },
  collapseBtnIcon: {
    color: '#f1f1f1'
  },
  quickAddRemoveBtn: {
    addBackgroundColor: '#262626',
    removeBackgroundColor: '#262626',
    addBorderColor: '#707070'
  },
  graph: {
    backgroundColor: '#1d1f20',
    borderColor: '#5d5d5d',
    tabColor: '#fff',
    tabBottomBorderColor: '#5d5d5d',
    tabTextColor: '#f1f1f1',
    tabBoxShadow: 'inset 16px 0 8px -8px rgba(255, 255, 255, 0.08)',
    loadingIcon: '#d7b7fd',
    loadingText: '#000'
  },
  sidebarDrawer: {
    backgroundColor: '#343239',
    borderColor: '#6b6471',
    hoverBackgroundColor: '#242229'
  },
  genericButton: {
    backgroundColor: '#444249',
    borderColor: '#7b7481',
    hoverBackgroundColor: '#343239'
  },
  bugIcon: {
    backgroundColor: darkBaseColors.purpleLight,
    borderColor: '#5f5a64',
    hoverBackgroundColor: '#6d6772'
  },
  loginSplash: {
    svgColor: '#332643',
    backgroundColor: '#191b1b'
  }
};
