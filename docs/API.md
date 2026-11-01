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
- `total_credits` is the sum of `credits_min`
 

## Endpoints (to be decided)

| Method | URL | Sends | Returns |
|---|---|---|---|
| GET | /api/health | – | `{ "status": "ok", "catalog": "found" }` or 503 |
| GET | /api/courses | ? | list of Course |
| GET | /api/courses/<code> | – | one Course |
| POST | /api/schedules | ? | list of Schedule |
