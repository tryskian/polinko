import "./styles.css";
import { gsap } from "gsap";
import { Observer } from "gsap/Observer";
import {
  Color,
  Mesh,
  MeshBasicMaterial,
  PerspectiveCamera,
  PlaneGeometry,
  Scene,
  WebGLRenderer,
} from "three";

gsap.registerPlugin(Observer);

const SANKEY_DATA_URL = "/portfolio/sankey-data";
const EVIDENCE_SURFACE_ID = "evidence-map";
const STAGE_STEP_DURATION = 0.92;
const STAGE_STEP_EASE = "power2.inOut";
const STAGE_GESTURE_TOLERANCE = 14;
const STAGE_GESTURE_COOLDOWN_MS = 180;

const EMPTY_GRAPHS = {
  legacy: { nodes: [], links: [] },
  bridge: { nodes: [], links: [] },
  current: { nodes: [], links: [] },
};

function setupSankeyDataWiring() {
  const evidenceSurface = document.getElementById(EVIDENCE_SURFACE_ID);
  if (!(evidenceSurface instanceof HTMLElement)) {
    return () => {};
  }

  const setSurfaceState = (state, reason = "") => {
    evidenceSurface.dataset.state = state;
    if (reason) {
      evidenceSurface.dataset.reason = reason;
    } else {
      delete evidenceSurface.dataset.reason;
    }
  };

  const load = async () => {
    setSurfaceState("loading");
    try {
      const response = await fetch(SANKEY_DATA_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      window.__POLINKO_SANKEY_DATA__ = payload;
      setSurfaceState(payload?.available ? "ready" : "empty", payload?.available ? "" : payload?.reason ?? "No Sankey data available");
      window.dispatchEvent(new CustomEvent("polinko:sankey-data", { detail: payload }));
    } catch (error) {
      const payload = {
        available: false,
        reason: error instanceof Error ? error.message : String(error),
        graphs: EMPTY_GRAPHS,
      };
      setSurfaceState("error", payload.reason);
    }
  };

  load();
  return () => {};
}

function setupPinnedStageStepper() {
  const board = document.querySelector(".board");
  const track = document.getElementById("horizontal-track");
  if (!(board instanceof HTMLElement) || !(track instanceof HTMLElement)) {
    return () => {};
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scenes = [
    { id: "hero", row: 0, column: 0 },
    { id: "intro", row: 1, column: 0 },
    { id: "pipeline-one", row: 2, column: 0 },
    { id: "evidence-map", row: 2, column: 1 },
    { id: "pipeline-two", row: 2, column: 2 },
    { id: "conclusion", row: 3, column: 2 },
    { id: "about-lab", row: 4, column: 2 },
  ].filter((scene) => document.getElementById(scene.id));

  if (scenes.length < 2) {
    return () => {};
  }

  if ("scrollRestoration" in window.history) {
    window.history.scrollRestoration = "manual";
  }
  window.scrollTo(0, 0);

  const clampSceneIndex = gsap.utils.clamp(0, scenes.length - 1);
  let currentIndex = Math.max(
    0,
    scenes.findIndex((scene) => scene.id === window.location.hash.slice(1))
  );
  let isAnimating = false;
  let gestureLockedUntil = 0;
  let stageUnlockTween = null;

  const setActiveScene = (index) => {
    currentIndex = clampSceneIndex(index);
    document.documentElement.dataset.activeScene = scenes[currentIndex].id;
  };

  const sceneTransforms = (scene) => ({
    boardY: -scene.row * window.innerHeight,
    trackX: -scene.column * window.innerWidth,
  });

  const goToScene = (index, immediate = false) => {
    const nextIndex = clampSceneIndex(index);
    const scene = scenes[nextIndex];
    const { boardY, trackX } = sceneTransforms(scene);
    const duration = immediate || prefersReducedMotion ? 0 : STAGE_STEP_DURATION;

    setActiveScene(nextIndex);
    stageUnlockTween?.kill();
    isAnimating = true;
    gestureLockedUntil = performance.now() + (duration * 1000) + STAGE_GESTURE_COOLDOWN_MS;

    gsap.to(board, {
      y: boardY,
      duration,
      ease: immediate || prefersReducedMotion ? "none" : STAGE_STEP_EASE,
      overwrite: true,
    });
    gsap.to(track, {
      x: trackX,
      duration,
      ease: immediate || prefersReducedMotion ? "none" : STAGE_STEP_EASE,
      overwrite: true,
    });
    if (duration === 0) {
      isAnimating = false;
      stageUnlockTween = null;
      return;
    }
    stageUnlockTween = gsap.delayedCall(duration, () => {
      isAnimating = false;
      stageUnlockTween = null;
    });
  };

  const stepScene = (direction) => {
    if (isAnimating || performance.now() < gestureLockedUntil) {
      return;
    }
    goToScene(currentIndex + direction);
  };

  const observer = Observer.create({
    target: window,
    type: "wheel,touch,pointer",
    preventDefault: true,
    allowClicks: true,
    lockAxis: true,
    tolerance: STAGE_GESTURE_TOLERANCE,
    wheelSpeed: -1,
    onUp: () => stepScene(1),
    onDown: () => stepScene(-1),
  });

  const onKeyDown = (event) => {
    if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {
      return;
    }
    const target = event.target;
    if (
      target instanceof HTMLElement
      && (
        target.isContentEditable
        || ["INPUT", "SELECT", "TEXTAREA", "BUTTON"].includes(target.tagName)
      )
    ) {
      return;
    }

    if (["ArrowDown", "PageDown", " ", "Spacebar", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      stepScene(1);
    } else if (["ArrowUp", "PageUp", "ArrowLeft"].includes(event.key)) {
      event.preventDefault();
      stepScene(-1);
    } else if (event.key === "Home") {
      event.preventDefault();
      goToScene(0);
    } else if (event.key === "End") {
      event.preventDefault();
      goToScene(scenes.length - 1);
    }
  };

  const onResize = () => goToScene(currentIndex, true);

  gsap.set([board, track], { force3D: true });
  goToScene(currentIndex, true);
  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("resize", onResize);

  return () => {
    observer.kill();
    stageUnlockTween?.kill();
    window.removeEventListener("keydown", onKeyDown);
    window.removeEventListener("resize", onResize);
    gsap.killTweensOf([board, track]);
    gsap.set([board, track], { clearProps: "transform" });
  };
}

function setupWebGLStage() {
  const canvas = document.getElementById("webgl-stage");
  if (!(canvas instanceof HTMLCanvasElement)) {
    return () => {};
  }

  const scene = new Scene();
  scene.background = new Color(0x202124);

  const camera = new PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.z = 3;

  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const plane = new Mesh(
    new PlaneGeometry(6, 6, 1, 1),
    new MeshBasicMaterial({ color: 0x202124 })
  );
  plane.position.z = -0.4;
  scene.add(plane);

  const render = () => renderer.render(scene, camera);
  render();

  const onResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    render();
  };

  window.addEventListener("resize", onResize);
  return () => {
    window.removeEventListener("resize", onResize);
    plane.geometry.dispose();
    plane.material.dispose();
    renderer.dispose();
  };
}

const teardownSankey = setupSankeyDataWiring();
const teardownStageStepper = setupPinnedStageStepper();
const teardownWebGL = setupWebGLStage();

window.addEventListener("beforeunload", () => {
  teardownSankey();
  teardownStageStepper();
  teardownWebGL();
});
