const USE_MOCK = false;
const BASE_URL = "";

async function request(path, options = {}) {
  const res = await fetch(BASE_URL + path, options);
  const body = await res.json();

  if (!res.ok) {
    throw new Error(body.error); // { error: "..." }
  }

  return body;
}

export async function getHealth() {
  if (USE_MOCK) {
    return { status: "ok", catalog: "found" };
  }

  const res = await fetch(BASE_URL + "/api/health");
  return res.json();
}

export async function getCourses(filters = {}) {
  if (USE_MOCK) {
    let results = MOCK_COURSES;

    if (filters.subject) {
      results = results.filter((c) => c.subject === filters.subject);
    }
    if (filters.gen_ed) {
      results = results.filter((c) => c.gen_ed.includes(filters.gen_ed));
    }
    if (filters.credits) {
      const credits = Number(filters.credits);
      results = results.filter((c) => c.credits_min <= credits && credits <= c.credits_max);
    }
    if (filters.q) {
      const q = filters.q.toLowerCase();
      results = results.filter(
        (c) =>
          c.title.toLowerCase().includes(q) ||
          c.sections.some((s) => s.instructor.toLowerCase().includes(q)) ||
          c.sections.some((s) => s.title.toLowerCase().includes(q)) ||
          c.code.toLowerCase().includes(q),
      );
    }

    return results;
  }

  const pairs = Object.entries(filters).filter(
    ([key, value]) => value !== "" && value != null,
  );
  const params = new URLSearchParams(pairs);
  return request(`/api/courses?${params}`);
}

export async function getCourse(code) {
  if (USE_MOCK) {
    const course = MOCK_COURSES.find((c) => c.code === code);

    if (!course) {
      throw new Error(`Course ${code} not found`);
    }

    return course;
  }

  return request(`/api/courses/${encodeURIComponent(code)}`);
}

export async function addCourse(course) {
  if (USE_MOCK) {
    const code = `${course.subject} ${course.number}`.toUpperCase();
    
    if (MOCK_COURSES.some((c) => c.code === code)) {
      throw new Error(`Course ${code} already exists`);
    }

    for (const s of course.sections) {
      for (const m of s.meetings ?? []) {
        if (m.start >= m.end) {
          throw new Error("Start must be before end");
        }
      }
    }

    const created = {
      code,
      subject: course.subject.toUpperCase(),
      title: course.title,
      credits_min: Number(course.credits),
      credits_max: Number(course.credits),
      gen_ed: [],
      source: "manual",
      sections: course.sections.map((s) => ({
        title: course.title,
        section: s.section,
        crn: null,
        instructor: s.instructor || "TBA",
        meetings: s.meetings ?? []
      }))
    }

    MOCK_COURSES.push(created);
    return created;
  }

  return request("/api/courses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(course)
  });
}

//-----------------------------------------------------------------------------
export async function generateSchedules(codes, preferences = {}, limit = 20) {
  if (USE_MOCK) {
    if (codes.length === 0) {
      throw new Error("Shortlist is empty");
    }

    for (let i = 0; i < codes.length; i++) {
      const course = MOCK_COURSES.find((c) => c.code === codes[i]);
      if (!course) {
        throw new Error(`Course ${codes[i]} not found`);
      }
    }

    const prefs = setPreferences(preferences);
    if (prefs.free_day && !"MTWRF".includes(prefs.free_day)) {
      throw new Error("Invalid free_day");
    }

    return MOCK_SCHEDULES
      .map((s) => ({ ...s, score: mockScore(s, prefs) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map((s, i) => ({ ...s, id: i + 1 }));
  }

  return request("/api/schedules", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ courses: codes, limit, preferences: setPreferences(preferences)}),
  });
}

function setPreferences(pref) {
  return {
    free_day: pref.free_day || null,
    earliest_start: pref.earliest_start || null,
    fewer_gaps: pref.fewer_gaps || null
  };
}

function mockScore(schedule, prefs) {
  const meetings = schedule.sections.flatMap((s) => s.meetings);
  let score = 100;

  if (prefs.free_day && meetings.some((m) => m.day === prefs.free_day)) {
    score -= 40;
  }
  if (prefs.earliest_start && meetings.some((m) => m.start < prefs.earliest_start)) {
    score -= 10;
  }

  return score;
}
//-----------------------------------------------------------------------------

export async function exportIcs(schedule) {
  const sections = schedule.sections.map((s) => ({ code: s.code, section: s.section }));

  if (USE_MOCK) {
    if (sections.length === 0) {
      throw new Error("No sections")
    }

    return new Blob([MOCK_ICS], { type: "text/calendar"});
  }

  const res = await fetch(BASE_URL + "/api/schedules/ics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sections })
  });
  if (!res.ok) {
    throw new Error((await res.json()).error);
  }

  return res.blob();
}

const MOCK_ICS = [
  "BEGIN:VCALENDAR",
  "VERSION:2.0",
  "PRODID:-//schedule-builder//mock//EN",
  "BEGIN:VEVENT",
  "UID:mock-1@schedule-builder",
  "DTSTAMP:20261116T000000Z",
  "DTSTART;TZID=Asia/Tokyo:20270112T103000",
  "DTEND;TZID=Asia/Tokyo:20270112T123000",
  "RRULE:FREQ=WEEKLY;BYDAY=TU,TH;UNTIL=20270421T145959Z",
  "SUMMARY:CIS 3296 Software Design (802)",
  "END:VEVENT",
  "END:VCALENDAR",
  "BEGIN:VTIMEZONE",
  "TZID:Asia/Tokyo",
  "BEGIN:STANDARD",
  "DTSTART:19700101T000000",
  "TZOFFSETFROM:+0900",
  "TZOFFSETTO:+0900",
  "TZNAME:JST",
  "END:STANDARD",
  "END:VTIMEZONE",
].join("\r\n");

export function downloadBlob(blob, filename = "schedule.ics") {
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url, download: filename });
  a.click();
  URL.revokeObjectURL(url);
}


// Mock data for testing the endpoints

const MOCK_COURSES = [
  {
    code: "CIS 3296",
    subject: "CIS",
    title: "Software Design",
    credits_min: 4,
    credits_max: 4,
    gen_ed: [],
    source: "import",
    sections: [
      {
        title: "Software Design",
        section: "802",
        crn: "56446",
        instructor: "Angela Faragasso",
        meetings: [
          { day: "T", start: "10:30", end: "12:30" },
          { day: "R", start: "10:30", end: "12:30" },
        ],
      },
    ],
  },
  {
    code: "ARTH 2000",
    subject: "ARTH",
    title: "History and Theory of Animation",
    credits_min: 1,
    credits_max: 4,
    gen_ed: [],
    source: "import",
    sections: [
      {
        title: "History and Theory of Animation",
        section: "750",
        crn: "55975",
        instructor: "Alexandra Schuch Pernau",
        meetings: [
          { day: "T", start: "10:30", end: "12:30" },
          { day: "R", start: "10:30", end: "12:30" },
        ],
      },
    ],
  },
  {
    code: "IH 0851",
    subject: "IH",
    title: "Intellectual Heritage I: The Good Life",
    credits_min: 3,
    credits_max: 3,
    gen_ed: ["Intellectual Heritage I"],
    source: "import",
    sections: [
      {
        title: "Intellectual Heritage I: The Good Life",
        section: "760",
        crn: "49421",
        instructor: "Michael E. Brady",
        meetings: [],
      },
    ],
  },
  {
    code: "ASST 2000",
    subject: "ASST",
    title: "Medieval and Early Modern Japanese Literature",
    credits_min: 2,
    credits_max: 4,
    gen_ed: [],
    source: "import",
    sections: [
      {
        title: "Medieval and Early Modern Japanese Literature",
        section: "801",
        crn: "51934",
        instructor: "Naohiko Umewaka",
        meetings: [
          { day: "T", start: "12:00", end: "13:30" },
          { day: "R", start: "12:00", end: "13:30" },
        ],
      },
      {
        title: "Ideology and Social Change in Japan",
        section: "802",
        crn: "58862",
        instructor: "Kyle L. Cleveland",
        meetings: [
          { day: "T", start: "17:00", end: "18:30" },
          { day: "R", start: "17:00", end: "18:30" },
        ],
      },
    ],
  },
];

// sample input to test addCourse()
export const MOCK_NEW_COURSE = {
  subject: "CIS",
  number: "1234",
  title: "Title",
  credits: 4,
  sections: [
    {
      section: "777",
      instructor: "John Bob",
      meetings: [
        { day: "T", start: "10:00", end: "11:00" },
        { day: "R", start: "10:00", end: "11:00" },
      ],
    },
  ],
};

const MOCK_SCHEDULES = [
  {
    id: 1,
    total_credits: 7,
    sections: [
      {
        code: "CIS 3296",
        title: "Software Design",
        section: "802",
        crn: "56446",
        instructor: "Angela Faragasso",
        meetings: [
          { day: "T", start: "10:30", end: "12:30" },
          { day: "R", start: "10:30", end: "12:30" },
        ],
      },
      {
        code: "IH 0851",
        title: "Intellectual Heritage I: The Good Life",
        section: "760",
        crn: "49421",
        instructor: "Michael E. Brady",
        meetings: [],
      },
    ],
  },
  {
    id: 2,
    total_credits: 5,
    sections: [
      {
        code: "ASST 2000",
        title: "Ideology and Social Change in Japan",
        section: "802",
        crn: "58862",
        instructor: "Kyle L. Cleveland",
        meetings: [
          { day: "T", start: "17:00", end: "18:30" },
          { day: "R", start: "17:00", end: "18:30" },
        ],
      },
      {
        code: "IH 0851",
        title: "Intellectual Heritage I: The Good Life",
        section: "760",
        crn: "49421",
        instructor: "Michael E. Brady",
        meetings: [],
      },
    ],
  },
];

