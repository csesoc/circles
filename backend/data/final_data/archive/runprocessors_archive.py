"""
The driver for running our processors for legacy years.
if you need to bash this, use
python3 -m data.final_data.archive.runprocessors_archive --year <year> --stage data-fix
if you are making a new year for the archive, use
python3 -m data.final_data.archive.runprocessors_archive --year <year> --stage all
"""

import argparse
from sys import exit

from data.processors.courses_processing import process_course_data
from data.scrapers.courses_formatting import format_course_data
from data.scrapers.courses_scraper import scrape_course_data

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year",
    type=int,
)
parser.add_argument(
    "--stage",
    type=str,
    help="""scrape, format, process, all, data-fix""",
)

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    parser.print_help()
    exit(0)



run = {
    "scrape": scrape_course_data,
    "format": format_course_data,
    "process": process_course_data,
}

if __name__ == "__main__":
    if args.stage is None:
        args.stage = "data-fix"

    if args.stage == "all":
        # Run all the stages from top to bottom
        res = input(
            "Careful. You are about to run all stages INCLUDING the scrapers... Enter 'y' if you wish to proceed or 'n' to cancel: "
        )
        if res == "y":
            for courseFunction in run.values():
                courseFunction(args.year)
    elif args.stage == "data-fix":
        for stage, func in run.items():
            if stage != "scrape":
                func(args.year)
    else:
        run[args.stage](args.year)
