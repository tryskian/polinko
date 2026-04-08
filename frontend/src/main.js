import "./styles.css";

const portfolioData = {
  snapshot: {
    tag: "portfolio-nucleus-v1-2026-04-07",
    commit: "da4ba66846dde5dd88062cd741ca635661975e2e2",
  },
  operator_console: {
    status: "Live editing shell ready; semantic kernel pending sync with Notion payload",
    risk: "Low structural risk, medium content drift risk",
    next_kernel: "Before/After evidence synthesis pass",
    last_completed_kernel: "Portfolio IA lock + navigation baseline"
  },
  failure_museum: [
    {
      card_id: "A",
      claim: "Prompt drift enters at long-context recoveries",
      observed_failure: "Session state fallback was not preserved across retry paths",
      intervention: "Add compact state checkpoint and deterministic fallback summary",
      before_metric: "recoveries 4/10",
      after_metric: "recoveries 8/10",
      stress_test: "replay with synthetic context truncation",
      decision: "Keep this as a test case archetype and ship low-fi evidence shell first.",
      anchors: {
        transcript: ["transcript/notes#1"],
        decision: ["docs/SESSION_HANDOFF.md#portfolio-timeline"],
        eval: [".local/eval_reports/portfolio-shell-mockup.json"],
      },
    },
    {
      card_id: "B",
      claim: "Fallback mode hides evaluation visibility",
      observed_failure: "Feedback and checkpoint context can diverge in review snapshots",
      intervention: "Align feedback display order to checkpoint key fields",
      before_metric: "checkpoint visibility 2/10",
      after_metric: "checkpoint visibility 7/10",
      stress_test: "high-cardinality reruns in local mock stream",
      decision: "Introduce shell layout first; wire evaluator later.",
      anchors: {
        transcript: ["transcript/notes#2"],
        decision: ["docs/governance/DECISIONS.md#d-199"],
        eval: [".local/eval_reports/ocr_growth_metrics.json"],
      },
    },
    {
      card_id: "C",
      claim: "Card-level evidence links are not immediately reachable",
      observed_failure: "Operators spend extra context hops to open evidence",
      intervention: "Keep evidence anchors adjacent to each card detail",
      before_metric: "avg hop 4",
      after_metric: "avg hop 1",
      stress_test: "rapid-open loop across all cards",
      decision: "Prioritise one-click evidence access in shell only.",
      anchors: {
        transcript: ["transcript/notes#3"],
        decision: ["docs/governance/DECISIONS.md#d-199"],
        eval: [".local/eval_reports/ocr_failures.json"],
      },
    },
  ],
  before_after_rows: [
    {
      card_id: "A",
      before_state: "Low-fi section order was not enforced.",
      after_state: "Operator's Console → Failure Museum → Before/After → What I'm Working On",
      metric_delta: "+100% sequence consistency",
      decision_impact: "Simplifies narrative scan for readers.",
      evidence_anchor: "docs/runtime/PORTFOLIO_UI_IA_WIREFRAME.md#screen-structure",
      metric_theme: "Narrative"
    },
    {
      card_id: "B",
      before_state: "Mobile and desktop navigations diverged in structure.",
      after_state: "Single anchor contract for both nav surfaces.",
      metric_delta: "+1 shared contract",
      decision_impact: "Lower editing friction for kernel notes.",
      evidence_anchor: "docs/governance/DECISIONS.md#d-199",
      metric_theme: "Navigation"
    },
    {
      card_id: "C",
      before_state: "Table filters required page rebuilds in earlier draft.",
      after_state: "Client-side card + theme filtering.",
      metric_delta: "Faster iteration, same shell data source",
      decision_impact: "Immediate content edits without backend coupling.",
      evidence_anchor: "docs/runtime/PORTFOLIO_UI_IA_WIREFRAME.md#section-contracts",
      metric_theme: "Interactivity"
    },
    {
      card_id: "D",
      before_state: "No card detail path for failure narratives.",
      after_state: "Inline detail panel with evidence anchors.",
      metric_delta: "Higher evidence accessibility",
      decision_impact: "Preserves low-fi structure while improving scan speed.",
      evidence_anchor: "docs/governance/SESSION_HANDOFF.md#portfolio-presentation-format",
      metric_theme: "Evidence"
    },
  ],
  work_queue: {
    queue: [
      "Populate Operator's Console fields from live source",
      "Add automated copy sync from Notion section stubs",
      "Attach export route to shell assets only when requested",
    ],
    blockers: [
      "No active UI route is reintroduced without approval",
      "Source of truth remains external documents (Notion + governance docs)",
    ],
    go_no_go: "GO",
  }
};

const commitNode = document.createElement("p");
commitNode.textContent = `${portfolioData.snapshot.tag} · ${portfolioData.snapshot.commit}`;
commitNode.style.cssText = "margin-top:0.6rem; color:#4b5563; font-size:0.85rem;";
document.querySelector(".hero").append(commitNode);

const operatorFields = {
  status: "Current status",
  risk: "Current risk",
  next_kernel: "Next kernel",
  last_completed_kernel: "Last completed kernel",
};

const operatorStatus = document.getElementById("operatorStatus");
Object.entries(portfolioData.operator_console).forEach(([key, value]) => {
  const card = document.createElement("div");
  card.className = "status-card";
  card.innerHTML = `<strong>${operatorFields[key] || key}</strong>${value}`;
  operatorStatus.append(card);
});

const cardsContainer = document.getElementById("failureCards");
const detail = document.getElementById("failureDetail");
const detailBody = document.getElementById("failureDetailBody");

portfolioData.failure_museum.forEach((entry, index) => {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "failure-card";
  card.setAttribute("aria-label", `Open detail for card ${entry.card_id}`);
  card.innerHTML = `
    <h3>Card ${entry.card_id}: ${entry.claim}</h3>
    <p><strong>Observed:</strong> ${entry.observed_failure}</p>
    <p><strong>${entry.before_metric} → ${entry.after_metric}</strong></p>
  `;
  card.addEventListener("click", () => {
    detail.className = "detail-drawer open";
    detailBody.innerHTML = `
      <div class="item"><strong>Intervention:</strong> ${entry.intervention}</div>
      <div class="item"><strong>Stress test:</strong> ${entry.stress_test}</div>
      <div class="item"><strong>Decision:</strong> ${entry.decision}</div>
      <div class="meta">
        <div><strong>Evidence anchors</strong></div>
        <a href="#">Transcript: ${entry.anchors.transcript.join(", ")}</a>
        <a href="#">Decision: ${entry.anchors.decision.join(", ")}</a>
        <a href="#">Eval: ${entry.anchors.eval.join(", ")}</a>
      </div>
    `;
  });
  cardsContainer.append(card);
});

const queue = document.getElementById("kernelQueue");
portfolioData.work_queue.queue.forEach((item) => {
  const li = document.createElement("li");
  li.textContent = item;
  queue.append(li);
});

const blockers = document.getElementById("kernelBlockers");
portfolioData.work_queue.blockers.forEach((item) => {
  const li = document.createElement("li");
  li.textContent = item;
  blockers.append(li);
});

const goNoGo = document.getElementById("goNoGo");
const isGo = portfolioData.work_queue.go_no_go.toUpperCase() === "GO";
goNoGo.className = `go-no-go ${isGo ? "go" : "no-go"}`;
goNoGo.textContent = `Go/No-Go: ${portfolioData.work_queue.go_no_go}`;

const cardFilter = document.getElementById("filterCard");
const themeFilter = document.getElementById("filterTheme");
const tbody = document.getElementById("beforeAfterBody");

const cards = [...new Set(portfolioData.before_after_rows.map((r) => r.card_id))].sort();
const themes = [...new Set(portfolioData.before_after_rows.map((r) => r.metric_theme))].sort();

const allCard = "All cards";
const allTheme = "All themes";
cardFilter.innerHTML = `
  <option value="">${allCard}</option>
  ${cards.map((c) => `<option value="${c}">${c}</option>`).join("")}
`;
themeFilter.innerHTML = `
  <option value="">${allTheme}</option>
  ${themes.map((t) => `<option value="${t}">${t}</option>`).join("")}
`;

function renderTable() {
  const cardValue = cardFilter.value;
  const themeValue = themeFilter.value;
  const rows = portfolioData.before_after_rows.filter((row) => {
    const matchCard = cardValue ? row.card_id === cardValue : true;
    const matchTheme = themeValue ? row.metric_theme === themeValue : true;
    return matchCard && matchTheme;
  });

  tbody.innerHTML = rows
    .map(
      (row) => `
    <tr>
      <td>${row.card_id}</td>
      <td>${row.before_state}</td>
      <td>${row.after_state}</td>
      <td>${row.metric_delta}</td>
      <td>${row.decision_impact}</td>
      <td><a href="#">${row.evidence_anchor}</a></td>
    </tr>
  `
    )
    .join("");
}

cardFilter.addEventListener("change", renderTable);
themeFilter.addEventListener("change", renderTable);
renderTable();

const mobileDrawer = document.getElementById("mobileDrawer");
const menuToggle = document.getElementById("menuToggle");
const drawerClose = document.getElementById("drawerClose");

menuToggle.addEventListener("click", () => {
  mobileDrawer.classList.add("open");
  mobileDrawer.setAttribute("aria-hidden", "false");
});

drawerClose.addEventListener("click", () => {
  mobileDrawer.classList.remove("open");
  mobileDrawer.setAttribute("aria-hidden", "true");
});

mobileDrawer.querySelectorAll("a").forEach((a) => {
  a.addEventListener("click", () => {
    mobileDrawer.classList.remove("open");
    mobileDrawer.setAttribute("aria-hidden", "true");
  });
});
