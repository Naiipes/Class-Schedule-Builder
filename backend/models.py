class Term:
    """A semester in the catalog. Holds every Course offered that term"""


class Course:
    """A course in the catalog.
    Should have a code, title, credits, department, optional Gen Ed tag, and one or more Sections"""


class Section:
    """A specific offering of a course (the number).
    Should have an instructor and one or more meetings."""


class Meeting:
    """time slot for a section. 
    Should have a day, start time, and end time.
    A Section with a lab has more than one meeting, just like the Physics courses at tuj"""



