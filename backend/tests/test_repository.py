from catalog.repository import matches_text, CatalogRepository
from catalog.csv_importer import CsvCatalogImporter
from models import Course, Term, Section
import pytest
from pathlib import Path

# matches_text

def test_matches_code():
    assert matches_text(Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4), "CIS 3296")

def test_matches_course_title():
    assert matches_text(Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4), "Software Design")

def test_matches_instructor():
    assert matches_text(
        Course(subject="CIS", 
               number="3296", 
               title="Software Design", 
               credits_min=4, 
               credits_max=4, 
               sections=[
                   Section(section="777", crn="12345", instructor="Angela Faragasso")
                ]), "Angela Faragasso")

def test_matches_section_title():
    assert matches_text(
        Course(subject="ASST", 
               number="3000", 
               title="Politics of India", 
               credits_min=3, 
               credits_max=3, 
               sections=[
                   Section(section="801", title="Politics of India"),
                   Section(section="802", title="Korean Politics")
                ]), "Korean Politics")    

def test_match_is_case_insensitive():
    assert matches_text(Course(subject="CIS", number="3223", title="Data Structures and Algorithms", credits_min=3, credits_max=3), "data structures and algorithms")

def test_match_is_partial():
    assert matches_text(Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4), "soft")

def test_no_match_returns_false():
    assert not matches_text(Course(subject="CIS", number="3296", title="Software Design", credits_min=4, credits_max=4), "CIS 3223")


# search() with single filters

@pytest.fixture 
def repo():
    term = Term("Spring 2027")
    term.add_course(Course(subject="CIS", number="3296", title="Software Design",
                           credits_min=4, credits_max=4))
    term.add_course(Course(subject="ENG", number="0857", title="The Detective Novel",
                           credits_min=3, credits_max=3, gen_ed=["Global/World Society"]))
    term.add_course(Course(subject="ARTU", number="2400", title="Special Topics",
                           credits_min=1, credits_max=3))
    return CatalogRepository(term)


def test_search_with_no_filters_returns_all_courses(repo):
    codes = [course.code for course in repo.search()]

    assert codes == ["ARTU 2400", "CIS 3296", "ENG 0857"]

def test_search_by_text_returns_only_matches(repo):
    codes = [course.code for course in repo.search(q="software")]

    assert codes == ["CIS 3296"]

def test_filter_by_subject_returns_only_that_subject(repo):
    codes = [course.code for course in repo.search(subject="ARTU")]

    assert codes == ["ARTU 2400"]

def test_filter_by_subject_is_case_insensitive(repo):
    codes = [course.code for course in repo.search(subject="artu")]

    assert codes == ["ARTU 2400"]

def test_filter_by_credits_exact_value(repo):
    codes = [course.code for course in repo.search(credits=4)]

    assert codes == ["CIS 3296"]

def test_filter_by_credits_inside_range(repo):
    codes = [course.code for course in repo.search(credits=2)]

    assert codes == ["ARTU 2400"]

def test_filter_by_credits_at_range_edges(repo):
    lower = [course.code for course in repo.search(credits=1)]
    upper = [course.code for course in repo.search(credits=3)]

    assert lower == ["ARTU 2400"]
    assert upper == ["ARTU 2400", "ENG 0857"]

def test_filter_by_gen_ed(repo):
    codes = [course.code for course in repo.search(gen_ed="Global/World Society")]

    assert codes == ["ENG 0857"]

def test_course_without_gen_ed_excluded_by_gen_ed_filter(repo):
    codes = [course.code for course in repo.search(gen_ed="Global/World Society")]

    assert "CIS 3296" not in codes
    assert "ARTU 2400" not in codes


# search() with combined filters + results

@pytest.fixture
def combined_repo():
    term = Term("Spring 2027")
    term.add_course(Course(subject="ENG", number="2001", title="Software and Society",
                           credits_min=3, credits_max=3, gen_ed=["Human Behavior"]))
    term.add_course(Course(subject="CIS", number="3296", title="Software Design",
                           credits_min=4, credits_max=4))
    term.add_course(Course(subject="CIS", number="1002", title="Software Ethics",
                           credits_min=4, credits_max=4, gen_ed=["Science & Technology"]))
    term.add_course(Course(subject="CIS", number="2168", title="Data Structures",
                           credits_min=4, credits_max=4))
    term.add_course(Course(subject="CIS", number="1001", title="Software in Everyday Life",
                           credits_min=3, credits_max=3, gen_ed=["Science & Technology"]))
    return CatalogRepository(term)

def test_text_and_subject_filters_combine_with_and(combined_repo):
    codes = [course.code for course in combined_repo.search(q="software", subject="CIS")]

    assert codes == ["CIS 1001", "CIS 1002", "CIS 3296"]

def test_all_filters_combined(combined_repo):
    codes = [course.code for course in combined_repo.search(
        q="software", subject="CIS", credits=3, gen_ed="Science & Technology")]

    assert codes == ["CIS 1001"]

def test_no_results_returns_empty_list(combined_repo):
    assert combined_repo.search(subject="CIS", gen_ed="Human Behavior") == []

def test_results_are_sorted_by_code(combined_repo):
    codes = [course.code for course in combined_repo.search()]

    assert codes == ["CIS 1001", "CIS 1002", "CIS 2168", "CIS 3296", "ENG 2001"]


# get()

def test_get_returns_course_by_code(combined_repo):
    course = combined_repo.get("CIS 3296")

    assert course.code == "CIS 3296"
    
def test_get_unknown_code_returns_none(combined_repo):
    assert combined_repo.get("CIS 9999") is None


# add()

def test_add_new_course_returns_true(repo):
    course = Course(subject="MATH", number="1041", title="Calculus I",
                    credits_min=4, credits_max=4, source="manual")

    assert repo.add(course) is True

def test_added_course_can_be_found_by_get_and_search(repo):
    course = Course(subject="MATH", number="1041", title="Calculus I",
                    credits_min=4, credits_max=4, source="manual")
    repo.add(course)

    assert repo.get("MATH 1041") is course
    assert [c.code for c in repo.search(q="calculus")] == ["MATH 1041"]

def test_add_duplicate_code_returns_false(repo):
    duplicate = Course(subject="CIS", number="3296", title="Another Title",
                       credits_min=3, credits_max=3, source="manual")

    assert repo.add(duplicate) is False

def test_add_duplicate_does_not_replace_original(repo):
    original = repo.get("CIS 3296")
    duplicate = Course(subject="CIS", number="3296", title="Another Title",
                       credits_min=3, credits_max=3, source="manual")

    repo.add(duplicate)

    assert repo.get("CIS 3296") is original
    assert repo.get("CIS 3296").title == "Software Design" 


# TUJ CSV file

REAL_CSV = Path(__file__).parent.parent / "data" / "TUJ_Spring2027_Courses.csv"

@pytest.fixture(scope="module") # scope="module" shares the catalog with all tests in this file (loaded only once)
def real_repo():
    return CatalogRepository(CsvCatalogImporter(REAL_CSV).load())

def test_real_catalog_search_accounting_returns_only_acct(real_repo):
    results = real_repo.search(q="accounting")

    assert [course.code for course in results] == ["ACCT 2103", "ACCT 2501", "ACCT 2521"]
    assert all(course.subject == "ACCT" for course in results)

def test_real_catalog_filter_cis_returns_only_cis(real_repo):
    results = real_repo.search(subject="CIS")

    assert len(results) > 0
    assert all(course.subject == "CIS" for course in results)
