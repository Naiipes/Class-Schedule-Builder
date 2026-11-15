from catalog.csv_importer import parse_meetings, parse_gen_ed, parse_credits, clean_text, to_iso, most_common_date, CsvCatalogImporter
from models import Meeting
import pytest
from pathlib import Path

# parse_meetings

def test_two_day_class_gives_one_meeting_per_day():
    assert parse_meetings("TR", "10:30-12:30") == [Meeting("T", "10:30", "12:30"), Meeting("R", "10:30", "12:30")]

def test_three_day_class_keeps_day_order():
    assert parse_meetings("MWF", "13:40-15:40") == [Meeting("M", "13:40", "15:40"), Meeting("W", "13:40", "15:40"), Meeting("F", "13:40", "15:40")]

def test_day_groups_with_different_times():
    assert parse_meetings("T; R", "13:40-15:40 ; 10:00-11:00") == [Meeting("T", "13:40", "15:40"), Meeting("R", "10:00", "11:00")]

def test_repeated_identical_groups_are_removed():
    assert parse_meetings("T; T", "10:00-11:00 ; 10:00-11:00") == [Meeting("T", "10:00", "11:00")]

def test_no_days_gives_no_meetings():
    assert parse_meetings("", "10:00-11:00") == []


# parse_credits

def test_single_credit_value():
    assert parse_credits("1") == (1, 1)

def test_credit_range():
    assert parse_credits("1-4") == (1, 4)

def test_non_number_credits_raise_error():
    with pytest.raises(ValueError):
        parse_credits("a-b")


# parse_gen_ed

def test_keeps_only_gen_ed_attributes():
    assert parse_gen_ed("GenEd Quantitative Literacy; Writing Intensive") == ["Quantitative Literacy"]

def test_gen_ed_html_entities_are_unescaped():
    assert parse_gen_ed("GenEd Science &amp; Technology") == ["Science & Technology"]

def test_non_gen_ed_attributes_gives_empty_list():
    assert parse_gen_ed("Writing Intensive") == []

def test_empty_attributes_give_empty_list():
    assert parse_gen_ed("") == []


# clean_text

def test_clean_text_unescapes_html_entities():
    assert clean_text("Gender/Sexuality/Women&#39;s St") == "Gender/Sexuality/Women's St"

def test_clean_text_collapses_extra_spaces():
    assert clean_text("Hello        World") == "Hello World"

def test_clean_text_strips_leading_and_trailing_spaces():
    assert clean_text("       hello world            ") == "hello world"


# to_iso and most_common_date

def test_to_iso_converst_us_date():
    assert to_iso("12/25/2026") == "2026-12-25"

def test_most_common_date_picks_most_frequent():
    rows = [
        {"Start Date": "03/02/2027"},
        {"Start Date": "01/12/2027"},
        {"Start Date": "01/12/2027"}
    ]
    assert most_common_date(rows, "Start Date") == "2027-01-12"

def test_most_common_date_ignores_blank_dates():
    rows = [
        {"Start Date": ""},
        {"Start Date": ""},
        {"Start Date": "12/12/2012"}
    ]
    assert most_common_date(rows, "Start Date") == "2012-12-12"

def test_most_common_date_all_blank_gives_empty_string():
    rows = [
        {"Start Date": ""},
        {"Start Date": ""}
    ]
    assert most_common_date(rows, "Start Date") == ""


# CsvCatalogImporter.load() with small CSV in tmp_path

HEADER = "Subject,Course Number,Section,CRN,Title,Credits,Days,Times,Instructor,Start Date,End Date,Attributes"

# helper
def write_csv(tmp_path, *rows):
    path = tmp_path / "courses.csv"
    path.write_text("\n".join([HEADER, *rows]) + "\n", encoding="utf-8")
    return path

def test_rows_with_the_same_code_become_one_course(tmp_path):
    path = write_csv(tmp_path,
        "ACCT,2103,801,58565,Accounting,4,MWF,13:30-14:50,Sunqian Ren,01/12/2027,04/21/2027,",
        "ACCT,2103,802,54078,Accounting,4,TR,10:30-12:30,David Sigaty,01/12/2027,04/21/2027,",
    )

    term = CsvCatalogImporter(path).load()

    assert list(term.courses) == ["ACCT 2103"]
    course = term.get_course("ACCT 2103")
    assert [section.section for section in course.sections] == ["801", "802"]

def test_course_code_keeps_leading_zeros(tmp_path):
    path = write_csv(tmp_path,
        "BIOL,0848,750,58196,DNA: Friend or Foe,3,TR,15:20-16:50,Zeidan Hala,01/12/2027,04/21/2027,",
    )

    term = CsvCatalogImporter(path).load()

    course = term.get_course("BIOL 0848")
    assert course is not None
    assert course.number == "0848"

def test_blank_crn_becomes_none(tmp_path):
    path = write_csv(tmp_path,
        "ACCT,2103,801,,Accounting,4,MWF,13:30-14:50,Sunqian Ren,01/12/2027,04/21/2027,",
    )

    course = CsvCatalogImporter(path).load().get_course("ACCT 2103")

    assert course.sections[0].crn is None

def test_blank_instructor_becomes_tba(tmp_path):
    path = write_csv(tmp_path,
        "ACCT,2103,801,58565,Accounting,4,MWF,13:30-14:50,   ,01/12/2027,04/21/2027,",
    )

    course = CsvCatalogImporter(path).load().get_course("ACCT 2103")

    assert course.sections[0].instructor == "TBA"

def test_online_row_is_kept_with_no_meetings(tmp_path):
    path = write_csv(tmp_path,
        "ADV,0853,750,49752,Advertising and Globalization,3,,,John K. Foster,01/12/2027,04/21/2027,",
    )

    course = CsvCatalogImporter(path).load().get_course("ADV 0853")

    assert course is not None
    assert len(course.sections) == 1
    assert course.sections[0].meetings == []

def test_course_gets_credits_and_gen_ed_from_row(tmp_path):
    path = write_csv(tmp_path,
        "CHEM,0821,750,49528,Chemistry of Wine,1-4,TR,19:10-20:40,Haniyeh Bidadi,01/12/2027,04/21/2027,"
        "GenEd Science &amp; Technology; Writing Intensive",
    )

    course = CsvCatalogImporter(path).load().get_course("CHEM 0821")

    assert course.credits_min == 1
    assert course.credits_max == 4
    assert course.gen_ed == ["Science & Technology"]

def test_term_dates_are_set(tmp_path):
    path = write_csv(tmp_path,
        "ACCT,2103,801,58565,Accounting,4,MWF,13:30-14:50,Sunqian Ren,03/02/2027,04/02/2027,",
        "ACCT,2103,802,54078,Accounting,4,TR,10:30-12:30,David Sigaty,01/12/2027,04/21/2027,",
        "ACCT,2103,803,54079,Accounting,4,TR,13:30-15:30,David Sigaty,01/12/2027,04/21/2027,",
    )

    term = CsvCatalogImporter(path).load()

    assert term.start_date == "2027-01-12"
    assert term.end_date == "2027-04-21"


# testing .load but now with the real TUJ file

REAL_CSV = Path(__file__).parent.parent / "data" / "TUJ_Spring2027_Courses.csv"

@pytest.fixture(scope="module")
def real_term():
    return CsvCatalogImporter(REAL_CSV).load()

def test_real_catalog_loads_all_500_sections(real_term):
    total = sum(len(course.sections) for course in real_term.courses.values())

    assert total == 500

def test_acct_2103_has_3_sections(real_term):
    course = real_term.get_course("ACCT 2103")

    assert [section.section for section in course.sections] == ["801", "802", "803"]

def test_acct_2103_section_801_meets_mwf_1330_1450(real_term):
    course = real_term.get_course("ACCT 2103")
    section = next(s for s in course.sections if s.section == "801")

    assert section.meetings == [
        Meeting("M", "13:30", "14:50"),
        Meeting("W", "13:30", "14:50"),
        Meeting("F", "13:30", "14:50"),
    ]
