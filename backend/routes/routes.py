from flask import Blueprint, current_app, jsonify, request
from scheduler import generate_schedule, schedule_to_dict

api = Blueprint("api", __name__, url_prefix="/api")

def get_repo():
    return current_app.config.get("REPO")

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
    result = []

    for i in range(len(schedules)):
        schedule_id = i + 1
        result.append(schedule_to_dict(schedule_id, schedules[i]))

    return jsonify(result)