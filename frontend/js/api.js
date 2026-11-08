const USE_MOCK = true;
const BASE_URL = "http://localhost:8000";

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
            results = results.filter((c) => c.title.toLowerCase().includes(q) || 
                                            c.sections.some((s) => s.instructor.toLowerCase().includes(q)) ||
                                            c.code.toLowerCase().includes(q));
        }

        return results;
    }

    const pairs = Object.entries(filters).filter(([key, value]) => value !== "" && value != null);
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

export async function generateSchedules(codes, limit = 20) {
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
        
        return MOCK_SCHEDULES.slice(0, limit);
    }

    return request("/api/schedules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ courses: codes, limit }),
    });
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
        section: "760",
        crn: "49421",
        instructor: "Michael E. Brady",
        meetings: [],
      },
    ],
  },
];

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
];
