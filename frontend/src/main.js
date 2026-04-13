import "./styles.css";
import { gsap } from "gsap";
import * as THREE from "three";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

const SECTION_SEQUENCE = [
  "hero",
  "intro",
  "beta-one-pipeline",
  "sankey-panel-one",
  "sankey-panel-two",
  "sankey-panel-three",
  "sankey-panel-four",
  "current-ocr-pipeline",
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

function cloneGraph(graph) {
  return {
    nodes: (graph?.nodes ?? []).map((node) => ({ ...node })),
    links: (graph?.links ?? []).map((link) => ({ ...link })),
  };
}

function remapGraphNodeId(nodeId) {
  if (nodeId.startsWith("bridge_signal_")) {
    return nodeId.replace("bridge_signal_", "legacy_signal_");
  }
  if (nodeId.startsWith("bridge_lane_")) {
    return nodeId.replace("bridge_lane_", "current_lane_");
  }
  return nodeId;
}

function buildTwinGraph(graphs) {
  const nodes = new Map();
  const rawNodeIncoming = new Map();
  const rawNodeOutgoing = new Map();
  const links = [];
  const legacyBridgeTotal = d3.sum(
    graphs?.bridge?.links ?? [],
    (link) => (link.kind === "legacy_signal_to_bridge" ? Number(link.value) || 0 : 0)
  );
  const currentBridgeTotal = d3.sum(
    graphs?.bridge?.links ?? [],
    (link) => (link.kind === "bridge_to_current_lane" ? Number(link.value) || 0 : 0)
  );
  const legacyVisualScale = legacyBridgeTotal > 0 && currentBridgeTotal > 0
    ? currentBridgeTotal / legacyBridgeTotal
    : 1;
  const scaledLegacyKinds = new Set([
    "legacy_feedback_to_outcome",
    "legacy_outcome_to_signal",
    "legacy_signal_to_bridge",
  ]);

  const addNode = (node) => {
    const id = remapGraphNodeId(String(node?.id ?? ""));
    if (!id || id === "current_binary_reports" || nodes.has(id)) {
      return;
    }
    nodes.set(id, { ...node, id });
  };

  const addLink = (link) => {
    const source = remapGraphNodeId(String(link?.source ?? ""));
    const target = remapGraphNodeId(String(link?.target ?? ""));
    if (!source || !target || source === "current_binary_reports" || target === "current_binary_reports") {
      return;
    }
    const rawValue = Number(link?.value) || 0;
    const visualValue = scaledLegacyKinds.has(String(link?.kind))
      ? rawValue * legacyVisualScale
      : rawValue;
    rawNodeOutgoing.set(source, (rawNodeOutgoing.get(source) ?? 0) + rawValue);
    rawNodeIncoming.set(target, (rawNodeIncoming.get(target) ?? 0) + rawValue);
    links.push({ ...link, source, target, rawValue, value: visualValue });
  };

  [graphs?.legacy, graphs?.bridge, graphs?.current].forEach((graph) => {
    (graph?.nodes ?? []).forEach(addNode);
    (graph?.links ?? []).forEach(addLink);
  });

  return {
    id: "twin",
    label: "Twin Sankey",
    nodes: Array.from(nodes.values()).map((node) => ({
      ...node,
      rawValue: Math.max(rawNodeIncoming.get(node.id) ?? 0, rawNodeOutgoing.get(node.id) ?? 0),
    })),
    links,
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

  const boundsNode = svgNode.parentElement instanceof HTMLElement ? svgNode.parentElement : section;
  const width = Math.max(boundsNode.clientWidth, 1);
  const height = Math.max(boundsNode.clientHeight, 1);
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

  const nodeWidth = Math.min(30, Math.max(12, Math.floor(width * 0.014)));
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
      return `${source} -> ${target}: ${formatNumber(link.rawValue ?? link.value)} (${link.provenance ?? "source data"})`;
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
    .text((node) => `${node.label ?? node.id}: ${formatNumber(node.rawValue ?? node.value)}`);

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
    const section = document.getElementById("sankey-film");
    if (section instanceof HTMLElement) {
      section.dataset.state = available ? "ready" : "empty";
    }
  };

  const render = () => {
    const graphs = payload?.graphs ?? EMPTY_GRAPHS;
    drawSankey({
      sectionId: "sankey-film",
      svgId: "sankey-flow",
      graph: buildTwinGraph(graphs),
      edgeInset: 0,
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

    const targetX = target.offsetLeft + Math.max(0, target.offsetWidth - window.innerWidth) / 2;
    const targetY = target.offsetTop + Math.max(0, target.offsetHeight - window.innerHeight) / 2;
    const duration = immediate ? 0 : 0.88;
    if (!immediate) {
      isTransitioning = true;
    }
    gsap.to(board, {
      x: -targetX,
      y: -targetY,
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

const teardownWebGL = setupWebGLStage();
const teardownSankey = setupFilmSankey();
const teardownPath = setupSectionPath();

window.addEventListener("beforeunload", () => {
  teardownWebGL();
  teardownSankey();
  teardownPath();
});
