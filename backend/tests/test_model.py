from models import conv_to_minutes, Meeting, Section, Course, Term

def test_meetings_on_same_day_with_overlapping_times_overlap():
    a = Meeting(day="M", start="10:00", end="12:30")
    b = Meeting(day="M", start="11:00", end="13:10")
    assert a.overlaps(b)

def test_meeting_ending_when_another_starts_does_not_overlap():
    a = Meeting(day="T", start="13:30", end="14:30")
    b = Meeting(day="T", start="14:30", end="15:30")
    assert not a.overlaps(b)

def test_same_time_meetings_on_different_days_dont_overlap():
    a = Meeting(day="T", start="13:30", end="14:30")
    b = Meeting(day="W", start="13:30", end="14:30")
    assert not a.overlaps(b)

def test_eleven_thirty_pm_equals_690_minutes():
    assert conv_to_minutes("11:30") == 690



