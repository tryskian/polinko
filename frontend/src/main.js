import "./styles.css";
import { gsap } from "gsap";
import * as THREE from "three";
import * as d3 from "d3";
import { sankey as d3Sankey, sankeyLinkHorizontal } from "d3-sankey";

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

const TWIN_SANKEY_CONFIG = [
  {
    id: "sankey-one",
    data: {
      nodes: [
        {
          id: "baseline_dense_gates",
          name: "Dense gate stack",
          stage: "Baseline",
          note: "High complexity routing before stable fail classification.",
        },
        {
          id: "baseline_summary_bias",
          name: "Summary-first routing",
          stage: "Baseline",
          note: "Compression logic over-prioritized concise output.",
        },
        {
          id: "baseline_uncertain_certainty",
          name: "Uncertainty -> certainty",
          stage: "Baseline",
          note: "Ambiguous states often collapsed into unsupported confidence.",
        },
        {
          id: "bridge_spine",
          name: "Bridge (Polinko Beta 1.0)",
          stage: "Bridge (Polinko Beta 1.0)",
          note: "Shared spine that normalizes flow into binary gate discipline.",
        },
      ],
      links: [
        {
          id: "l1",
          source: "baseline_dense_gates",
          target: "bridge_spine",
          value: 8,
          note: "Complexity tightened into explicit route boundaries.",
        },
        {
          id: "l2",
          source: "baseline_summary_bias",
          target: "bridge_spine",
          value: 6,
          note: "Summary bias rerouted through inspect-first checks.",
        },
        {
          id: "l3",
          source: "baseline_uncertain_certainty",
          target: "bridge_spine",
          value: 7,
          note: "Uncertainty now carried into explicit gate decisions.",
        },
      ],
    },
  },
  {
    id: "sankey-two",
    data: {
      nodes: [
        {
          id: "bridge_spine",
          name: "Bridge (Polinko Beta 1.0)",
          stage: "Bridge (Polinko Beta 1.0)",
          note: "Shared spine between Sankey A and Sankey B.",
        },
        {
          id: "beta2_lockset",
          name: "Lockset release lane",
          stage: "Polinko Beta 2.0",
          note: "Strict binary release lane with fail-closed authority.",
        },
        {
          id: "beta2_growth",
          name: "Growth learning lane",
          stage: "Polinko Beta 2.0",
          note: "Fail-rich lane for pass-from-fail learning signal.",
        },
        {
          id: "beta2_calibration",
          name: "Calibration discipline",
          stage: "Polinko Beta 2.0",
          note: "Explicit uncertainty boundaries and inspect-first posture.",
        },
      ],
      links: [
        {
          id: "l4",
          source: "bridge_spine",
          target: "beta2_lockset",
          value: 7,
          note: "Bridge stability routed into strict release gates.",
        },
        {
          id: "l5",
          source: "bridge_spine",
          target: "beta2_growth",
          value: 6,
          note: "Bridge lane split supports fail-rich exploration.",
        },
        {
          id: "l6",
          source: "bridge_spine",
          target: "beta2_calibration",
          value: 8,
          note: "Bridge logic carries uncertainty boundary controls.",
        },
      ],
    },
  },
];

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

  const updateActiveState = () => {
    sections.forEach((section, index) => {
      section.classList.toggle("is-active", index === activeIndex);
    });
  };

  const moveTo = (index, immediate = false) => {
    activeIndex = Math.max(0, Math.min(index, sections.length - 1));
    const target = sections[activeIndex];
    if (!(target instanceof HTMLElement)) {
      return;
    }
    updateActiveState();

    const duration = immediate ? 0 : 0.88;
    gsap.to(board, {
      x: -target.offsetLeft,
      y: -target.offsetTop,
      duration,
      ease: "power3.inOut",
      onStart: () => {
        isTransitioning = !immediate;
      },
      onComplete: () => {
        isTransitioning = false;
      },
    });
    window.dispatchEvent(
      new CustomEvent("polinko:section-change", {
        detail: { id: target.id, index: activeIndex },
      })
    );
  };

  const onWheel = (event) => {
    event.preventDefault();
    if (isTransitioning || Math.abs(event.deltaY) < 8) {
      return;
    }
    const direction = event.deltaY > 0 ? 1 : -1;
    moveTo(activeIndex + direction);
  };

  const onKey = (event) => {
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
    const detailElement = wrap.querySelector(".sankey-detail");
    const resetButton = wrap.querySelector(".sankey-detail-reset");
    if (!(svgElement instanceof SVGElement) || !(detailElement instanceof HTMLElement)) {
      return;
    }

    let pinned = null;
    let graph = null;
    let nodeGroups = null;
    let linkPaths = null;

    const setDetail = ({ mode, title, body }) => {
      const kicker = detailElement.querySelector(".sankey-detail-kicker");
      const titleNode = detailElement.querySelector(".sankey-detail-title");
      const bodyNode = detailElement.querySelector(".sankey-detail-body");
      if (kicker instanceof HTMLElement) {
        kicker.textContent = mode === "pinned" ? "Pinned Detail" : "Hover Detail";
      }
      if (titleNode instanceof HTMLElement) {
        titleNode.textContent = title;
      }
      if (bodyNode instanceof HTMLElement) {
        bodyNode.textContent = body;
      }
      detailElement.dataset.mode = mode;
      if (resetButton instanceof HTMLButtonElement) {
        resetButton.disabled = mode !== "pinned";
      }
    };

    const resetDetail = () => {
      setDetail({
        mode: "hover",
        title: "Hover a node or link",
        body: "Detail text appears here. Click to pin details.",
      });
    };

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

    const activateNode = (node, mode) => {
      const inbound = graph.links
        .filter((link) => link.target.id === node.id)
        .reduce((sum, link) => sum + link.value, 0);
      const outbound = graph.links
        .filter((link) => link.source.id === node.id)
        .reduce((sum, link) => sum + link.value, 0);
      applyHighlight({ type: "node", id: node.id });
      setDetail({
        mode,
        title: `${node.name} (${node.stage})`,
        body: `${node.note} Flow in: ${inbound}. Flow out: ${outbound}.`,
      });
    };

    const activateLink = (link, mode) => {
      applyHighlight({ type: "link", id: link.id });
      setDetail({
        mode,
        title: `${link.source.name} -> ${link.target.name}`,
        body: `${link.note} Placeholder weight: ${link.value}.`,
      });
    };

    const clearActive = () => {
      applyHighlight(null);
      resetDetail();
    };

    const render = () => {
      const bounds = wrap.getBoundingClientRect();
      const width = Math.max(480, Math.floor(bounds.width));
      const height = Math.max(260, Math.floor(bounds.height * 0.6));
      const margin = { top: 20, right: 16, bottom: 16, left: 16 };

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
        .on("mouseenter", (_, link) => {
          if (!pinned) {
            activateLink(link, "hover");
          }
        })
        .on("mouseleave", () => {
          if (!pinned) {
            clearActive();
          }
        })
        .on("click", (event, link) => {
          event.stopPropagation();
          if (pinned?.type === "link" && pinned.id === link.id) {
            pinned = null;
            clearActive();
            return;
          }
          pinned = { type: "link", id: link.id };
          activateLink(link, "pinned");
        });

      nodeGroups = svg
        .append("g")
        .selectAll("g")
        .data(graph.nodes)
        .join("g")
        .on("mouseenter", (_, node) => {
          if (!pinned) {
            activateNode(node, "hover");
          }
        })
        .on("mouseleave", () => {
          if (!pinned) {
            clearActive();
          }
        })
        .on("click", (event, node) => {
          event.stopPropagation();
          if (pinned?.type === "node" && pinned.id === node.id) {
            pinned = null;
            clearActive();
            return;
          }
          pinned = { type: "node", id: node.id };
          activateNode(node, "pinned");
        });

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

      svg.on("click", () => {
        pinned = null;
        clearActive();
      });

      if (pinned) {
        if (pinned.type === "node") {
          const node = graph.nodes.find((entry) => entry.id === pinned.id);
          if (node) {
            activateNode(node, "pinned");
          } else {
            pinned = null;
            clearActive();
          }
        } else if (pinned.type === "link") {
          const link = graph.links.find((entry) => entry.id === pinned.id);
          if (link) {
            activateLink(link, "pinned");
          } else {
            pinned = null;
            clearActive();
          }
        }
      } else {
        clearActive();
      }
    };

    const resizeObserver = new ResizeObserver(() => render());
    resizeObserver.observe(wrap);

    if (resetButton instanceof HTMLButtonElement) {
      const onReset = (event) => {
        event.stopPropagation();
        pinned = null;
        clearActive();
      };
      resetButton.addEventListener("click", onReset);
      cleanups.push(() => resetButton.removeEventListener("click", onReset));
    }

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
