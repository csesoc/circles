'''The driver for our procsesors. Provide the relevant command line arguments
in order to run the relevant drivers'''

import sys
import argparse
import glob
import subprocess 

from data.scrapers.programsScraper import scrape_programs as scrape_prg_data
from data.scrapers.specialisationsScraper import scrape_spn_data
from data.scrapers.coursesScraper import scrape_courses as scrape_course_data

from data.scrapers.programsFormatting import format_data as format_prg_data
from data.scrapers.specialisationsFormatting import format_spn_data
from data.scrapers.coursesFormatting import format_course_data

from data.processors.programsProcessing import process_data as process_prg_data
from data.processors.specialisationsProcessing import customise_spn_data
from data.processors.coursesProcessing import process_courses as process_course_data

from data.processors.conditionsPreprocessing import preprocess_conditions
from data.processors.conditions_tokenising import tokenise_conditions

from algorithms.cache.cache import cache_exclusions
from algorithms.cache.cache import cache_warnings
from algorithms.cache.cache import cache_mappings
from algorithms.cache.cache import cache_course_codes

parser = argparse.ArgumentParser()
parser.add_argument('--type', type=str,
                    help='program, specialisation, course, condition, algorithm')
parser.add_argument('--stage', type=str,
                    help=
                    '''
                    (any) --> all
                    program/specialisation/course --> scrape, format, process
                    condition --> process, manual, tokenise
                    algorithm --> exclusion, warning, mapping, code
                    ''')

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)

def run_manual_fixes():
    subprocess.run(['data/processors/manualFixes/runManualFixes.sh'])

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
        'scrape': scrape_course_data,
        'format': format_course_data,
        'process': process_course_data
    },
    'condition': {
        'process': preprocess_conditions,
        'manual': run_manual_fixes,
        'tokenise': tokenise_conditions
    },
    'algorithm': {
        'exclusion': cache_exclusions,
        'warnings': cache_warnings,
        'mapping': cache_mappings,
        'code': cache_course_codes
    }
}


if args.stage == 'all':
    # Run all the stages from top to bottom
    if args.type in ["program", "specialisation", "course"]:
        # NOTE: Be careful when using this as this will rerun the scrapers
        res = input(
            f"Careful. You are about to run all stages of {args.type} INCLUDING the scrapers... Enter 'y' if you wish to proceed or 'n' to cancel: ")
        if res == 'y':
            for s in run[args.type]:
                run[args.type][s]()
    else:
        # Conditions
        for s in run[args.type]:
            run[args.type][s]()
else:
    # Run the specific process
    run[args.type][args.stage]()


