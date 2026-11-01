# API - Class Schedule Builder (Sprint 1)

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
- `code` = `subject` + `course number`. Keep leading zeros (`ENG 0711`)
- `gen_ed`: list of Gen Ed names, e.g. `["Science & Technology"]`. Empty if none.
- `source`: `"import"` or `"manual"`. (Not used in Sprint 1)

---

### Section
 
```json
{
  "section": "802",
  "crn": "56446",
  "instructor": "Angela Faragasso",
  "meetings": [ Meeting, ... ]
}
```
 
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
  "total_credits": 8,
  "sections": [ ScheduledSection, ... ]
}
```

- One section per shortlisted course; no two meetings overlap.
- Each item is a Section plus its course's `code` and `title`, so the weekly view can label the blocks.
- `total_credits` is the total credits of the schedule. For courses with a credit range, the minimum is used (e.g. `1-4` counts as 1).
 
## Endpoints

| Method | URL | Sends | Returns |
|---|---|---|---|
| GET | /api/health | – | 200 `{ "status": "ok", "catalog": "found" }` or 503 `{ "status": "error", "catalog": "missing" }` |
| GET | /api/courses | query params (below) | 200, list of Course |
| GET | /api/courses/<code> | – | 200, one Course · 404 if unknown |
| POST | /api/schedules | JSON body (below) | 200, list of Schedule |

### GET /api/courses

All parameters are optional and combine with AND. No parameters returns every course.

| Param | Example | Matches |
|---|---|---|
| `q` | `accounting` | code, title or instructor (case-insensitive, partial) |
| `subject` | `CIS` | exact subject |
| `credits` | `4` | `credits_min <= credits <= credits_max` |
| `gen_ed` | `Science & Technology` | course has this Gen Ed |

Example: `GET /api/courses?q=design&subject=CIS`

Errors: 400 `{ "error": "credits must be a number" }`

### GET /api/courses/<code>

The code contains a space, so the frontend URL-encodes it: `/api/courses/CIS%203296`.

Errors: 404 `{ "error": "Course CIS 9999 not found" }`

### POST /api/schedules

Request:
```json
{ "courses": ["CIS 3296", "ACCT 2103", "ENG 0711"], "limit": 20 }
```
- `courses`: list of course codes (the shortlist). Required.
- `limit`: max schedules returned. Optional, default 20.

Response: list of Schedule. `[]` if no conflict-free schedule exists (this is not an error).

Errors:
- 400 `{ "error": "Shortlist is empty" }`
- 404 `{ "error": "Course XYZ 1234 not found" }`