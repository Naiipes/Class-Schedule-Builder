export let state = {
  shortlist: [],
};

// main.js sets this so the page redraws when the shortlist changes
export let updateShortlistUI = () => {};
export function setShortlistUpdater(fn) {
  updateShortlistUI = fn;
}

export function inShortlist(code) {
  for (let course of state.shortlist) {
    if (course.code === code) return true;
  }
  return false;
}

export function addToShortlist(course) {
  if (inShortlist(course.code)) return;
  state.shortlist.push(course);
  updateShortlistUI();
}

export function removeFromShortlist(code) {
  state.shortlist = state.shortlist.filter((c) => c.code !== code);
  updateShortlistUI();
}

export function totalCredits() {
  let total = 0;
  for (let course of state.shortlist) {
    total += course.credits_min; // backend also uses min for 1-4 credit courses
  }
  return total;
}

export function showPage(name) {
  for (let page of document.querySelectorAll(".page")) {
    page.hidden = page.id !== name + "-page";
  }
  for (let tab of document.querySelectorAll(".tab")) {
    tab.classList.toggle("active", tab.dataset.page === name);
  }
}

const DAY_NAMES = { M: "M", T: "T", W: "W", R: "Th", F: "F", S: "Sa", U: "Su" };

export function creditText(course) {
  if (course.credits_min === course.credits_max) {
    return course.credits_min + " credits";
  }
  return course.credits_min + "-" + course.credits_max + " credits";
}

// ex: "TTh 10:30-12:30"
export function meetingText(meetings) {
  if (meetings.length === 0) return "Online / TBA";

  let times = {};
  for (let m of meetings) {
    let key = m.start + "-" + m.end;
    if (!times[key]) times[key] = "";
    times[key] += DAY_NAMES[m.day];
  }

  let parts = [];
  for (let time in times) {
    parts.push(times[time] + " " + time);
  }
  return parts.join(", ");
}
