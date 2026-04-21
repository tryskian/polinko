import fs from "node:fs";
import path from "node:path";
import { JSDOM } from "jsdom";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

const [, , inputPath, outputPath] = process.argv;

if (!inputPath || !outputPath) {
  console.error("Usage: node tools/render_public_d3_diagrams.mjs <input.json> <output.svg>");
  process.exit(1);
}

const payload = JSON.parse(fs.readFileSync(inputPath, "utf8"));
const legacyGraph = payload.graphs?.legacy;
const bridgeGraph = payload.graphs?.bridge;

if (!legacyGraph || !bridgeGraph) {
  console.error("Required legacy/bridge graphs are missing from the Sankey payload.");
  process.exit(1);
}

const width = 1440;
const height = 760;
const margin = { top: 96, right: 64, bottom: 56, left: 64 };
const diagramTop = 150;
const diagramBottom = height - 72;
const nodeWidth = 16;

const dom = new JSDOM("<!DOCTYPE html><body></body>");
const body = d3.select(dom.window.document).select("body");
const svg = body
  .append("svg")
  .attr("xmlns", "http://www.w3.org/2000/svg")
  .attr("width", width)
  .attr("height", height)
  .attr("viewBox", `0 0 ${width} ${height}`)
  .attr("role", "img")
  .attr("aria-label", "Polinko evidence sankey")
  .style("background", "transparent");

const signalNodeMap = new Map();
legacyGraph.nodes
  .filter((node) => node.group === "legacy_signal")
  .forEach((node) => {
    signalNodeMap.set(node.id, {
      id: node.id.replace("legacy_signal_", "signal_"),
      label: node.label,
      group: "signal",
    });
  });

const laneNodeMap = new Map();
bridgeGraph.nodes
  .filter((node) => node.group === "current_lane")
  .forEach((node) => {
    laneNodeMap.set(node.id, {
      id: node.id.replace("bridge_lane_", "lane_"),
      label: node.label,
      group: "current_lane",
    });
  });

function remapNodeId(id) {
  if (id.startsWith("legacy_signal_")) {
    return id.replace("legacy_signal_", "signal_");
  }
  if (id.startsWith("bridge_signal_")) {
    return id.replace("bridge_signal_", "signal_");
  }
  if (id.startsWith("bridge_lane_")) {
    return id.replace("bridge_lane_", "lane_");
  }
  return id;
}

const nodes = new Map();

function upsertNode(node) {
  if (!nodes.has(node.id)) {
    nodes.set(node.id, { ...node });
  }
}

legacyGraph.nodes
  .filter((node) => node.group !== "legacy_signal")
  .forEach((node) => upsertNode(node));
signalNodeMap.forEach((node) => upsertNode(node));
laneNodeMap.forEach((node) => upsertNode(node));

const links = [];

legacyGraph.links.forEach((link) => {
  links.push({
    source: remapNodeId(link.source),
    target: remapNodeId(link.target),
    value: link.value,
    kind: link.kind,
  });
});

bridgeGraph.links.forEach((link) => {
  links.push({
    source: remapNodeId(link.source),
    target: remapNodeId(link.target),
    value: link.value,
    kind: link.kind,
  });
});

const graph = {
  nodes: Array.from(nodes.values()),
  links,
};

svg
  .append("text")
  .attr("x", margin.left)
  .attr("y", 50)
  .attr("fill", "#171717")
  .attr("font-family", "Arial, Helvetica, sans-serif")
  .attr("font-size", 20)
  .attr("font-weight", 600)
  .text("Polinko Evidence Sankey");

svg
  .append("text")
  .attr("x", margin.left)
  .attr("y", 76)
  .attr("fill", "#666666")
  .attr("font-family", "Arial, Helvetica, sans-serif")
  .attr("font-size", 12)
  .text(
    `Static D3 Sankey generated from /portfolio/sankey-data • ${payload.summary.legacy_signal_mentions} tagged signal mentions`
  );

svg
  .append("text")
  .attr("x", width - margin.right)
  .attr("y", 76)
  .attr("fill", "#666666")
  .attr("font-family", "Arial, Helvetica, sans-serif")
  .attr("font-size", 12)
  .attr("text-anchor", "end")
  .text("Legacy -> bridge continuity");

const layout = sankey()
  .nodeId((d) => d.id)
  .nodeAlign((node, n) => {
    const layerByGroup = {
      legacy_source: 0,
      legacy_outcome: 1,
      signal: 2,
      current_lane: 3,
    };
    const layer = layerByGroup[node.group];
    if (typeof layer === "number") {
      return Math.min(layer, n - 1);
    }
    return Math.min(node.depth ?? 0, n - 1);
  })
  .nodeWidth(nodeWidth)
  .nodePadding(20)
  .nodeSort(null)
  .extent([
    [margin.left, diagramTop],
    [width - margin.right, diagramBottom],
  ]);

const sankeyData = layout({
  nodes: graph.nodes.map((node) => ({ ...node })),
  links: graph.links.map((link) => ({ ...link })),
});

function nodeColor(node) {
  const id = node.id ?? "";
  const group = node.group ?? "";

  if (group === "legacy_source") return "#4E79A7";
  if (group === "legacy_outcome") {
    if (id.includes("fail")) return "#E15759";
    if (id.includes("partial")) return "#F28E2B";
    if (id.includes("pass")) return "#59A14F";
    return "#777777";
  }
  if (group === "signal") return "#76B7B2";
  if (group === "current_lane") {
    if (id.includes("handwriting")) return "#B07AA1";
    if (id.includes("illustration")) return "#9C755F";
    if (id.includes("text")) return "#EDC948";
    return "#A0CBE8";
  }
  return "#7a7a7a";
}

function linkColor(link) {
  const sourceGroup = link.source.group ?? "";
  const baseNode =
    sourceGroup === "signal" || sourceGroup === "legacy_source" ? link.target : link.source;
  const base = d3.color(nodeColor(baseNode));
  base.opacity = 0.38;
  return base.formatRgb();
}

svg
  .append("g")
  .attr("fill", "none")
  .selectAll("path")
  .data(sankeyData.links)
  .join("path")
  .attr("d", sankeyLinkHorizontal())
  .attr("stroke", linkColor)
  .attr("stroke-width", (d) => Math.max(1, d.width))
  .attr("stroke-linecap", "butt");

const nodesGroup = svg
  .append("g")
  .selectAll("g")
  .data(sankeyData.nodes)
  .join("g");

nodesGroup
  .append("rect")
  .attr("x", (d) => d.x0)
  .attr("y", (d) => d.y0)
  .attr("height", (d) => Math.max(1, d.y1 - d.y0))
  .attr("width", (d) => d.x1 - d.x0)
  .attr("rx", 0)
  .attr("fill", nodeColor)
  .attr("stroke", "#4a4a4a")
  .attr("stroke-width", 0.5);

nodesGroup
  .append("text")
  .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + 10 : d.x0 - 10))
  .attr("y", (d) => (d.y0 + d.y1) / 2 - 4)
  .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
  .attr("fill", "#202020")
  .attr("font-family", "Arial, Helvetica, sans-serif")
  .attr("font-size", 11.5)
  .attr("font-weight", 600)
  .text((d) => d.label);

nodesGroup
  .append("text")
  .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + 10 : d.x0 - 10))
  .attr("y", (d) => (d.y0 + d.y1) / 2 + 13)
  .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
  .attr("fill", "#666666")
  .attr("font-family", "Arial, Helvetica, sans-serif")
  .attr("font-size", 11)
  .text((d) => `${Math.round(d.value ?? 0)}`);

const stageMeta = [
  { group: "legacy_source", label: "Manual evals" },
  { group: "legacy_outcome", label: "Manual outcomes" },
  { group: "signal", label: "Signal classes" },
  { group: "current_lane", label: "Current OCR lanes" },
];

stageMeta.forEach((stage) => {
  const stageNodes = sankeyData.nodes.filter((node) => node.group === stage.group);
  if (!stageNodes.length) return;
  const centerX = d3.mean(stageNodes, (node) => (node.x0 + node.x1) / 2);
  svg
    .append("text")
    .attr("x", centerX)
    .attr("y", 124)
    .attr("text-anchor", "middle")
    .attr("fill", "#555555")
    .attr("font-family", "Arial, Helvetica, sans-serif")
    .attr("font-size", 11)
    .attr("font-weight", 600)
    .text(stage.label);
});

svg
  .append("text")
  .attr("x", margin.left)
  .attr("y", height - 26)
  .attr("fill", "#666666")
  .attr("font-family", "Arial, Helvetica, sans-serif")
  .attr("font-size", 11)
  .text("Beta 1.0 manual evals flow into tagged failure signals, then into current OCR lane weighting.");

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, body.html());
