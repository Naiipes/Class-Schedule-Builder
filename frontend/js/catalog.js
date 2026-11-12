import { getCourses } from "./api.js";
import { inShortlist, addToShortlist, removeFromShortlist, creditText, meetingText } from "./state.js";

// "" = all
let filters = { q: "", subject: "", credits: "", gen_ed: "" };
let currentResults = [];
let openCourses = [];

export function setupCatalog() {
  // wait till they stop typing
  let timer = null;
  document.getElementById("search").addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      filters.q = document.getElementById("search").value.trim();
      search();
    }, 300);
  });

  makeFilterButtons("credit-buttons", ["1", "2", "3", "4"], "credits");

  document.getElementById("gen-ed").addEventListener("change", (e) => {
    filters.gen_ed = e.target.value;
    search();
  });
}

export async function loadCatalog() {
  let allCourses = await getCourses();

  let subjects = [];
  let genEds = [];
  for (let course of allCourses) {
    if (!subjects.includes(course.subject)) subjects.push(course.subject);
    for (let g of course.gen_ed) {
      if (!genEds.includes(g)) genEds.push(g);
    }
  }
  subjects.sort();
  genEds.sort();

  makeFilterButtons("dept-buttons", subjects, "subject");

  let select = document.getElementById("gen-ed");
  select.innerHTML = '<option value="">All</option>';
  for (let g of genEds) {
    let option = document.createElement("option");
    option.value = g;
    option.textContent = g;
    select.appendChild(option);
  }

  search();
}

function makeFilterButtons(containerId, values, filterName) {
  let container = document.getElementById(containerId);
  container.innerHTML = "";

  let allValues = [""].concat(values);
  for (let value of allValues) {
    let btn = document.createElement("button");
    btn.className = "filter-btn";
    btn.textContent = value === "" ? "All" : value;
    if (filters[filterName] === value) btn.classList.add("selected");

    btn.addEventListener("click", () => {
      filters[filterName] = value;
      for (let b of container.children) b.classList.remove("selected");
      btn.classList.add("selected");
      search();
    });

    container.appendChild(btn);
  }
}

async function search() {
  try {
    currentResults = await getCourses(filters);
    showResults();
  } catch (err) {
    document.getElementById("result-count").textContent = "Error: " + err.message;
  }
}

export function showResults() {
  let count = currentResults.length;
  document.getElementById("result-count").textContent = count + (count === 1 ? " course found" : " courses found");

  let results = document.getElementById("results");
  results.innerHTML = "";

  if (currentResults.length === 0) {
    results.innerHTML = '<p class="gray">No courses match your search.</p>';
    return;
  }

  for (let course of currentResults) {
    results.appendChild(makeCourseCard(course));
  }
}

function makeCourseCard(course) {
  let card = document.createElement("div");
  card.className = "course-card";

  let isOpen = openCourses.includes(course.code);
  let added = inShortlist(course.code);

  let top = document.createElement("div");
  top.className = "course-top";

  let info = document.createElement("div");
  let name = document.createElement("b");
  name.textContent = course.code + " " + course.title;
  let details = document.createElement("div");
  details.className = "gray small";
  details.textContent = creditText(course) + " · " + course.sections.length + " section(s)";
  if (course.gen_ed.length > 0) details.textContent += " · Gen Ed: " + course.gen_ed.join(", ");
  info.appendChild(name);
  info.appendChild(details);

  let buttons = document.createElement("div");
  buttons.className = "course-buttons";

  let sectionsBtn = document.createElement("button");
  sectionsBtn.textContent = isOpen ? "Hide sections" : "Show sections";
  sectionsBtn.addEventListener("click", () => {
    if (isOpen) {
      openCourses = openCourses.filter((c) => c !== course.code);
    } else {
      openCourses.push(course.code);
    }
    card.replaceWith(makeCourseCard(course));
  });

  let addBtn = document.createElement("button");
  if (added) {
    addBtn.textContent = "Remove";
    addBtn.className = "remove-btn";
    addBtn.addEventListener("click", () => removeFromShortlist(course.code));
  } else {
    addBtn.textContent = "Add";
    addBtn.className = "add-btn";
    addBtn.addEventListener("click", () => addToShortlist(course));
  }

  buttons.appendChild(sectionsBtn);
  buttons.appendChild(addBtn);
  top.appendChild(info);
  top.appendChild(buttons);
  card.appendChild(top);

  if (isOpen) {
    card.appendChild(makeSectionsTable(course));
  }
  return card;
}

function makeSectionsTable(course) {
  let table = document.createElement("table");
  table.innerHTML = "<tr><th>Section</th><th>Instructor</th><th>Meeting</th></tr>";

  for (let s of course.sections) {
    let row = document.createElement("tr");
    let title = "";
    // special topics have different titles per section
    if (s.title !== course.title) title = " (" + s.title + ")";

    for (let text of [s.section + title, s.instructor, meetingText(s.meetings)]) {
      let td = document.createElement("td");
      td.textContent = text;
      row.appendChild(td);
    }
    table.appendChild(row);
  }
  return table;
}
