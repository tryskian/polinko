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
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

gsap.registerPlugin(Observer);

const SANKEY_DATA_URL = "/portfolio/sankey-data";
const SANKEY_SURFACES = [
  {
    graphKey: "legacy",
    surfaceId: "beta-one-sankey",
    svgId: "beta-one-sankey-svg",
    emptyText: "No Beta 1.0 Sankey data available",
  },
  {
    graphKey: "bridge",
    surfaceId: "sankey-bridge",
    svgId: "sankey-bridge-svg",
    emptyText: "No continuity bridge data available",
  },
  {
    graphKey: "current",
    surfaceId: "beta-two-sankey",
    svgId: "beta-two-sankey-svg",
    emptyText: "No Beta 2.0 Sankey data available",
  },
];
const SANKEY_LAYOUT_MIN_VALUE = 2;
const SANKEY_LAYOUT_MAX_VALUE = 16;
const STAGE_STEP_DURATION = 0.92;
const STAGE_STEP_EASE = "power2.inOut";
const STAGE_GESTURE_TOLERANCE = 14;
const STAGE_GESTURE_COOLDOWN_MS = 180;

const FLOW_COLORS = {
  // Beta 1.0 source block: manual feedback as the legacy evidence root.
  legacy_source: "#3f4a41",
  // Beta 1.0 outcome blocks: manual PASS / PARTIAL / FAIL buckets.
  legacy_outcome: "#6f6a67",
  // Beta 1.0 signal blocks: extracted manual-eval signal categories.
  legacy_signal: "#985323",
  // Middle continuity block: evidence continuity between eras.
  bridge: "#3f4a41",
  // Beta 2.0 source block: current OCR binary gate report root.
  current_source: "#2f2336",
  // Beta 2.0 lane blocks: OCR lanes such as text, handwriting, illustration.
  current_lane: "#8fa09c",
  // Beta 2.0 outcome blocks: binary gate PASS / FAIL buckets.
  current_outcome: "#4d485f",
  // Beta 1.0 source -> outcome ribbons.
  legacy_feedback_to_outcome: "#3f4a41",
  // Beta 1.0 outcome -> signal ribbons.
  legacy_outcome_to_signal: "#985323",
  // Beta 1.0 signal -> continuity bridge ribbons.
  legacy_signal_to_bridge: "#3f4a41",
  // Continuity bridge -> Beta 2.0 lane ribbons.
  bridge_to_current_lane: "#2f2336",
  // Beta 2.0 source -> OCR lane ribbons.
  current_report_to_lane: "#2f2336",
  // Beta 2.0 OCR lane -> outcome ribbons.
  current_lane_to_outcome: "#4d485f",
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

function scaleGraphForLayout(graph) {
  const rawIncoming = new Map();
  const rawOutgoing = new Map();
  const positiveRawValues = (graph?.links ?? [])
    .map((link) => {
      const rawValue = Number(link?.value) || 0;
      const source = String(link?.source ?? "");
      const target = String(link?.target ?? "");
      rawOutgoing.set(source, (rawOutgoing.get(source) ?? 0) + rawValue);
      rawIncoming.set(target, (rawIncoming.get(target) ?? 0) + rawValue);
      return rawValue;
    })
    .filter((value) => value > 0);
  const minRaw = positiveRawValues.length ? Math.min(...positiveRawValues) : 0;
  const maxRaw = positiveRawValues.length ? Math.max(...positiveRawValues) : 0;
  const minLog = Math.log1p(minRaw);
  const maxLog = Math.log1p(maxRaw);
  const denom = Math.max(maxLog - minLog, Number.EPSILON);

  return {
    nodes: (graph?.nodes ?? []).map((node) => ({
      ...node,
      rawValue: Math.max(rawIncoming.get(node.id) ?? 0, rawOutgoing.get(node.id) ?? 0),
    })),
    links: (graph?.links ?? []).map((link) => {
      const rawValue = Number(link?.value) || 0;
      const scaledValue = rawValue > 0
        ? SANKEY_LAYOUT_MIN_VALUE
          + ((Math.log1p(rawValue) - minLog) / denom) * (SANKEY_LAYOUT_MAX_VALUE - SANKEY_LAYOUT_MIN_VALUE)
        : 0;
      return { ...link, rawValue, value: scaledValue };
    }),
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
  return FLOW_COLORS[link.kind] ?? "rgba(35, 35, 35, 0.45)";
}

function formatNumber(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    return "0";
  }
  return new Intl.NumberFormat("en").format(n);
}

function drawGraphSankey(payload, surfaceConfig) {
  const sankeySurface = document.getElementById(surfaceConfig.surfaceId);
  const svgNode = document.getElementById(surfaceConfig.svgId);
  if (!(sankeySurface instanceof HTMLElement) || !(svgNode instanceof SVGSVGElement)) {
    return;
  }

  const width = Math.max(svgNode.clientWidth, 1);
  const height = Math.max(svgNode.clientHeight, 1);
  const svg = d3.select(svgNode);
  svg.attr("viewBox", `0 0 ${width} ${height}`);
  svg.selectAll("*").remove();

  const graphs = payload?.graphs ?? EMPTY_GRAPHS;
  const graph = scaleGraphForLayout(graphs[surfaceConfig.graphKey] ?? EMPTY_GRAPHS[surfaceConfig.graphKey]);
  if (!graphHasData(graph)) {
    svg
      .append("text")
      .attr("class", "sankey-empty-text")
      .attr("x", width / 2)
      .attr("y", height / 2)
      .attr("text-anchor", "middle")
      .text(surfaceConfig.emptyText);
    return;
  }

  const chartWidth = width;
  const chartLeft = 0;
  const insetX = 0;
  const chartHeight = Math.round(
    Math.min(height - 32, Math.max(260, height * 0.52))
  );
  const chartTop = Math.round((height - chartHeight) / 2);
  const insetY = Math.max(16, Math.round(chartHeight * 0.07));

  const layout = sankey()
    .nodeId((node) => node.id)
    .nodeWidth(Math.max(16, Math.round(chartWidth * 0.011)))
    .nodePadding(Math.max(10, Math.round(height * 0.02)))
    .extent([
      [chartLeft + insetX, chartTop + insetY],
      [chartLeft + chartWidth - insetX, chartTop + chartHeight - insetY],
    ]);

  const sankeyGraph = layout(cloneGraph(graph));

  const nodeAdjacency = new Map();
  sankeyGraph.nodes.forEach((node) => nodeAdjacency.set(node.id, new Set([node.id])));
  sankeyGraph.links.forEach((link) => {
    nodeAdjacency.get(link.source.id)?.add(link.target.id);
    nodeAdjacency.get(link.target.id)?.add(link.source.id);
  });

  const linkSelection = svg
    .append("g")
    .selectAll("path")
    .data(sankeyGraph.links)
    .join("path")
    .attr("class", "sankey-link")
    .attr("d", sankeyLinkHorizontal())
    .attr("stroke", (link) => linkColor(link))
    .attr("stroke-width", (link) => Math.max(1, link.width));

  linkSelection
    .append("title")
    .text((link) => {
      const source = link.source.label ?? link.source.id;
      const target = link.target.label ?? link.target.id;
      return `${source} -> ${target}: ${formatNumber(link.rawValue ?? link.value)}`;
    });

  const nodeSelection = svg
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
    .attr("rx", 1.5);

  svg
    .append("g")
    .attr("class", "sankey-node-caps")
    .selectAll("line")
    .data(sankeyGraph.nodes)
    .join("line")
    .attr("class", "sankey-node-cap")
    .attr("x1", (node) => node.x0)
    .attr("x2", (node) => node.x1)
    .attr("y1", (node) => node.y0)
    .attr("y2", (node) => node.y0);

  nodeSelection
    .append("title")
    .text((node) => `${node.label ?? node.id}: ${formatNumber(node.rawValue ?? node.value)}`);

  const clearFocus = () => {
    svg.classed("is-focus", false);
    nodeSelection.classed("is-active", false).classed("is-dimmed", false);
    linkSelection.classed("is-active", false).classed("is-dimmed", false);
  };

  const focusNode = (focusNodeDatum) => {
    const relatedNodes = nodeAdjacency.get(focusNodeDatum.id) ?? new Set([focusNodeDatum.id]);
    svg.classed("is-focus", true);
    nodeSelection
      .classed("is-active", (node) => relatedNodes.has(node.id))
      .classed("is-dimmed", (node) => !relatedNodes.has(node.id));
    linkSelection
      .classed("is-active", (link) => link.source.id === focusNodeDatum.id || link.target.id === focusNodeDatum.id)
      .classed("is-dimmed", (link) => !(link.source.id === focusNodeDatum.id || link.target.id === focusNodeDatum.id));
  };

  const focusLink = (focusLinkDatum) => {
    const relatedNodes = new Set([focusLinkDatum.source.id, focusLinkDatum.target.id]);
    svg.classed("is-focus", true);
    nodeSelection
      .classed("is-active", (node) => relatedNodes.has(node.id))
      .classed("is-dimmed", (node) => !relatedNodes.has(node.id));
    linkSelection
      .classed("is-active", (link) => link === focusLinkDatum)
      .classed("is-dimmed", (link) => link !== focusLinkDatum);
  };

  nodeSelection
    .on("mouseenter", (_, node) => focusNode(node))
    .on("mouseleave", clearFocus);

  linkSelection
    .on("mouseenter", (_, link) => focusLink(link))
    .on("mouseleave", clearFocus);

  svg.on("mouseleave", clearFocus);
}

function setupSankeyDataWiring() {
  const sankeySurfaces = SANKEY_SURFACES
    .map((surfaceConfig) => document.getElementById(surfaceConfig.surfaceId))
    .filter((element) => element instanceof HTMLElement);
  if (!sankeySurfaces.length) {
    return () => {};
  }

  let resizeFrame = 0;
  let payload = null;

  const setSurfaceState = (state, reason = "") => {
    sankeySurfaces.forEach((surface) => {
      surface.dataset.state = state;
      if (reason) {
        surface.dataset.reason = reason;
      } else {
        delete surface.dataset.reason;
      }
    });
  };

  const render = () => {
    SANKEY_SURFACES.forEach((surfaceConfig) => drawGraphSankey(payload, surfaceConfig));
  };

  const onResize = () => {
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
    }
    resizeFrame = requestAnimationFrame(render);
  };

  const load = async () => {
    setSurfaceState("loading");
    try {
      const response = await fetch(SANKEY_DATA_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      payload = await response.json();
      window.__POLINKO_SANKEY_DATA__ = payload;
      setSurfaceState(payload?.available ? "ready" : "empty", payload?.available ? "" : payload?.reason ?? "No Sankey data available");
      window.dispatchEvent(new CustomEvent("polinko:sankey-data", { detail: payload }));
    } catch (error) {
      payload = {
        available: false,
        reason: error instanceof Error ? error.message : String(error),
        graphs: EMPTY_GRAPHS,
      };
      setSurfaceState("error", payload.reason);
    }
    render();
  };

  window.addEventListener("resize", onResize);
  load();
  return () => {
    window.removeEventListener("resize", onResize);
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
    }
  };
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
    { id: "beta-one-sankey", row: 2, column: 1 },
    { id: "sankey-bridge", row: 2, column: 2 },
    { id: "beta-two-sankey", row: 2, column: 3 },
    { id: "pipeline-two", row: 2, column: 4 },
    { id: "conclusion", row: 3, column: 4 },
    { id: "about-lab", row: 4, column: 4 },
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
