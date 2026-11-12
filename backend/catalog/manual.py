import re
from models import Course, Meeting, Section

DAYS = "MTWRFSU"
PATTERN = re.compile(r"^\d{2}:\d{2}$")

def parse_meeting(data: dict) -> Meeting:
    day = str(data.get("day", "")).upper()
    start = str(data.get("start", ""))
    end = str(data.get("end", ""))

    if len(day) != 1 or day not in DAYS:
        raise ValueError(f"Day must be in {DAYS}")
    if not PATTERN.match(start) or not PATTERN.match(end):
        raise ValueError("start and end must look like HH:MM")
    if start >= end:
        raise ValueError("Start must be before end")

    return Meeting(day, start, end)

def parse_section(data: dict, title: str) -> Section:
    section = str(data.get("section", "")).strip()

    if not section:
        raise ValueError("Section is required")

    meetings = []

    for meeting_data in data.get("meetings") or []:
        meetings.append(parse_meeting(meeting_data))

    return Section(
        section=section,
        instructor=str(data.get("instructor") or "TBA").strip(),
        meetings=meetings,
        title=title,
    )

def course_from_json(body: dict) -> Course:
    subject = str(body.get("subject", "")).strip().upper()
    number = str(body.get("number", "")).strip()
    title = str(body.get("title", "")).strip()

    if not subject or not number or not title:
        raise ValueError("subject, number and title are required")

    try:
        credits = int(body.get("credits"))
    except (TypeError, ValueError):
        raise ValueError("credits must be a number")

    sections_data = body.get("sections") or []

    if not sections_data:
        raise ValueError("at least one section is required")

    course = Course(
        subject=subject,
        number=number,
        title=title,
        credits_min=credits,
        credits_max=credits,
        source="manual",
    )
    
    for section_data in sections_data:
        course.sections.append(parse_section(section_data, title))

    return course