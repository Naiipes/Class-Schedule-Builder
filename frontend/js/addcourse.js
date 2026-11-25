import { addCourse } from "./api.js";
import { loadCatalog } from "./catalog.js";

let addedCourses = [];

export function setupAddCourse() {
  addMeetingRow();
  document.getElementById("add-meeting").addEventListener("click", addMeetingRow);
  document.getElementById("clear-btn").addEventListener("click", clearForm);
  document.getElementById("add-form").addEventListener("submit", submitCourse);
  showAddedList();
}

function addMeetingRow() {
  let row = document.createElement("div");
  row.className = "meeting-row";
  row.innerHTML = `
    <button type="button" class="day" data-day="M">M</button>
    <button type="button" class="day" data-day="T">T</button>
    <button type="button" class="day" data-day="W">W</button>
    <button type="button" class="day" data-day="R">Th</button>
    <button type="button" class="day" data-day="F">F</button>
    <input type="time" class="start" />
    <span>to</span>
    <input type="time" class="end" />
    <button type="button" class="x-btn">X</button>
  `;

  for (let dayButton of row.querySelectorAll(".day")) {
    dayButton.addEventListener("click", () => dayButton.classList.toggle("selected"));
  }

  row.querySelector(".x-btn").addEventListener("click", () => {
    row.remove();
    if (document.getElementById("meetings").children.length === 0) {
      addMeetingRow();
    }
  });

  document.getElementById("meetings").appendChild(row);
}

function getMeetings() {
  let meetings = [];

  for (let row of document.querySelectorAll(".meeting-row")) {
    let start = row.querySelector(".start").value;
    let end = row.querySelector(".end").value;
    let days = [];
    for (let button of row.querySelectorAll(".day.selected")) {
      days.push(button.dataset.day);
    }

    if (days.length === 0 && start === "" && end === "") continue;

    if (days.length === 0) throw new Error("Pick at least one day for each meeting");
    if (start === "" || end === "") throw new Error("Each meeting needs a start and end time");
    if (start >= end) throw new Error("Start time has to be before end time");

    for (let day of days) {
      meetings.push({ day: day, start: start, end: end });
    }
  }

  return meetings;
}

function clearForm() {
  document.getElementById("add-form").reset();
  document.getElementById("meetings").innerHTML = "";
  addMeetingRow();
  document.getElementById("add-error").textContent = "";
}

async function submitCourse(e) {
  e.preventDefault();
  let error = document.getElementById("add-error");
  let success = document.getElementById("add-success");
  error.textContent = "";
  success.textContent = "";

  let subject = document.getElementById("add-subject").value.trim();
  let number = document.getElementById("add-number").value.trim();
  let title = document.getElementById("add-title").value.trim();
  let credits = document.getElementById("add-credits").value;
  let section = document.getElementById("add-section").value.trim();
  let instructor = document.getElementById("add-instructor").value.trim();

  try {
    if (!subject || !number || !title || credits === "" || !section) {
      throw new Error("Please fill in subject, course number, credits, title and section");
    }

    let course = await addCourse({
      subject: subject,
      number: number,
      title: title,
      credits: Number(credits),
      sections: [
        {
          section: section,
          instructor: instructor,
          meetings: getMeetings(),
        },
      ],
    });

    addedCourses.push(course);
    showAddedList();
    clearForm();
    success.textContent = course.code + " was added to the catalog.";
    loadCatalog();
  } catch (err) {
    error.textContent = err.message;
  }
}

function showAddedList() {
  let list = document.getElementById("added-list");
  list.innerHTML = "";
  document.getElementById("added-empty").hidden = addedCourses.length > 0;

  for (let course of addedCourses) {
    let li = document.createElement("li");
    li.textContent = course.code + " " + course.title;
    list.appendChild(li);
  }
}
