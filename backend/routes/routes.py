from flask import Blueprint, current_app, jsonify, request
from scheduler import generate_schedule, rank_schedules, schedule_to_dict
from catalog.manual import course_from_json
import re

MAX_CANDIDATES = 1000
TIME_PATTERN = re.compile(r"^\d{2}:\d{2}$")

api = Blueprint("api", __name__, url_prefix="/api")

def get_repo():
    return current_app.config.get("REPO")

@api.post("/courses")
def add_course():

    repo = get_repo()
    
    if repo is None:
        return jsonify(error="Catalog is not loaded"), 503

    body = request.get_json(silent=True) or {}

    try:
        course = course_from_json(body)
    except ValueError as error:
        return jsonify(error=str(error)), 400

    if not repo.add(course):
        return jsonify(error=f"Course {course.code} already exists"), 409

    return jsonify(course.to_dict()), 201

@api.get("/courses")
def list_courses():
    repo = get_repo()
    if repo is None:
        return jsonify(error="Catalog is not loaded"), 503

    credits = None
    credits_text = request.args.get("credits")

    if credits_text:
        try:
            credits = int(credits_text)
        except ValueError:
            return jsonify(error="credits must be a number"), 400

    courses = repo.search(
        q=request.args.get("q"),
        subject=request.args.get("subject"),
        credits=credits,
        gen_ed=request.args.get("gen_ed"),
    )

    return jsonify([course.to_dict() for course in courses])

@api.get("/courses/<code>")
def get_course(code):
    repo = get_repo()
    if repo is None:
        return jsonify(error="Catalog is not loaded"), 503

    course = repo.get(code.upper())

    if course is None:
        return jsonify(error=f"Course {code} not found"), 404

    return jsonify(course.to_dict())

@api.post("/schedules")
def create_schedule():
    repo = get_repo()

    if repo is None:
        return jsonify(error="Catalog is not loaded"), 503

    body = request.get_json(silent=True) or {}
    codes = body.get("courses") or []

    if not codes:
        return jsonify(error="Shortlist is empty"), 400

    try:
        limit = int(body.get("limit", 20))
    except (TypeError, ValueError):
        return jsonify(error="limit must be a number"), 400

    courses = []

    for code in codes:
        course = repo.get(code.upper())

        if course is None:
            return jsonify(error=f"Course {code} not found"), 404
        
        if course not in courses:
            courses.append(course)

    schedules = generate_schedule(courses, limit)

    preferences = body.get("preferences") or {}

    if not isinstance(preferences, dict):
        return jsonify(error="preferences must be an object"), 400

    free_day = preferences.get("free_day")

    if free_day is not None and free_day not in ["M", "T", "W", "R", "F"]:
        return jsonify(error="free_day must be one of M, T, W, R, F"), 400

    earliest_start = preferences.get("earliest_start")

    if earliest_start is not None and not TIME_PATTERN.match(str(earliest_start)):
        return jsonify(error="earliest_start must look like HH:MM"), 400

    fewer_gaps = preferences.get("fewer_gaps")

    if fewer_gaps is not None and not isinstance(fewer_gaps, bool):
        return jsonify(error="fewer_gaps must be true or false"), 400

    schedules = generate_schedule(courses, MAX_CANDIDATES)
    ranked = rank_schedules(schedules, preferences)

    result = []
    count = min(limit, len(ranked))
    
    for i in range(count):
        score, schedule = ranked[i]
        data = schedule_to_dict(i + 1, schedule)
        data["score"] = score
        result.append(data)

    return jsonify(result)