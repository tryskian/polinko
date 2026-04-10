import "./styles.css";
import { gsap } from "gsap";
import * as THREE from "three";

const SECTION_SEQUENCE = [
  "hero",
  "intro",
  "pipeline-one",
  "sankey-one",
  "sankey-two",
  "pipeline-two",
  "conclusion",
  "about",
];

function setupWebGLStage() {
  const canvas = document.getElementById("webgl-stage");
  if (!(canvas instanceof HTMLCanvasElement)) {
    return () => {};
  }

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xfdfdfd);

  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.z = 3.2;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const geometry = new THREE.PlaneGeometry(5.4, 5.4, 1, 1);
  const material = new THREE.MeshBasicMaterial({ color: 0xf8f7ef });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.z = -0.25;
  scene.add(mesh);

  const renderFrame = () => renderer.render(scene, camera);
  renderFrame();

  const handleResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderFrame();
  };
  window.addEventListener("resize", handleResize);

  return () => {
    window.removeEventListener("resize", handleResize);
    geometry.dispose();
    material.dispose();
    renderer.dispose();
  };
}

function setupSectionPath() {
  const board = document.querySelector(".board");
  if (!(board instanceof HTMLElement)) {
    return () => {};
  }

  const sections = SECTION_SEQUENCE.map((id) => document.getElementById(id)).filter(Boolean);
  let activeIndex = 0;
  let isTransitioning = false;

  const updateActiveState = () => {
    sections.forEach((section, index) => {
      section.classList.toggle("is-active", index === activeIndex);
    });
  };

  const moveTo = (index, immediate = false) => {
    activeIndex = Math.max(0, Math.min(index, sections.length - 1));
    const target = sections[activeIndex];
    if (!(target instanceof HTMLElement)) {
      return;
    }
    updateActiveState();

    const duration = immediate ? 0 : 0.88;
    gsap.to(board, {
      x: -target.offsetLeft,
      y: -target.offsetTop,
      duration,
      ease: "power3.inOut",
      onStart: () => {
        isTransitioning = !immediate;
      },
      onComplete: () => {
        isTransitioning = false;
      },
    });
  };

  const onWheel = (event) => {
    event.preventDefault();
    if (isTransitioning || Math.abs(event.deltaY) < 8) {
      return;
    }
    const direction = event.deltaY > 0 ? 1 : -1;
    moveTo(activeIndex + direction);
  };

  const onKey = (event) => {
    if (event.key === "ArrowDown" || event.key === "ArrowRight" || event.key === "PageDown") {
      event.preventDefault();
      moveTo(activeIndex + 1);
    }
    if (event.key === "ArrowUp" || event.key === "ArrowLeft" || event.key === "PageUp") {
      event.preventDefault();
      moveTo(activeIndex - 1);
    }
  };

  const handleResize = () => moveTo(activeIndex, true);

  window.addEventListener("wheel", onWheel, { passive: false });
  window.addEventListener("keydown", onKey);
  window.addEventListener("resize", handleResize);

  gsap.fromTo(
    ".block",
    { opacity: 0, scale: 0.985 },
    {
      opacity: 1,
      scale: 1,
      duration: 0.66,
      ease: "power2.out",
      stagger: 0.045,
    }
  );

  moveTo(0, true);

  return () => {
    window.removeEventListener("wheel", onWheel);
    window.removeEventListener("keydown", onKey);
    window.removeEventListener("resize", handleResize);
  };
}

const teardownWebGL = setupWebGLStage();
const teardownPath = setupSectionPath();

window.addEventListener("beforeunload", () => {
  teardownWebGL();
  teardownPath();
});
