# Class Schedule Builder

A web app where a student searches a course catalog (TUJ Spring 2027) or adds courses by hand, builds a shortlist of up to eight courses, and gets conflict-free schedules ranked by their preferences, shown on a weekly grid. A chosen schedule can be exported as an iCalendar (`.ics`) file.

## Team Members

| Member         | GitHub       |
|----------------|--------------|
| Otavio Seki    | @Naiipes     |
| Andrei Ushakov | @0xume       |
| Kody K. Wong   | @kodywong1   |

## Requirements

- **Python 3.13** 
- **Optional:** Docker and Docker Compose, to run the app without installing Python packages

Python dependencies are listed in `backend/requirements.txt`: Flask, gunicorn, and pytest.

## Setup and Running

### Option 1: Docker

From the repository root:

```bash
docker compose up --build
```

Then open http://localhost:8000. Stop the app with `Ctrl+C`.

Next time, you only need to run:
```bash
docker compose up
```

### Option 2: Local Python environment

**1. Create and activate a virtual environment** (from the repository root)

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**2. Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**3. Run the app** (from `backend/`)
```bash
python app.py
```

Then open http://localhost:8000.

Next time, you only need to activate the environment and run `python app.py` from `backend/`.

## Running the Tests

From `backend/`, with the virtual environment active:

```bash
python -m pytest
```

All 225 tests should pass. They cover the data model and overlap rule, the CSV importer, search, schedule generation, ranking, manual entry, calendar export, and the API routes. GitHub Actions runs the same tests on every push and pull request to `main`.

### Performance benchmark

```bash
python benchmark.py
```

Prints the time to generate and rank schedules for the heaviest request, a complete search, and 100 random shortlists, and how many random shortlists reach the 50,000 candidate limit.

## Project Structure

```
backend/
  app.py              Flask app: loads the catalog and serves the front end
  models.py           Term, Course, Section, Meeting
  scheduler.py        Schedule generation and ranking
  calendar_export.py  .ics export
  benchmark.py        Performance benchmark
  catalog/            CSV importer, repository, manual entry validation
  routes/             API routes
  data/               TUJ Spring 2027 catalog (CSV)
  tests/              pytest tests
frontend/             HTML, CSS, and JavaScript (catalog, shortlist, schedules)
docs/API.md           API contract
```

## Known Issues and Limitations

- **Candidate limit:** at most 50,000 schedules are generated and ranked per request. For shortlists with more valid schedules (mostly those with several courses without meeting times), the results are the best among the 50,000 evaluated, not of all valid schedules. In 100 random 8-course shortlists, none reached the limit.
- **Sections without meeting times** (online asynchronous, internships, independent study) never conflict and are listed under the grid instead of on it.
- **One-time data:** the catalog is a copy of TUJ's Spring 2027 data downloaded once; later changes to sections are not reflected.
- **CSV format:** the importer expects the column names of Temple's registration export.
- **Time zone:** exported calendars always use Asia/Tokyo.
- **Shortlist limit:** the eight-course limit is enforced by the front end only; the API accepts longer shortlists.
- **Preferences:** only one free day can be chosen.
- **No conflict explanation:** when no schedule fits, the app does not say which courses conflict.
- **Not included:** seat availability, prerequisites, CSV upload by the student, user accounts, and saving schedules inside the app (future work).
- **Manual courses are not saved:** courses added by hand are kept in memory and are lost when the app restarts.