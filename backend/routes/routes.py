from flask import Blueprint, current_app, jsonify, request

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