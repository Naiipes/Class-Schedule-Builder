from datetime import date, datetime, timedelta, timezone
from models import Course, Section, Term

DAY_CODES = {"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR", "S": "SA", "U": "SU"}
WEEKDAY_NUMBERS = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}

def escape_text(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")

    return text

def fold_line(line: str) -> list[str]:
    if len(line) <= 70:
        return [line]

    parts = [line[:70]]
    rest = line[70:]

    while len(rest) > 0:
        parts.append(" " + rest[:69])
        rest = rest[69:]

    return parts

def first_day_on_or_after(start: date, day: str) -> date:
    current = start

    while current.weekday() != WEEKDAY_NUMBERS[day]:
        current = current + timedelta(days=1)

    return current

def group_meetings(section: Section) -> dict:
    groups = {}

    for meeting in section.meetings:
        key = (meeting.start, meeting.end)

        if key not in groups:
            groups[key] = []

        groups[key].append(meeting.day)

    return groups

def build_ics(items: list[tuple[Course, Section]], term: Term) -> str:
    term_start = date.fromisoformat(term.start_date)
    term_end = date.fromisoformat(term.end_date)

    until = term_end.strftime("%Y%m%d") + "T145959Z"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Class Schedule Builder//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Tokyo",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "TZNAME:JST",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]

    number = 0

    for course, section in items:
        groups = group_meetings(section)

        for key in groups:
            start = key[0]
            end = key[1]
            days = groups[key]

            first = None

            for day in days:
                candidate = first_day_on_or_after(term_start, day)

                if first is None or candidate < first:
                    first = candidate

            byday = []

            for day in days:
                byday.append(DAY_CODES[day])

            number += 1
            title = section.title or course.title

            first_text = first.strftime("%Y%m%d")
            start_text = start.replace(":", "") + "00"
            end_text = end.replace(":", "") + "00"
            byday_text = ",".join(byday)

            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:{number}-{course.subject}{course.number}-{section.section}@class-schedule-builder")
            lines.append(f"DTSTAMP:{stamp}")
            lines.append(f"DTSTART;TZID=Asia/Tokyo:{first_text}T{start_text}")
            lines.append(f"DTEND;TZID=Asia/Tokyo:{first_text}T{end_text}")
            lines.append(f"RRULE:FREQ=WEEKLY;BYDAY={byday_text};UNTIL={until}")
            lines.append("SUMMARY:" + escape_text(f"{course.code} {title}"))

            if section.instructor and section.instructor != "TBA":
                lines.append("DESCRIPTION:" + escape_text(f"Instructor: {section.instructor}"))

            lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    folded = []

    for line in lines:
        for part in fold_line(line):
            folded.append(part)

    return "\r\n".join(folded) + "\r\n"