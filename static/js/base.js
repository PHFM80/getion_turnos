// JS base para futuras interacciones globales.
(() => {
  const THEME_KEY = "gt-theme";
  const root = document.documentElement;
  const toggleButton = document.querySelector("[data-theme-toggle]");

  const getPreferredTheme = () => {
    if (!window.matchMedia) {
      return "light";
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const updateToggleLabel = (theme) => {
    if (!toggleButton) {
      return;
    }
    const label = theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro";
    toggleButton.setAttribute("aria-label", label);
    toggleButton.setAttribute("title", label);
  };

  const setTheme = (theme, persist = true) => {
    root.setAttribute("data-theme", theme);
    if (persist) {
      try {
        localStorage.setItem(THEME_KEY, theme);
      } catch (err) {
        // Sin persistencia si el storage no esta disponible.
      }
    }
    updateToggleLabel(theme);
  };

  const initTheme = () => {
    let stored = null;
    try {
      stored = localStorage.getItem(THEME_KEY);
    } catch (err) {
      stored = null;
    }
    const current = root.getAttribute("data-theme");
    const theme = stored || current || getPreferredTheme();
    setTheme(theme, false);
  };

  initTheme();

  if (toggleButton) {
    toggleButton.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || getPreferredTheme();
      const next = current === "dark" ? "light" : "dark";
      setTheme(next);
    });
  }
})();

(() => {
  const toggles = document.querySelectorAll("[data-password-toggle]");

  toggles.forEach((toggle) => {
    const targetSelector = toggle.getAttribute("data-target");
    if (!targetSelector) {
      return;
    }
    const input = document.querySelector(targetSelector);
    if (!input) {
      return;
    }

    const setVisible = (visible) => {
      input.type = visible ? "text" : "password";
      toggle.setAttribute("data-visible", visible ? "true" : "false");
      const label = visible ? "Ocultar contrasena" : "Mostrar contrasena";
      toggle.setAttribute("aria-label", label);
      toggle.setAttribute("title", label);
    };

    toggle.addEventListener("click", () => {
      const isVisible = toggle.getAttribute("data-visible") === "true";
      setVisible(!isVisible);
    });
  });
})();
