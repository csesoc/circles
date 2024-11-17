type Route = {
  label: string;
  link: string;
  dev?: boolean;
};

const routes: Route[] = [
  {
    label: 'Degree Wizard',
    link: '/degree-wizard'
  },
  {
    label: 'Course Selector',
    link: '/course-selector'
  },
  {
    label: 'Graphical Selector',
    link: '/graphical-selector',
    dev: true
  },
  {
    label: 'Term Planner',
    link: '/term-planner'
  },
  {
    label: 'Progression Checker',
    link: '/progression-checker'
  },
  {
    label: 'Logout',
    link: '/logout'
  }
];

export default routes;
