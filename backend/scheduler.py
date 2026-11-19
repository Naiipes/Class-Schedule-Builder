from models import Course, Section, conv_to_minutes

def fits(section: Section, chosen: list[tuple[Course, Section]]) -> bool:
    for _, other in chosen:
        if section.conflicts_with(other):
            return False

    return True

def generate_schedule(courses: list[Course], limit: int = 20) -> list[list[tuple[Course, Section]]]:
    chosen = []
    results = []

    def backtracking(i: int):
        if len(results) >= limit:
            return

        if len(courses) == i:
            results.append(list(chosen))
            return

        course = courses[i]

        for section in course.sections:
            if fits(section, chosen):
                chosen.append((course, section))
                backtracking(i + 1)
                chosen.pop()

    backtracking(0)
    return results

def schedule_to_dict(schedule_id: int, schedule: list[tuple[Course, Section]]) -> dict:
    sections = []
    credits = 0

    for course, section in schedule:
        data = section.to_dict()
        data["code"] = course.code

        sections.append(data)
        credits += course.credits_min

    return {"id": schedule_id, "total_credits": credits, "sections": sections}

def meetings_of(schedule: list[tuple[Course, Section]]) -> list:
    meetings = []

    for _, section in schedule:
        for meeting in section.meetings:
            meetings.append(meeting)

    return meetings

def gap_minutes(meetings: list) -> int:
    total = 0

    for day in "MTWRFSU":
        times = []

        for meeting in meetings:
            if meeting.day == day:
                times.append((conv_to_minutes(meeting.start), conv_to_minutes(meeting.end)))

        times.sort()

        for i in range(1, len(times)):
            gap = times[i][0] - times[i - 1][1]

            if gap > 0:
                total += gap

    return total

def score_schedule(schedule: list[tuple[Course, Section]], preferences: dict) -> int:
    meetings = meetings_of(schedule)
    penalty = 0

    free_day = preferences.get("free_day")

    if free_day:
        for meeting in meetings:
            if meeting.day == free_day:
                penalty += 40
                break

    earliest_start = preferences.get("earliest_start")

    if earliest_start:
        earliest = conv_to_minutes(earliest_start)

        for meeting in meetings:
            if not meeting.start:
                continue
            if conv_to_minutes(meeting.start) < earliest:
                penalty += 10

    if preferences.get("fewer_gaps"):
        penalty += gap_minutes(meetings) // 30

    return max(0, 100 - penalty)

def rank_schedules(schedules: list, preferences: dict) -> list:
    scored = []

    for schedule in schedules:
        scored.append((score_schedule(schedule, preferences), schedule))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return scored