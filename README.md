## Class Schedule Builder
A web app where a student searches a course catalog (TUJ Spring 2027) or adds courses by hand, builds a shortlist of up to eight courses, and gets conflict-free schedules ranked by their preferences, shown on a weekly grid.

## Team Members

| Member         | GitHub       |
|----------------|--------------|
| Otavio Seki    | @Naiipes     |
| Andrei Ushakov | @0xume       |
| Kody K. Wong   | @kodywong1   |

## Unfinished Features
- **Manual entry UI**
- **Preferences and ranking UI**
- **Calendar export (`.ics`)**
- **Tests** for ranking (`score_schedule`, `rank_schedules`), preference validation, manual entry validation, and export
- **Performance measurements** (requirement N1) on one test computer

## Report sections still to be completed
- 1 Abstract: sentence on `.ics` export
- 5.3 UML Class Diagram: update the diagram 
- 5.4 Sequence Diagram: update the diagram 
- 6.2 Implementation: manual entry UI, preferences UI, candidate limit paragraph, and calendar export
- 7.1 Resources: test computer specs
- 8.1 Completion status: update the "In progress" rows
- 8.2 Testing and Results: updated test results and performance results
- 8.3 Limitations: reasons for features not completed by November 26
- 9.1 Summary of Achievements: final state of the unfinished features

## Setup after cloning

### 1. Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

Then open http://localhost:8000 in your browser.

### Next time
You only need to activate the environment and run the app:
```bash
source .venv/bin/activate     
python app.py
```
