const prepareUserPayload = (degree, planner) => {
  const { startYear, courses } = planner;
  const { programCode, specialisation, minor } = degree;

  const specialisations = {};
  specialisations[specialisation] = 1;
  if (minor !== "") specialisations[minor] = 1;

  const selectedCourses = {};
  Array.from(courses.keys()).forEach((course) => {
    selectedCourses[course] = 70;
  });

  return {
    program: programCode,
    specialisations,
    courses: selectedCourses,
    year: new Date().getFullYear() - startYear,
  };
};

export default prepareUserPayload;
