(() => {
  const themeSelect = document.querySelector("#theme-select");
  const validThemes = ["ink", "pine", "steel", "lantern"];
  let savedTheme = "ink";

  try {
    const storedTheme = window.localStorage.getItem("ronin-task-board-theme");
    if (validThemes.includes(storedTheme)) {
      savedTheme = storedTheme;
    }
  } catch (error) {
    savedTheme = "ink";
  }

  document.body.dataset.theme = savedTheme;

  const particleLayer = document.querySelector(".leaf-layer");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const drawWorld = (theme) => {
    if (!particleLayer) {
      return;
    }

    particleLayer.replaceChildren();
    if (reducedMotion.matches) {
      return;
    }

    const particleTypes = {
      ink: ["falling-leaf", 14],
      pine: ["falling-leaf pine-needle", 14],
      steel: ["moon-star", 24],
      lantern: ["ember-drift", 16],
    };
    const [className, count] = particleTypes[theme] || particleTypes.ink;

    for (let index = 0; index < count; index += 1) {
      const particle = document.createElement("span");
      particle.className = className;
      particle.setAttribute("aria-hidden", "true");
      particle.style.setProperty("--particle-left", `${Math.random() * 100}%`);
      particle.style.setProperty("--particle-top", `${Math.random() * 76}%`);
      particle.style.setProperty("--particle-size", `${3 + Math.random() * 7}px`);
      particle.style.setProperty("--particle-duration", `${16 + Math.random() * 24}s`);
      particle.style.setProperty("--particle-delay", `${-Math.random() * 40}s`);
      particle.style.setProperty("--particle-drift", `${Math.random() * 130 - 65}px`);
      particleLayer.appendChild(particle);
    }
  };

  drawWorld(savedTheme);

  if (themeSelect) {
    themeSelect.value = savedTheme;
    themeSelect.addEventListener("change", () => {
      const selectedTheme = validThemes.includes(themeSelect.value) ? themeSelect.value : "ink";
      document.body.dataset.theme = selectedTheme;
      drawWorld(selectedTheme);

      try {
        window.localStorage.setItem("ronin-task-board-theme", selectedTheme);
      } catch (error) {
        return;
      }
    });
  }
})();