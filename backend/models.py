from dataclasses import dataclass, field

def conv_to_minutes(hhmm: str) -> int:
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)

@dataclass
class Meeting:
    day: str
    start: str
    end: str

    def overlaps(self, other: "Meeting") -> bool:
        if not self.start or not self.end or not other.start or not other.end:
            return False
        return (
            self.day == other.day
            and conv_to_minutes(self.start) < conv_to_minutes(other.end)
            and conv_to_minutes(other.start) < conv_to_minutes(self.end)
        )

    def to_dict(self) -> dict:
        return {"day": self.day,"start": self.start,"end": self.end}

@dataclass
class Section:
    section: str
    crn: str | None = None
    instructor: str = "TBA"
    meetings: list[Meeting] = field(default_factory=list)
    title: str = ""

    def conflicts_with(self, other: "Section") -> bool:
        for this_meeting in self.meetings:
            for other_meeting in other.meetings:
                if this_meeting.overlaps(other_meeting):
                    return True
        return False

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "section": self.section,
            "crn": self.crn,
            "instructor": self.instructor,
            "meetings": [m.to_dict() for m in self.meetings],
        }

@dataclass
class Course:
    subject: str
    number: str
    title: str
    credits_min: int
    credits_max: int
    gen_ed: list[str] = field(default_factory=list)
    source: str = "import"            # "import" or "manual"
    sections: list[Section] = field(default_factory=list)

    @property
    def code(self) -> str:
        return f"{self.subject} {self.number}"

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "subject": self.subject,
            "title": self.title,
            "credits_min": self.credits_min,
            "credits_max": self.credits_max,
            "gen_ed": self.gen_ed,
            "source": self.source,
            "sections": [s.to_dict() for s in self.sections],
        }

@dataclass
class Term:
    name: str
    start_date: str = ""
    end_date: str = ""
    courses: dict[str, Course] = field(default_factory=dict)

    def add_course(self, course: Course) -> None:
        self.courses[course.code] = course

    def get_course(self, code: str) -> Course | None:
        return self.courses.get(code)

    def to_dict(self) -> dict:
        return {"name": self.name, "start_date": self.start_date, "end_date": self.end_date}