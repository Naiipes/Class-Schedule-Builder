import { state, showPage, setShortlistUpdater, totalCredits, removeFromShortlist } from "./state.js";
import { setupCatalog, loadCatalog, showResults } from "./catalog.js";
import { setupSchedules, showShortlist } from "./schedules.js";

// nav tabs + "go to shortlist" button
document.addEventListener("click", (e) => {
  let button = e.target.closest("[data-page]");
  if (button) showPage(button.dataset.page);
});

function shortlistChanged() {
  document.getElementById("tab-count").textContent = state.shortlist.length;
  document.getElementById("side-credits").textContent = totalCredits();
  document.getElementById("side-empty").hidden = state.shortlist.length > 0;

  let sideList = document.getElementById("side-shortlist");
  sideList.innerHTML = "";
  for (let course of state.shortlist) {
    let li = document.createElement("li");
    li.textContent = course.code + " ";
    let x = document.createElement("button");
    x.className = "x-btn";
    x.textContent = "X";
    x.addEventListener("click", () => removeFromShortlist(course.code));
    li.appendChild(x);
    sideList.appendChild(li);
  }

  showResults(); // updates the add/remove buttons
  showShortlist();
}

setShortlistUpdater(shortlistChanged);
setupCatalog();
setupSchedules();
loadCatalog();
shortlistChanged();
showPage("catalog");
