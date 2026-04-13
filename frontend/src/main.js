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

const SANKEY_DATA_URL = "/portfolio/sankey-data";

const FLOW_COLORS = {
  legacy_source: "#2f5f8f",
  legacy_outcome: "#7aa9cb",
  legacy_signal: "#ee7321",
  bridge: "#f2d35d",
  current_source: "#1e5f35",
  current_lane: "#8cc66c",
  current_outcome: "#83558e",
  legacy_feedback_to_outcome: "#2f5f8f",
  legacy_outcome_to_signal: "#ee7321",
  legacy_signal_to_bridge: "#ee7321",
  bridge_to_current_lane: "#1e5f35",
  current_report_to_lane: "#1e5f35",
  current_lane_to_outcome: "#83558e",
};

const EMPTY_GRAPHS = {
  legacy: { nodes: [], links: [] },
  bridge: { nodes: [], links: [] },
  current: { nodes: [], links: [] },
};

const STAGE_CONFIG = [
  {
    sectionId: "pipeline-one",
    svgId: "sankey-baseline",
    graphKey: "legacy",
    title: "Beta 1.0 manual evals",
    meta: "manual feedback outcomes and signal tags",
    edgeInset: 44,
  },
  {
    sectionId: "bridge-one",
    svgId: "sankey-bridge-a",
    graphKey: "bridge",
    title: "Signal bridge",
    meta: "legacy signal categories to current OCR lanes",
    edgeInset: 0,
  },
  {
    sectionId: "bridge-two",
    svgId: "sankey-bridge-b",
    graphKey: "bridge",
    title: "Evidence continuity",
    meta: "source-side counts only; no row-level join implied",
    edgeInset: 0,
  },
  {
    sectionId: "pipeline-two",
    svgId: "sankey-beta2",
    graphKey: "current",
    title: "Current OCR binary gates",
    meta: "strict binary gate cases by OCR lane and outcome",
    edgeInset: 44,
  },
];

function cloneGraph(graph) {
  return {
    nodes: (graph?.nodes ?? []).map((node) => ({ ...node })),
    links: (graph?.links ?? []).map((link) => ({ ...link })),
  };
}

function graphHasData(graph) {
  return Array.isArray(graph?.nodes) && graph.nodes.length > 0
    && Array.isArray(graph?.links) && graph.links.length > 0;
}

function nodeColor(node) {
  return FLOW_COLORS[node.group] ?? FLOW_COLORS[node.id] ?? "#161616";
}

function linkColor(link) {
  return FLOW_COLORS[link.kind] ?? nodeColor(link.source) ?? "rgba(30, 30, 30, 0.55)";
}

function formatNumber(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return "0";
  }
  return new Intl.NumberFormat("en").format(numeric);
}

function setText(selector, value) {
  const node = document.querySelector(selector);
  if (node instanceof HTMLElement) {
    node.textContent = value;
  }
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
  const svg = d3.select(svgNode);
  svg.selectAll("*").remove();
  svg.attr("viewBox", `0 0 ${width} ${height}`);

  if (!graphHasData(graph)) {
    svg
      .append("text")
      .attr("class", "sankey-empty-text")
      .attr("x", width / 2)
      .attr("y", height / 2)
      .attr("text-anchor", "middle")
      .text("No real twin-sankey data available");
    return;
  }

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

  const root = svg.append("g");

  root
    .append("g")
    .selectAll("path")
    .data(sankeyGraph.links)
    .join("path")
    .attr("class", "sankey-link")
    .attr("d", sankeyLinkHorizontal())
    .attr("stroke", (link) => linkColor(link))
    .attr("stroke-width", (link) => Math.max(1, link.width))
    .attr("stroke-opacity", 0.52)
    .attr("fill", "none")
    .append("title")
    .text((link) => {
      const source = link.source.label ?? link.source.id;
      const target = link.target.label ?? link.target.id;
      return `${source} -> ${target}: ${formatNumber(link.value)} (${link.provenance ?? "source data"})`;
    });

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
    .attr("fill", (node) => nodeColor(node))
    .append("title")
    .text((node) => `${node.label ?? node.id}: ${formatNumber(node.value)}`);

  root
    .append("g")
    .attr("class", "sankey-labels")
    .selectAll("text")
    .data(sankeyGraph.nodes)
    .join("text")
    .attr("class", "sankey-label")
    .attr("x", (node) => (node.x0 < width / 2 ? node.x1 + 10 : node.x0 - 10))
    .attr("y", (node) => (node.y0 + node.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", (node) => (node.x0 < width / 2 ? "start" : "end"))
    .text((node) => node.label ?? node.id);
}

function setupFilmSankey() {
  let resizeFrame = 0;
  let payload = null;

  const updateCopy = () => {
    const available = Boolean(payload?.available);
    const summary = payload?.summary ?? {};
    setText("#legacyRows", `${formatNumber(summary.legacy_feedback_rows)} manual evals`);
    setText("#legacySignals", `${formatNumber(summary.legacy_signal_mentions)} signal mentions`);
    setText("#currentCases", `${formatNumber(summary.current_binary_cases)} gate cases`);
    setText("#currentReports", `${formatNumber(summary.current_binary_reports)} reports`);
    setText("#bridgeCategories", `${formatNumber(summary.bridge_categories)} bridge categories`);
    setText("#dataState", available ? "real data connected" : "waiting for real data");
    setText("#dataReason", available ? "No decorative fallback is rendered." : payload?.reason ?? "Loading local sources.");

    STAGE_CONFIG.forEach((stage) => {
      const section = document.getElementById(stage.sectionId);
      if (!(section instanceof HTMLElement)) {
        return;
      }
      section.dataset.state = available ? "ready" : "empty";
      const title = section.querySelector(".sankey-stage-title");
      const meta = section.querySelector(".sankey-stage-meta");
      if (title instanceof HTMLElement) {
        title.textContent = stage.title;
      }
      if (meta instanceof HTMLElement) {
        meta.textContent = available ? stage.meta : "Explicit no-data state. Add/restore required source data to render.";
      }
    });
  };

  const render = () => {
    const graphs = payload?.graphs ?? EMPTY_GRAPHS;
    STAGE_CONFIG.forEach((stage) => {
      drawSankey({
        sectionId: stage.sectionId,
        svgId: stage.svgId,
        graph: graphs[stage.graphKey],
        edgeInset: stage.edgeInset,
      });
    });
    updateCopy();
  };

  const load = async () => {
    try {
      const response = await fetch(SANKEY_DATA_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      payload = await response.json();
    } catch (error) {
      payload = {
        available: false,
        reason: `Unable to load ${SANKEY_DATA_URL}: ${error.message}`,
        summary: {},
        graphs: EMPTY_GRAPHS,
      };
    }
    render();
  };

  const onResize = () => {
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
    }
    resizeFrame = requestAnimationFrame(render);
  };

  updateCopy();
  render();
  load();
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
