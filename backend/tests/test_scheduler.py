from scheduler import fits, generate_schedule, schedule_to_dict
from models import Course, Meeting, Section
import pytest

# helpers ------------------------------------------------------------------------------------------------------------------
def make_course(*sections: Section, number: str = "101") -> Course:
    return Course(subject="CIS", number=number, title="Intro", credits_min=3, credits_max=3, sections=list(sections))

def make_section(name: str, day: str, start: str, end: str) -> Section:
    return Section(section=name, meetings=[Meeting(day=day, start=start, end=end)])
# --------------------------------------------------------------------------------------------------------------------------


# fits

def test_section_fits_empty_schedule():
    assert fits(Section(title="Software Design", section="802"), [])

def test_section_fits_when_no_conflicts_with_chosen():
    a = make_section("01", "M", "08:00", "09:00")
    b = make_section("02", "T", "10:00", "11:00")
    c = make_section("03", "M", "12:00", "13:00")
    chosen = [(make_course(a), a), (make_course(b), b)]
    assert fits(c, chosen)

def test_section_does_not_fit_when_conflicting_with_one_chosen():
    a = make_section("01", "M", "08:00", "09:00")
    b = make_section("02", "M", "10:00", "11:00")
    c = make_section("03", "M", "08:30", "09:30")
    chosen = [(make_course(a), a), (make_course(b), b)]
    assert not fits(c, chosen)

def test_section_does_not_fit_when_conflicting_with_last_chosen():
    a = make_section("01", "M", "08:00", "09:00")
    b = make_section("02", "T", "08:00", "09:00")
    c = make_section("03", "W", "10:00", "11:00")
    d = make_section("04", "W", "10:30", "11:30")
    chosen = [(make_course(a), a), (make_course(b), b), (make_course(c), c)]
    assert not fits(d, chosen)

def test_online_section_always_fits():
    a = make_section("01", "M", "08:00", "09:00")
    no_meetings = Section(section="111")
    blank_times = make_section("222", "", "", "")
    chosen = [(make_course(a), a)]
    assert fits(no_meetings, chosen)
    assert fits(blank_times, chosen)

def test_section_ending_when_chosen_starts_fits():
    a = make_section("01", "M", "10:00", "11:00")
    b = make_section("02", "M", "09:00", "10:00")
    chosen = [(make_course(a), a)]
    assert fits(b, chosen)


# generate_schedule

def test_no_courses_returns_one_empty_schedule():
    assert generate_schedule([]) == [[]]

def test_single_course_returns_one_schedule_per_section():
    course = Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4, sections=[
        make_section("01", "M", "10:00", "11:00"),
        make_section("02", "M", "09:00", "10:00"),
    ])
    schedules = generate_schedule([course])
    assert schedules == [[(course, course.sections[0])], [(course, course.sections[1])]]

def test_course_with_no_sections_returns_no_schedules():
    assert generate_schedule([make_course()]) == []

def test_two_non_conflicting_courses_return_all_combinations():
    a = make_course(make_section("01", "M", "08:00", "09:00"), make_section("02", "M", "10:00", "11:00"), number="101")
    b = make_course(make_section("01", "T", "08:00", "09:00"), make_section("02", "T", "10:00", "11:00"), number="102")
    schedules = generate_schedule([a, b])
    picked = [(s[0][1].section, s[1][1].section) for s in schedules]
    assert picked == [("01", "01"), ("01", "02"), ("02", "01"), ("02", "02")]

def test_conflicting_sections_are_excluded():
    a = make_course(make_section("01", "M", "08:00", "09:00"), make_section("02", "M", "10:00", "11:00"), number="101")
    b = make_course(make_section("01", "M", "08:30", "09:30"), make_section("02", "T", "10:00", "11:00"), number="102")
    schedules = generate_schedule([a, b])
    picked = [(s[0][1].section, s[1][1].section) for s in schedules]
    assert ("01", "01") not in picked
    assert picked == [("01", "02"), ("02", "01"), ("02", "02")]

def test_all_sections_conflict_returns_no_schedules():
    a = make_course(make_section("01", "M", "08:00", "09:00"), make_section("02", "M", "10:00", "11:00"), number="101")
    b = make_course(make_section("01", "M", "08:00", "11:00"), number="102")
    assert generate_schedule([a, b]) == []

def test_schedule_preserves_course_order():
    a = make_course(make_section("01", "M", "08:00", "09:00"), number="101")
    b = make_course(make_section("01", "T", "08:00", "09:00"), number="102")
    assert [c.code for c, _ in generate_schedule([a, b])[0]] == ["CIS 101", "CIS 102"]
    assert [c.code for c, _ in generate_schedule([b, a])[0]] == ["CIS 102", "CIS 101"]

# helper: 5 courses x 2 sections with no meetings = 32 possible schedules, none conflicting
def many_online_courses() -> list[Course]:
    return [make_course(Section(section="01"), Section(section="02"), number=str(n)) for n in range(5)]

def test_results_capped_at_default_limit_of_20():
    assert len(generate_schedule(many_online_courses())) == 20

def test_results_capped_at_custom_limit():
    assert len(generate_schedule(many_online_courses(), limit=5)) == 5
    assert len(generate_schedule(many_online_courses(), limit=100)) == 32

def test_limit_zero_returns_no_schedules():
    assert generate_schedule(many_online_courses(), limit=0) == []


# schedule_to_dict

def test_schedule_to_dict_includes_id():
    a = make_section("01", "M", "08:00", "09:00")
    assert schedule_to_dict(7, [(make_course(a), a)])["id"] == 7

def test_schedule_to_dict_sums_credits_min():
    a = make_section("01", "M", "08:00", "09:00")
    b = make_section("01", "T", "08:00", "09:00")
    four_credit_course = Course(subject="MATH", number="1041", title="Calculus I", credits_min=4, credits_max=4, sections=[b])
    result = schedule_to_dict(1, [(make_course(a), a), (four_credit_course, b)])
    assert result["total_credits"] == 7

def test_schedule_to_dict_uses_credits_min_for_variable_credit_course():
    a = make_section("01", "M", "08:00", "09:00")
    variable = Course(subject="CIS", number="4282", title="Independent Study", credits_min=1, credits_max=4, sections=[a])
    assert schedule_to_dict(1, [(variable, a)])["total_credits"] == 1

def test_schedule_to_dict_adds_course_code_to_each_section():
    a = make_section("01", "M", "08:00", "09:00")
    b = make_section("02", "T", "08:00", "09:00")
    result = schedule_to_dict(1, [(make_course(a, number="101"), a), (make_course(b, number="102"), b)])
    assert [s["code"] for s in result["sections"]] == ["CIS 101", "CIS 102"]

def test_empty_schedule_to_dict_has_zero_credits_and_no_sections():
    assert schedule_to_dict(0, []) == {"id": 0, "total_credits": 0, "sections": []}
