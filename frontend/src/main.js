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
const SANKEY_NODE_WIDTH = 12;
const SANKEY_NODE_PADDING = 8;
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
    linkWidthScale: 0.6,
  },
];
const SANKEY_LAYOUT_MIN_VALUE = 2;
const SANKEY_LAYOUT_MAX_VALUE = 10;
const STAGE_STEP_DURATION = 0.92;
const STAGE_STEP_EASE = "power2.inOut";
const STAGE_GESTURE_TOLERANCE = 14;
const STAGE_GESTURE_COOLDOWN_MS = 180;
const NODE_BAR_COLOR = "#080806";

// SANKey palette edit zone START
// Edit swatch values here for live visual tuning. Keep the keys stable unless
// the backend graph groups/kinds change.
const FLOW_COLORS = {
  // Shared source blocks.
  legacy_source: "#3C5F40",
  bridge: "#3C5F40",
  current_source: "#503286",

  // Group fallbacks when a node/link does not have a specific colour below.
  legacy_outcome: "#CBDCCC",
  legacy_signal: "#FF8D28",
  current_lane: "#9DC5C3",
  current_outcome: "#FB9497",

  // Beta 1.0 outcome buckets.
  legacy_outcome_fail: "#FF8D28",
  legacy_outcome_partial: "#FFD9B7",
  legacy_outcome_pass: "#9DC5C3",

  // Beta 1.0 signal categories.
  legacy_signal_correctness: "#9DC5C3",
  legacy_signal_general_eval: "#CBDCCC",
  legacy_signal_grounding: "#3C5F40",
  legacy_signal_hallucination_risk: "#FF8D28",
  legacy_signal_ocr_signal: "#503286",
  legacy_signal_recovery: "#D3C8E6",
  legacy_signal_style_voice: "#FB9497",
  bridge_signal_correctness: "#9DC5C3",
  bridge_signal_general_eval: "#CBDCCC",
  bridge_signal_grounding: "#3C5F40",
  bridge_signal_hallucination_risk: "#FF8D28",
  bridge_signal_ocr_signal: "#503286",
  bridge_signal_recovery: "#D3C8E6",
  bridge_signal_style_voice: "#FB9497",

  // Beta 2.0 OCR lanes.
  bridge_lane_handwriting: "#9DC5C3",
  bridge_lane_illustration: "#503286",
  bridge_lane_text: "#3C5F40",
  current_lane_handwriting: "#9DC5C3",
  current_lane_illustration: "#503286",
  current_lane_text: "#3C5F40",

  // Beta 2.0 binary gate outcomes.
  current_outcome_fail: "#FF8D28",
  current_outcome_pass: "#CBDCCC",

  // Link fallbacks. Specific node colours above take precedence.
  legacy_feedback_to_outcome: "#3C5F40",
  legacy_outcome_to_signal: "#FF8D28",
  legacy_signal_to_bridge: "#3C5F40",
  bridge_to_current_lane: "#503286",
  current_report_to_lane: "#503286",
  current_lane_to_outcome: "#FB9497",
};
// SANKey palette edit zone END

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

function scaleGraphValues(graph, scale = 1) {
  if (scale === 1) {
    return graph;
  }

  return {
    nodes: graph.nodes,
    links: graph.links.map((link) => ({
      ...link,
      value: link.value * scale,
    })),
  };
}

function graphHasData(graph) {
  return Array.isArray(graph?.nodes) && graph.nodes.length > 0
    && Array.isArray(graph?.links) && graph.links.length > 0;
}

function nodeColor(node) {
  return NODE_BAR_COLOR;
}

function linkColor(link) {
  const sourceId = typeof link.source === "object" ? link.source.id : link.source;
  const targetId = typeof link.target === "object" ? link.target.id : link.target;
  if (link.kind === "bridge_signal_to_lane") {
    return FLOW_COLORS[sourceId] ?? FLOW_COLORS[link.kind] ?? "rgba(35, 35, 35, 0.45)";
  }
  return FLOW_COLORS[`${sourceId}->${targetId}`]
    ?? FLOW_COLORS[`${link.kind}:${targetId}`]
    ?? FLOW_COLORS[`${link.kind}:${sourceId}`]
    ?? FLOW_COLORS[targetId]
    ?? FLOW_COLORS[sourceId]
    ?? FLOW_COLORS[link.kind]
    ?? "rgba(35, 35, 35, 0.45)";
}

function formatNumber(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    return "0";
  }
  return new Intl.NumberFormat("en").format(n);
}

function chartLeftFor(width, chartWidth, align = "start") {
  if (align === "end") {
    return width - chartWidth;
  }
  if (align === "center") {
    return Math.round((width - chartWidth) / 2);
  }
  return 0;
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
  const graph = scaleGraphValues(
    scaleGraphForLayout(graphs[surfaceConfig.graphKey] ?? EMPTY_GRAPHS[surfaceConfig.graphKey]),
    surfaceConfig.linkWidthScale ?? 1
  );
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

  const chartWidth = Math.round(width * (surfaceConfig.chartWidthScale ?? 1));
  const chartLeft = chartLeftFor(width, chartWidth, surfaceConfig.chartAlign);
  const insetX = 0;
  const chartHeight = Math.round(
    Math.min(height - 32, Math.max(260, height * 0.52))
  );
  const chartTop = Math.round((height - chartHeight) / 2);
  const insetY = Math.max(16, Math.round(chartHeight * 0.07));

  const layout = sankey()
    .nodeId((node) => node.id)
    .nodeWidth(Math.max(SANKEY_NODE_WIDTH, Math.round(chartWidth * 0.00825)))
    .nodePadding(SANKEY_NODE_PADDING)
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
