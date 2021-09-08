'''The driver for our procsesors. Provide the relevant command line arguments
in order to run the relevant drivers'''

# TODO: import courseScraper

import sys
import argparse

from data.scrapers.programsScraper import scrape_programs as scrape_prg_data
from data.scrapers.specialisationsScraper import scrape_spn_data

from data.scrapers.programsFormatting import format_data as format_prg_data
from data.scrapers.specialisationsFormatting import format_spn_data
from data.scrapers.coursesFormatting import format_course_data

from data.processors.programsProcessing import process_data as process_prg_data
from data.processors.specialisationsProcessing import customise_spn_data
from data.processors.coursesProcessing import process_courses as process_course_data

from data.processors.conditionsPreprocessing import preprocess_conditions
from data.processors.conditionsManualFixes import fix_conditions
from data.processors.conditions_tokenising import tokenise_conditions

parser = argparse.ArgumentParser()
parser.add_argument('--type', type=str,
                    help='all, program, specialisation, course or condition')
parser.add_argument('--stage', type=str,
                    help='all, scrape, format, process (or manual/tokenise for conditions manual fixes)')

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)

run = {
    'program': {
        'scrape': scrape_prg_data,
        'format': format_prg_data,
        'process': process_prg_data
    },
    'specialisation': {
        'scrape': scrape_spn_data,
        'format': format_spn_data,
        'process': customise_spn_data
    },
    'course': {
        'format': format_course_data,
        'process': process_course_data
    },
    << << << < HEAD
    'condition': {
        'process': preprocess_conditions,
        'manual': fix_conditions,
        'tokenise': tokenise_conditions
    }
    == == == =
    # 'condition': {
    #     'preprocess': preprocess_conditions,
    #     'parse': parse_conditions_logic
    # }
    >>>>>> > fe/dev
}

if args.type == 'all':
    for t in run:
        if args.stage == 'all':
            # Run all the stages from top to bottom
            for s in run[args.type]:
                run[t][s]()
        else:
            # Run the specific file
            run[t][args.type]()
else:
    if args.stage == 'all':
        # Run all the stages from top to bottom
        for s, in run[args.stage]:
            run[args.stage][s]()
    else:
        # Run the specific file
        run[args.type][args.stage]()
