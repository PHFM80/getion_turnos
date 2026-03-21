// JS especifico del dashboard.
(() => {
  if (!window.bootstrap || !window.bootstrap.Tooltip) {
    return;
  }
  const tooltipTriggerList = document.querySelectorAll("[data-bs-toggle='tooltip']");
  tooltipTriggerList.forEach((triggerEl) => {
    // eslint-disable-next-line no-new
    new window.bootstrap.Tooltip(triggerEl);
  });
})();

(() => {
  const lists = document.querySelectorAll("[data-filter-list]");

  lists.forEach((list) => {
    const selectId = list.getAttribute("data-filter-select");
    const select = document.getElementById(selectId);
    if (!select) {
      return;
    }

    const items = Array.from(list.querySelectorAll(".complemento-item"));
    const emptyState = list.querySelector("[data-filter-empty]");

    const updateList = () => {
      const value = select.value;
      let visible = 0;

      items.forEach((item) => {
        const parentId = item.getAttribute("data-parent-id");
        const show = value && parentId === value;
        item.style.display = show ? "block" : "none";
        if (show) {
          visible += 1;
        }
      });

      if (emptyState) {
        if (!value) {
          emptyState.style.display = "block";
        } else {
          emptyState.style.display = visible ? "none" : "block";
        }
      }
    };

    select.addEventListener("change", updateList);
    updateList();
  });
})();

(() => {
  const searchInput = document.getElementById("empresa-search");
  const list = document.querySelector("[data-empresa-list]");
  const form = document.querySelector("[data-empresa-search-form]");
  const filterButtons = document.querySelectorAll("[data-empresa-filter]");

  if (!list || !searchInput) {
    return;
  }

  let activeFilter = "all";
  const cards = Array.from(list.querySelectorAll("[data-empresa-card]"));

  const applyFilters = () => {
    const query = searchInput.value.trim().toLowerCase();

    cards.forEach((card) => {
      const name = card.getAttribute("data-empresa-name") || "";
      const status = card.getAttribute("data-empresa-status") || "";
      const matchesQuery = !query || name.includes(query);
      const matchesStatus =
        activeFilter === "all" ||
        (activeFilter === "active" && status === "active") ||
        (activeFilter === "inactive" && status === "inactive");

      card.style.display = matchesQuery && matchesStatus ? "block" : "none";
    });
  };

  searchInput.addEventListener("input", applyFilters);

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.getAttribute("data-empresa-filter") || "all";
      filterButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      applyFilters();
    });
  });

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      applyFilters();
    });
  }

  applyFilters();
})();

(() => {
  const phoneInputs = document.querySelectorAll("[data-phone-input]");
  if (!phoneInputs.length) {
    return;
  }

  const getCountryCode = (input) => {
    const form = input.closest("form");
    if (!form) {
      return "54";
    }
    const countrySelect = form.querySelector("select[name='pais']");
    if (!countrySelect) {
      return "54";
    }
    const selectedOption = countrySelect.options[countrySelect.selectedIndex];
    const code = selectedOption ? selectedOption.getAttribute("data-code") : null;
    if (code && code.trim()) {
      return code.replace(/\D/g, "");
    }
    return "54";
  };

  const formatPhone = (value, countryCode) => {
    const digits = value.replace(/\D/g, "");
    if (!digits) {
      return "";
    }
    const normalized = digits.replace(/^0+/, "");
    if (normalized.startsWith(countryCode)) {
      return `+${normalized}`;
    }
    return `+${countryCode}${normalized}`;
  };

  phoneInputs.forEach((input) => {
    input.addEventListener("input", () => {
      input.value = input.value.replace(/\D/g, "");
    });

    input.addEventListener("blur", () => {
      const code = getCountryCode(input);
      input.value = formatPhone(input.value, code);
    });

    const form = input.closest("form");
    if (form) {
      const countrySelect = form.querySelector("select[name='pais']");
      if (countrySelect) {
        countrySelect.addEventListener("change", () => {
          const code = getCountryCode(input);
          if (input.value) {
            input.value = formatPhone(input.value, code);
          }
        });
      }
    }
  });
})();

(() => {
  const geoForms = document.querySelectorAll("[data-geo-form]");
  if (!geoForms.length) {
    return;
  }

  geoForms.forEach((form) => {
    const paisSelect = form.querySelector("select[name='pais']");
    const provinciaSelect = form.querySelector("[data-provincia-select]");
    const localidadSelect = form.querySelector("[data-localidad-select]");

    if (!paisSelect || !provinciaSelect || !localidadSelect) {
      return;
    }

    const provinciaOptions = Array.from(provinciaSelect.options);
    const localidadOptions = Array.from(localidadSelect.options);

    const filterProvincias = () => {
      const paisId = paisSelect.value;
      let hasSelected = false;

      provinciaOptions.forEach((option, idx) => {
        if (idx === 0) {
          option.hidden = false;
          return;
        }
        const parentPaisId = option.getAttribute("data-pais-id");
        const show = !paisId || parentPaisId === paisId;
        option.hidden = !show;
        if (!show && option.selected) {
          option.selected = false;
        }
        if (show && option.selected) {
          hasSelected = true;
        }
      });

      if (!hasSelected) {
        provinciaSelect.selectedIndex = 0;
      }
    };

    const filterLocalidades = () => {
      const provinciaId = provinciaSelect.value;
      let hasSelected = false;

      localidadOptions.forEach((option, idx) => {
        if (idx === 0) {
          option.hidden = false;
          return;
        }
        const parentProvinciaId = option.getAttribute("data-provincia-id");
        const show = !provinciaId || parentProvinciaId === provinciaId;
        option.hidden = !show;
        if (!show && option.selected) {
          option.selected = false;
        }
        if (show && option.selected) {
          hasSelected = true;
        }
      });

      if (!hasSelected) {
        localidadSelect.selectedIndex = 0;
      }
    };

    paisSelect.addEventListener("change", () => {
      filterProvincias();
      filterLocalidades();
    });
    provinciaSelect.addEventListener("change", filterLocalidades);

    filterProvincias();
    filterLocalidades();
  });
})();
