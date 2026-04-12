import "./styles.css";
import { gsap } from "gsap";
import * as THREE from "three";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

const SECTION_SEQUENCE = [
  "hero",
  "intro",
  "pipeline-one",
  "bridge-one",
  "bridge-two",
  "pipeline-two",
  "conclusion",
  "about",
];

const FLOW_COLORS = {
  input: "#5079A8",
  prompt_router: "#996FD5",
  memory_probe: "#53A7AF",
  policy_gate: "#E96666",
  summary_stack: "#E29757",
  response: "#3FA756",
  noise_bucket: "#B9B7AE",
  trigger_surface: "#7A7EE6",
  evidence_parse: "#5079A8",
  certainty_gate: "#3FA756",
  uncertainty_gate: "#53A7AF",
  fail_routing: "#E96666",
  pass_routing: "#996FD5",
  release_gate: "#E29757",
  emit: "#3A70B5",
};

const BASELINE_GRAPH = {
  nodes: [
    { id: "input" },
    { id: "prompt_router" },
    { id: "memory_probe" },
    { id: "policy_gate" },
    { id: "summary_stack" },
    { id: "response" },
    { id: "noise_bucket" },
    { id: "trigger_surface" },
  ],
  links: [
    { source: "input", target: "prompt_router", value: 18 },
    { source: "prompt_router", target: "memory_probe", value: 12 },
    { source: "prompt_router", target: "policy_gate", value: 6 },
    { source: "memory_probe", target: "summary_stack", value: 8 },
    { source: "memory_probe", target: "trigger_surface", value: 4 },
    { source: "policy_gate", target: "summary_stack", value: 3 },
    { source: "policy_gate", target: "noise_bucket", value: 3 },
    { source: "trigger_surface", target: "summary_stack", value: 3 },
    { source: "trigger_surface", target: "noise_bucket", value: 1 },
    { source: "summary_stack", target: "response", value: 10 },
    { source: "summary_stack", target: "noise_bucket", value: 4 },
  ],
};

const BETA2_GRAPH = {
  nodes: [
    { id: "evidence_parse" },
    { id: "certainty_gate" },
    { id: "uncertainty_gate" },
    { id: "fail_routing" },
    { id: "pass_routing" },
    { id: "release_gate" },
    { id: "emit" },
    { id: "noise_bucket" },
  ],
  links: [
    { source: "evidence_parse", target: "certainty_gate", value: 10 },
    { source: "evidence_parse", target: "uncertainty_gate", value: 8 },
    { source: "certainty_gate", target: "pass_routing", value: 9 },
    { source: "certainty_gate", target: "fail_routing", value: 1 },
    { source: "uncertainty_gate", target: "fail_routing", value: 6 },
    { source: "uncertainty_gate", target: "pass_routing", value: 2 },
    { source: "fail_routing", target: "noise_bucket", value: 2 },
    { source: "fail_routing", target: "release_gate", value: 5 },
    { source: "pass_routing", target: "release_gate", value: 11 },
    { source: "release_gate", target: "emit", value: 14 },
    { source: "release_gate", target: "noise_bucket", value: 2 },
  ],
};

const BRIDGE_A_GRAPH = {
  nodes: [
    { id: "input" },
    { id: "prompt_router" },
    { id: "memory_probe" },
    { id: "certainty_gate" },
    { id: "uncertainty_gate" },
    { id: "release_gate" },
    { id: "response" },
    { id: "noise_bucket" },
  ],
  links: [
    { source: "input", target: "prompt_router", value: 18 },
    { source: "prompt_router", target: "memory_probe", value: 11 },
    { source: "prompt_router", target: "uncertainty_gate", value: 7 },
    { source: "memory_probe", target: "certainty_gate", value: 9 },
    { source: "memory_probe", target: "uncertainty_gate", value: 2 },
    { source: "certainty_gate", target: "release_gate", value: 8 },
    { source: "certainty_gate", target: "noise_bucket", value: 1 },
    { source: "uncertainty_gate", target: "release_gate", value: 5 },
    { source: "uncertainty_gate", target: "noise_bucket", value: 4 },
    { source: "release_gate", target: "response", value: 11 },
    { source: "release_gate", target: "noise_bucket", value: 2 },
  ],
};

const BRIDGE_B_GRAPH = {
  nodes: [
    { id: "evidence_parse" },
    { id: "certainty_gate" },
    { id: "uncertainty_gate" },
    { id: "fail_routing" },
    { id: "pass_routing" },
    { id: "release_gate" },
    { id: "emit" },
    { id: "noise_bucket" },
  ],
  links: [
    { source: "evidence_parse", target: "certainty_gate", value: 11 },
    { source: "evidence_parse", target: "uncertainty_gate", value: 7 },
    { source: "certainty_gate", target: "pass_routing", value: 9 },
    { source: "certainty_gate", target: "fail_routing", value: 2 },
    { source: "uncertainty_gate", target: "fail_routing", value: 4 },
    { source: "uncertainty_gate", target: "pass_routing", value: 3 },
    { source: "fail_routing", target: "release_gate", value: 3 },
    { source: "fail_routing", target: "noise_bucket", value: 3 },
    { source: "pass_routing", target: "release_gate", value: 12 },
    { source: "release_gate", target: "emit", value: 13 },
    { source: "release_gate", target: "noise_bucket", value: 2 },
  ],
};

function cloneGraph(graph) {
  return {
    nodes: graph.nodes.map((node) => ({ ...node })),
    links: graph.links.map((link) => ({ ...link })),
  };
}

function stretchSankeyYToFit(graph, top, bottom) {
  const minY = d3.min(graph.nodes, (node) => node.y0);
  const maxY = d3.max(graph.nodes, (node) => node.y1);
  if (typeof minY !== "number" || typeof maxY !== "number") {
    return;
  }
  const span = maxY - minY;
  const targetSpan = bottom - top;
  if (span <= 0) {
    return;
  }
  const scale = targetSpan / span;
  graph.nodes.forEach((node) => {
    node.y0 = top + (node.y0 - minY) * scale;
    node.y1 = top + (node.y1 - minY) * scale;
  });
  graph.links.forEach((link) => {
    link.y0 = top + (link.y0 - minY) * scale;
    link.y1 = top + (link.y1 - minY) * scale;
    link.width *= scale;
  });
}

function drawSankey({ sectionId, svgId, graph, edgeInset = 0 }) {
  const section = document.getElementById(sectionId);
  const svgNode = document.getElementById(svgId);
  if (!(section instanceof HTMLElement) || !(svgNode instanceof SVGSVGElement)) {
    return;
  }

  const width = Math.max(section.clientWidth, 1);
  const height = Math.max(section.clientHeight, 1);
  const nodeWidth = Math.max(12, Math.floor(width * 0.014));
  const nodePadding = Math.max(10, Math.floor(height * 0.022));

  const layout = sankey()
    .nodeId((node) => node.id)
    .nodeWidth(nodeWidth)
    .nodePadding(nodePadding)
    .extent([
      [0, 0],
      [width, height],
    ]);

  const sankeyGraph = layout(cloneGraph(graph));
  stretchSankeyYToFit(sankeyGraph, edgeInset, height - edgeInset);
  const svg = d3.select(svgNode);
  svg.selectAll("*").remove();
  svg.attr("viewBox", `0 0 ${width} ${height}`);

  const root = svg.append("g");

  root
    .append("g")
    .selectAll("path")
    .data(sankeyGraph.links)
    .join("path")
    .attr("class", "sankey-link")
    .attr("d", sankeyLinkHorizontal())
    .attr("stroke", (link) => FLOW_COLORS[link.source.id] ?? "rgba(30, 30, 30, 0.55)")
    .attr("stroke-width", (link) => Math.max(1, link.width))
    .attr("stroke-opacity", 0.43)
    .attr("fill", "none");

  root
    .append("g")
    .selectAll("rect")
    .data(sankeyGraph.nodes)
    .join("rect")
    .attr("class", "sankey-node")
    .attr("x", (node) => node.x0)
    .attr("y", (node) => node.y0)
    .attr("width", (node) => Math.max(1, node.x1 - node.x0))
    .attr("height", (node) => Math.max(1, node.y1 - node.y0))
    .attr("fill", (node) => FLOW_COLORS[node.id] ?? "#111");

}

function setupFilmSankey() {
  let resizeFrame = 0;

  const render = () => {
    drawSankey({
      sectionId: "pipeline-one",
      svgId: "sankey-baseline",
      graph: BASELINE_GRAPH,
      edgeInset: 44,
    });
    drawSankey({
      sectionId: "bridge-one",
      svgId: "sankey-bridge-a",
      graph: BRIDGE_A_GRAPH,
      edgeInset: 0,
    });
    drawSankey({
      sectionId: "bridge-two",
      svgId: "sankey-bridge-b",
      graph: BRIDGE_B_GRAPH,
      edgeInset: 0,
    });
    drawSankey({
      sectionId: "pipeline-two",
      svgId: "sankey-beta2",
      graph: BETA2_GRAPH,
      edgeInset: 44,
    });
  };

  const onResize = () => {
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
    }
    resizeFrame = requestAnimationFrame(render);
  };

  render();
  window.addEventListener("resize", onResize);
  return () => {
    window.removeEventListener("resize", onResize);
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
    }
  };
}

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
  const material = new THREE.MeshBasicMaterial({ color: 0xfdfdfd });
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
  let wheelLockedUntil = 0;

  const updateActiveState = () => {
    sections.forEach((section, index) => {
      section.classList.toggle("is-active", index === activeIndex);
    });
  };

  const moveTo = (index, immediate = false) => {
    const nextIndex = Math.max(0, Math.min(index, sections.length - 1));
    if (nextIndex === activeIndex) {
      return;
    }
    activeIndex = nextIndex;
    const target = sections[activeIndex];
    if (!(target instanceof HTMLElement)) {
      return;
    }
    updateActiveState();

    const duration = immediate ? 0 : 0.88;
    if (!immediate) {
      isTransitioning = true;
    }
    gsap.to(board, {
      x: -target.offsetLeft,
      y: -target.offsetTop,
      duration,
      ease: "power3.inOut",
      onComplete: () => {
        isTransitioning = false;
      },
      onInterrupt: () => {
        isTransitioning = false;
      },
      overwrite: "auto",
    });
    window.dispatchEvent(
      new CustomEvent("polinko:section-change", {
        detail: { id: target.id, index: activeIndex },
      })
    );
  };

  const onWheel = (event) => {
    event.preventDefault();
    const now = performance.now();
    if (now < wheelLockedUntil || isTransitioning || Math.abs(event.deltaY) < 8) {
      return;
    }
    wheelLockedUntil = now + 420;
    const direction = event.deltaY > 0 ? 1 : -1;
    moveTo(activeIndex + direction);
  };

  const onKey = (event) => {
    if (isTransitioning) {
      return;
    }
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

function setupConclusionMorph() {
  const stages = Array.from(document.querySelectorAll(".morph-stage"));
  const replayButton = document.querySelector(".morph-replay");
  if (!(replayButton instanceof HTMLButtonElement) || stages.length === 0) {
    return () => {};
  }

  const stageOrder = ["baseline", "bridge", "beta2"];
  let running = false;
  let timers = [];

  const setStage = (key) => {
    stages.forEach((node) => {
      node.classList.toggle("active", node.getAttribute("data-stage") === key);
    });
  };

  const clearTimers = () => {
    timers.forEach((timer) => timer.kill());
    timers = [];
  };

  const replay = () => {
    if (running) {
      clearTimers();
    }
    running = true;
    stageOrder.forEach((stageKey, index) => {
      const timer = gsap.delayedCall(index * 0.55, () => setStage(stageKey));
      timers.push(timer);
    });
    timers.push(
      gsap.delayedCall(stageOrder.length * 0.55 + 0.05, () => {
        running = false;
      })
    );
  };

  const onSectionChange = (event) => {
    if (event.detail?.id === "conclusion") {
      replay();
    }
  };

  replayButton.addEventListener("click", replay);
  window.addEventListener("polinko:section-change", onSectionChange);
  setStage("baseline");

  return () => {
    replayButton.removeEventListener("click", replay);
    window.removeEventListener("polinko:section-change", onSectionChange);
    clearTimers();
  };
}

const teardownWebGL = setupWebGLStage();
const teardownSankey = setupFilmSankey();
const teardownPath = setupSectionPath();
const teardownMorph = setupConclusionMorph();

window.addEventListener("beforeunload", () => {
  teardownWebGL();
  teardownSankey();
  teardownPath();
  teardownMorph();
});
