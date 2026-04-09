import "./styles.css";

const portfolioData = {
  snapshot: {
    tag: "portfolio-nucleus-v1",
    commit: "main",
  },
  operator_console: {
    status: "Case-study nucleus locked to binary eval architecture and fail-first OCR hardening.",
    risk: "Evidence drift risk if non-binary lanes are mixed into core portfolio claims.",
    next_kernel: "Promote claim anchors into the final application one-pager with line-precise evidence callouts.",
    last_completed_kernel: "Failure Museum v1 body + claims-to-evidence map aligned to Apr 1+ binary-only sources."
  },
  failure_museum: [
    {
      card_id: "A",
      claim: "Pass-from-fail gate architecture improves release clarity and development signal.",
      observed_failure: "Pass-only optimization mixed release gating with exploratory learning, hiding remediation signal.",
      intervention: "Split lockset and growth lanes; keep release decisions strict PASS/FAIL and track fail-to-pass metrics.",
      before_metric: "metrics instrumented: 0",
      after_metric: "metrics instrumented: 4",
      stress_test: "Claim fails if growth fail volume can alter lockset release outcomes.",
      decision: "Accepted as the baseline binary eval architecture for portfolio v1.",
      anchors: {
        transcript: ["docs/peanut/transcripts/co_reasoning/08_novel_ocr_exposure_pass_from_fail_2026-04-01.md"],
        decision: ["docs/governance/DECISIONS.md (D-117, D-120)"],
        eval: [".local/eval_reports/ocr_growth_metrics.md"],
      },
    },
    {
      card_id: "B",
      claim: "Fail-rich growth lane increases actionable OCR learning signal.",
      observed_failure: "Lockset-only coverage under-represented novel OCR variation and delayed failure clustering.",
      intervention: "Expanded growth cases, materialized deterministic fail cohorts, and filtered non-actionable noise.",
      before_metric: "strict baseline: 21 cases",
      after_metric: "growth set: 87 cases",
      stress_test: "Claim fails if growth widening degrades lockset stability or pollutes cohorts with non-OCR noise.",
      decision: "Accepted for continuous hardening: failures are now explicit engineering input.",
      anchors: {
        transcript: ["docs/peanut/transcripts/co_reasoning/10_ocr_mining_signal_update_excerpt_2026-04-02.md"],
        decision: ["docs/governance/DECISIONS.md (D-121, D-122, D-126, D-127)"],
        eval: [".local/eval_reports/ocr_growth_fail_cohort.md"],
      },
    },
    {
      card_id: "C",
      claim: "Calibration improves when certainty is bounded by binary gate discipline.",
      observed_failure: "Weak evidence could appear compliant while still carrying factual OCR errors.",
      intervention: "Applied evidence-first flow: capture signal -> score certainty -> apply policy under split lanes.",
      before_metric: "boundary existed conceptually only",
      after_metric: "lockset stability: 20 stable / 0 flaky",
      stress_test: "Claim fails if lockset decision flakiness rises above zero.",
      decision: "Accepted as calibration framing for uncertainty without loosening release control.",
      anchors: {
        transcript: ["docs/peanut/transcripts/co_reasoning/12_ocr_confidence_boundary_and_safety_transfer_2026-04-03.md"],
        decision: ["docs/governance/DECISIONS.md (D-119, D-130)"],
        eval: [".local/eval_reports/ocr_transcript_stability.json"],
      },
    },
  ],
  before_after_rows: [
    {
      card_id: "A",
      before_state: "Release and exploratory learning were coupled in one eval lane.",
      after_state: "Binary release lockset separated from fail-rich growth lane.",
      metric_delta: "0 -> 4 pass-from-fail metrics",
      decision_impact: "Cleaner go/no-go decisions and measurable remediation flow.",
      evidence_anchor: "docs/peanut/refs/PORTFOLIO_CASE_STUDY_NUCLEUS_V1.md",
      metric_theme: "Architecture"
    },
    {
      card_id: "B",
      before_state: "Novel OCR variation was under-covered by strict baseline cases.",
      after_state: "Growth lane widened and fail cohorts promoted as first-class artifacts.",
      metric_delta: "21 -> 87 growth cases",
      decision_impact: "Higher-value hardening queue grounded in explicit failures.",
      evidence_anchor: "docs/peanut/refs/PORTFOLIO_FAILURE_MUSEUM_V1.md",
      metric_theme: "Coverage"
    },
    {
      card_id: "C",
      before_state: "Uncertainty handling was implicit and mixed into release interpretation.",
      after_state: "Evidence-first certainty boundary with stable binary lockset discipline.",
      metric_delta: "20 stable / 0 flaky decisions",
      decision_impact: "Calibration improves without compromising deterministic release behavior.",
      evidence_anchor: "docs/peanut/refs/PORTFOLIO_CLAIMS_EVIDENCE_MAP_V1.md",
      metric_theme: "Calibration"
    },
  ],
  work_queue: {
    queue: [
      "Draft the final application-facing one-pager using C1-C5 claim boundaries.",
      "Attach line-precise anchor callouts for each Failure Museum claim.",
      "Prepare visual shell pass (top-nav and section rhythm already locked).",
    ],
    blockers: [
      "Need final excerpt pass to avoid duplicating transcript evidence across sections.",
      "Must keep theory lane out of core binary-eval claim bodies.",
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
        <div>Transcript: ${entry.anchors.transcript.join(", ")}</div>
        <div>Decision: ${entry.anchors.decision.join(", ")}</div>
        <div>Eval: ${entry.anchors.eval.join(", ")}</div>
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
