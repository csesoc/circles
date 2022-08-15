export type ViewSubgroupCourse = {
  courseCode: string
  title: string
  UOC: number
  plannedFor: string
  // isUnplanned used to differentiate course in planner cart but has not been planned
  isUnplanned: boolean
  isMultiterm: boolean
};

export type ViewSubgroup = {
  isCoursesOverflow: boolean
  courses: ViewSubgroupCourse[]
};

export type ProgressionViewStructure = {
  [groupKey: string]: {
    [subgroupKey: string]: ViewSubgroup
  }
};

/* GridView types */
export enum Views {
  TABLE,
  GRID,
  GRID_CONCISE,
}
