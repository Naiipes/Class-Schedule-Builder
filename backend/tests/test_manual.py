import pytest
from catalog.manual import parse_meeting, parse_section, course_from_json
from models import Course, Meeting, Section

# parse_meeting

def test_parse_meeting_returns_meeting():
    assert parse_meeting({"day": "M", "start": "10:00", "end": "11:00"}) == Meeting(day="M", start="10:00", end="11:00")

def test_parse_meeting_uppercases_day():
    assert parse_meeting({"day": "m", "start": "10:00", "end": "11:00"}) == Meeting(day="M", start="10:00", end="11:00")   

def test_parse_meeting_rejects_invalid_day():
    with pytest.raises(ValueError, match="Day must be in"):
        parse_meeting({"day": "X", "start": "10:00", "end": "11:00"})

def test_parse_meeting_rejects_multiple_days():
    with pytest.raises(ValueError, match="Day must be in"):
        parse_meeting({"day": "TR", "start": "10:00", "end": "11:00"})

def test_parse_meeting_rejects_missing_day():
    with pytest.raises(ValueError, match="Day must be in"):
        parse_meeting({"day": "", "start": "10:00", "end": "11:00"})

def test_parse_meeting_rejects_bad_time_format():
    with pytest.raises(ValueError, match="start and end must look like HH:MM"):
        parse_meeting({"day": "T", "start": "9:00", "end": "10:00"})
    with pytest.raises(ValueError, match="start and end must look like HH:MM"):
        parse_meeting({"day": "T", "start": "09:00", "end": "10am"})
    with pytest.raises(ValueError, match="start and end must look like HH:MM"):
        parse_meeting({"day": "T", "start": "0900", "end": "10:00"})

def test_parse_meeting_rejects_start_equal_to_end():
    with pytest.raises(ValueError, match="Start must be before end"):
        parse_meeting({"day": "T", "start": "10:00", "end": "10:00"})

def test_parse_meeting_rejects_start_after_end():
    with pytest.raises(ValueError, match="Start must be before end"):
        parse_meeting({"day": "T", "start": "10:00", "end": "08:00"})


# parse_section

def test_parse_section_returns_section_with_title():
    data = {"section": "802", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
    assert parse_section(data, "Software Design") == Section(
        section="802",
        instructor="Angela",
        meetings=[Meeting(day="T", start="10:00", end="12:00")],
        title="Software Design",
    )

def test_parse_section_strips_section_number():
    data = {"section": "   802         ", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
    assert parse_section(data, "Software Design") == Section(
        section="802",
        instructor="Angela",
        meetings=[Meeting(day="T", start="10:00", end="12:00")],
        title="Software Design",
    )

def test_parse_section_rejects_missing_or_blank_section():
    data = {"section": "", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
    with pytest.raises(ValueError, match="Section is required"):
        parse_section(data, "Software Design")
    data = {"section":  " ", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
    with pytest.raises(ValueError, match="Section is required"):
        parse_section(data, "Software Design")

def test_parse_section_defaults_instructor_to_tba():
    data = {"section": "802", "instructor": "", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
    assert parse_section(data, "Software Design") == Section(
            section="802",
            instructor="TBA",
            meetings=[Meeting(day="T", start="10:00", end="12:00")],
            title="Software Design",
        )

def test_parse_section_strips_instructor():
    data = {"section": "802", "instructor": "   Angela   ", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
    assert parse_section(data, "Software Design") == Section(
            section="802",
            instructor="Angela",
            meetings=[Meeting(day="T", start="10:00", end="12:00")],
            title="Software Design",
        )

def test_parse_section_without_meetings_has_empty_list():
    data = {"section": "802", "instructor": "Angela", "meetings": []}
    assert parse_section(data, "Software Design") == Section(
            section="802",
            instructor="Angela",
            meetings=[],
            title="Software Design",
        )

def test_parse_section_parses_each_meeting():
    data = {"section": "802", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}, {"day": "R", "start": "10:00", "end": "12:00"}]}
    assert parse_section(data, "Software Design") == Section(
        section="802",
        instructor="Angela",
        meetings=[Meeting(day="T", start="10:00", end="12:00"),
                  Meeting(day="R", start="10:00", end="12:00")],
        title="Software Design",
    )

def test_parse_section_rejects_invalid_meeting():
    data = {"section": "802", "instructor": "Angela", "meetings": [{"day": "", "start": "10:00", "end": "12:00"}]}
    with pytest.raises(ValueError, match="Day must be in"):
        parse_section(data, "Software Design")

def test_parse_section_rejects_null_section():
    with pytest.raises(ValueError, match="Section is required"):
        parse_section({"section": None}, "Software Design")


# course_from_json

def test_course_from_json_returns_manual_course():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": 4,
        "sections": [
            {"section": "802", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
        ],
    }
    assert course_from_json(body) == Course(
        subject="CIS",
        number="3296",
        title="Software Design",
        credits_min=4,
        credits_max=4,
        source="manual",
        sections=[Section(section="802", instructor="Angela", meetings=[Meeting(day="T", start="10:00", end="12:00")], title="Software Design")]
    )
    

def test_course_from_json_uppercases_and_strips_subject_and_number():
    body = {
        "subject": "     cis      ",
        "number": "   3296   ",
        "title": "Software Design",
        "credits": 4,
        "sections": [
            {"section": "802", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
        ],
    }
    assert course_from_json(body) == Course(
        subject="CIS",
        number="3296",
        title="Software Design",
        credits_min=4,
        credits_max=4,
        source="manual",
        sections=[Section(section="802", instructor="Angela", meetings=[Meeting(day="T", start="10:00", end="12:00")], title="Software Design")]
    )

    

def test_course_from_json_accepts_numeric_string_credits():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": "4",
        "sections": [
            {"section": "802", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]}
        ],
    }
    assert course_from_json(body) == Course(
        subject="CIS",
        number="3296",
        title="Software Design",
        credits_min=4,
        credits_max=4,
        source="manual",
        sections=[Section(section="802", instructor="Angela", meetings=[Meeting(day="T", start="10:00", end="12:00")], title="Software Design")]
    )

def test_course_from_json_parses_multiple_sections():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": 4,
        "sections": [
            {"section": "802", "instructor": "Angela", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]},
            {"section": "804", "instructor": "John Bob", "meetings": [{"day": "M", "start": "08:00", "end": "10:00"}]},
        ],
    }
    assert course_from_json(body) == Course(
        subject="CIS",
        number="3296",
        title="Software Design",
        credits_min=4,
        credits_max=4,
        source="manual",
        sections=[
            Section(section="802", instructor="Angela", meetings=[Meeting(day="T", start="10:00", end="12:00")], title="Software Design"),
            Section(section="804", instructor="John Bob", meetings=[Meeting(day="M", start="08:00", end="10:00")], title="Software Design")
        ]
    )

def test_course_from_json_rejects_missing_required_fields():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": 4,
        "sections": [{"section": "802"}],
    }
    for field in ["subject", "number", "title"]:
        missing = {key: value for key, value in body.items() if key != field}
        with pytest.raises(ValueError, match="subject, number and title are required"):
            course_from_json(missing)
        with pytest.raises(ValueError, match="subject, number and title are required"):
            course_from_json({**body, field: ""})
        with pytest.raises(ValueError, match="subject, number and title are required"):
            course_from_json({**body, field: "   "})

def test_course_from_json_rejects_null_required_fields():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": 4,
        "sections": [{"section": "802"}],
    }
    for field in ["subject", "number", "title"]:
        with pytest.raises(ValueError, match="subject, number and title are required"):
            course_from_json({**body, field: None})

def test_course_from_json_rejects_non_numeric_credits():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": "four",
        "sections": [{"section": "802"}],
    }
    with pytest.raises(ValueError, match="credits must be a number"):
        course_from_json(body)
    with pytest.raises(ValueError, match="credits must be a number"):
        course_from_json({**body, "credits": None})

def test_course_from_json_rejects_missing_or_empty_sections():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": 4,
        "sections": [],
    }
    with pytest.raises(ValueError, match="at least one section is required"):
        course_from_json(body)
    del body["sections"]
    with pytest.raises(ValueError, match="at least one section is required"):
        course_from_json(body)

def test_course_from_json_rejects_invalid_section():
    body = {
        "subject": "CIS",
        "number": "3296",
        "title": "Software Design",
        "credits": 4,
        "sections": [
            {"section": "802", "meetings": [{"day": "T", "start": "10:00", "end": "12:00"}]},
            {"section": "", "meetings": [{"day": "M", "start": "08:00", "end": "10:00"}]},
        ],
    }
    with pytest.raises(ValueError, match="Section is required"):
        course_from_json(body)
