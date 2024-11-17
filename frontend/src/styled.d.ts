// import original module declarations
import 'styled-components';

// and extend them!
declare module 'styled-components' {
  export interface DefaultTheme {
    purplePrimary: string;
    purpleLight: string;
    purpleDark: string;

    body: string;
    text: string;
    scrollbar: {
      trackingAreaColor: string;
      scrollbarColor: string;
      scollbarBorderColor: string;
    };
    droppable: {
      backgroundColor: string;
    };
    plannerCartCard: {
      backgroundColorHover: string;
    };
    plannerCartMenu: {
      backgroundColor: string;
    };
    draggableTab: {
      backgroundColor: string;
      borderColor: string;
    };

    degreeCard: {
      backgroundColor: string;
    };
    draggableCourse: {
      backgroundColor: string;
      warningBackgroundColor: string;
      dragDisabledBackgroundColor: string;
      iconColor: string;
    };
    termCheckbox: {
      color: string;
    };
    warningOutlined: {
      color: string;
    };
    termBoxWrapper: {
      borderColor: string;
    };

    optionsHeader: {
      borderColor: string;
      borderAlternativeColor: string;
      buttonBorderColor: string;
      buttonBackgroundColor: string;
      buttonHoverColor: string;
      buttonHoverAlternativeColor: string;
    };
    editMark: {
      backgroundColor: string;
      color: string;
      borderColor: string;
      borderColorHeader: string;
      backgroundColorHover: string;
    };
    settingsMenuSelect: {
      selectBackgroundColor: string;
      selectBorderColor: string;
      selectArrowColor: string;
      optionBackgroundColor: string;
      optionTextColor: string;
      optionHoverBackgroundColor: string;
    };
    datePicker: {
      inputBackgroundColor: string;
      inputBorderColor: string;
      calendarSvgFill: string;
      clearSvgFill: string;
      clearBackgroundColor: string;
      bodyBackgroundColor: string;
      arrowColor: string;
      yearHoverBackgroundColor: string;
      cellNotInViewColor: string;
    };
    popconfirm: {
      backgroundColor: string;
    };
    infoOutlined: {
      color: string;
    };
    uocBadge: {
      backgroundColor: string;
    };

    courseTag?: {
      backgroundColor: string;
    };
    courseSidebar?: {
      menuSubColor: string;
    };
    courseButton: {
      backgroundColor: string;
      hoverBackgroundColor: string;
    };
    courseMenu?: {
      backgroundColor: string;
      borderColor: string;
      hrefColor: string;
      hrefHoverColor: string;
    };
    searchBar: {
      spinBackgroundColor: string;
      backgroundColor: string;
      boxShadow: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    courseDescription: {
      paddingColor: string;
    };
    collapseBtnIcon: {
      color: string;
    };
    quickAddRemoveBtn: {
      addBackgroundColor: string;
      removeBackgroundColor: string;
      addBorderColor: string;
    };
    graph: {
      backgroundColor: string;
      borderColor: string;
      tabColor: string;
      tabBottomBorderColor: string;
      tabTextColor: string;
      tabBoxShadow?: string;
      loadingIcon?: string;
      loadingText: string;
    };
    sidebarDrawer: {
      backgroundColor: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    genericButton: {
      backgroundColor: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    bugIcon: {
      backgroundColor: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    loginSplash?: {
      svgColor: string;
      backgroundColor: string;
    };
    searchBar: {
      spinBackgroundColor: string;
      backgroundColor: string;
      boxShadow: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    courseDescription: {
      paddingColor: string;
    };
    collapseBtnIcon: {
      color: string;
    };
    quickAddRemoveBtn: {
      addBackgroundColor: string;
      removeBackgroundColor: string;
      addBorderColor: string;
    };
    graph: {
      backgroundColor: string;
      borderColor: string;
      tabColor: string;
      tabBottomBorderColor: string;
      tabTextColor: string;
      tabBoxShadow?: string;
      loadingIcon?: string;
      loadingText: string;
    };
    sidebarDrawer: {
      backgroundColor: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    genericButton: {
      backgroundColor: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
    bugIcon: {
      backgroundColor: string;
      borderColor: string;
      hoverBackgroundColor: string;
    };
  }
}
