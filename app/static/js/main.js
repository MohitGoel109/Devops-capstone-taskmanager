(() => {
  const leafLayer = document.querySelector(".leaf-layer");

  if (!leafLayer || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  for (let index = 0; index < 14; index += 1) {
    const leaf = document.createElement("span");
    leaf.className = "falling-leaf";
    leaf.setAttribute("aria-hidden", "true");
    leaf.style.setProperty("--leaf-left", `${Math.random() * 100}%`);
    leaf.style.setProperty("--leaf-size", `${8 + Math.random() * 7}px`);
    leaf.style.setProperty("--leaf-duration", `${22 + Math.random() * 20}s`);
    leaf.style.setProperty("--leaf-delay", `${-Math.random() * 40}s`);
    leaf.style.setProperty("--leaf-drift", `${Math.random() * 150 - 75}px`);
    leafLayer.appendChild(leaf);
  }
})();