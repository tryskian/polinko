const root = document.documentElement;
const button = document.querySelector("[data-theme-toggle]");
const storageKey = "krystian-io-theme";
const themeSwitchDelay = 220;
let themeSwitchTimer = 0;

function readTheme() {
  try {
    const theme = localStorage.getItem(storageKey);

    return theme === "dark" || theme === "light" ? theme : "light";
  } catch {
    return "light";
  }
}

function writeTheme(theme) {
  try {
    localStorage.setItem(storageKey, theme);
  } catch {
    return;
  }
}

function applyTheme(theme) {
  root.dataset.theme = theme;
  button?.setAttribute(
    "aria-label",
    theme === "dark" ? "Switch to light theme" : "Switch to dark theme",
  );
}

function applyThemeInstantly(theme) {
  root.setAttribute("data-theme-switching", "");
  applyTheme(theme);

  if (themeSwitchTimer) {
    window.clearTimeout(themeSwitchTimer);
  }

  themeSwitchTimer = window.setTimeout(() => {
    root.removeAttribute("data-theme-switching");
    themeSwitchTimer = 0;
  }, themeSwitchDelay);
}

// Theme state is shared across every static research route.
applyTheme(readTheme());

button?.addEventListener("click", () => {
  const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";

  writeTheme(nextTheme);
  applyThemeInstantly(nextTheme);
});

const header = document.querySelector(".site-header");
const menuButton = document.querySelector("[data-menu-toggle]");
const menuPanel = document.querySelector("[data-menu-panel]");

function setMenu(open) {
  menuButton?.setAttribute("aria-expanded", String(open));
  menuButton?.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  menuPanel?.toggleAttribute("data-open", open);
}

if (header && menuButton && menuPanel) {
  header.classList.add("menu-ready");
  setMenu(false);

  menuButton.addEventListener("click", () => {
    setMenu(menuButton.getAttribute("aria-expanded") !== "true");
  });

  menuPanel.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      setMenu(false);
    }
  });

  document.addEventListener("click", (event) => {
    if (!header.contains(event.target)) {
      setMenu(false);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton.getAttribute("aria-expanded") === "true") {
      setMenu(false);
      menuButton.focus();
    }
  });
}

const diagramImages = Array.from(document.querySelectorAll(".source-diagram"));

if (diagramImages.length > 0) {
  const dialog = document.createElement("dialog");

  dialog.className = "diagram-lightbox";
  dialog.innerHTML = `
    <div class="diagram-lightbox__inner">
      <button class="diagram-lightbox__close" type="button">Close</button>
      <img class="diagram-lightbox__image" alt="" />
      <p class="diagram-lightbox__caption"></p>
    </div>
  `;

  document.body.append(dialog);

  const closeButton = dialog.querySelector(".diagram-lightbox__close");
  const zoomImage = dialog.querySelector(".diagram-lightbox__image");
  const caption = dialog.querySelector(".diagram-lightbox__caption");

  function closeDiagram() {
    if (dialog.open) {
      dialog.close();
    }
  }

  function openDiagram(image) {
    const source = image.currentSrc || image.src;
    const text = image.alt || "Polinko diagram";

    zoomImage.src = source;
    zoomImage.alt = text;
    caption.textContent = text;

    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
  }

  diagramImages.forEach((image) => {
    image.setAttribute("role", "button");
    image.setAttribute("tabindex", "0");
    image.setAttribute("aria-label", `Zoom diagram: ${image.alt}`);

    image.addEventListener("click", () => openDiagram(image));
    image.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      event.preventDefault();
      openDiagram(image);
    });
  });

  closeButton?.addEventListener("click", closeDiagram);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      closeDiagram();
    }
  });
}
