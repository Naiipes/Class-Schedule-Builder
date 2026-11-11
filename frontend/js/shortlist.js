import { state, removeFromShortlist, totalCredits, creditText } from "./state.js";

export function showShortlist() {
  let list = document.getElementById("shortlist");
  list.innerHTML = "";

  document.getElementById("shortlist-credits").textContent = totalCredits();
  document.getElementById("shortlist-empty").hidden = state.shortlist.length > 0;

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
