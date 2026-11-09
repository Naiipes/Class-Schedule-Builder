from models import Course, Section

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

