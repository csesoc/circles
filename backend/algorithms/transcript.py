import re
from typing import Any, BinaryIO, Dict, Tuple
from pypdf import PdfReader




Term = str
YearInt = int
CourseCode = str
Grade = str | Any | None
Mark = int | None
UOC = int | None

CoursesByYear = Dict[YearInt, Dict[Term, Dict[CourseCode, Tuple[UOC, Mark, Grade]]]]

def parse_transcript(file: BinaryIO) -> CoursesByYear:
    # pylint: disable=too-many-locals
    reader = PdfReader(file)

    page_texts = list(map(lambda p: p.extract_text(), reader.pages))

    for i, page_text in enumerate(page_texts):
        search = re.search("Student ID: [0-9]*\n", page_text)
        if not search:
            continue
        page_texts[i] = page_text[search.end(0):] # chop off page beginning text

    text = "".join(page_texts)
    lines = text.split('\n')

    complete_exp = r"([A-Z]{4}) ([0-9]{4}) .* ([^ ]+) ([^ ]+) ([0-9]+) ([A-Z]{2})"
    def parse_course_line(line):
        match = re.fullmatch(complete_exp, line)
        if match:
            course_letters, course_number, uattempted, _upassed, mark, grade = match.groups()
            course_code = course_letters + course_number
            mark = int(mark)
            try:
                uattempted = int(uattempted)
            except ValueError:
                uattempted = None
            return course_code, mark, uattempted, grade
        match = re.fullmatch(r"([A-Z]{4}) ([0-9]{4}) .* ([0-9]+\.[0-9]+) ", line)
        if match:
            course_letters, course_number, uattempted = match.groups()
            course_code = course_letters + course_number
            try:
                uattempted = int(uattempted)
            except ValueError:
                uattempted = None
            return course_code, None, uattempted, None
        return None


    years: CoursesByYear = {}

    i = 0
    while i < len(lines):
        year_raw, term_raw = None, None
        if re.fullmatch("Summer Term [0-9]{4}", lines[i]):
            term = '0'
            year = lines[i].split(' ')[-1]
        if re.fullmatch("Term [1-3] [0-9]{4}", lines[i]):
            _, term_raw, year = lines[i].split(' ')
        if year_raw is not None and term_raw is not None:
            year = int(year_raw)
            term = 'T' + term_raw

            years[year] = years.get(year, {})
            years[year][term] = {}

            while lines[i] != "Course Title Attempted Passed Mark Grade":
                i += 1
            i += 1

            course_tup = parse_course_line(lines[i])
            while course_tup:
                course_code, mark, uoc, grade = course_tup
                years[year][term][course_code] = (uoc, mark, grade)
                i += 1
                course_tup = parse_course_line(lines[i])
        else:
            i += 1

    return years
