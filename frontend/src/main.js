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
const SANKEY_SURFACE_ID = "beta-one-sankey";
const SANKEY_SVG_ID = "beta-one-sankey-svg";
const SANKEY_LAYOUT_MIN_VALUE = 2;
const SANKEY_LAYOUT_MAX_VALUE = 16;
const STAGE_STEP_DURATION = 0.92;
const STAGE_STEP_EASE = "power2.inOut";
const STAGE_GESTURE_TOLERANCE = 14;
const STAGE_GESTURE_COOLDOWN_MS = 180;

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

function remapNodeId(id) {
  if (id.startsWith("bridge_signal_")) {
    return id.replace("bridge_signal_", "legacy_signal_");
  }
  if (id.startsWith("bridge_lane_")) {
    return id.replace("bridge_lane_", "current_lane_");
  }
  return id;
}

function buildComparativeGraph(graphs) {
  const nodes = new Map();
  const links = new Map();
  const incoming = new Map();
  const outgoing = new Map();

  const addNode = (node) => {
    const id = remapNodeId(String(node?.id ?? ""));
    if (!id) {
      return;
    }
    if (!nodes.has(id)) {
      nodes.set(id, { ...node, id });
    }
  };

  const addLink = (link) => {
    const source = remapNodeId(String(link?.source ?? ""));
    const target = remapNodeId(String(link?.target ?? ""));
    if (!source || !target) {
      return;
    }
    const value = Number(link?.value) || 0;
    const kind = String(link?.kind ?? "");
    const key = `${source}__${target}__${kind}`;
    if (!links.has(key)) {
      links.set(key, {
        source,
        target,
        value: 0,
        kind,
        provenance: link?.provenance ?? "",
      });
    }
    const row = links.get(key);
    row.value += value;
    outgoing.set(source, (outgoing.get(source) ?? 0) + value);
    incoming.set(target, (incoming.get(target) ?? 0) + value);
  };

  [graphs?.legacy, graphs?.bridge, graphs?.current].forEach((graph) => {
    (graph?.nodes ?? []).forEach(addNode);
    (graph?.links ?? []).forEach(addLink);
  });

  return {
    nodes: Array.from(nodes.values()).map((node) => ({
      ...node,
      rawValue: Math.max(incoming.get(node.id) ?? 0, outgoing.get(node.id) ?? 0),
    })),
    links: Array.from(links.values()),
  };
}

function scaleGraphForLayout(graph) {
  const positiveRawValues = (graph?.links ?? [])
    .map((link) => Number(link?.value) || 0)
    .filter((value) => value > 0);
  const minRaw = positiveRawValues.length ? Math.min(...positiveRawValues) : 0;
  const maxRaw = positiveRawValues.length ? Math.max(...positiveRawValues) : 0;
  const minLog = Math.log1p(minRaw);
  const maxLog = Math.log1p(maxRaw);
  const denom = Math.max(maxLog - minLog, Number.EPSILON);

  return {
    nodes: (graph?.nodes ?? []).map((node) => ({ ...node })),
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

function drawComparativeSankey(payload) {
  const sankeySurface = document.getElementById(SANKEY_SURFACE_ID);
  const svgNode = document.getElementById(SANKEY_SVG_ID);
  if (!(sankeySurface instanceof HTMLElement) || !(svgNode instanceof SVGSVGElement)) {
    return;
  }

  const width = Math.max(svgNode.clientWidth, 1);
  const height = Math.max(svgNode.clientHeight, 1);
  const svg = d3.select(svgNode);
  svg.attr("viewBox", `0 0 ${width} ${height}`);
  svg.selectAll("*").remove();

  const graphs = payload?.graphs ?? EMPTY_GRAPHS;
  const graph = scaleGraphForLayout(buildComparativeGraph(graphs));
  if (!graphHasData(graph)) {
    svg
      .append("text")
      .attr("class", "sankey-empty-text")
      .attr("x", width / 2)
      .attr("y", height / 2)
      .attr("text-anchor", "middle")
      .text("No Sankey data available");
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
    .nodeWidth(Math.max(19, Math.round(chartWidth * 0.0135)))
    .nodePadding(Math.max(8, Math.round(height * 0.018)))
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
    .attr("fill", (node) => nodeColor(node));

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
  const sankeySurface = document.getElementById(SANKEY_SURFACE_ID);
  if (!(sankeySurface instanceof HTMLElement)) {
    return () => {};
  }

  let resizeFrame = 0;
  let payload = null;

  const render = () => drawComparativeSankey(payload);

  const onResize = () => {
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
    }
    resizeFrame = requestAnimationFrame(render);
  };

  const load = async () => {
    sankeySurface.dataset.state = "loading";
    try {
      const response = await fetch(SANKEY_DATA_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      payload = await response.json();
      window.__POLINKO_SANKEY_DATA__ = payload;
      sankeySurface.dataset.state = payload?.available ? "ready" : "empty";
      if (!payload?.available) {
        sankeySurface.dataset.reason = payload?.reason ?? "No Sankey data available";
      }
      window.dispatchEvent(new CustomEvent("polinko:sankey-data", { detail: payload }));
    } catch (error) {
      payload = {
        available: false,
        reason: error instanceof Error ? error.message : String(error),
        graphs: EMPTY_GRAPHS,
      };
      sankeySurface.dataset.state = "error";
      sankeySurface.dataset.reason = payload.reason;
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
