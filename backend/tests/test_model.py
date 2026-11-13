from models import conv_to_minutes, Meeting, Section, Course, Term
import pytest

# overlaps

def test_meetings_on_same_day_with_overlapping_times_overlap():
    a = Meeting(day="M", start="10:00", end="12:30")
    b = Meeting(day="M", start="10:00", end="12:30")
    assert a.overlaps(b)

def test_meetings_on_same_day_inside_another_overlaps():
    a = Meeting(day="M", start="10:00", end="12:30")
    b = Meeting(day="M", start="10:30", end="11:30")
    assert a.overlaps(b)

def test_meetings_on_same_day_starting_earlier_but_finishing_inside_another_overlaps():
    a = Meeting(day="M", start="9:00", end="10:01")
    b = Meeting(day="M", start="10:00", end="12:30")
    assert a.overlaps(b)

def test_meetings_on_same_day_inside_another_overlaps_reverse_direction():
    a = Meeting(day="M", start="10:00", end="12:30")
    b = Meeting(day="M", start="10:30", end="11:30")
    assert b.overlaps(a) 

def test_meetings_on_same_day_with_a_minute_difference_dont_overlap():
    a = Meeting(day="M", start="10:00", end="12:30")
    b = Meeting(day="M", start="12:31", end="13:10")
    assert not a.overlaps(b)

def test_meeting_ending_when_another_starts_does_not_overlap():
    a = Meeting(day="T", start="13:30", end="14:30")
    b = Meeting(day="T", start="14:30", end="15:30")
    assert not a.overlaps(b)

def test_same_time_meetings_on_different_days_dont_overlap():
    a = Meeting(day="T", start="13:30", end="14:30")
    b = Meeting(day="W", start="13:30", end="14:30")
    assert not a.overlaps(b)

def test_online_meetings_never_conflict():
    a = Meeting(day="", start="", end="")
    b = Meeting(day="T", start="08:00", end="09:00")
    assert not a.overlaps(b)

def test_two_online_meetings_dont_overlap():
    a = Meeting(day="", start="", end="")
    b = Meeting(day="", start="", end="")
    assert not a.overlaps(b) 

def test_meeting_to_dict():
    m = Meeting(day="M", start="13:40", end="15:40")
    assert m.to_dict() == {"day": "M", "start": "13:40", "end": "15:40"}

# conv_to_minutes

def test_eleven_thirty_am_equals_690_minutes():
    assert conv_to_minutes("11:30") == 690

def test_midnight_equals_0_minutes():
    assert conv_to_minutes("00:00") == 0

def test_eleven_fiftynine_pm_equals_1439_minutes():
    assert conv_to_minutes("23:59") == 1439

def test_ten_raises_error():
    with pytest.raises(ValueError):
        conv_to_minutes("10")

def test_empty_time_raises_error():
    with pytest.raises(ValueError):
        conv_to_minutes("")

def test_non_digits_raises_error():
    with pytest.raises(ValueError):
        conv_to_minutes("ab:cd")

# section 

def test_two_sections_with_overlapping_meeting_conflicts():
    a = Section(section="801", 
                crn="58565", 
                instructor="Sunqian Ren", 
                title="Financial and Managerial Accounting for Decision Making",
                meetings=[Meeting(day="M", start="10:00", end="11:30")])
    b = Section(section="803", 
                crn="87592", 
                instructor="John Bob", 
                title="The Art of Larping",
                meetings=[Meeting(day="M", start="09:00", end="10:01")])
    assert a.conflicts_with(b)
    
def test_two_sections_with_meetings_on_different_days_dont_conflict():
    a = Section(section="801", 
                    crn="58565", 
                    instructor="Sunqian Ren", 
                    title="Financial and Managerial Accounting for Decision Making",
                    meetings=[
                        Meeting(day="M", start="10:00", end="11:30"),
                        Meeting(day="W", start="10:00", end="11:30"),
                        Meeting(day="F", start="10:00", end="11:30")
                        ])
    b = Section(section="803", 
                crn="87592", 
                instructor="John Bob", 
                title="The Art of Larping",
                meetings=[
                    Meeting(day="T", start="09:00", end="10:01"),
                    Meeting(day="R", start="09:00", end="10:01")
                    ])
    assert not a.conflicts_with(b)

def test_sections_conflict_when_only_later_meetings_overlap():
    a = Section(section="801", 
                    crn="58565", 
                    instructor="Sunqian Ren", 
                    title="Financial and Managerial Accounting for Decision Making",
                    meetings=[
                        Meeting(day="M", start="10:00", end="11:30"),
                        Meeting(day="W", start="10:00", end="11:30"),
                        Meeting(day="F", start="10:00", end="11:30")
                        ])
    b = Section(section="803", 
                crn="87592", 
                instructor="John Bob", 
                title="The Art of Larping",
                meetings=[
                    Meeting(day="T", start="09:00", end="10:01"),
                    Meeting(day="F", start="09:00", end="10:01")
                    ])
    assert a.conflicts_with(b)   

def test_section_with_no_meetings_dont_conflicts():  
    a = Section(section="801", 
                    crn="58565", 
                    instructor="Sunqian Ren", 
                    title="Financial and Managerial Accounting for Decision Making",
                    meetings=[
                        Meeting(day="M", start="10:00", end="11:30"),
                        Meeting(day="W", start="10:00", end="11:30"),
                        Meeting(day="F", start="10:00", end="11:30")
                        ])
    b = Section(section="803", 
                crn="87592", 
                instructor="John Bob", 
                title="The Art of Larping",
                meetings=[])
    assert not a.conflicts_with(b)

def test_section_to_dict():
    a = Section(section="801", 
                crn="58565", 
                instructor="Sunqian Ren", 
                title="Financial and Managerial Accounting for Decision Making",
                meetings=[
                    Meeting(day="M", start="10:00", end="11:30"),
                    Meeting(day="W", start="10:00", end="11:30"),
                    Meeting(day="F", start="10:00", end="11:30")
                    ])
    assert a.to_dict() == {"section": "801", 
                           "crn": "58565", 
                           "instructor": "Sunqian Ren", 
                           "title": "Financial and Managerial Accounting for Decision Making",
                           "meetings": [
                                {"day": "M", "start": "10:00", "end": "11:30"},
                                {"day": "W", "start": "10:00", "end": "11:30"},
                                {"day": "F", "start": "10:00", "end": "11:30"}]
                           }

# course

def test_get_code():
    a = Course(
        subject="CIS",
        number="3296",
        title="Software Design",
        credits_min=4,
        credits_max=4
    )
    assert a.code == "CIS 3296"

def test_course_to_dict():
    a = Course(
        subject="CIS",
        number="3296",
        title="Software Design",
        credits_min=4,
        credits_max=4,
        gen_ed=["GQ"],
        sections=[
            Section(section="777",
                    crn="11111",
                    instructor="Angela Faragasso",
                    title="Software Design",
                    meetings=[
                        Meeting(day="T", start="10:30", end="12:30"),
                        Meeting(day="R", start="10:30", end="12:30"),
                    ])
        ])
    assert a.to_dict() == {
        "code": "CIS 3296",
        "subject": "CIS",
        "title": "Software Design",
        "credits_min": 4,
        "credits_max": 4,
        "gen_ed": ["GQ"],
        "source": "import",
        "sections": [
            {"title": "Software Design",
             "section": "777",
             "crn": "11111",
             "instructor": "Angela Faragasso",
             "meetings": [
                 {"day": "T", "start": "10:30", "end": "12:30"},
                 {"day": "R", "start": "10:30", "end": "12:30"},
             ]}
        ],
    }

# term

def test_get_course_returns_added_course():
    term = Term(name="Spring 2027")

    course = Course(subject="CIS", 
                    number="3296", 
                    title="Software Design",
                    credits_min=4, 
                    credits_max=4)
    
    term.add_course(course)
    assert term.get_course("CIS 3296") is course

def test_get_course_returns_none_for_unknown_code():
    term = Term(name="Spring 2027")
    assert term.get_course("CIS 9999") is None

def test_get_course_finds_correct_course_among_several():
    term = Term(name="Spring 2027")

    cis = Course(subject="CIS", 
                 number="3296", 
                 title="Software Design",
                 credits_min=4, 
                 credits_max=4)
    
    math = Course(subject="MATH", 
                  number="1041", 
                  title="Calculus I",
                  credits_min=4, 
                  credits_max=4)
    
    term.add_course(cis)
    term.add_course(math)
    assert term.get_course("CIS 3296") is cis
    assert term.get_course("MATH 1041") is math


