import random
import time
from catalog.csv_importer import CsvCatalogImporter
from scheduler import generate_schedule, rank_schedules

preferences = {"free_day": "F", "earliest_start": "10:00", "fewer_gaps": True}

def section_count(course):
    return len(course.sections)

def test_speed(courses, name, limit=None):
    start = time.time()
    schedules = generate_schedule(courses, limit)
    after_generate = time.time()

    rank_schedules(schedules, preferences)
    end = time.time()

    print(name)
    print("  schedules:", len(schedules))
    print("  generate time:", round(after_generate - start, 3), "s")
    print("  rank time:", round(end - after_generate, 3), "s")
    print("  total time:", round(end - start, 3), "s")

term = CsvCatalogImporter("data/TUJ_Spring2027_Courses.csv").load()

courses = list(term.courses.values())
courses.sort(key=section_count, reverse=True)

print("Courses with the most sections:")
for i in range(8):
    print(" ", courses[i].code, "-", len(courses[i].sections), "sections")

test_speed(courses[:8], "Worst case with limit 50000", 50000)
test_speed(courses[:5], "5 courses with the most sections")

courses_with_choice = []
for course in courses:
    if len(course.sections) >= 2:
        courses_with_choice.append(course)

random.seed(1)
slowest_time = 0
slowest_count = 0
hit_cap = 0

for i in range(100):
    shortlist = random.sample(courses_with_choice, 8)

    start = time.time()
    schedules = generate_schedule(shortlist, None)
    rank_schedules(schedules, preferences)
    time_taken = time.time() - start

    if len(schedules) > 50000:
        hit_cap += 1

    if time_taken > slowest_time:
        slowest_time = time_taken
        slowest_count = len(schedules)

print("100 random shortlists of 8 courses")
print("  slowest:", round(slowest_time, 3), "s with", slowest_count, "schedules")
print("  shortlists over the 50000 cap:", hit_cap)