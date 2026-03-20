// JS especifico del dashboard.
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
