# API - Class Schedule Builder (Sprint 2)

Errors should look like this: 
```json
{ "error": "Shortlist is empty" }
```

## JSON Structure

### Term
 
```json
{ 
    "name": "Spring 2027", 
    "start_date": "2027-01-12", 
    "end_date": "2027-04-21" 
}
```
- `start_date` / `end_date`: ISO format (YYYY-MM-DD), taken from the most common `Start Date` and `End Date` in the catalog file. Used for the .ics export.

---

### Course
 
```json
{
  "code": "CIS 3296",
  "subject": "CIS",
  "title": "Software Design",
  "credits_min": 4,
  "credits_max": 4,
  "gen_ed": [],
  "source": "import",
  "sections": [ Section, ... ]
}
```

- `title`: for special topics courses, this is the first section's title. Use the section's `title` when showing a specific section.
- `code` = `subject` + `course number`. Keep leading zeros (`ENG 0711`)
- `gen_ed`: list of Gen Ed names, e.g. `["Science & Technology"]`. Empty if none.
- `source`: `"import"` (from the catalog CSV) or `"manual"` (added with `POST /api/courses`).

---

### Section
 
```json
{
  "title": "Software Design",
  "section": "802",
  "crn": "56446",
  "instructor": "Angela Faragasso",
  "meetings": [ Meeting, ... ]
}
```
 
- `title` is the title of this section. Usually the same as the course's `title`,
  but "special topics" courses have a different title per section
  (e.g. ASST 3000: "Politics of India" and "Korean Politics").
- `crn` is `null` for courses added manually.
- `instructor` is `"TBA"` when the catalog has none.
- `meetings` is an empty list for asynchronous courses.

---

### Meeting
 
```json
{ "day": "T", "start": "12:50", "end": "14:50" }
```
 
- `day`: one of `M T W R F S U` (R = Thursday, U = Sunday). One object per day.
- `start` / `end`: 24-hour `HH:MM`.

### Overlap rule
 
Two meetings overlap only if they are on the same day **and** `a.start < b.end` **and** `b.start < a.end`.
A class ending at 12:20 and one starting at 12:20 do **not** overlap.
Example:
- **A** = 10:00–12:20, **B** = 12:20–13:30
- `a.start` < `b.end` → 10:00 < 13:30 ✓
- `b.start` < `a.end` → 12:20 < 12:20 ✗ (equal, not less)
Both conditions must be true, so there’s no clash.

- Sections with no meetings (online/TBA) never conflict.

---

### Schedule

```json
{
  "id": 1,
  "score": 67,
  "total_credits": 8,
  "sections": [ ScheduledSection, ... ]
}
```

- `id`: schedule number (1..n). The list is sorted by `score`, so 1 is the best match. Numbers are reassigned on every request.
- `score`: integer from 0 to 100, higher is better. It is always present. With no preferences every schedule scores `100`.

- One section per shortlisted course; no two meetings overlap.
- Each item is a Section plus its course's `code`, so the weekly view can label the blocks with `code` and the section's `title`.
- `total_credits` is the total credits of the schedule. For courses with a credit range, the minimum is used (e.g. `1-4` counts as 1).
 
### Preferences

```json
{
  "free_day": "F",
  "earliest_start": "10:00",
  "fewer_gaps": true
}
```

All fields are optional. A field that is missing or `null` means "no preference".

| Field | Type | Meaning | Valid values |
|---|---|---|---|
| `free_day` | string | Prefer schedules with no class on this day | one of `M T W R F` |
| `earliest_start` | string | Prefer schedules with no class starting before this time | 24-hour `HH:MM` |
| `fewer_gaps` | boolean | Prefer schedules with less idle time between classes on the same day | `true` / `false` |

- A class starting exactly at `earliest_start` is not early (for `"10:00"`, a 10:00 class is fine and a 9:59 class is early).
- Sections with no meetings (online/TBA) are ignored by every preference.
- `fewer_gaps: false` is treated the same as leaving it out.

---

### Scoring

The backend decides how each preference is weighted. The frontend and tests can rely on these rules:

- `score` is an integer from 0 to 100, and higher is better.
- Schedules are sorted by `score` from highest to lowest.
- A schedule with a class on `free_day` scores lower than an otherwise similar schedule without one.
- With no preferences, every schedule scores `100` and the order is the same as before.
- Ranking covers all generated schedules, not only the first `limit`. The top `limit` are returned after sorting.

## Endpoints

| Method | URL | Sends | Returns |
|---|---|---|---|
| GET | /api/health | – | 200 `{ "status": "ok", "catalog": "found" }` or 503 `{ "status": "error", "catalog": "missing" }` |
| GET | /api/courses | query params (below) | 200, list of Course |
| GET | /api/courses/<code> | – | 200, one Course · 404 if unknown |
| POST | /api/courses | JSON body (below) | 201, the new Course |
| POST | /api/schedules | JSON body (below) | 200, list of Schedule (sorted by `score`) |
| POST | /api/schedules/ics | JSON body (below) | 200, `.ics` file (`text/calendar`) |

Every endpoint returns 503 `{ "error": "Catalog is not loaded" }` if the catalog file is missing.

### GET /api/courses

All parameters are optional and combine with AND. No parameters returns every course.

| Param | Example | Matches |
|---|---|---|
| `q` | `accounting` | code, course or section title, or instructor (case-insensitive, partial) |
| `subject` | `CIS` | exact subject |
| `credits` | `4` | `credits_min <= credits <= credits_max` |
| `gen_ed` | `Science & Technology` | course has this Gen Ed |

Example: `GET /api/courses?q=design&subject=CIS`

Errors: 400 `{ "error": "credits must be a number" }`

### GET /api/courses/<code>

The code contains a space, so the frontend URL-encodes it: `/api/courses/CIS%203296`.

Errors: 404 `{ "error": "Course CIS 9999 not found" }`

### POST /api/courses

Adds a course by hand. It shows up in `GET /api/courses` right away with `"source": "manual"`. It is kept in memory only, so it is gone after the server restarts.

Request:
```json
{
  "subject": "CIS",
  "number": "1234",
  "title": "Title of a class",
  "credits": 3,
  "sections": [
    {
      "section": "007",
      "instructor": "James Bond",
      "meetings": [
        { "day": "T", "start": "10:00", "end": "11:20" },
        { "day": "R", "start": "10:00", "end": "11:20" }
      ]
    }
  ]
}
```
- `subject`, `number`, `title`: required. `subject` and `number` are upper-cased.
- `credits`: required whole number. It is stored as both `credits_min` and `credits_max`.
- `sections`: at least one. `section` is required. `instructor` is optional (default `"TBA"`). `meetings` is optional (empty = online/TBA).
- Each meeting follows the Meeting format. `crn` is always `null`.

Response: 201, the created Course.

Errors: 400 if a field is missing or invalid (e.g. `{ "error": "Start must be before end" }`), 409 if the course already exists. Show `error` under the form as-is.

### POST /api/schedules

Request:
```json
{
  "courses": ["CIS 3296", "ACCT 2103", "ENG 0711"],
  "limit": 20,
  "preferences": { "free_day": "F", "earliest_start": "10:00", "fewer_gaps": true }
}
```
- `courses`: list of course codes (the shortlist). Required.
- `limit`: max schedules returned. Optional, default 20.
- `preferences`: a Preferences object. Optional. If you leave it out, or send `{}` or `null`, you get the Sprint 1 behaviour (every `score` is 100).

Response: list of Schedule, sorted by `score` from highest to lowest, with `id` 1..n in that order. `[]` if no conflict-free schedule exists (this is not an error).

Errors: 400 for an empty shortlist, an invalid `limit` or invalid preferences. 404 for an unknown course.

### POST /api/schedules/ics

Turns one schedule into an iCalendar file. The frontend sends only the course code and section number of each section. The backend looks up the meeting times in the catalog itself, so the export cannot get different times from what the catalog has.

Request:
```json
{
  "sections": [
    { "code": "CIS 3296", "section": "802" },
    { "code": "ACCT 2103", "section": "001" }
  ]
}
```
- `sections`: required, non-empty. Use the `code` and `section` of each item in `Schedule.sections`.

Response: 200 with the file body (not JSON).
```
Content-Type: text/calendar; charset=utf-8
Content-Disposition: attachment; filename="schedule.ics"
```

What is inside the file:
- One weekly recurring event (`RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=...`) per meeting.
- The first event is on the first matching weekday on or after `Term.start_date`. The last one is on or before `Term.end_date`.
- Times are Japan time (`TZID=Asia/Tokyo`), so Google Calendar and Apple Calendar show the same clock times as the catalog.
- `SUMMARY`: `"<code> <section title>"`, e.g. `CIS 3296 Software Design`.
- `DESCRIPTION`: instructor (if any).
- Sections with no meetings are skipped.

Errors (JSON, like the other endpoints): 400 if `sections` is missing, empty or malformed. 404 for an unknown course or section.

