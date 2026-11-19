from scheduler import fits, generate_schedule, schedule_to_dict, meetings_of, gap_minutes, score_schedule, rank_schedules
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


# --------------------- Preferences and Ranking --------------------------------------------------------------

# meetings_of

def test_meetings_of_empty_schedule_is_empty():
    assert meetings_of([]) == []

def test_meetings_of_single_section_returns_its_meetings():
    a = make_section("01", "T", "10:00", "11:00")
    assert meetings_of([(make_course(a), a)]) == a.meetings
    
def test_meetings_of_includes_every_meeting_of_a_section():
    a = Section(section="123", meetings=[
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="R", start="10:00", end="11:00")
    ])
    assert meetings_of([(make_course(a), a)]) == a.meetings

def test_meetings_of_combines_sections_in_schedule_order():
    a = make_section("01", "T", "08:00", "10:00")
    b = make_section("02", "R", "10:30", "12:30")
    schedule = [(make_course(a, number="3296"), a), (make_course(b, number="3223"), b)]
    assert meetings_of(schedule) == a.meetings + b.meetings

def test_meetings_of_skips_sections_without_meetings():
    a = Section(section="01")
    b = make_section("02", "R", "10:30", "12:30")
    schedule = [(make_course(a, number="3296"), a), (make_course(b, number="3223"), b)]
    assert meetings_of(schedule) == b.meetings


# gap_minutes

def test_gap_minutes_no_meetings_is_zero():
    assert gap_minutes([]) == 0

def test_gap_minutes_single_meeting_is_zero():
    meetings = [Meeting(day="T", start="10:00", end="11:00")]
    assert gap_minutes(meetings) == 0

def test_gap_minutes_one_gap_on_one_day():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="T", start="12:00", end="13:00"),
    ]
    assert gap_minutes(meetings) == 60

def test_gap_minutes_back_to_back_meetings_is_zero():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="T", start="11:00", end="12:00"),
    ]
    assert gap_minutes(meetings) == 0

def test_gap_minutes_adds_multiple_gaps_on_same_day():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="T", start="12:00", end="13:00"),
        Meeting(day="T", start="14:30", end="15:30"),
    ]
    assert gap_minutes(meetings) == 150

def test_gap_minutes_adds_gaps_across_days():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="T", start="12:00", end="13:00"),  # 60 minute gap
        Meeting(day="R", start="10:00", end="11:00"),
        Meeting(day="R", start="12:00", end="13:00"),  # 60 minute gap
    ]
    assert gap_minutes(meetings) == 120

def test_gap_minutes_ignores_time_between_different_days():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="R", start="12:00", end="13:00"),
    ]
    assert gap_minutes(meetings) == 0

def test_gap_minutes_ignores_online_meetings():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="T", start="12:00", end="13:00"),
        Meeting(day="", start="", end="")
    ]
    assert gap_minutes(meetings) == 60

def test_gap_minutes_overlapping_meetings_add_no_gap():
    meetings = [
        Meeting(day="T", start="10:00", end="11:00"),
        Meeting(day="T", start="10:30", end="12:30"),
    ]
    assert gap_minutes(meetings) == 0


# score_schedule

def test_score_with_no_preferences_is_100():
    a = make_section("01", "T", "10:00", "12:30")
    assert score_schedule([(make_course(a), a)], {}) == 100

def test_score_of_empty_schedule_is_100():
    assert score_schedule([], {"free_day": "F"}) == 100

def test_free_day_with_no_class_that_day_scores_100():
    a = make_section("01", "T", "10:00", "11:00")
    assert score_schedule([(make_course(a), a)], {"free_day": "F"}) == 100

def test_class_on_free_day_costs_40():
    a = make_section("01", "T", "10:00", "11:00")
    assert score_schedule([(make_course(a), a)], {"free_day": "T"}) == 60    

def test_free_day_penalty_applies_only_once():
    a = make_section("01", "T", "10:00", "11:00")
    b = make_section("02", "T", "12:00", "13:00")
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"free_day": "T"}) == 60

def test_meeting_before_earliest_start_costs_10():
    a = make_section("01", "T", "08:00", "10:00")
    assert score_schedule([(make_course(a), a)], {"earliest_start": "09:00"}) == 90

def test_each_early_meeting_costs_10():
    a = make_section("01", "T", "08:00", "10:00")
    b = make_section("02", "T", "08:30", "09:30")
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"earliest_start": "09:00"}) == 80         

def test_meeting_starting_at_earliest_start_is_not_penalized():
    a = make_section("01", "T", "09:00", "10:00")
    assert score_schedule([(make_course(a), a)], {"earliest_start": "09:00"}) == 100

def test_earliest_start_ignores_online_meetings():
    a = make_section("01", "", "", "")
    assert score_schedule([(make_course(a), a)], {"earliest_start": "10:00"}) == 100

def test_fewer_gaps_with_no_gaps_scores_100():
    a = make_section("01", "T", "08:00", "10:00")
    b = make_section("02", "T", "10:00", "12:00")
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"fewer_gaps": True}) == 100

def test_fewer_gaps_costs_1_point_per_30_minutes():
    a = make_section("01", "T", "08:00", "10:00")
    b = make_section("02", "T", "10:30", "12:00")
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"fewer_gaps": True}) == 99    

def test_fewer_gaps_rounds_down_partial_half_hours():
    a = make_section("01", "T", "08:00", "09:00")
    b = make_section("02", "T", "10:29", "11:00")   # 89-minute gap -> 2 points
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"fewer_gaps": True}) == 98    

def test_fewer_gaps_false_is_ignored():
    a = make_section("01", "T", "08:00", "10:00")
    b = make_section("02", "T", "10:30", "12:00")
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"fewer_gaps": False}) == 100    

def test_all_penalties_combined_adds_up():
    a = make_section("01", "T", "08:00", "10:00") 
    b = make_section("02", "T", "10:30", "12:00")
    assert score_schedule([(make_course(a, number="101"), a), (make_course(b, number="102"), b)], {"fewer_gaps": True, "earliest_start": "10:00", "free_day": "T"}) == 49        

def test_score_never_goes_bellow_0():
    a = make_section("01", "T", "08:00", "09:00") 
    b = make_section("02", "T", "08:00", "09:00") 
    c = make_section("03", "T", "08:00", "09:00") 
    d = make_section("04", "T", "08:00", "09:00") 
    e = make_section("05", "T", "08:00", "09:00") 
    f = make_section("06", "T", "08:00", "09:00") 
    g = make_section("07", "T", "08:00", "09:00") 
    
    assert score_schedule([(make_course(a, number="101"), a), 
                           (make_course(b, number="102"), b), 
                           (make_course(c, number="103"), c),
                           (make_course(d, number="104"), d),
                           (make_course(e, number="105"), e),
                           (make_course(f, number="106"), f),
                           (make_course(g, number="107"), g)], {"earliest_start": "10:00", "free_day": "T"}) == 0  


# rank_schedules

def test_rank_empty_list_returns_empty():
    assert rank_schedules([], {}) == []

def test_rank_single_schedule_returns_its_rank():
    a = make_section("01", "T", "10:00", "11:00")
    schedule = [(make_course(a), a)]
    assert rank_schedules([schedule], {}) == [(100, schedule)]

def test_rank_returns_score_and_schedule_pairs():
    a = make_section("01", "T", "10:00", "11:00")
    b = make_section("02", "R", "11:00", "12:00")
    schedule = [(make_course(a, number="101"), a), (make_course(b, number="102"), b)]
    assert rank_schedules([schedule], {}) == [(100, schedule)]

def test_ranks_sorts_highest_score_first():
    a = make_section("01", "T", "08:00", "09:00")
    b = make_section("02", "R", "10:00", "12:00")
    c = make_section("03", "M", "09:30", "10:30")
    first = [(make_course(a, number="101"), a)]
    second = [(make_course(b, number="102"), b)]
    third = [(make_course(c, number="103"), c)]
    assert rank_schedules([first, second, third], {"free_day": "T", "earliest_start": "10:00"}) == [(100, second), (90, third), (50, first)]

def test_rank_keeps_generation_order_for_ties():
    a = make_section("01", "T", "08:00", "09:00")
    b = make_section("02", "R", "10:00", "12:00")
    c = make_section("03", "M", "11:00", "13:00")
    first = [(make_course(a, number="101"), a)]
    second = [(make_course(b, number="102"), b)]
    third = [(make_course(c, number="103"), c)] 
    # Here second and third have the same score, but since third was passed in before second, its order has been kept.
    assert rank_schedules([first, third, second], {"free_day": "T", "earliest_start": "10:00"}) == [(100, third), (100, second), (50, first)]

def test_rank_with_no_preferences_keeps_original_order():
    a = make_section("01", "T", "08:00", "09:00")
    b = make_section("02", "R", "10:00", "12:00")
    c = make_section("03", "M", "11:00", "13:00")
    first = [(make_course(a, number="101"), a)]
    second = [(make_course(b, number="102"), b)]
    third = [(make_course(c, number="103"), c)] 
    assert rank_schedules([first, second, third], {}) == [(100, first), (100, second), (100, third)]

