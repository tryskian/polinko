import "./styles.css";
import { gsap } from "gsap";
import * as THREE from "three";
import * as d3 from "d3";
import { sankey as d3Sankey, sankeyLinkHorizontal } from "d3-sankey";
import twinSankeyRaw from "./data/twin_sankey_raw.json";

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

function normalizeTwinSankeyConfig(rawPayload) {
  if (!rawPayload || !Array.isArray(rawPayload.sankeys)) {
    return [];
  }
  return rawPayload.sankeys
    .filter((entry) => entry && typeof entry.id === "string" && entry.data)
    .map((entry) => ({
      id: entry.id,
      data: {
        nodes: Array.isArray(entry.data.nodes) ? entry.data.nodes : [],
        links: Array.isArray(entry.data.links) ? entry.data.links : [],
      },
    }));
}

const TWIN_SANKEY_CONFIG = normalizeTwinSankeyConfig(twinSankeyRaw);

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

function cloneSankeyData(data) {
  return {
    nodes: data.nodes.map((node) => ({ ...node })),
    links: data.links.map((link) => ({ ...link })),
  };
}

function setupTwinSankeys() {
  const cleanups = [];

  TWIN_SANKEY_CONFIG.forEach((config) => {
    const wrap = document.querySelector(`.sankey-chart-wrap[data-sankey-id="${config.id}"]`);
    if (!(wrap instanceof HTMLElement)) {
      return;
    }

    const svgElement = wrap.querySelector(".sankey-chart");
    if (!(svgElement instanceof SVGElement)) {
      return;
    }

    let graph = null;
    let nodeGroups = null;
    let linkPaths = null;

    const applyHighlight = (activeItem) => {
      if (!graph || !nodeGroups || !linkPaths) {
        return;
      }
      const activeNodeIds = new Set();
      const activeLinkIds = new Set();

      if (activeItem?.type === "node") {
        activeNodeIds.add(activeItem.id);
        graph.links.forEach((link) => {
          if (link.source.id === activeItem.id || link.target.id === activeItem.id) {
            activeLinkIds.add(link.id);
            activeNodeIds.add(link.source.id);
            activeNodeIds.add(link.target.id);
          }
        });
      } else if (activeItem?.type === "link") {
        const link = graph.links.find((entry) => entry.id === activeItem.id);
        if (link) {
          activeLinkIds.add(link.id);
          activeNodeIds.add(link.source.id);
          activeNodeIds.add(link.target.id);
        }
      }

      nodeGroups
        .selectAll("rect")
        .classed("is-active", (node) => activeNodeIds.has(node.id))
        .classed("is-dim", (node) => activeNodeIds.size > 0 && !activeNodeIds.has(node.id));

      linkPaths
        .classed("is-active", (link) => activeLinkIds.has(link.id))
        .classed("is-dim", (link) => activeLinkIds.size > 0 && !activeLinkIds.has(link.id));
    };

    const activateNode = (node) => {
      applyHighlight({ type: "node", id: node.id });
    };

    const activateLink = (link) => {
      applyHighlight({ type: "link", id: link.id });
    };

    const clearActive = () => {
      applyHighlight(null);
    };

    const render = () => {
      const bounds = wrap.getBoundingClientRect();
      const width = Math.max(1, Math.floor(bounds.width));
      const height = Math.max(1, Math.floor(bounds.height));
      const isFull = wrap.closest(".sankey-shell-full");
      const margin = isFull
        ? { top: 0, right: 0, bottom: 0, left: 0 }
        : { top: 20, right: 16, bottom: 16, left: 16 };

      const svg = d3.select(svgElement);
      svg.selectAll("*").remove();
      svg.attr("viewBox", `0 0 ${width} ${height}`);
      svg.attr("preserveAspectRatio", "xMidYMid meet");

      const sankey = d3Sankey()
        .nodeId((node) => node.id)
        .nodeWidth(18)
        .nodePadding(20)
        .extent([
          [margin.left, margin.top],
          [width - margin.right, height - margin.bottom],
        ]);

      graph = sankey(cloneSankeyData(config.data));

      linkPaths = svg
        .append("g")
        .attr("fill", "none")
        .selectAll("path")
        .data(graph.links)
        .join("path")
        .attr("class", "sankey-link-path")
        .attr("d", sankeyLinkHorizontal())
        .attr("stroke-width", (link) => Math.max(2, link.width))
        .on("mouseenter", (_, link) => activateLink(link))
        .on("mouseleave", () => clearActive());

      nodeGroups = svg
        .append("g")
        .selectAll("g")
        .data(graph.nodes)
        .join("g")
        .on("mouseenter", (_, node) => activateNode(node))
        .on("mouseleave", () => clearActive());

      nodeGroups
        .append("rect")
        .attr("class", "sankey-node-rect")
        .attr("x", (node) => node.x0)
        .attr("y", (node) => node.y0)
        .attr("width", (node) => Math.max(1, node.x1 - node.x0))
        .attr("height", (node) => Math.max(1, node.y1 - node.y0));

      nodeGroups
        .append("text")
        .attr("class", "sankey-node-label")
        .attr("x", (node) => (node.x0 < width / 2 ? node.x1 + 8 : node.x0 - 8))
        .attr("y", (node) => (node.y0 + node.y1) / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", (node) => (node.x0 < width / 2 ? "start" : "end"))
        .text((node) => node.name);

      clearActive();
    };

    const resizeObserver = new ResizeObserver(() => render());
    resizeObserver.observe(wrap);

    render();

    cleanups.push(() => {
      resizeObserver.disconnect();
    });
  });

  return () => {
    cleanups.forEach((cleanup) => cleanup());
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
const teardownPath = setupSectionPath();
const teardownSankeys = setupTwinSankeys();
const teardownMorph = setupConclusionMorph();

window.addEventListener("beforeunload", () => {
  teardownWebGL();
  teardownPath();
  teardownSankeys();
  teardownMorph();
});
