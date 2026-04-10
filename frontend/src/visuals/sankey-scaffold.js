import { select } from "d3-selection";
import { sankey as createSankeyGenerator, sankeyLinkHorizontal } from "d3-sankey";

const EVIDENCE_GRAPHS = {
  established: {
    title: "Established Interaction Surface",
    nodes: [
      { name: "Prompt Inputs" },
      { name: "Policy Routing" },
      { name: "Response Assembly" },
      { name: "User Interpretation" },
    ],
    links: [
      {
        source: 0,
        target: 1,
        value: 72,
        evidence: "conversation 69740f67: assumption enters before reset",
      },
      {
        source: 1,
        target: 2,
        value: 63,
        evidence: "assistant reframing pressure before direct answer",
      },
      {
        source: 2,
        target: 3,
        value: 58,
        evidence: "interpretation burden shifts to user correction",
      },
    ],
  },
  binary: {
    title: "Binary Eval Architecture Surface",
    nodes: [
      { name: "Observed Failures" },
      { name: "Intervention Buckets" },
      { name: "Replay Outcomes" },
      { name: "Pass/Fail Gate" },
    ],
    links: [
      {
        source: 0,
        target: 1,
        value: 16,
        evidence: "fail cohort snapshot: selected_fail_cases=16",
      },
      {
        source: 1,
        target: 2,
        value: 23,
        evidence: "growth lane run: growth_cases=23",
      },
      {
        source: 2,
        target: 3,
        value: 21,
        evidence: "stability replay: 21/21 pass reference",
      },
    ],
  },
};

function buildGraph(surfaceType) {
  return EVIDENCE_GRAPHS[surfaceType] ?? EVIDENCE_GRAPHS.established;
}

export function initSankeyScaffold() {
  const surfaces = Array.from(document.querySelectorAll("[data-sankey-surface]"));
  if (!surfaces.length) {
    return;
  }

  surfaces.forEach((surface) => {
    const surfaceType = surface.getAttribute("data-sankey-surface") ?? "established";
    const graphInput = buildGraph(surfaceType);
    const root = select(surface);
    root.selectAll("*").remove();

    const width = surface.clientWidth || 840;
    const height = surface.clientHeight || 420;

    const svg = root
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    svg
      .append("text")
      .attr("x", 20)
      .attr("y", 26)
      .attr("font-size", 13)
      .attr("font-weight", 700)
      .attr("fill", "rgba(0,0,0,0.62)")
      .text(graphInput.title);

    const generator = createSankeyGenerator()
      .nodeWidth(18)
      .nodePadding(22)
      .extent([
        [20, 46],
        [width - 20, height - 24],
      ]);

    const graph = generator({
      nodes: graphInput.nodes.map((node) => ({ ...node })),
      links: graphInput.links.map((link) => ({ ...link })),
    });

    const linkGroup = svg.append("g");
    const linkPath = sankeyLinkHorizontal();

    linkGroup
      .selectAll("path")
      .data(graph.links)
      .enter()
      .append("path")
      .attr("d", linkPath)
      .attr("fill", "none")
      .attr("stroke", "rgba(0,0,0,0.28)")
      .attr("stroke-linecap", "round")
      .attr("stroke-width", (d) => Math.max(1, d.width))
      .append("title")
      .text((d) => `${d.source.name} -> ${d.target.name}\n${d.evidence}`);

    svg
      .append("g")
      .selectAll("rect")
      .data(graph.nodes)
      .enter()
      .append("rect")
      .attr("x", (d) => d.x0)
      .attr("y", (d) => d.y0)
      .attr("width", (d) => d.x1 - d.x0)
      .attr("height", (d) => Math.max(1, d.y1 - d.y0))
      .attr("rx", 8)
      .attr("fill", "rgba(255,255,255,0.35)")
      .attr("stroke", "rgba(0,0,0,0.2)");

    svg
      .append("g")
      .selectAll("text")
      .data(graph.nodes)
      .enter()
      .append("text")
      .attr("x", (d) => d.x0 + 6)
      .attr("y", (d) => d.y0 - 8)
      .attr("font-size", 12)
      .attr("fill", "rgba(0,0,0,0.64)")
      .text((d) => d.name);
  });
}
