""" a script that is used to compare 2 years in the archive (or with the current active year) """


import argparse
import json
from contextlib import suppress
from sys import exit

from data.processors.models import Course

parser = argparse.ArgumentParser()
parser.add_argument(
    "--target",
    type=str,
    help="the year to be compared",
)
parser.add_argument(
    "--source",
    type=str,
    help=""" optional - if a year is selected, compare to that year in the archive """,
)

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    parser.print_help()
    exit(0)

def check_in_fixes(cname: str, ls: list[tuple[str,str]], error: str) -> None:
    """ mutates the list given to add the course name if it is in manual fixes"""
    with suppress(FileNotFoundError):
        with open(f"data/processors/manual_fixes/{cname[0:4]}Fixes.py", "r", encoding="utf8") as file:
            if f"CONDITIONS[\"{cname}\"]" in file.read():
                ls.append((cname, error))


def main():
    """ runs the comparison between a target and a source year """
    source_course_location = (
        "data/final_data/coursesProcessed.json"
        if args.source is None
        else f"data/final_data/archive/processed/{args.source}.json"
    )

    target_course_location = f"data/final_data/archive/processed/{args.target}.json"

    with open(source_course_location, "r", encoding="utf8") as f:
        source_courses: dict[str, Course] = json.loads(f.read())

    with open(target_course_location, "r", encoding="utf8") as f:
        target_courses: dict[str, Course] = json.loads(f.read())

    all_source = set(source_courses.keys())
    all_target = set(target_courses.keys())
    courses_in_manual: list[tuple[str, str]] = []

    print("removed:")
    for removed in sorted(all_target - all_source):
        check_in_fixes(removed, courses_in_manual, "\t\t- removed")
        print(f"\t- {removed}")

    print("added:")
    for added in sorted(all_source - all_target):
        check_in_fixes(added, courses_in_manual, f"\t\t- added: \"{source_courses[added]['raw_requirements']}\"")
        print(f"\t- {added}")

    print("changed:")
    for coursename in sorted(all_source.intersection(all_target)):
        target_course = target_courses[coursename]["raw_requirements"]
        source_course = source_courses[coursename]["raw_requirements"]
        if target_course != source_course:
            print()
            print(f"\t{coursename}:")
            check_in_fixes(coursename, courses_in_manual, f"\t\t- from:  \"{target_course}\"\n\t\t- to:    \"{source_course}\"")
            print(f"\t\t - from:  \"{target_course}\"")
            print(f"\t\t - to:    \"{source_course}\"")
    print("inFixes:")
    for added, error in sorted(courses_in_manual):
        print(f"\t- {added}: \n{error}")

if __name__ == "__main__":
    main()
