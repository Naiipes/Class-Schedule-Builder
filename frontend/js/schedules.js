import { generateSchedules, exportIcs } from "./api.js";
import { state, showPage, meetingText } from "./state.js";

const DAYS = ["M", "T", "W", "R", "F"];
const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const START_HOUR = 8;
const END_HOUR = 21;
const PX_PER_HOUR = 48;
const COLORS = ["#cfe2ff", "#ffe0b3", "#d4f0d4", "#f9d0e0", "#e2d6f7", "#fff3b0", "#c9eef0"];

function toMinutes(time) {
  let parts = time.split(":");
  return Number(parts[0]) * 60 + Number(parts[1]);
}

export function setupSchedules() {
  document.getElementById("generate-btn").addEventListener("click", generate);
  document.getElementById("prev-btn").addEventListener("click", () => changeSchedule(-1));
  document.getElementById("next-btn").addEventListener("click", () => changeSchedule(1));
  document.getElementById("download-btn").addEventListener("click", downloadCalendar);
}

async function generate() {
  let error = document.getElementById("generate-error");
  error.textContent = "";

  let codes = state.shortlist.map((c) => c.code);
  try {
    state.schedules = await generateSchedules(codes, getPreferences());
    state.scheduleIndex = 0;
    showSchedule();
    showPage("schedules");
  } catch (err) {
    error.textContent = err.message;
  }
}

function getPreferences() {
  return {
    free_day: document.getElementById("free-day").value,
    earliest_start: document.getElementById("earliest-start").value,
    fewer_gaps: document.getElementById("fewer-gaps").checked,
  };
}

async function downloadCalendar() {
  let error = document.getElementById("download-error");
  error.textContent = "";

  let schedule = state.schedules[state.scheduleIndex];
  try {
    let file = await exportIcs(schedule);
    let url = URL.createObjectURL(file);

    let link = document.createElement("a");
    link.href = url;
    link.download = "schedule.ics";
    link.click();

    URL.revokeObjectURL(url);
  } catch (err) {
    error.textContent = err.message;
  }
}

function changeSchedule(step) {
  let newIndex = state.scheduleIndex + step;
  if (newIndex < 0 || newIndex >= state.schedules.length) return;
  state.scheduleIndex = newIndex;
  showSchedule();
}

function showSchedule() {
  let message = document.getElementById("schedule-message");
  let switcher = document.getElementById("schedule-switcher");
  let total = state.schedules.length;

  if (total === 0) {
    message.textContent = "No schedule works for these courses (some of them always overlap). Try removing one.";
    message.hidden = false;
    switcher.hidden = true;
    document.getElementById("calendar").innerHTML = "";
    document.getElementById("extra-classes").textContent = "";
    return;
  }

  let schedule = state.schedules[state.scheduleIndex];
  document.getElementById("download-error").textContent = "";
  message.hidden = true;
  switcher.hidden = false;

  document.getElementById("schedule-label").textContent =
    "Schedule " + (state.scheduleIndex + 1) + " of " + total +
    " (" + schedule.total_credits + " credits, score " + schedule.score + "/100)";
  document.getElementById("prev-btn").disabled = state.scheduleIndex === 0;
  document.getElementById("next-btn").disabled = state.scheduleIndex === total - 1;

  drawGrid(schedule);
  drawBlocks(schedule);
}

function lastHour(schedule) {
  let hour = END_HOUR;
  for (let s of schedule.sections) {
    for (let m of s.meetings) {
      hour = Math.max(hour, Math.ceil(toMinutes(m.end) / 60));
    }
  }
  return hour;
}

function drawGrid(schedule) {
  let calendar = document.getElementById("calendar");
  calendar.innerHTML = "";
  let endHour = lastHour(schedule);
  let gridHeight = (endHour - START_HOUR) * PX_PER_HOUR;

  let timeColumn = document.createElement("div");
  timeColumn.className = "time-column";
  timeColumn.innerHTML = '<div class="day-header"></div>';

  let hours = document.createElement("div");
  hours.className = "day-body hours";
  hours.style.height = gridHeight + "px";

  for (let h = START_HOUR; h < endHour; h++) {
    let label = document.createElement("div");
    label.className = "hour-label";
    label.style.top = (h - START_HOUR) * PX_PER_HOUR + "px";
    label.textContent = h + ":00";
    hours.appendChild(label);
  }

  timeColumn.appendChild(hours);
  calendar.appendChild(timeColumn);

  for (let i = 0; i < DAYS.length; i++) {
    let column = document.createElement("div");
    column.className = "day-column";

    let header = document.createElement("div");
    header.className = "day-header";
    header.textContent = DAY_NAMES[i];

    let body = document.createElement("div");
    body.className = "day-body";
    body.id = "day-" + DAYS[i];
    body.style.height = gridHeight + "px";
    body.style.backgroundSize = "100% " + PX_PER_HOUR + "px";

    column.appendChild(header);
    column.appendChild(body);
    calendar.appendChild(column);
  }
}

function drawBlocks(schedule) {
  let notOnGrid = [];

  schedule.sections.forEach((s, index) => {
    if (s.meetings.length === 0) {
      notOnGrid.push(s.code + " (online)");
      return;
    }

    for (let m of s.meetings) {
      let column = document.getElementById("day-" + m.day);
      if (!column) {
        notOnGrid.push(s.code + " (" + meetingText([m]) + ")");
        continue;
      }

      let start = toMinutes(m.start);
      let end = toMinutes(m.end);

      let block = document.createElement("div");
      block.className = "class-block";
      block.style.top = ((start - START_HOUR * 60) / 60) * PX_PER_HOUR + "px";
      block.style.height = ((end - start) / 60) * PX_PER_HOUR + "px";
      block.style.backgroundColor = COLORS[index % COLORS.length];

      let code = document.createElement("b");
      code.textContent = s.code;
      let time = document.createElement("div");
      time.textContent = m.start + "-" + m.end;
      let title = document.createElement("div");
      title.textContent = s.title;

      block.appendChild(code);
      block.appendChild(time);
      block.appendChild(title);
      column.appendChild(block);
    }
  });

  let extra = document.getElementById("extra-classes");
  extra.textContent = notOnGrid.length > 0 ? "Not on the grid: " + notOnGrid.join(", ") : "";
}
