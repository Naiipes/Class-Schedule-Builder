import csv
import html
from collections import Counter
from datetime import datetime
from pathlib import Path

from models import Course, Meeting, Section, Term

def parse_credits(text: str) -> tuple[int, int]:
    if "-" in text:
        low, high = text.split("-")
        return int(low), int(high)
    return int(text), int(text)

def to_iso(date: str) -> str:
    return datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")

def most_common_date(rows: list[dict], column: str) -> str:
    dates = [row[column] for row in rows if row[column]]
    if not dates:
        return ""
    
    counts = Counter(dates)
    top_date = max(counts, key=counts.get)

    return to_iso(top_date)

def parse_gen_ed(text: str) -> list[str]:
    text = html.unescape(text)
    result = []
    for part in text.split(";"):
        part = part.strip()
        if part.startswith("GenEd "):
            result.append(part.removeprefix("GenEd "))

    return result

def parse_meetings(days: str, times: str) -> list[Meeting]:
    if days.strip() == "":
        return []

    day_groups = days.split(";")
    time_ranges = times.split(";")

    meetings = []
    for i in range(len(day_groups)):
        day_group = day_groups[i].strip()
        time_range = time_ranges[i].strip()
        start, end = time_range.split("-")

        for day in day_group:
            new_meeting = Meeting(day, start, end)
            if new_meeting not in meetings:
                meetings.append(new_meeting)

    return meetings

class CsvCatalogImporter:
    def __init__(self, path, term_name: str = "Spring 2027"):
        self.path = Path(path)
        self.term_name = term_name

    def load(self) -> Term:
        with open(self.path, encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))

        term = Term(self.term_name)

        for row in rows:
            code = row["Subject"] + " " + row["Course Number"]
            course = term.get_course(code)

            if course is None:
                credits_min, credits_max = parse_credits(row["Credits"])
                course = Course(
                    subject=row["Subject"],
                    number=row["Course Number"],
                    title=row["Title"],
                    credits_min=credits_min,
                    credits_max=credits_max,
                    gen_ed=parse_gen_ed(row["Attributes"]),
                )
                term.add_course(course)

            section = Section(
                section=row["Section"],
                crn=row["CRN"] or None,
                instructor=row["Instructor"].strip() or "TBA",
                meetings=parse_meetings(row["Days"], row["Times"]),
            )
            course.sections.append(section)

        term.start_date = most_common_date(rows, "Start Date")
        term.end_date = most_common_date(rows, "End Date")

        return term