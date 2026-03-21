(() => {
  const root = document.getElementById("dashboard-root");
  if (!root) {
    return;
  }

  const grid = document.getElementById("calendar-grid");
  const title = document.getElementById("calendar-title");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const todayBtn = document.getElementById("today-btn");
  const monthBtn = document.getElementById("view-month");
  const weekBtn = document.getElementById("view-week");
  const todayLabel = document.getElementById("today-label");
  const selectedLabel = document.getElementById("selected-date-label");
  const activitiesList = document.getElementById("activities-list");
  const activitiesEmpty = document.getElementById("activities-empty");
  const dataNode = document.getElementById("calendar-data");

  if (!grid || !title || !prevBtn || !nextBtn || !todayBtn || !monthBtn || !weekBtn || !selectedLabel || !activitiesList || !activitiesEmpty || !dataNode) {
    return;
  }

  const calendarItems = JSON.parse(dataNode.textContent || "[]");
  const selectedIso = root.dataset.selectedDate || "";

  const today = new Date();
  let view = "month";
  let current = new Date(today.getFullYear(), today.getMonth(), 1);
  let selected = selectedIso ? new Date(selectedIso + "T00:00:00") : new Date(today);

  function monthTitle(date) {
    const text = date.toLocaleDateString("es-AR", { month: "long", year: "numeric" });
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function dateKey(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function formatDate(date) {
    const dd = String(date.getDate()).padStart(2, "0");
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const yyyy = date.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
  }

  function startOfWeek(date) {
    const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    d.setDate(d.getDate() - d.getDay());
    d.setHours(0, 0, 0, 0);
    return d;
  }

  function clearGrid() {
    while (grid.firstChild) {
      grid.removeChild(grid.firstChild);
    }
  }

  function itemsByDate(key) {
    return calendarItems.filter((item) => item.date === key);
  }

  function appendItems(cell, key) {
    const items = itemsByDate(key);
    const limit = 2;

    items.slice(0, limit).forEach((item) => {
      const tag = document.createElement("div");
      tag.className = "calendar-item";
      tag.textContent = item.label;
      cell.appendChild(tag);
    });

    if (items.length > limit) {
      const more = document.createElement("div");
      more.className = "calendar-empty";
      more.textContent = `+${items.length - limit} mas`;
      cell.appendChild(more);
    }

    if (items.length === 0) {
      const empty = document.createElement("div");
      empty.className = "calendar-empty";
      empty.textContent = "Sin turnos";
      cell.appendChild(empty);
    }
  }

  function renderActivities() {
    const key = dateKey(selected);
    const items = itemsByDate(key);
    activitiesList.innerHTML = "";

    if (items.length === 0) {
      activitiesEmpty.classList.remove("d-none");
      return;
    }

    activitiesEmpty.classList.add("d-none");

    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "activity-card";

      const titleEl = document.createElement("div");
      titleEl.className = "fw-semibold";
      titleEl.textContent = item.label;

      const meta = document.createElement("div");
      meta.className = "text-muted small";
      meta.textContent = `Estado: ${item.estado}`;

      card.appendChild(titleEl);
      card.appendChild(meta);
      activitiesList.appendChild(card);
    });
  }

  function buildDayCell(date, isSunday) {
    const cell = document.createElement("div");
    cell.className = "calendar-cell";

    if (isSunday) {
      cell.classList.add("sunday");
    }

    const span = document.createElement("div");
    span.className = "calendar-day";
    span.textContent = String(date.getDate());

    const key = dateKey(date);

    if (key === dateKey(today)) {
      cell.classList.add("calendar-today");
    }
    if (key === dateKey(selected)) {
      cell.classList.add("calendar-selected");
    }

    cell.appendChild(span);
    appendItems(cell, key);

    cell.addEventListener("click", () => {
      selected = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      selectedLabel.textContent = formatDate(selected);
      render();
    });

    return cell;
  }

  function renderMonth() {
    clearGrid();
    const year = current.getFullYear();
    const month = current.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startOffset = firstDay.getDay();
    const totalCells = Math.ceil((startOffset + lastDay.getDate()) / 7) * 7;

    title.textContent = monthTitle(current);

    for (let i = 0; i < totalCells; i++) {
      const dayNumber = i - startOffset + 1;
      if (dayNumber > 0 && dayNumber <= lastDay.getDate()) {
        const date = new Date(year, month, dayNumber);
        grid.appendChild(buildDayCell(date, i % 7 === 0));
      } else {
        const empty = document.createElement("div");
        empty.className = "calendar-cell";
        if (i % 7 === 0) {
          empty.classList.add("sunday");
        }
        grid.appendChild(empty);
      }
    }
  }

  function renderWeek() {
    clearGrid();
    const start = startOfWeek(current);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);

    title.textContent = `Semana ${formatDate(start)} - ${formatDate(end)}`;

    for (let i = 0; i < 7; i++) {
      const date = new Date(start);
      date.setDate(start.getDate() + i);
      grid.appendChild(buildDayCell(date, i === 0));
    }
  }

  function render() {
    if (view === "month") {
      renderMonth();
    } else {
      renderWeek();
    }
    renderActivities();
  }

  function setView(nextView) {
    view = nextView;
    monthBtn.classList.toggle("active", view === "month");
    weekBtn.classList.toggle("active", view === "week");

    if (view === "month") {
      current = new Date(current.getFullYear(), current.getMonth(), 1);
    } else {
      current = startOfWeek(selected);
    }

    render();
  }

  monthBtn.addEventListener("click", () => {
    setView("month");
  });

  weekBtn.addEventListener("click", () => {
    setView("week");
  });

  prevBtn.addEventListener("click", () => {
    if (view === "month") {
      current = new Date(current.getFullYear(), current.getMonth() - 1, 1);
    } else {
      current.setDate(current.getDate() - 7);
    }
    render();
  });

  nextBtn.addEventListener("click", () => {
    if (view === "month") {
      current = new Date(current.getFullYear(), current.getMonth() + 1, 1);
    } else {
      current.setDate(current.getDate() + 7);
    }
    render();
  });

  todayBtn.addEventListener("click", () => {
    selected = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    if (view === "month") {
      current = new Date(today.getFullYear(), today.getMonth(), 1);
    } else {
      current = startOfWeek(today);
    }
    selectedLabel.textContent = formatDate(selected);
    render();
  });

  todayLabel.textContent = `Hoy es: ${formatDate(today)}`;
  selectedLabel.textContent = formatDate(selected);
  render();
})();
