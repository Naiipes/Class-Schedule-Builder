import { generateSchedules } from "./api.js";
import { state, showPage, removeFromShortlist, totalCredits, creditText, meetingText, toMinutes } from "./state.js";

const GRID_DAYS = ["M", "T", "W", "R", "F"];
const DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const START_HOUR = 8;
const END_HOUR = 21;
const PX_PER_HOUR = 48;

const COLORS = ["#cfe2ff", "#ffe0b3", "#d4f0d4", "#f9d0e0", "#e2d6f7", "#fff3b0", "#c9eef0"];

export function setupSchedules() {
  document.getElementById("generate-btn").addEventListener("click", generate);
  document.getElementById("prev-btn").addEventListener("click", () => changeSchedule(-1));
  document.getElementById("next-btn").addEventListener("click", () => changeSchedule(1));
}

// shortlist page
export function showShortlist() {
  let list = document.getElementById("shortlist");
  list.innerHTML = "";

  document.getElementById("shortlist-credits").textContent = totalCredits();
  document.getElementById("shortlist-empty").hidden = state.shortlist.length > 0;
  document.getElementById("generate-btn").disabled = state.shortlist.length === 0;

  for (let course of state.shortlist) {
    let card = document.createElement("div");
    card.className = "course-card course-top";

    let info = document.createElement("div");
    info.innerHTML = "<b></b><div class='gray small'></div>";
    info.querySelector("b").textContent = course.code + " " + course.title;
    info.querySelector("div").textContent = creditText(course) + " · " + course.sections.length + " section(s)";

    let removeBtn = document.createElement("button");
    removeBtn.className = "remove-btn";
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => removeFromShortlist(course.code));

    card.appendChild(info);
    card.appendChild(removeBtn);
    list.appendChild(card);
  }
}

async function generate() {
  let error = document.getElementById("generate-error");
  error.textContent = "";

  let codes = state.shortlist.map((c) => c.code);
  try {
    state.schedules = await generateSchedules(codes);
    state.scheduleIndex = 0;
    showSchedule();
    showPage("schedules");
  } catch (err) {
    error.textContent = err.message;
  }
}

// schedules page
function changeSchedule(step) {
  let newIndex = state.scheduleIndex + step;
  if (newIndex < 0 || newIndex >= state.schedules.length) return;
  state.scheduleIndex = newIndex;
  showSchedule();
}

export function showSchedule() {
  let message = document.getElementById("schedule-message");
  let switcher = document.getElementById("schedule-switcher");
  let calendar = document.getElementById("calendar");
  let extra = document.getElementById("extra-classes");

  if (state.schedules.length === 0) {
    message.textContent = "No schedule works for these courses (some of them always overlap). Try removing one.";
    message.hidden = false;
    switcher.hidden = true;
    calendar.innerHTML = "";
    extra.innerHTML = "";
    return;
  }

  let schedule = state.schedules[state.scheduleIndex];
  message.hidden = true;
  switcher.hidden = false;
  document.getElementById("schedule-label").textContent =
    "Schedule " + (state.scheduleIndex + 1) + " of " + state.schedules.length +
    " (" + schedule.total_credits + " credits)";
  document.getElementById("prev-btn").disabled = state.scheduleIndex === 0;
  document.getElementById("next-btn").disabled = state.scheduleIndex === state.schedules.length - 1;

  drawCalendar(schedule);
}

function drawCalendar(schedule) {
  let calendar = document.getElementById("calendar");
  calendar.innerHTML = "";

  // some classes end at 21:30 so make the grid taller if needed
  let endHour = END_HOUR;
  for (let s of schedule.sections) {
    for (let m of s.meetings) {
      endHour = Math.max(endHour, Math.ceil(toMinutes(m.end) / 60));
    }
  }
  let gridHeight = (endHour - START_HOUR) * PX_PER_HOUR;

  // hour labels
  let timeColumn = document.createElement("div");
  timeColumn.className = "time-column";
  timeColumn.innerHTML = '<div class="day-header"></div>';
  let hours = document.createElement("div");
  hours.className = "day-body hours";
  hours.style.height = gridHeight + "px";
  for (let h = START_HOUR; h <= endHour; h++) {
    let label = document.createElement("div");
    label.className = "hour-label";
    label.style.top = (h - START_HOUR) * PX_PER_HOUR + "px";
    label.textContent = h + ":00";
    hours.appendChild(label);
  }
  timeColumn.appendChild(hours);
  calendar.appendChild(timeColumn);

  let dayBodies = {};
  for (let i = 0; i < GRID_DAYS.length; i++) {
    let column = document.createElement("div");
    column.className = "day-column";

    let header = document.createElement("div");
    header.className = "day-header";
    header.textContent = DAY_HEADERS[i];

    let body = document.createElement("div");
    body.className = "day-body";
    body.style.height = gridHeight + "px";
    body.style.backgroundSize = "100% " + PX_PER_HOUR + "px";

    column.appendChild(header);
    column.appendChild(body);
    calendar.appendChild(column);
    dayBodies[GRID_DAYS[i]] = body;
  }

  let notOnGrid = []; // online classes and sat/sun meetings

  schedule.sections.forEach((s, index) => {
    let color = COLORS[index % COLORS.length];

    if (s.meetings.length === 0) {
      notOnGrid.push(s.code + " (online)");
      return;
    }

    for (let m of s.meetings) {
      if (!dayBodies[m.day]) {
        notOnGrid.push(s.code + " (" + meetingText([m]) + ")");
        continue;
      }

      let start = toMinutes(m.start);
      let end = toMinutes(m.end);

      let block = document.createElement("div");
      block.className = "class-block";
      block.style.top = ((start - START_HOUR * 60) / 60) * PX_PER_HOUR + "px";
      block.style.height = ((end - start) / 60) * PX_PER_HOUR + "px";
      block.style.background = color;

      let code = document.createElement("b");
      code.textContent = s.code;
      let time = document.createElement("div");
      time.className = "small";
      time.textContent = m.start + "-" + m.end;
      let title = document.createElement("div");
      title.textContent = s.title;

      block.appendChild(code);
      block.appendChild(time);
      block.appendChild(title);
      dayBodies[m.day].appendChild(block);
    }
  });

  let extra = document.getElementById("extra-classes");
  extra.textContent = notOnGrid.length > 0 ? "Not on the grid: " + notOnGrid.join(", ") : "";
}

