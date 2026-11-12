from models import Course, Term

def matches_text(course: Course, q: str) -> bool:
    q = q.lower().strip()

    if q in course.code.lower():
        return True
    if q in course.title.lower():
        return True
    for section in course.sections:
        if q in section.instructor.lower():
            return True
        if q in section.title.lower():
            return True

    return False

class CatalogRepository:
    def __init__(self, term: Term):
        self.term = term

    def get(self, code: str) -> Course | None:
        return self.term.get_course(code)

    def add(self, course: Course) -> bool:
        if self.term.get_course(course.code) is not None:
            return False
        
        self.term.add_course(course)

        return True

    def search(self, q=None, subject=None, credits=None, gen_ed=None) -> list[Course]:
        results = []

        for course in self.term.courses.values():
            if q and not matches_text(course, q):
                continue
            if subject and course.subject != subject.upper():
                continue
            if credits is not None and not (course.credits_min <= credits <= course.credits_max):
                continue
            if gen_ed and gen_ed not in course.gen_ed:
                continue
            results.append(course)

        return sorted(results, key=lambda c: c.code)