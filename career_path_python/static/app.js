(function () {
  "use strict";

  let skills = [];
  let interests = [];
  let paths = [];
  let selectedPathId = null;
  let progress = {};

  function setupTagInput(boxId, inputId, arr) {
    const box = document.getElementById(boxId);
    const input = document.getElementById(inputId);
    function render() {
      box.querySelectorAll(".chip").forEach((c) => c.remove());
      arr.forEach((val, i) => {
        const chip = document.createElement("span");
        chip.className = "chip";
        const label = document.createElement("span");
        label.textContent = val;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.setAttribute("aria-label", "Remove " + val);
        btn.textContent = "\u00d7";
        btn.onclick = () => { arr.splice(i, 1); render(); };
        chip.appendChild(label);
        chip.appendChild(btn);
        box.insertBefore(chip, input);
      });
    }
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === ",") {
        e.preventDefault();
        const v = input.value.trim().replace(/,$/, "");
        if (v && !arr.includes(v)) { arr.push(v); render(); }
        input.value = "";
      } else if (e.key === "Backspace" && input.value === "" && arr.length) {
        arr.pop(); render();
      }
    });
    input.addEventListener("blur", () => {
      const v = input.value.trim();
      if (v && !arr.includes(v)) { arr.push(v); render(); }
      input.value = "";
    });
    render();
    return render;
  }
  const renderSkills = setupTagInput("skills-box", "skills-input", skills);
  const renderInterests = setupTagInput("interests-box", "interests-input", interests);

  function escapeHtml(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
    } catch (e) { return ""; }
  }

  const resultsSection = document.getElementById("results-section");
  const pathsList = document.getElementById("paths-list");
  const journeySection = document.getElementById("journey-section");
  const journeyCard = document.getElementById("journey-card");

  function renderPaths() {
    pathsList.innerHTML = "";
    if (!paths.length) { resultsSection.hidden = true; return; }
    resultsSection.hidden = false;
    paths.forEach((p) => {
      const el = document.createElement("div");
      el.className = "path";
      const isSelected = p.id === selectedPathId;
      const skillsHtml = (p.skillsToDevelop || []).map((s) => `<span class="skill-pill">${escapeHtml(s)}</span>`).join("");
      const stepsHtml = (p.learningPath || []).map((s, i) => `
        <div class="step">
          <div class="marker">${i + 1}</div>
          <p class="step-title">${escapeHtml(s.title)}</p>
          <p class="step-desc">${escapeHtml(s.description)}</p>
          ${s.estWeeks ? `<p class="step-weeks">~${escapeHtml(String(s.estWeeks))} week${s.estWeeks == 1 ? "" : "s"}</p>` : ""}
        </div>`).join("");

      el.innerHTML = `
        <h3 class="path-role"><span class="dot"></span>${escapeHtml(p.role)}</h3>
        <p class="path-reason">${escapeHtml(p.matchReason)}</p>
        <div class="skills-list">${skillsHtml}</div>
        <div class="steps">${stepsHtml}</div>
        <button class="btn ${isSelected ? "secondary" : ""} small follow-btn" type="button">
          ${isSelected ? "Following this path" : "Follow this path"}
        </button>`;

      el.querySelector(".follow-btn").addEventListener("click", async () => {
        selectedPathId = p.id;
        renderPaths();
        renderJourney();
        await fetch("/api/select-path", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path_id: p.id }),
        });
        journeySection.scrollIntoView({ behavior: "smooth", block: "start" });
      });

      pathsList.appendChild(el);
    });
  }

  function renderJourney() {
    const p = paths.find((x) => x.id === selectedPathId);
    if (!p) { journeySection.hidden = true; return; }
    journeySection.hidden = false;

    const steps = p.learningPath || [];
    const doneCount = steps.filter((s) => progress[s.id]).length;
    const pct = steps.length ? Math.round((doneCount / steps.length) * 100) : 0;

    const rows = steps.map((s) => {
      const done = !!progress[s.id];
      return `
        <label class="check-step ${done ? "done" : ""}">
          <input type="checkbox" data-step-id="${s.id}" ${done ? "checked" : ""}>
          <span>
            <div class="t">${escapeHtml(s.title)}</div>
            <div class="d">${escapeHtml(s.description)}</div>
            ${done ? `<div class="done-date">Completed ${formatDate(progress[s.id])}</div>` : ""}
          </span>
        </label>`;
    }).join("");

    journeyCard.innerHTML = `
      <div class="journey-head">
        <span class="journey-role">${escapeHtml(p.role)}</span>
        <span class="progress-pct">${pct}% underway</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
      ${rows}
      <div class="nudge-box">
        <button class="btn secondary small" id="nudge-btn" type="button">Get a nudge</button>
        <div id="nudge-text"></div>
      </div>`;

    journeyCard.querySelectorAll('input[type="checkbox"]').forEach((cb) => {
      cb.addEventListener("change", async () => {
        const id = cb.getAttribute("data-step-id");
        if (cb.checked) progress[id] = new Date().toISOString();
        else delete progress[id];
        renderJourney();
        await fetch("/api/progress", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ step_id: id, completed: cb.checked }),
        });
      });
    });

    document.getElementById("nudge-btn").addEventListener("click", async () => {
      const btn = document.getElementById("nudge-btn");
      const box = document.getElementById("nudge-text");
      btn.disabled = true;
      box.innerHTML = '<div class="nudge-text">Thinking&hellip;</div>';
      try {
        const res = await fetch("/api/nudge", { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "failed");
        box.innerHTML = `<div class="nudge-text">${escapeHtml(data.text)}</div>`;
      } catch (e) {
        box.innerHTML = '<div class="nudge-text">Couldn\u2019t get a nudge right now — try again shortly.</div>';
      } finally {
        btn.disabled = false;
      }
    });
  }

  const chartBtn = document.getElementById("chart-btn");
  const loadingRow = document.getElementById("loading-row");
  const formError = document.getElementById("form-error");

  chartBtn.addEventListener("click", async () => {
    formError.hidden = true;
    if (skills.length === 0 && interests.length === 0) {
      formError.textContent = "Add at least one skill or interest so we have something to work from.";
      formError.hidden = false;
      return;
    }
    const experience = document.getElementById("experience-select").value;
    const goals = document.getElementById("goals-input").value.trim();

    chartBtn.disabled = true;
    loadingRow.hidden = false;

    try {
      const res = await fetch("/api/recommend", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skills, interests, experience, goals }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      paths = data.paths;
      selectedPathId = null;
      progress = {};
      renderPaths();
      renderJourney();
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (e) {
      formError.textContent = e.message || "Couldn't chart your path just now — try again in a moment.";
      formError.hidden = false;
    } finally {
      chartBtn.disabled = false;
      loadingRow.hidden = true;
    }
  });

  async function init() {
    try {
      const res = await fetch("/api/state");
      const state = await res.json();
      if (state && state.profile) {
        (state.profile.skills || []).forEach((s) => skills.push(s));
        (state.profile.interests || []).forEach((s) => interests.push(s));
        renderSkills(); renderInterests();
        if (state.profile.experience) document.getElementById("experience-select").value = state.profile.experience;
        if (state.profile.goals) document.getElementById("goals-input").value = state.profile.goals;
      }
      if (state && Array.isArray(state.paths) && state.paths.length) {
        paths = state.paths;
        selectedPathId = state.selected_path_id;
        progress = state.progress || {};
        renderPaths();
        renderJourney();
      }
    } catch (e) { /* fresh session, nothing to restore */ }
  }
  init();
})();
