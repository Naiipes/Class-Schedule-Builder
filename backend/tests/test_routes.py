from app import app
from catalog.repository import CatalogRepository
from models import Course, Meeting, Section, Term
import pytest


# helpers ------------------------------------------------------------------------------------------------------------------
def make_term() -> Term:
    term = Term(name="Test")
    term.add_course(Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4, sections=[
        Section(section="01", meetings=[Meeting(day="T", start="10:30", end="12:30"), Meeting(day="R", start="10:30", end="12:30")]),
        Section(section="02", meetings=[Meeting(day="T", start="08:00", end="10:00"), Meeting(day="R", start="10:30", end="12:30")]),
    ]))
    term.add_course(Course(subject="MATH", number="1041", title="Calculus I", credits_min=4, credits_max=4, sections=[
        Section(section="01", meetings=[Meeting(day="T", start="08:00", end="09:00")]),
    ]))
    return term

def new_course_body() -> dict:
    return {
        "subject": "art",
        "number": "1001",
        "title": "Drawing",
        "credits": 3,
        "sections": [{"section": "01", "meetings": [{"day": "W", "start": "09:00", "end": "10:00"}]}],
    }

@pytest.fixture
def client():
    original = app.config.get("REPO")
    app.config["REPO"] = CatalogRepository(make_term())
    yield app.test_client()
    app.config["REPO"] = original

@pytest.fixture
def client_no_catalog():
    original = app.config.get("REPO")
    app.config["REPO"] = None # sets repo to None for the 503 case
    yield app.test_client()
    app.config["REPO"] = original
# --------------------------------------------------------------------------------------------------------------------------


# POST /api/schedules

def test_create_schedule_returns_schedules_with_ids_starting_at_1(client):
    response = client.post("/api/schedules", json={"courses": ["CIS 3296", "MATH 1041"]})
    assert response.status_code == 200
    data = response.get_json()
    assert [s["id"] for s in data] == [1, 2]
    assert [s["total_credits"] for s in data] == [8, 8]
    assert [sec["code"] for sec in data[0]["sections"]] == ["CIS 3296", "MATH 1041"]

def test_create_schedule_with_empty_shortlist_returns_400(client):
    assert client.post("/api/schedules", json={"courses": []}).status_code == 400

def test_create_schedule_with_non_numeric_limit_returns_400(client):
    response = client.post("/api/schedules", json={"courses": ["CIS 3296"], "limit": "infinite"})
    assert response.status_code == 400

def test_create_schedule_with_unknown_course_returns_404(client):
    response = client.post("/api/schedules", json={"courses": ["CIS 3296", "HIST 9999"]})
    assert response.status_code == 404

def test_create_schedule_accepts_lowercase_codes(client):
    response = client.post("/api/schedules", json={"courses": ["cis 3296"]})
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_create_schedule_ignores_duplicate_codes(client):
    response = client.post("/api/schedules", json={"courses": ["CIS 3296", "cis 3296"]})
    assert response.status_code == 200
    for schedule in response.get_json():
        assert len(schedule["sections"]) == 1

def test_create_schedule_without_catalog_returns_503(client_no_catalog):
    response = client_no_catalog.post("/api/schedules", json={"courses": ["CIS 3296"]})
    assert response.status_code == 503


# GET /api/courses

def test_list_courses_returns_all_courses_sorted_by_code(client):
    response = client.get("/api/courses")
    assert response.status_code == 200
    assert [c["code"] for c in response.get_json()] == ["CIS 3296", "MATH 1041"]

def test_list_courses_applies_filters(client):
    response = client.get("/api/courses?subject=math")
    assert [c["code"] for c in response.get_json()] == ["MATH 1041"]

def test_list_courses_with_non_numeric_credits_returns_400(client):
    assert client.get("/api/courses?credits=three").status_code == 400


# GET /api/courses/<code>

def test_get_course_returns_course(client):
    response = client.get("/api/courses/CIS 3296")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Software Design"

def test_get_unknown_course_returns_404(client):
    assert client.get("/api/courses/HIST 9999").status_code == 404

def test_get_course_accepts_lowercase_code(client):
    assert client.get("/api/courses/math 1041").status_code == 200


# POST /api/courses

def test_add_course_returns_201_with_course(client):
    response = client.post("/api/courses", json=new_course_body())
    assert response.status_code == 201
    data = response.get_json()
    assert data["code"] == "ART 1001"
    assert data["source"] == "manual"

def test_add_course_with_invalid_body_returns_400(client):
    body = new_course_body()
    del body["title"]
    assert client.post("/api/courses", json=body).status_code == 400
    assert client.post("/api/courses", json={}).status_code == 400

def test_add_duplicate_course_returns_409(client):
    body = new_course_body()
    body["subject"], body["number"] = "CIS", "3296"
    assert client.post("/api/courses", json=body).status_code == 409

def test_added_course_can_be_fetched(client):
    client.post("/api/courses", json=new_course_body())
    response = client.get("/api/courses/ART 1001")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Drawing"
