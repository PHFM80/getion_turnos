// JS especifico de la pagina de inicio.
(() => {
  const filter = document.querySelector("[data-rubro-filter]");
  const cards = document.querySelectorAll("[data-rubro-card]");

  if (!filter || !cards.length) {
    return;
  }

  const applyFilter = () => {
    const value = filter.value;
    cards.forEach((card) => {
      const rubro = card.getAttribute("data-rubro");
      const show = value === "all" || rubro === value;
      card.style.display = show ? "block" : "none";
    });
  };

  filter.addEventListener("change", applyFilter);
  applyFilter();
})();

(() => {
  const slots = document.querySelectorAll("[data-turno-slot]");
  const form = document.querySelector("[data-turno-form]");
  const fechaInput = document.getElementById("turno-fecha");
  const horaInput = document.getElementById("turno-hora");
  const message = document.querySelector("[data-turno-message]");

  if (!slots.length || !form || !fechaInput || !horaInput) {
    return;
  }

  const setActive = (slot) => {
    slots.forEach((btn) => btn.classList.remove("active"));
    slot.classList.add("active");
    fechaInput.value = slot.getAttribute("data-fecha") || "";
    horaInput.value = slot.getAttribute("data-hora") || "";
  };

  slots.forEach((slot) => {
    slot.addEventListener("click", () => setActive(slot));
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!fechaInput.value || !horaInput.value) {
      if (message) {
        message.textContent = "Selecciona un horario antes de solicitar el turno.";
      }
      return;
    }
    if (message) {
      message.textContent = "Turno solicitado. Nos comunicaremos para confirmar.";
    }
    form.reset();
    fechaInput.value = "";
    horaInput.value = "";
    slots.forEach((btn) => btn.classList.remove("active"));
  });
})();
