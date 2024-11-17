"""
Preprocessing the conditions and logging to conditionsProcessed.json
Some examples of preprocessing are:
- Getting rid of "Prerequisite:" or similar at start of line
- Fixing extra white space
- Normalising AND/OR/and/or to && and ||
- Converting specialisation and program names to corresponding codes
"""

import json
import re
from functools import reduce

from data.utility.data_helpers import read_data, write_data

PREPROCESSED_CONDITIONS: dict[str, dict[str, str]] = {}
CODE_MAPPING = read_data("data/utility/programCodeMappings.json")["title_to_code"]

# TODO: think of how to automate some of this
SPECIALISATION_MAPPINGS = {
    r'7005 UNSW Global Diploma in Media and Communication Program': '7005',
    r'Academic program must be 7016, Humanities Pathway Program': '7016',
    r'the Social Research and Policy honours program': '4504',
    r'4529 Social Science \(Honours\)': '4529',
    r'4511 B Arts \(Honours\)': '4511',
    r'3880 Bachelor of International Public Health': '3880',
    r'3894 Nutrition\/Dietetics and Food Innovation': '3894',
    r'3897 Applied Exercise Science\/Clinical Exercise Physiology': '3897',
    r'3895 Pharmaceutical Medicine\/Pharmacy': '3895',
    r'3896 Exercise Science\/Physiotherapy and Exercise Physiology': '3896',
    r'FINSD1 Finance Co-Op': 'FINSD1',
    r'(a )?Politics, Philosophy, and Economics program': 'PPES#',
    r"(a )?Politics and International Relations specialisation": 'POLSG?',
    r'School of the Arts and Media honours': 'MDIA?H',
    r'Business \(Honours\) Program 4512': '4512',
    r'School of Social Sciences, Asian Studies or European Studies honours': 'ASIABH || EUROBH',
    r'Creative Writing honours': 'CRWTWH',
    r'Nanoscience Honours' : 'NANO?H',
    r'4508 Music \(Honours\)': '4508',
    r'Construction Management and Property undergraduate program or minor': 'BLDG??',
    r'Media, Culture and Technology honours': 'MECTBH',
    r'Theatre and Performance Studies honours': 'THSTBH',
    r'Environmental Humanities honours': 'ENVPEH',
    r'Physics Honours': 'ZPEMPH || PHYSGH',
    r'Fine Arts \(Visual Arts\)': 'DARTE1',
    r'Film Studies honours': 'FILMBH',
    r'FINSBH Finance Co-Op Honours': 'FINSBH',
    r'Creative Writing Major or minor': 'CRWTA1 || CRWTAH || CRWTA2',
    r'Creative Writing Major': 'CRWTA1 || CRWTAH',
    r'English honours': 'ENGLDH',
    r'Dance Studies honours': 'DANCBH',
    r'History honours': 'HISTCH || ZHSSHH',
    r'Philosophy honours': 'PHILBH',
    r'Asian Studies honours': 'ASIABH',
    r'Chinese Studies honours': 'CHINBH',
    r'French Studies honours': 'FRENBH',
    r'Spanish Studies honours': 'SPANEH',
    r'Japanese Studies honours': 'JAPNDH',
    r'Korean Studies honours': 'KORECH',
    r'Linguistics honours': 'LINGCH',
    r'Currently program 3880 Bachelor of International Public Health': '3880',
    r'German Studies honours': 'GERSBH',
    r'Neuroscience Honours': 'NEUR?H',
    r'(3831)? Science \(Medicine\) Honours': '3831',
    r'European Studies honours': 'EUROBH',
    r'Sociology and Anthropology honours': 'SOCACH',
    r'Politics and International Relations honours': 'POLSGH',
    r'Global Development honours': 'COMDFH',
    r'Media honours': 'MDIA?H',
    r'Education honours': '4509',
    r'Criminology honours': '4505',
    r'Medical Science': '3991',
    r'Medicinal Chemistry honours': 'CHEMFH',
    r'Politics, Philosophy and Economics': '3478 || 4797',
    r'single or double Music (Honours)': 'MUSC?H || 4508',
    r'development studies honours': '8942',
    r'International Relations honours': 'POLSGH',
    r'Politics honours': 'ZHSSPH || POLSGH',
    r'Music program': 'MUSC?? || 4508',
    r'Social Work': '4033',
    r'single or dual award Media': '4510 || 3454 || 3438 || 3453',
    r'single or double degree Media': '4510 || 3454 || 3438 || 3453',
    r'Social Science or Social Research and Policy': '3321 || 3420',
    r'single or double Music \(Honours\) program': '4508',
    r'Education program': '4509 || 4056',
    r'Landscape Architecture minor': 'LANDA2',
    r'International Studies(?:\s+single)?(?:\s+or\s+((double)|(dual))\s+((degree)|(program)))?(?:\s*\(2017 onwards\))?': '3447',
}

def preprocess_conditions():
    """
    As title says. Preprocess conditions. Clean HTMl to something readable,
    convert symbols like brackets, grades, etc to their objects. Also
    process logical operators, logic and fix spacing and brackets.
    """
    data = read_data("data/scrapers/coursesFormattedRaw.json")

    for code, course in data.items():
        # if not course["enrolment_rules"]:
        #     # Store it as empty rule
        #     continue
        conditions = preprocess_condition(code, course)
        PREPROCESSED_CONDITIONS[code] = conditions

    write_data(PREPROCESSED_CONDITIONS, "data/final_data/conditionsProcessed.json")


def preprocess_condition(code, course=None):
    original = course["enrolment_rules"] if course is not None else ""
    conditions = {}

    # Store original text for debugging
    conditions["original"] = original
    processed = original

    # Phase 1: Deletions
    processed = delete_exclusions_and_equivalents(processed)
    processed = delete_HTML(processed)
    note, processed = remove_extraneous_handbook_data(processed)
    if note != "":
        conditions["handbook_note"] = note
    processed = delete_self_referencing(code, processed)
    processed = delete_extraneous_phrasing(processed)
    processed = delete_prereq_label(processed)
    processed = delete_trailing_punc(processed)

    # Phase 2: Conversions
    processed = convert_semicolon(processed)
    processed = convert_square_brackets(processed)
    processed = convert_UOC(processed)
    processed = convert_WAM(processed)
    processed = convert_GRADE(processed)
    processed = convert_level(processed)
    processed = convert_manual_programs_and_specialisations(processed)
    processed = convert_program_type(processed)
    processed = convert_fslash(processed)
    processed = convert_including(processed)
    processed = convert_AND_OR(processed)
    processed = convert_coreqs(processed)
    processed = convert_core(processed)

    # Phase 3: Algo logic
    processed = joining_terms(processed)
    processed = handle_comma_logic(processed)

    # Phase 4: Final touches
    processed = strip_spaces(processed)
    processed = strip_specialisation(processed)
    processed = strip_bracket_spaces(processed)

    # Phase 5: Common patterns
    processed = uoc_in_business_school(processed)
    processed = uoc_in_school(processed)
    processed = enrolment_in_program(processed)
    processed = l2_math_courses(processed)
    processed = unsw_global_degrees(processed)
    processed = international_public_health(processed)
    processed = business_honours(processed)
    processed = honours_plan(processed)
    processed = research_thesis(code, processed)

    conditions["processed"] = processed
    return conditions



# -----------------------------------------------------------------------------
# Phase 1: Deletions
# -------------------


def delete_exclusions_and_equivalents(processed: str) -> str:
    """Removes exclusions from enrolment conditions"""
    # Remove exclusion string which appears before prerequisite plaintext
    excl_string = re.search(r"(excl.*?:.*?)(pre|co-?req)", processed, flags=re.IGNORECASE)
    equiv_string = re.search(r"(equiv.*?:.*?)(pre|co-?req)", processed, flags=re.IGNORECASE)
    if excl_string:
        processed = re.sub(excl_string.group(1), "", processed)

    if equiv_string:
        processed = re.sub(equiv_string.group(1), "", processed)

    # Remove exclusion string appearing after prerequisite plaintext, typically
    # at the end of the enrolment rule
    processed = re.sub(r"((\.|,)?\s)?excl.*", "", processed, flags=re.IGNORECASE)
    processed = re.sub(r"((\.|,)?\s)?equiv.*?:.*", "", processed, flags=re.IGNORECASE)

    return processed


def delete_HTML(processed: str) -> str:
    """Remove HTML tags"""
    # Will replace with a space because they sometimes appear in the middle of the text
    # so "and<br/>12 UOC" would turn into and12 UOC
    return re.sub("<[a-z]*/>", " ", processed, flags=re.IGNORECASE)


def delete_self_referencing(code, processed):
    """Remove any references to this course"""
    # E.g. "COMP4962: {
    #     "processed_rule": "COMP4962 COMP4951"
    # } "
    return re.sub(code, "", processed)

def delete_extraneous_phrasing(processed: str) -> str:
    """Sometimes there's extraneous phrasing which needs to be handled"""
    # Must have completed COMP1511 ==> COMP1511
    # processed = re.sub("Must have completed ", "", processed, flags=re.IGNORECASE)

    # Remove 'Both' as it also usually preceeds handled logical phrases
    processed = re.sub("Both", "", processed, flags=re.IGNORECASE)

    # Remove 'or higher' as XXWAM implies XX minimum
    processed = re.sub("or higher", "", processed)
    processed = re.sub("or above", "", processed)
    # dont care
    processed = re.sub(r"or\s*equivalent", "", processed)
    processed = re.sub(r"^None", "", processed)

    # Remove 'student' references as it is implied
    processed = re.sub("students?", "", processed, flags=re.IGNORECASE)

    # Remove enrollment language since course and program codes imply this
    processed = re.sub("enrol(led|ment) in( program)?", "", processed, flags=re.IGNORECASE)

    # remove 'undergrad' because its implied
    processed = re.sub(r"UG", "", processed, flags=re.IGNORECASE)
    processed = re.sub(r"undergrad(uate)?", "", processed, flags=re.IGNORECASE)

    # Remove tautological endings
    processed = re.sub("(prior )?(in order )?to enrol(l)?(ing)?(ment)?( in(to)? this course)?", "", processed, flags=re.IGNORECASE)
    processed = re.sub("to be eligible for this course", "", processed, flags=re.IGNORECASE)

    # Remove completion language
    completion_text = [
        "^currently",
        "Successful completion of",
        "completion of",
        "must successfully complete",
        "should have completed",
        "must have completed",
        "completing",
        "have completed",
        "completed",
        "a pass in",
        "should have",
        "No prerequisites required"
    ]
    for text in completion_text:
        processed = re.sub(text, "", processed, flags=re.IGNORECASE)

    return processed


def delete_prereq_label(processed: str) -> str:
    """Removes 'prerequisite' and variations"""
    # variations incude ["prerequisite", "pre-requisite", "prer-requisite", "pre req", "prereq:"]
    return re.sub(r"pre( req)?[a-z\/_\-]*( (is|conditions))? *[:;]*", "", processed, flags=re.IGNORECASE)

def convert_semicolon(processed: str) -> str:
    return re.sub(r"(.*);", r"(\1)", processed)

def delete_trailing_punc(processed: str) -> str:
    """Deletes any trailing punctuation"""
    return re.sub(r"(\.|;)\s*$", "", processed)


# -----------------------------------------------------------------------------
# Phase 2: Conversions
# -------------------


def convert_square_brackets(processed: str) -> str:
    """Converts '[' to '(' and ']' to ')'"""
    processed = re.sub(r"\[", r"(", processed)
    processed = re.sub(r"]", r")", processed)
    return processed


def convert_UOC(processed: str) -> str:
    """Converts to XXUOC"""
    # Converts unit(s) of credit(s) to UOC and removes spacing
    processed = re.sub(
        r"\s*units? (of credits?|completed?)", "UOC", processed, flags=re.IGNORECASE
    )
    # Places UOC right next to the numbers
    processed = re.sub(r"\s*UOC", "UOC", processed, flags=re.IGNORECASE)

    # After UOC has been mainly converted, remove some extraneous phrasing
    processed = re.sub(
        r"((are\s*required|need)\s*to\s*have\s*a\s*minimum)?\s*(of|at least)?\s*(\d+UOC)", r" \4", processed, flags=re.IGNORECASE
    )
    processed = re.sub(
        r"(\d+UOC)(\s*(overall|(to undertake this|of) courses?)\s*)", r"\1 ", processed, flags=re.IGNORECASE
    )

    # Remove "minimum" since it is implied
    processed = re.sub(r"minimum (?:of )?(\d+UOC)", r"\1", processed, flags=re.IGNORECASE)

    return processed


def convert_WAM(processed: str) -> str:
    """Converts WAM requirements. WAM refers to overall mark."""
    # Look for integer within 3 words after 'WAM' or 'mark', e.g.:
    #    - "WAM of 65" -> "65WAM"
    #    - "WAM of at least 65" -> "65WAM"
    processed = re.sub(
        r"WAM ([a-z]* ){0,3}(>=)?(\d\d)(%)?", r"\3WAM", processed, flags=re.IGNORECASE
    )

    # Then delete any superfluous preceding words, chars or spaces, e.g.:
    #    - "minimum 65WAM" -> "65WAM"
    #    - "A 65WAM" -> "65WAM"
    processed = re.sub(
        r"[a|minimum|must have]+ (\d\d)\s*WAM", r" \1WAM", processed, flags=re.IGNORECASE
    )

    # Compress any remaining spaces between digits and WAM and remove misc chars
    # like '+' and '>', e.g.:
    #    - ">65WAM" -> "65WAM"
    #    - "65+ WAM" -> "65WAM"
    #    - "65WAM+" -> "65WAM"
    processed = re.sub(
        r">?=?(\d\d)\+?\s*WAM\+?", r"\1WAM", processed, flags=re.IGNORECASE
    )

    return processed


def convert_GRADE(processed: str) -> str:
    """Converts mark/grade requirements, usually relating to a specific course.
    NOTE: We prefer to use 'GRADE' here because 'MARK' could interfere with Marketing
    courses"""

    # Converts "mark of at least XX to XXGRADE"
    processed = re.sub(
        r"(a )?(minimum )?mark of (at least )?(\d\d)( or (greater|above))?",
        r"\4GRADE",
        processed,
        flags=re.IGNORECASE,
    )

    # Further handle CR and DN. These usually follow a course code
    # MATH1141 (CR) ==> 65WAM MATH1141
    # Use "in" as a joining word"
    processed = re.sub(r"([A-Z]{4}[\d]{4})\s*\(CR\)", r"65GRADE in \1", processed)
    processed = re.sub(r"([A-Z]{4}[\d]{4})\s*\(DN\)", r"75GRADE in \1", processed)
    processed = re.sub(r"([A-Z]{4}[\d]{4})\s*\(HD\)", r"85GRADE in \1", processed)

    return processed


def convert_level(processed):
    """Converts level X and X year to LX"""
    processed = re.sub(r"3rd year", r"L3", processed, flags=re.IGNORECASE)
    processed = re.sub(r"((at|in|of) )?level (\d)( courses)?", r"in L\3", processed, flags=re.IGNORECASE)
    return re.sub(r"in L(\d)( [A-Z]{4})( courses)?", r"in L\1\2", processed, flags=re.IGNORECASE)

def convert_program_type(processed: str) -> str:
    """Converts complex phrases into something of the form CODE# for specifying a program type"""
    with open("algorithms/cache/cache_config.json", encoding="utf8") as f:
        cache: dict[str, list[str]] = json.loads(f.read())
        processed = reduce((lambda a,b: b if b != processed else a), (map_word_to_program_type(processed, string, hashlist[0]) for string, hashlist in cache.items()))
    return processed


def convert_fslash(processed: str) -> str:
    """Converts forward slashes to || and surrounds in brackets"""
    # E.g.:
    #    - "(COMP1521/DPST1092 && COMP2521)" -> "((COMP1521 || DPST1092) && COMP2521)"
    #    - "COMP9444 / COMP9417 / COMP9517/COMP4418" -> "(COMP9444 || COMP9417 || COMP9517 || COMP4418)"
    matches = re.findall(r"[A-Z]{4}[\d]{4}(?:\s*/\s*[A-Z]{4}[\d]{4})+", processed)

    for match in matches:
        subbed_phrase = re.sub(r"/", r" || ", match)
        subbed_phrase = f"({subbed_phrase})"
        processed = re.sub(match, subbed_phrase, processed)

    return processed


def convert_including(processed: str) -> str:
    """Convert 'including' to &&"""
    return re.sub("including", "&&", processed)


def convert_manual_programs_and_specialisations(processed: str) -> str:
    """
    Deals with the following cases:
    - Enrolment in a x program
    - Enrolment in x program
    - Enrolment in x
    - Enrolment in the x honours program
    """
    for prog_str, code in SPECIALISATION_MAPPINGS.items():
        processed = re.sub(
            rf"(this course is\s*)?(enrolment\s+in\s+|restricted\s+to\s+)?((?:an?\s+)|(?:the\s+))?{prog_str}(\s*\({code}\))?(?:\s+(program|plan))?\s*",
            f" ({code}) ",
            processed,
            flags=re.IGNORECASE
        )
    return processed


def convert_AND_OR(processed: str) -> str:
    """Convert 'and' to '&&' and 'or' to '||'"""
    processed = re.sub(" and ", " && ", processed, flags=re.IGNORECASE)
    processed = re.sub(" & ", " && ", processed, flags=re.IGNORECASE)
    processed = re.sub(" and/or ", " || ", processed, flags=re.IGNORECASE)
    processed = re.sub(" with ", " && ", processed, flags=re.IGNORECASE)
    processed = re.sub(" plus ", " && ", processed, flags=re.IGNORECASE)
    processed = re.sub(r" \+ ", " && ", processed, flags=re.IGNORECASE)
    processed = re.sub(" or ", " || ", processed, flags=re.IGNORECASE)
    return processed


def convert_coreqs(processed: str) -> str:
    """Puts co-requisites inside square brackets"""
    processed = processed.rstrip()
    return re.sub(
        r",*;*\.*\s*(co-?(re)?requisites?|concurrentl?y?)\s*;?:?\s*(.*)", r" [\3]", processed, flags=re.IGNORECASE
    )

def convert_core(processed):
    """ Converts 'core' to 'CORES' for core course conditions """
    processed = re.sub("core", "CORES", processed, flags=re.IGNORECASE)
    return re.sub(r"(L\d) CORES", r"CORES in \1", processed, flags=re.IGNORECASE)

# -----------------------------------------------------------------------------
# Phase 3: Algo logic
# -------------------


def joining_terms(processed: str) -> str:
    """Currently, we aim to use "in" as a joining term"""
    # UOC at LX ==> UOC in LX
    processed = re.sub(r"UOC at (L\d)", r"UOC in \1", processed)

    # UOC of LX ==> UOC in LX
    processed = re.sub(r"UOC of (L\d)", r"UOC in \1", processed)

    return processed


def handle_comma_logic(processed: str) -> str:
    """
    Handles commas and either removes or converts into AND/OR
    We might need to perform lookaheads to detect if the comma should become an AND or an OR.
    3 main types of cases:
    A, B, && C ==> , becomes &&
    A, B, || C ==> , becomes ||
    A, B, C ==> , becomes &&
    NOTE: This logic will mishandle some conditions where its ambiguous,
    e.g. COMP1531, and COMP2521 or COMP1927 ??????????
    --> we turn it into COMP1531 && COMP2521 || COMP1927 < YO BUT THIS EVALUATES PROPERLY AHAHAHAHA
    """
    # If the word 'either' is still in processed. If so, must replace commas with ||s instead of &&s later on
    # when it's ambiguous between the two
    if 'either' in processed:
        joining_cond = '||'
    else:
        joining_cond = '&&'
    processed = re.sub("either", "", processed, flags=re.IGNORECASE)

    # First we will just convert , || and , && into || and &&
    processed = re.sub(r",\s*(&&|\|\|)", r" \1", processed)

    # Scan for combos of commas until we hit the first || or && and replace the
    # the commas with that
    # e.g. phrase, phrase || phrase ==> phrase || phrase || phrase
    # e.g. phrase, phrase && phrase ==> phrase && phrase && phrase
    if bool(re.match(r'^\s*[A-Z]{4}[0-9]{4}', processed)):
        matches = re.findall(r'([^&|]+,\s*[^&|]+\s*)(&&|\|\|)', processed)

        for match in matches:
            # Substitute the commas in the phrase with their respective logic operators
            subbed_phrase = re.sub(r',\s*', f" {match[1]} ", match[0])

            # Escape the matched phrase so regex doesn't misintrepret unclosed brackets, etc
            escaped_phrase = re.escape(match[0])

            processed = re.sub(escaped_phrase, subbed_phrase, processed)

        # Check if there were only commas in between course codes. If work has already been done DO NOTHING.
        # E.g, "72UOC , room in degree for course, Good academic standing" -> considered but no changes
        # "2303, 3303 && 3304" -> Not considered
        # "CEIC2001, CEIC2002, MATH2019, CEIC3000" -> "CEIC2001 && CEIC2002 && MATH2019 && CEIC3000"
        # "at least one of the following: ECON2112, ECON2206, ..." -> Not considered

        # If there are no &&s and ||s between course codes, just replace them with &&s.
        if '&&' not in processed and '||' not in processed:
            matches = re.findall(r'(?=([A-Z]{4}[0-9]{4}\s*,\s*[A-Z]{4}[0-9]{4}))', processed)
            for match in matches:
                # Replace each ' , ' with ' && ', where the amount
                # of whitespace on either side of the comma doesn't matter
                replacement = match.split(',')
                processed = re.sub(match, f'{replacement[0]} {joining_cond} {replacement[1]}', processed)

    # add &&s before coreqs if coreqs is not preceded by an OR logic
    if re.search(r'(?<!\|\|\s)\[.*\]', processed):
        processed = re.sub(r'&*\s*\[(.*)\]', r' && [\1]', processed)

    # remove &&s or ||s if it's the start of string
    processed = re.sub(r'^\s*&&', '', processed)
    processed = re.sub(r'^\s*\|\|', '', processed)

    return processed


# -----------------------------------------------------------------------------
# Phase 4: Final touches
# -------------------


def strip_spaces(processed: str) -> str:
    """Strip multiple repeated whitespace"""
    processed = re.sub(" +", " ", processed)

    # Get rid of white spaces at start and end of word
    return processed.strip()

def strip_bracket_spaces(processed: str) -> str:
    """Strips spaces immediately before and after brackets"""
    processed = re.sub(r"([([]) ", r"\1", processed)
    processed = re.sub(r" ([)]])", r"\1", processed)

    return processed


def strip_specialisation(processed: str) -> str:
    """Converts majors and minors into their respective specialisation codes.
    E.g. Bsc COMP major """
    return re.sub(r"be ([A-Z]{6}) (major|minor|honours)", r"\1", processed)

# """
# Maybe don't need here, put it in another file at the end.
# Adds opening and closing brackets if they do not exist. Apparently it helps
# to make the code cleaner in enrolment algorithms.
# TODO: Ensure brackets are evenly matched and any mismatched brackets are fixed
# before this point
# """
# def surround_brackets(processed: str) -> str:
#     return "(" + processed + ")"


# -----------------------------------------------------------------------------
# Phase 5: Common patterns
# -------------------
def uoc_in_business_school(processed: str) -> str:
    """Converts {number}UOC offered by the UNSW Business School to {number}UOC in F Business"""
    processed = re.sub(
        r"(\d+UOC) offered by the UNSW Business School", r"\1 in F Business", processed
    )

    return processed

def uoc_in_school(processed: str) -> str:
    return re.sub(r"(\d+ *UOC) (in|of|at) ([A-Z]{4})(\*{4})? courses", r"\1 in \3", processed)

def l2_math_courses(processed: str) -> str:
    """Converts L2 Maths courses to L@ MATH"""
    processed = re.sub(r"L2 Maths? courses", r"L2 MATH", processed, flags=re.IGNORECASE)
    processed = re.sub(
        r"L2 Mathematics? courses", r"L2 MATH", processed, flags=re.IGNORECASE
    )
    return processed


def map_word_to_program_type(processed: str, regex_word: str, type: str):
    return re.sub(
        rf"(a )?(enrolment )?(in )?(a )?(single or (double|dual) (degree|award) )?(B.)?{regex_word}( studies)? (programs?( \(.*\))?|single or dual degrees?)",
        type,
        processed,
        flags=re.IGNORECASE,
    )

def enrolment_in_program(processed: str):
    processed = re.sub(r"enrolment in program (.*)", r"(\1)", processed, flags=re.IGNORECASE)
    processed = re.sub(r"^([0-9]{4}) program$", r"(\1)", processed, flags=re.IGNORECASE)
    return re.sub(r"^program ([0-9]{4})$", r"(\1)", processed, flags=re.IGNORECASE)

def unsw_global_degrees(processed: str):
    processed =  re.sub(
        r"UNSW Global Diplomas only \(7001, 7002, 7003, 7004\)",
        "(7001 || 7002 || 7003 || 7004)",
        processed,
        flags=re.IGNORECASE,
    )

    processed =  re.sub(
        r"\(7001 \|\| 7002 \|\| 7003 \|\| 7004\),",
        "(7001 || 7002 || 7003 || 7004) &&",
        processed,
        flags=re.IGNORECASE,
    )

    return processed

def add_note_if_found(processed, find, note, substitute_with, add_to_note):
    """Checks processed for find, substitutes find with substitute_with, adds add_to_note to note """
    processed, number_of_subs = re.subn(find, substitute_with, processed, flags=re.IGNORECASE)
    return processed, note + add_to_note * (number_of_subs > 0)

def remove_extraneous_handbook_data(processed):
    """Adds handbook notes and removes phrasing
    example: 'good academic standing' -> '' with a handbook_note:'Students must be in Good Academic Standing.' """
    note = ""
    # Academic Standing note
    processed, note = add_note_if_found(processed, r"(Students )?(must )?(be )?[io]n Good (Academic)? Standing( and)?", note, r"", "Students must be in Good Academic Standing.")

    # Final 2 terms note
    processed, note = add_note_if_found(processed, r"It is strongly recommended that students only complete this course within their final 2 terms of study", note, r"", "Recommended to take this course within their final 2 terms of study.")
    # Business school students terms notes
    terms_string = re.findall(r"Only available to single and double degree Business School students in Term \d. It will be offered to non-Business School students in Terms \d and \d.", processed)
    processed, number_of_subs = re.subn(
        r"Only available to single and double degree Business School students in Term \d. It will be offered to non-Business School students in Terms \d and \d.", r"", processed, flags=re.IGNORECASE
    )
    if number_of_subs > 0:
        terms_numbers = re.findall(r'[0-9]+', terms_string[0])
        note += r"Only available to single and double degree Business School students in Term " + terms_numbers[0] + ". It will be offered to non-Business School students in Terms " + terms_numbers[1] +" and " + terms_numbers[2] +"."

    find = r"Only available to single and double degree Business School students in Term 2. It will be offered to non-Business School students in Term 3."
    processed, note = add_note_if_found(processed, find, note, r"", find)
    # Application and progression check notes
    find = r"This course is by application only. Please contact the Co-op office for more information"
    processed, note = add_note_if_found(processed, find, note, r"", find)
    find = r"This course is by application only."
    processed, note = add_note_if_found(processed, find, note, r"", find)
    find = r"Its recommended to seek a progression check prior to application."
    processed, note = add_note_if_found(processed, find, note, r"", find)
    processed, note = add_note_if_found(processed, r"This course is by application only.( )?Please visit Business School website for more information", note, r"", "This course is by application only. Please visit Business School website for more information")
    processed, note = add_note_if_found(processed, r"or language placement approval", note, r"", "language placement approval can also be used.")
    processed, note = add_note_if_found(processed, r"or with Head of School approval", note, r"", "Head of school approval can also be used.")
    # Commerce degree notes
    processed, note = add_note_if_found(processed, r"(Students are expected to be )?in their final year of a( single or )?(double)?(dual)? Bachelor of Commerce( single or dual)?( degree)?", note, r"COMM#", "Students must be in their final year of a single or double Commerce degree")
    processed = re.sub(
    r"Only available to students completing a Bachelor of Commerce as part of a single or double-degree", r"COMM#", processed, flags=re.IGNORECASE
    )
    processed = re.sub(
    r"be enrolled in a Commerce Program", r"COMM#", processed, flags=re.IGNORECASE
    )

    # need to change this/review these
    processed = re.sub(
        r"(\d+UOC) of Business courses", r"\1 in ZBUS && COMM#", processed
    )
    return note, processed

def international_public_health(processed: str):
    return re.sub("Currently program 3880 Bachelor of International Public Health", '3880', processed, flags=re.IGNORECASE)

def business_honours(processed: str):
    return re.sub(r"Enrolment in Business \(Honours\) Program 4512", '4512', processed, flags=re.IGNORECASE)

def research_thesis(code: str, processed: str):
    return re.sub(r"Research Thesis [A|B] \(([0-9]{4})\)", rf"{code[0:4]}\1", processed)

def honours_plan(processed: str):
    return re.sub(r"^([A-Z]{4}) (h|H)on(our)?s( (p|P)lan)?$", r"\1" + "?H", processed)

if __name__ == "__main__":
    preprocess_conditions()
