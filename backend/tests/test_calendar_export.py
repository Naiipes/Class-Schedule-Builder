from calendar_export import escape_text, fold_line, first_day_on_or_after, group_meetings, build_ics
from datetime import date, datetime, timedelta, timezone
from models import Course, Section, Term, Meeting
import pytest

# escape_text

def test_escape_text_escapes_special_characters():
    assert escape_text("\\;,\n") == "\\\\\\;\\,\\n"

def test_escape_text_escapes_backslash_first():
    assert escape_text(";\\") == "\\;\\\\"


# fold_line

def test_fold_line_keeps_short_line():
    assert fold_line("123456789") == ["123456789"]

def test_fold_line_splits_line_over_70_characters():
    line = "a" * 71
    assert fold_line(line) == ["a" * 70, " a"]

def test_fold_line_keeps_line_at_boundary():
    line = "a" * 70
    assert fold_line(line) == ["a" * 70]

def test_fold_line_splits_long_line_into_several_parts():
    parts = fold_line("a" * 200)
    assert [len(p) for p in parts] == [70, 70, 62] 
    assert all(p.startswith(" ") for p in parts[1:])


# first_day_on_or_after

def test_first_day_is_same_day_when_it_matches():
    tuesday = date(2027, 1, 12)
    assert first_day_on_or_after(tuesday, "T") == date(2027, 1, 12)

def test_first_day_moves_forward_to_next_weekday():
    tuesday = date(2027, 1, 12)
    assert first_day_on_or_after(tuesday, "W") == date(2027, 1, 13)
    assert first_day_on_or_after(tuesday, "F") == date(2027, 1, 15)

def test_first_day_wraps_into_next_week():
    # Monday comes before Tuesday so the first Monday on or after Jan 12 is the next week
    tuesday = date(2027, 1, 12)
    assert first_day_on_or_after(tuesday, "M") == date(2027, 1, 18)


# group_meetings

def test_group_meetings_combines_days_with_the_same_times():
    section = Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30"),
                                              Meeting(day="R", start="10:30", end="12:30")])
    assert group_meetings(section) == {("10:30", "12:30"): ["T", "R"]}

def test_group_meetings_keeps_different_times_separate():
    section = Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30"),
                                              Meeting(day="R", start="10:30", end="12:30"),
                                              Meeting(day="F", start="09:30", end="11:30")])
    assert group_meetings(section) == {("10:30", "12:30"): ["T", "R"],
                                       ("09:30", "11:30"): ["F"]}

def test_group_meetings_of_section_without_meetings_is_empty():
    section = Section(section="01", meetings=[])
    assert group_meetings(section) == {}


# build_ics

def test_build_ics_starts_on_first_class_date():
    term = Term(name="Spring 2027", start_date="2027-01-12", end_date="2027-04-21")
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4)

    tr = Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30"),
                                         Meeting(day="R", start="10:30", end="12:30")])
    mw = Section(section="02", meetings=[Meeting(day="M", start="09:00", end="10:00"),
                                         Meeting(day="W", start="09:00", end="10:00")])

    tr_text = build_ics([(course, tr)], term)
    assert "DTSTART;TZID=Asia/Tokyo:20270112T103000" in tr_text
    assert "DTEND;TZID=Asia/Tokyo:20270112T123000" in tr_text

    # Monday is listed first but the first class is Wednesday Jan 13, not Monday Jan 18
    mw_text = build_ics([(course, mw)], term)
    assert "DTSTART;TZID=Asia/Tokyo:20270113T090000" in mw_text

def test_build_ics_repeats_until_term_end():
    term = Term(name="Spring 2027", start_date="2027-01-12", end_date="2027-04-21")
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4)
    section = Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30")])

    # 23:59:59 in Tokyo on the last day, written in UTC
    assert "RRULE:FREQ=WEEKLY;BYDAY=TU;UNTIL=20270421T145959Z" in build_ics([(course, section)], term)

def test_build_ics_creates_one_event_per_time_group():
    term = Term(name="Spring 2027", start_date="2027-01-12", end_date="2027-04-21")
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4)
    section = Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30"),
                                              Meeting(day="R", start="10:30", end="12:30"),
                                              Meeting(day="F", start="09:00", end="10:00")])

    text = build_ics([(course, section)], term)
    assert text.count("BEGIN:VEVENT") == 2
    assert "BYDAY=TU,TH;" in text
    assert "BYDAY=FR;" in text

def test_build_ics_summary_falls_back_to_course_title():
    term = Term(name="Spring 2027", start_date="2027-01-12", end_date="2027-04-21")
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4)

    with_title = Section(section="01", title="Special Topics", meetings=[Meeting(day="T", start="10:30", end="12:30")])
    without_title = Section(section="02", title="", meetings=[Meeting(day="T", start="10:30", end="12:30")])

    assert "SUMMARY:CIS 3296 Special Topics" in build_ics([(course, with_title)], term)
    assert "SUMMARY:CIS 3296 Software Design" in build_ics([(course, without_title)], term)

def test_build_ics_omits_description_for_tba():
    term = Term(name="Spring 2027", start_date="2027-01-12", end_date="2027-04-21")
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4)

    named = Section(section="01", instructor="Angela", meetings=[Meeting(day="T", start="10:30", end="12:30")])
    tba = Section(section="02", instructor="TBA", meetings=[Meeting(day="T", start="10:30", end="12:30")])
    blank = Section(section="03", instructor="", meetings=[Meeting(day="T", start="10:30", end="12:30")])

    assert "DESCRIPTION:Instructor: Angela" in build_ics([(course, named)], term)
    assert "DESCRIPTION" not in build_ics([(course, tba)], term)
    assert "DESCRIPTION" not in build_ics([(course, blank)], term)

def test_build_ics_uses_crlf_line_endings():
    term = Term(name="Spring 2027", start_date="2027-01-12", end_date="2027-04-21")
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4)
    section = Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30")])

    text = build_ics([(course, section)], term)
    assert text.endswith("\r\n")
    # every newline is part of a \r\n pair, so there are no bare \n line endings
    assert text.count("\n") == text.count("\r\n")
