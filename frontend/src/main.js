import "./style.css";
import { createExportUiState } from "./export-ui-state.js";

const STORAGE_ACTIVE_CHAT_KEY = "polinko.active_chat_id.v2";
const STORAGE_THEME_KEY = "polinko.theme.v1";
const THEME_LIGHT = "light";
const THEME_DARK = "dark";

const chatEl = document.getElementById("chat");
const composerEl = document.getElementById("composer");
const composerAttachmentsEl = document.getElementById("composer-attachments");
const messageEl = document.getElementById("message");
const ocrFileInputEl = document.getElementById("ocr-file-input");
const ocrUploadEl = document.getElementById("ocr-upload");
const memorySearchToggleEl = document.getElementById("memory-search-toggle");
const memorySearchPanelEl = document.getElementById("memory-search-panel");
const memorySearchFormEl = document.getElementById("memory-search-form");
const memorySearchQueryEl = document.getElementById("memory-search-query");
const memorySearchSourceEl = document.getElementById("memory-search-source");
const memorySearchSessionScopeEl = document.getElementById("memory-search-session-scope");
const memorySearchRunEl = document.getElementById("memory-search-run");
const memorySearchStatusEl = document.getElementById("memory-search-status");
const memorySearchResultsEl = document.getElementById("memory-search-results");
const shellEl = document.querySelector(".shell");
const resetEl = document.getElementById("reset");
const themeToggleEl = document.getElementById("theme-toggle");
const themeToggleIconEl = document.getElementById("theme-toggle-icon");
const memoryScopeSelectEl = document.getElementById("memory-scope-select");
const exportMarkdownEl = document.getElementById("export-markdown");
const exportJsonEl = document.getElementById("export-json");
const exportOcrEl = document.getElementById("export-ocr");
const evalSubmitEl = document.getElementById("eval-submit");
const emptyStateEl = document.getElementById("empty-state");
const newChatEl = document.getElementById("new-chat");
const drawerToggleEl = document.getElementById("drawer-toggle");
const drawerEl = document.getElementById("chat-drawer");
const drawerBackdropEl = document.getElementById("drawer-backdrop");
const chatListEl = document.getElementById("chat-list");
const RESPONSE_RENDER_DELAY_MS = 220;
const ASSISTANT_TYPE_MIN_MS = 120;
const ASSISTANT_TYPE_MAX_MS = 700;
const ASSISTANT_TYPE_MS_PER_CHAR = 1.1;
const DEFAULT_ATTACHMENT_PROMPT =
  "Transcribe visible text from the attached image(s) verbatim. Do not interpret.";
const MEMORY_SEARCH_ENABLED = false;
const FEEDBACK_POSITIVE_TAG_OPTIONS = [
  "accurate",
  "high_value",
  "medium_value",
  "low_value",
  "ocr_accurate",
  "grounded",
  "style",
  "complete",
  "useful",
];
const FEEDBACK_NEGATIVE_TAG_OPTIONS = [
  "ocr_miss",
  "grounding_gap",
  "style_mismatch",
  "hallucination_risk",
  "needs_retry",
];
const memorySearchAvailable =
  MEMORY_SEARCH_ENABLED &&
  Boolean(
    memorySearchToggleEl &&
      memorySearchPanelEl &&
      memorySearchQueryEl &&
      memorySearchSourceEl &&
      memorySearchSessionScopeEl &&
      memorySearchRunEl &&
      memorySearchStatusEl &&
      memorySearchResultsEl,
  );

let chats = [];
let activeChatId = "";
let activeMemoryScope = "global";
let currentMessages = [];
let messageFeedbackById = new Map();
let memorySearchOpen = false;
let activeTheme = THEME_LIGHT;
let pendingAttachments = [];
let attachmentDragDepth = 0;
const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

function normalizeTheme(value) {
  return value === THEME_DARK ? THEME_DARK : THEME_LIGHT;
}

function readSavedTheme() {
  try {
    const raw = localStorage.getItem(STORAGE_THEME_KEY);
    if (!raw) {
      return null;
    }
    return normalizeTheme(raw);
  } catch {
    return null;
  }
}

function writeSavedTheme(theme) {
  try {
    localStorage.setItem(STORAGE_THEME_KEY, theme);
  } catch {
    // Ignore localStorage failures.
  }
}

function applyTheme(theme) {
  activeTheme = normalizeTheme(theme);
  document.documentElement.setAttribute("data-theme", activeTheme);
  updateThemeUi();
}

function setTheme(theme) {
  applyTheme(theme);
  writeSavedTheme(activeTheme);
}

function updateThemeUi() {
  let icon = "light_mode";
  let title = "Switch to dark mode";
  if (activeTheme === THEME_DARK) {
    icon = "dark_mode";
    title = "Switch to light mode";
  }

  if (themeToggleIconEl) {
    themeToggleIconEl.textContent = icon;
  }
  if (themeToggleEl) {
    themeToggleEl.title = title;
    themeToggleEl.setAttribute("aria-label", title);
  }
}

function toggleTheme() {
  const nextTheme = activeTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
  setTheme(nextTheme);
}

function initTheme() {
  const saved = readSavedTheme();
  if (saved) {
    applyTheme(saved);
  } else {
    applyTheme(prefersDarkScheme.matches ? THEME_DARK : THEME_LIGHT);
  }

  prefersDarkScheme.addEventListener("change", (event) => {
    if (readSavedTheme()) {
      return;
    }
    applyTheme(event.matches ? THEME_DARK : THEME_LIGHT);
  });

  themeToggleEl?.addEventListener("click", toggleTheme);

  // Expose simple hooks for upcoming theme controls.
  window.polinkoTheme = {
    get: () => activeTheme,
    getResolved: () => activeTheme,
    set: setTheme,
  };
}

const exportUiState = createExportUiState({
  getActiveChatId: () => activeChatId,
  setButtonsDisabled(disabled) {
    exportMarkdownEl.disabled = disabled;
    exportJsonEl.disabled = disabled;
    exportOcrEl.disabled = disabled;
  },
});

function autoSizeComposer() {
  messageEl.style.height = "auto";
  messageEl.style.height = `${Math.min(messageEl.scrollHeight, 128)}px`;
}

function readActiveChatId() {
  try {
    return localStorage.getItem(STORAGE_ACTIVE_CHAT_KEY) || "";
  } catch {
    return "";
  }
}

function setComposerText(value) {
  messageEl.value = value;
  autoSizeComposer();
  messageEl.focus();
  const cursor = messageEl.value.length;
  messageEl.setSelectionRange(cursor, cursor);
}

function appendComposerText(value) {
  const trimmedCurrent = messageEl.value.trim();
  const next = trimmedCurrent ? `${messageEl.value}\n\n${value}` : value;
  setComposerText(next);
}

function writeActiveChatId(value) {
  try {
    localStorage.setItem(STORAGE_ACTIVE_CHAT_KEY, value);
  } catch {
    // Ignore localStorage failures.
  }
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderMarkdown(value) {
  const escaped = escapeHtml(value);
  const codeBlocks = [];

  let html = escaped.replace(/```([a-zA-Z0-9_+-]+)?\n?([\s\S]*?)```/g, (_m, lang = "", code) => {
    const idx = codeBlocks.length;
    const cleanCode = code.replace(/\n$/, "");
    const langAttr = lang ? ` data-lang="${lang}"` : "";
    codeBlocks.push(`<pre><code${langAttr}>${cleanCode}</code></pre>`);
    return `@@CODE_BLOCK_${idx}@@`;
  });

  html = html
    .replace(/`([^`\n]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*\n]+)\*/g, "<em>$1</em>");

  const chunks = html
    .split(/\n{2,}/)
    .map((chunk) => chunk.trimEnd())
    .filter((chunk) => chunk.length > 0);

  html = chunks
    .map((chunk) => {
      const onlyCodeBlock = /^@@CODE_BLOCK_\d+@@$/.test(chunk.trim());
      if (onlyCodeBlock) {
        return chunk.trim();
      }
      return `<p>${chunk.replace(/\n/g, "<br>")}</p>`;
    })
    .join("");

  html = html.replace(/@@CODE_BLOCK_(\d+)@@/g, (_m, idx) => codeBlocks[Number(idx)] ?? "");
  return html;
}

function syncEmptyState() {
  const hasMessages = chatEl.querySelector(".msg") !== null;
  emptyStateEl.style.display = hasMessages ? "none" : "";
}

function formatFeedbackStatusText(feedback) {
  if (!feedback) {
    return "";
  }
  const outcome = (feedback.outcome || "").toLowerCase();
  const parts = [outcome.toUpperCase()];
  const positiveTags = Array.isArray(feedback.positive_tags) ? feedback.positive_tags : [];
  const negativeTags = Array.isArray(feedback.negative_tags) ? feedback.negative_tags : [];
  if (outcome === "pass" && positiveTags.length > 0) {
    parts.push(positiveTags.join(", "));
  } else if (outcome === "fail" && negativeTags.length > 0) {
    parts.push(negativeTags.join(", "));
  } else if (outcome === "partial") {
    if (positiveTags.length > 0) {
      parts.push(`+ ${positiveTags.join(", ")}`);
    }
    if (negativeTags.length > 0) {
      parts.push(`- ${negativeTags.join(", ")}`);
    }
  } else if (Array.isArray(feedback.tags) && feedback.tags.length > 0) {
    parts.push(feedback.tags.join(", "));
  }
  return parts.filter(Boolean).join(" • ");
}

function createAssistantFeedbackControls({ sessionId, messageId, feedback }) {
  const root = document.createElement("section");
  root.className = "msg-feedback";
  root.dataset.messageId = messageId;

  const buttons = document.createElement("div");
  buttons.className = "msg-feedback-buttons";

  const passButton = document.createElement("button");
  passButton.type = "button";
  passButton.className = "msg-feedback-toggle";
  passButton.textContent = "Pass";

  const failButton = document.createElement("button");
  failButton.type = "button";
  failButton.className = "msg-feedback-toggle";
  failButton.textContent = "Fail";

  const partialButton = document.createElement("button");
  partialButton.type = "button";
  partialButton.className = "msg-feedback-toggle";
  partialButton.textContent = "Partial";

  const status = document.createElement("p");
  status.className = "msg-feedback-status";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.className = "msg-feedback-edit";
  editButton.textContent = "Edit";
  editButton.hidden = true;

  const summaryRow = document.createElement("div");
  summaryRow.className = "msg-feedback-summary";
  summaryRow.append(status, editButton);

  const card = document.createElement("div");
  card.className = "msg-feedback-card";
  card.hidden = true;

  const cardTitle = document.createElement("h4");
  cardTitle.className = "msg-feedback-title";
  cardTitle.textContent = "Evaluate response";

  const cardClose = document.createElement("button");
  cardClose.type = "button";
  cardClose.className = "msg-feedback-close";
  cardClose.setAttribute("aria-label", "Close evaluation");
  cardClose.textContent = "×";

  const cardHead = document.createElement("div");
  cardHead.className = "msg-feedback-head";
  cardHead.append(cardTitle, cardClose);

  const positiveBlock = document.createElement("div");
  positiveBlock.className = "msg-feedback-reason-block";
  const positiveLabel = document.createElement("p");
  positiveLabel.className = "msg-feedback-label";
  positiveLabel.textContent = "Pass reasons";
  const positiveTagsWrap = document.createElement("div");
  positiveTagsWrap.className = "msg-feedback-tags";
  positiveBlock.append(positiveLabel, positiveTagsWrap);

  const negativeBlock = document.createElement("div");
  negativeBlock.className = "msg-feedback-reason-block";
  const negativeLabel = document.createElement("p");
  negativeLabel.className = "msg-feedback-label";
  negativeLabel.textContent = "Fail reasons";
  const negativeTagsWrap = document.createElement("div");
  negativeTagsWrap.className = "msg-feedback-tags";
  negativeBlock.append(negativeLabel, negativeTagsWrap);

  const noteLabel = document.createElement("label");
  noteLabel.className = "msg-feedback-label";
  noteLabel.textContent = "Notes";

  const noteEl = document.createElement("textarea");
  noteEl.className = "msg-feedback-note";
  noteEl.rows = 3;
  noteEl.maxLength = 1200;
  noteEl.placeholder = "Optional context";

  const actionHint = document.createElement("p");
  actionHint.className = "msg-feedback-action";

  const saveButton = document.createElement("button");
  saveButton.type = "button";
  saveButton.className = "msg-feedback-save";
  saveButton.textContent = "Save";

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "msg-feedback-cancel";
  cancelButton.textContent = "Cancel";

  const actions = document.createElement("div");
  actions.className = "msg-feedback-actions";
  actions.append(saveButton, cancelButton);

  card.append(cardHead, positiveBlock, negativeBlock, noteLabel, noteEl, actionHint, actions);
  buttons.append(passButton, partialButton, failButton);
  root.append(buttons, summaryRow, card);

  let current = feedback ? { ...feedback } : null;
  let selectedOutcome = null;
  let selectedPositiveTags = new Set();
  let selectedNegativeTags = new Set();

  function setSelectionsFromFeedback(entry) {
    const outcome = (entry?.outcome || "").toLowerCase();
    const positive = Array.isArray(entry?.positive_tags) ? entry.positive_tags : [];
    const negative = Array.isArray(entry?.negative_tags) ? entry.negative_tags : [];
    if (positive.length > 0 || negative.length > 0) {
      selectedPositiveTags = new Set(positive);
      selectedNegativeTags = new Set(negative);
      return;
    }
    const legacyTags = Array.isArray(entry?.tags) ? entry.tags : [];
    if (outcome === "fail") {
      selectedPositiveTags = new Set();
      selectedNegativeTags = new Set(legacyTags);
      return;
    }
    if (outcome === "partial") {
      const positiveSet = new Set(FEEDBACK_POSITIVE_TAG_OPTIONS);
      const negativeSet = new Set(FEEDBACK_NEGATIVE_TAG_OPTIONS);
      selectedPositiveTags = new Set(legacyTags.filter((tag) => positiveSet.has(tag)));
      selectedNegativeTags = new Set(legacyTags.filter((tag) => negativeSet.has(tag)));
      return;
    }
    selectedPositiveTags = new Set(legacyTags);
    selectedNegativeTags = new Set();
  }

  setSelectionsFromFeedback(current);

  function renderTagChips(targetWrap, options, selectedTags) {
    targetWrap.innerHTML = "";
    options.forEach((tag) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "msg-feedback-chip";
      chip.textContent = tag;
      if (selectedTags.has(tag)) {
        chip.classList.add("active");
      }
      chip.addEventListener("click", () => {
        if (selectedTags.has(tag)) {
          selectedTags.delete(tag);
        } else {
          selectedTags.add(tag);
        }
        renderTagChips(targetWrap, options, selectedTags);
      });
      targetWrap.appendChild(chip);
    });
  }

  function renderStatus() {
    const text = formatFeedbackStatusText(current);
    status.textContent = text;
    status.hidden = !text;
    renderActionHint();
  }

  function renderActionHint() {
    const isEditing = !card.hidden;
    const currentOutcome = (current?.outcome || "").toLowerCase();
    const shouldShow =
      isEditing &&
      Boolean(current?.recommended_action) &&
      selectedOutcome === currentOutcome &&
      currentOutcome !== "pass";
    actionHint.textContent = shouldShow ? String(current?.recommended_action || "") : "";
    actionHint.hidden = !shouldShow;
  }

  function renderToggleState() {
    const isEditing = !card.hidden;
    passButton.classList.toggle("active", isEditing && selectedOutcome === "pass");
    partialButton.classList.toggle("active", isEditing && selectedOutcome === "partial");
    failButton.classList.toggle("active", isEditing && selectedOutcome === "fail");
  }

  function renderOutcomeSections() {
    positiveBlock.hidden = selectedOutcome === "fail";
    negativeBlock.hidden = selectedOutcome === "pass";
    renderTagChips(positiveTagsWrap, FEEDBACK_POSITIVE_TAG_OPTIONS, selectedPositiveTags);
    renderTagChips(negativeTagsWrap, FEEDBACK_NEGATIVE_TAG_OPTIONS, selectedNegativeTags);
  }

  function renderReadState() {
    const isEditing = !card.hidden;
    const hasSaved = Boolean(current);
    const showSavedState = hasSaved && !isEditing;
    buttons.hidden = showSavedState;
    editButton.hidden = !showSavedState;
    root.classList.toggle("is-saved", showSavedState);
  }

  function openCard(outcome) {
    selectedOutcome = ["pass", "partial", "fail"].includes(outcome) ? outcome : "pass";
    if (!current) {
      selectedPositiveTags = new Set();
      selectedNegativeTags = new Set();
      noteEl.value = "";
    } else {
      setSelectionsFromFeedback(current);
      noteEl.value = current?.note || "";
      if (selectedOutcome === "pass") {
        selectedNegativeTags = new Set();
      } else if (selectedOutcome === "fail") {
        selectedPositiveTags = new Set();
      }
    }
    if (selectedOutcome === "pass") {
      cardTitle.textContent = "Pass reasons";
    } else if (selectedOutcome === "partial") {
      cardTitle.textContent = "Partial reasons";
    } else {
      cardTitle.textContent = "Fail reasons";
    }
    card.hidden = false;
    renderOutcomeSections();
    renderToggleState();
    renderActionHint();
    renderReadState();
  }

  function closeCard() {
    card.hidden = true;
    selectedOutcome = null;
    renderToggleState();
    renderActionHint();
    renderReadState();
  }

  passButton.addEventListener("click", () => openCard("pass"));
  partialButton.addEventListener("click", () => openCard("partial"));
  failButton.addEventListener("click", () => openCard("fail"));
  editButton.addEventListener("click", () => openCard((current?.outcome || "pass").toLowerCase()));
  cardClose.addEventListener("click", closeCard);
  cancelButton.addEventListener("click", closeCard);
  saveButton.addEventListener("click", async () => {
    const positiveTags = [...selectedPositiveTags];
    const negativeTags = [...selectedNegativeTags];
    if (selectedOutcome === "pass" && positiveTags.length === 0) {
      status.textContent = "Pass requires at least one pass reason.";
      status.hidden = false;
      return;
    }
    if (selectedOutcome === "fail" && negativeTags.length === 0) {
      status.textContent = "Fail requires at least one fail reason.";
      status.hidden = false;
      return;
    }
    if (selectedOutcome === "partial" && (positiveTags.length === 0 || negativeTags.length === 0)) {
      status.textContent = "Partial requires at least one pass reason and one fail reason.";
      status.hidden = false;
      return;
    }
    saveButton.disabled = true;
    cancelButton.disabled = true;
    try {
      const payload = {
        message_id: messageId,
        outcome: selectedOutcome,
        positive_tags: selectedOutcome === "fail" ? [] : positiveTags,
        negative_tags: selectedOutcome === "pass" ? [] : negativeTags,
        note: noteEl.value.trim() || null,
      };
      const saved = await apiSubmitFeedback(sessionId, {
        ...payload,
      });
      current = saved;
      messageFeedbackById.set(messageId, saved);
      renderStatus();
      closeCard();
    } catch (error) {
      status.textContent = String(error);
      status.hidden = false;
    } finally {
      saveButton.disabled = false;
      cancelButton.disabled = false;
    }
  });

  renderToggleState();
  renderStatus();
  renderReadState();
  return root;
}

function appendMessage(
  kind,
  text,
  { persist = true, scroll = true, messageId = null, sessionId = activeChatId, feedback = null } = {},
) {
  const node = document.createElement("article");
  node.className = `msg ${kind}`;
  if (kind === "assistant" || kind === "user") {
    node.innerHTML = renderMarkdown(text);
  } else {
    node.textContent = text;
  }
  if (kind === "assistant" && messageId) {
    const controls = createAssistantFeedbackControls({ sessionId, messageId, feedback });
    node.appendChild(controls);
  }
  chatEl.appendChild(node);
  if (persist) {
    currentMessages.push({ kind, text, messageId, feedback });
  }
  syncEmptyState();
  if (scroll) {
    chatEl.scrollTop = chatEl.scrollHeight;
  }
}

function appendImagePrompt(src, sourceName, { scroll = true } = {}) {
  const node = document.createElement("article");
  node.className = "msg user user-image";

  const image = document.createElement("img");
  image.className = "user-image-preview";
  image.src = src;
  image.alt = sourceName ? `Uploaded image: ${sourceName}` : "Uploaded image";
  image.loading = "lazy";
  node.appendChild(image);

  if (sourceName) {
    const label = document.createElement("p");
    label.className = "user-image-label";
    label.textContent = sourceName;
    node.appendChild(label);
  }

  chatEl.appendChild(node);
  syncEmptyState();
  if (scroll) {
    chatEl.scrollTop = chatEl.scrollHeight;
  }
}

async function appendAssistantTypedMessage(
  text,
  { persist = true, messageId = null, sessionId = activeChatId, feedback = null } = {},
) {
  const content = String(text ?? "");
  const node = document.createElement("article");
  node.className = "msg assistant";
  node.textContent = "";
  chatEl.appendChild(node);

  const durationMs = Math.min(
    ASSISTANT_TYPE_MAX_MS,
    Math.max(ASSISTANT_TYPE_MIN_MS, Math.round(content.length * ASSISTANT_TYPE_MS_PER_CHAR)),
  );
  const totalChars = content.length;
  if (totalChars === 0) {
    node.innerHTML = renderMarkdown(content);
    if (messageId) {
      node.appendChild(createAssistantFeedbackControls({ sessionId, messageId, feedback }));
    }
    if (persist) {
      currentMessages.push({ kind: "assistant", text: content, messageId, feedback });
    }
    syncEmptyState();
    chatEl.scrollTop = chatEl.scrollHeight;
    return;
  }

  await new Promise((resolve) => {
    const start = performance.now();
    let lastCount = -1;

    function step(now) {
      const elapsed = now - start;
      const rawProgress = durationMs <= 0 ? 1 : Math.min(1, elapsed / durationMs);
      // Ease-out so the first part feels lively while still ending smoothly.
      const eased = 1 - (1 - rawProgress) * (1 - rawProgress);
      const count = Math.min(totalChars, Math.floor(eased * totalChars));

      if (count !== lastCount) {
        lastCount = count;
        node.textContent = content.slice(0, count);
        chatEl.scrollTop = chatEl.scrollHeight;
      }

      if (rawProgress >= 1 || count >= totalChars) {
        resolve();
        return;
      }
      requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  });

  node.innerHTML = renderMarkdown(content);
  if (messageId) {
    node.appendChild(createAssistantFeedbackControls({ sessionId, messageId, feedback }));
  }
  if (persist) {
    currentMessages.push({ kind: "assistant", text: content, messageId, feedback });
  }
  syncEmptyState();
  chatEl.scrollTop = chatEl.scrollHeight;
}

function renderCurrentMessages() {
  chatEl.querySelectorAll(".msg").forEach((node) => node.remove());
  currentMessages.forEach((entry) => {
    appendMessage(entry.kind, entry.text, {
      persist: false,
      scroll: false,
      messageId: entry.messageId || null,
      sessionId: activeChatId,
      feedback: entry.feedback || null,
    });
  });
  syncEmptyState();
  chatEl.scrollTop = chatEl.scrollHeight;
}

function headers() {
  return {
    "Content-Type": "application/json",
  };
}

async function requestJson(path, options = {}) {
  const resp = await fetch(path, {
    headers: headers(),
    ...options,
  });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    const retryAfter = resp.headers.get("Retry-After");
    const detail = body.detail || `HTTP ${resp.status}`;
    throw new Error(retryAfter ? `${detail} (retry in ~${retryAfter}s)` : detail);
  }

  return resp.json();
}

async function apiListChats() {
  return requestJson("/chats");
}

async function apiCreateChat() {
  return requestJson("/chats", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

async function apiListMessages(sessionId) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/messages`);
}

async function apiListFeedback(sessionId) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/feedback`);
}

async function apiSubmitFeedback(sessionId, payload) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/feedback`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function apiRenameChat(sessionId, title) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

async function apiDeprecateChat(sessionId) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/deprecate`, {
    method: "POST",
  });
}

async function apiAddNote(sessionId, note) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/notes`, {
    method: "POST",
    body: JSON.stringify({ note }),
  });
}

async function apiGetPersonalization(sessionId) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/personalization`);
}

async function apiSetPersonalization(sessionId, memoryScope) {
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/personalization`, {
    method: "POST",
    body: JSON.stringify({ memory_scope: memoryScope }),
  });
}

async function sendMessage(messageText, sessionId, { attachments = [] } = {}) {
  const body = { message: messageText, session_id: sessionId };
  if (Array.isArray(attachments) && attachments.length > 0) {
    body.attachments = attachments;
  }
  return requestJson("/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

async function apiFileSearch({ query, sessionId, sourceTypes, limit = 6 }) {
  const body = {
    query,
    limit,
    source_types: sourceTypes,
  };
  if (sessionId) {
    body.session_id = sessionId;
  }
  return requestJson("/skills/file_search", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

async function apiExportChat(sessionId, { includeMarkdown = false } = {}) {
  const query = includeMarkdown ? "?include_markdown=true" : "";
  return requestJson(`/chats/${encodeURIComponent(sessionId)}/export${query}`);
}

function safeFilePart(value, fallback) {
  const cleaned = String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 64);
  return cleaned || fallback;
}

function formatExportTimestamp(value) {
  const date = new Date(Number(value) || Date.now());
  const pad = (num) => String(num).padStart(2, "0");
  return (
    `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}` +
    `-${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}Z`
  );
}

function exportBaseName(payload) {
  const titlePart = safeFilePart(payload?.title, "chat");
  const sessionPart = safeFilePart(payload?.session_id || activeChatId, "session");
  const stampPart = formatExportTimestamp(payload?.exported_at);
  return `${titlePart}-${sessionPart}-${stampPart}`;
}

function triggerDownload(filename, content, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function downloadJson(filename, payload) {
  triggerDownload(filename, `${JSON.stringify(payload, null, 2)}\n`, "application/json;charset=utf-8");
}

function syncExportControls() {
  exportUiState.sync();
}

async function withExportLock(task) {
  await exportUiState.runLocked(task);
}

async function submitEvalCheckpoint() {
  if (!activeChatId) {
    throw new Error("No active chat selected.");
  }
  const payload = await apiListFeedback(activeChatId);
  const entries = Array.isArray(payload.feedback) ? payload.feedback : [];
  if (entries.length === 0) {
    throw new Error("No saved evals in this chat yet.");
  }
  let passCount = 0;
  let failCount = 0;
  let otherCount = 0;
  entries.forEach((entry) => {
    const outcome = (entry?.outcome || "").toLowerCase();
    if (outcome === "pass") {
      passCount += 1;
      return;
    }
    if (outcome === "fail") {
      failCount += 1;
      return;
    }
    otherCount += 1;
  });
  const note = `EVAL_SUBMIT ${new Date().toISOString()} total=${entries.length} pass=${passCount} fail=${failCount} other=${otherCount}`;
  await apiAddNote(activeChatId, note);
  appendMessage(
    "meta",
    `Eval submit logged for ${activeChatId}: total=${entries.length}, pass=${passCount}, fail=${failCount}, other=${otherCount}.`,
    { persist: false },
  );
}

function parsePreferenceNote(value) {
  const match = value.match(/^\/note(?:\s+|:\s*)([\s\S]+)$/i);
  if (!match) {
    return "";
  }
  return match[1].trim();
}

function normalizeMemoryScope(value) {
  if (value === "session") {
    return "session";
  }
  return "global";
}

async function resetSession(sessionId) {
  return requestJson("/session/reset", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

async function startFreshChat({ deprecateCurrent = false } = {}) {
  if (deprecateCurrent && activeChatId) {
    await resetSession(activeChatId);
  }
  const created = await apiCreateChat();
  await refreshChats();
  await setActiveChat(created.session_id);
  messageEl.focus();
}

function appendThinkingIndicator() {
  const node = document.createElement("article");
  node.className = "msg assistant thinking";
  node.innerHTML = `
    <span class="thinking-dots" aria-label="Thinking" role="status">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </span>
  `;
  chatEl.appendChild(node);
  syncEmptyState();
  chatEl.scrollTop = chatEl.scrollHeight;
  return node;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Failed to read file."));
    reader.onload = () => resolve(String(reader.result || ""));
    reader.readAsDataURL(file);
  });
}

function escapeAttachmentName(value) {
  return String(value || "attachment")
    .replace(/[\r\n\t]+/g, " ")
    .trim();
}

function attachmentId() {
  if (typeof crypto?.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `att-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

function renderPendingAttachments() {
  if (!composerAttachmentsEl) {
    return;
  }
  composerAttachmentsEl.innerHTML = "";
  if (pendingAttachments.length === 0) {
    composerAttachmentsEl.hidden = true;
    return;
  }

  for (const item of pendingAttachments) {
    const pill = document.createElement("div");
    pill.className = "composer-attachment";

    const thumb = document.createElement("img");
    thumb.className = "composer-attachment-thumb";
    thumb.src = item.data_base64;
    thumb.alt = item.source_name ? `Attachment: ${item.source_name}` : "Attachment";
    thumb.loading = "lazy";
    pill.appendChild(thumb);

    const label = document.createElement("span");
    label.className = "composer-attachment-label";
    label.textContent = item.source_name || "attachment";
    pill.appendChild(label);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "composer-attachment-remove";
    removeButton.setAttribute("aria-label", `Remove ${item.source_name || "attachment"}`);
    removeButton.innerHTML = '<span class="material-symbols-outlined" aria-hidden="true">close</span>';
    removeButton.addEventListener("click", () => {
      pendingAttachments = pendingAttachments.filter((candidate) => candidate.id !== item.id);
      renderPendingAttachments();
    });
    pill.appendChild(removeButton);

    composerAttachmentsEl.appendChild(pill);
  }

  composerAttachmentsEl.hidden = false;
}

function clearPendingAttachments() {
  pendingAttachments = [];
  renderPendingAttachments();
}

async function queueAttachmentFiles(files) {
  const nextFiles = [...files].filter((file) => file instanceof File);
  if (nextFiles.length === 0) {
    return;
  }

  const added = [];
  for (const file of nextFiles) {
    if ((file.type || "").trim() && !file.type.startsWith("image/")) {
      throw new Error(`Only image attachments are supported right now: ${file.name}`);
    }
    const dataBase64 = await readFileAsDataUrl(file);
    added.push({
      id: attachmentId(),
      source_name: escapeAttachmentName(file.name),
      mime_type: file.type || null,
      data_base64: dataBase64,
      memory_scope: "global",
    });
  }
  pendingAttachments = [...pendingAttachments, ...added];
  renderPendingAttachments();
}

function setComposerDropActive(active) {
  composerEl.classList.toggle("drop-active", active);
}

function compactSessionId(value) {
  if (!value || value.length <= 16) {
    return value || "";
  }
  return `${value.slice(0, 8)}…${value.slice(-4)}`;
}

function normalizeSearchSourceTypes() {
  if (!memorySearchAvailable) {
    return ["ocr"];
  }
  const mode = memorySearchSourceEl.value;
  if (mode === "both") {
    return ["ocr", "chat"];
  }
  if (mode === "chat") {
    return ["chat"];
  }
  return ["ocr"];
}

function setMemorySearchOpen(open) {
  if (!memorySearchAvailable) {
    memorySearchOpen = false;
    return;
  }
  memorySearchOpen = open;
  memorySearchPanelEl.hidden = !open;
  memorySearchToggleEl.classList.toggle("active", open);
  memorySearchToggleEl.setAttribute("aria-expanded", open ? "true" : "false");
  if (open) {
    memorySearchQueryEl.focus();
  }
}

function setMemorySearchStatus(message, { isError = false } = {}) {
  if (!memorySearchAvailable) {
    return;
  }
  const text = String(message || "").trim();
  if (!text) {
    memorySearchStatusEl.hidden = true;
    memorySearchStatusEl.textContent = "";
    memorySearchStatusEl.classList.remove("error");
    return;
  }
  memorySearchStatusEl.hidden = false;
  memorySearchStatusEl.textContent = text;
  memorySearchStatusEl.classList.toggle("error", isError);
}

function buildAskPrompt(match) {
  const sourceName = String(match.metadata?.source_name || "").trim();
  const descriptor = sourceName ? `${match.source_type} • ${sourceName}` : match.source_type;
  return `Use this retrieved context (${descriptor}):\n${match.snippet}\n\nQuestion: `;
}

function renderMemorySearchResults(matches) {
  if (!memorySearchAvailable) {
    return;
  }
  memorySearchResultsEl.innerHTML = "";
  if (!Array.isArray(matches) || matches.length === 0) {
    return;
  }

  matches.forEach((match) => {
    const item = document.createElement("article");
    item.className = "memory-search-match";

    const meta = document.createElement("p");
    meta.className = "memory-search-meta";
    const score = Number(match.score || 0);
    meta.textContent = `${String(match.source_type || "unknown").toUpperCase()} • ${compactSessionId(
      String(match.session_id || ""),
    )} • ${score.toFixed(2)}`;

    const snippet = document.createElement("p");
    snippet.className = "memory-search-snippet";
    snippet.textContent = String(match.snippet || "");

    const actions = document.createElement("div");
    actions.className = "memory-search-actions";

    const insertButton = document.createElement("button");
    insertButton.type = "button";
    insertButton.className = "memory-search-action";
    insertButton.textContent = "Insert";
    insertButton.addEventListener("click", () => {
      appendComposerText(String(match.snippet || ""));
    });

    const askButton = document.createElement("button");
    askButton.type = "button";
    askButton.className = "memory-search-action";
    askButton.textContent = "Ask";
    askButton.addEventListener("click", () => {
      setComposerText(buildAskPrompt(match));
    });

    actions.append(insertButton, askButton);
    item.append(meta, snippet, actions);
    memorySearchResultsEl.appendChild(item);
  });
}

function sortChatsByRecent(nextChats) {
  return [...nextChats].sort((a, b) => b.updated_at - a.updated_at || b.created_at - a.created_at);
}

function openDrawer() {
  drawerEl.classList.add("open");
  drawerBackdropEl.classList.add("open");
  shellEl?.classList.remove("drawer-collapsed");
  drawerToggleEl.setAttribute("aria-expanded", "true");
}

function closeDrawer() {
  drawerEl.classList.remove("open");
  drawerBackdropEl.classList.remove("open");
  shellEl?.classList.add("drawer-collapsed");
  drawerToggleEl.setAttribute("aria-expanded", "false");
}

function isDrawerOpen() {
  return !shellEl?.classList.contains("drawer-collapsed");
}

function toggleDrawer() {
  if (isDrawerOpen()) {
    closeDrawer();
    return;
  }
  openDrawer();
}

function renderChatList() {
  chatListEl.innerHTML = "";
  chats.forEach((chat) => {
    const row = document.createElement("div");
    row.className = "chat-item-row";

    const chatButton = document.createElement("button");
    chatButton.type = "button";
    chatButton.className = "chat-item";
    if (chat.session_id === activeChatId) {
      chatButton.classList.add("active");
    }
    chatButton.textContent = chat.title;
    chatButton.title = "Double-click to rename";
    let clickTimer = null;

    async function renameChat() {
      const currentTitle = chat.title || "New chat";
      const nextTitle = window.prompt("Rename chat", currentTitle);
      if (nextTitle === null) {
        return;
      }
      const trimmed = nextTitle.trim();
      if (!trimmed || trimmed === currentTitle) {
        return;
      }
      try {
        await apiRenameChat(chat.session_id, trimmed);
        await refreshChats();
      } catch (error) {
        appendMessage("error", String(error), { persist: false });
      }
    }

    chatButton.addEventListener("click", async (event) => {
      if (event.detail > 1) {
        return;
      }
      if (clickTimer !== null) {
        clearTimeout(clickTimer);
      }
      clickTimer = window.setTimeout(async () => {
        clickTimer = null;
        if (chat.session_id === activeChatId) {
          return;
        }
        try {
          await setActiveChat(chat.session_id);
        } catch (error) {
          appendMessage("error", String(error), { persist: false });
        }
      }, 220);
    });

    chatButton.addEventListener("dblclick", async () => {
      if (clickTimer !== null) {
        clearTimeout(clickTimer);
        clickTimer = null;
      }
      await renameChat();
    });

    chatButton.addEventListener("touchstart", () => {
      if (clickTimer !== null) {
        clearTimeout(clickTimer);
        clickTimer = null;
      }
    });

    const actions = document.createElement("div");
    actions.className = "chat-item-actions";

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "chat-item-action";
    closeButton.setAttribute("aria-label", "Close chat");
    closeButton.title = "Close";
    closeButton.innerHTML = '<span class="material-symbols-outlined" aria-hidden="true">close</span>';
    closeButton.addEventListener("click", async (event) => {
      event.stopPropagation();
      const confirmed = window.confirm("Close this chat? It will be hidden from the sidebar.");
      if (!confirmed) {
        return;
      }
      try {
        const wasActive = chat.session_id === activeChatId;
        await apiDeprecateChat(chat.session_id);
        const knownChats = await refreshChats();
        if (!wasActive) {
          return;
        }
        if (knownChats.length === 0) {
          const created = await apiCreateChat();
          await refreshChats();
          await setActiveChat(created.session_id);
          return;
        }
        await setActiveChat(knownChats[0].session_id);
      } catch (error) {
        appendMessage("error", String(error), { persist: false });
      }
    });

    actions.append(closeButton);
    row.append(chatButton, actions);
    chatListEl.appendChild(row);
  });
}

function applyChats(nextChats) {
  chats = sortChatsByRecent(nextChats);
  renderChatList();
}

async function refreshChats() {
  const payload = await apiListChats();
  applyChats(payload.chats ?? []);
  return chats;
}

async function loadActiveMessages() {
  if (!activeChatId) {
    currentMessages = [];
    messageFeedbackById = new Map();
    renderCurrentMessages();
    return;
  }

  const [payload, feedbackPayload] = await Promise.all([
    apiListMessages(activeChatId),
    apiListFeedback(activeChatId),
  ]);
  messageFeedbackById = new Map(
    (feedbackPayload.feedback || []).map((item) => [item.message_id, item]),
  );
  currentMessages = (payload.messages ?? []).map((entry) => ({
    kind: entry.role === "assistant" ? "assistant" : "user",
    text: entry.content,
    messageId: entry.message_id || null,
    feedback: messageFeedbackById.get(entry.message_id) || null,
  }));
  renderCurrentMessages();
}

async function setActiveChat(sessionId) {
  clearPendingAttachments();
  activeChatId = sessionId;
  writeActiveChatId(activeChatId);
  renderChatList();
  syncExportControls();
  await loadActiveMessages();
  await loadActivePersonalization(activeChatId);
}

async function loadActivePersonalization(sessionId) {
  if (!sessionId) {
    return;
  }
  memoryScopeSelectEl.disabled = true;
  try {
    const payload = await apiGetPersonalization(sessionId);
    if (sessionId !== activeChatId) {
      return;
    }
    activeMemoryScope = normalizeMemoryScope(payload.memory_scope);
    memoryScopeSelectEl.value = activeMemoryScope;
  } catch (error) {
    if (sessionId === activeChatId) {
      appendMessage("error", String(error), { persist: false });
      memoryScopeSelectEl.value = activeMemoryScope;
    }
  } finally {
    if (sessionId === activeChatId) {
      memoryScopeSelectEl.disabled = false;
    }
  }
}

async function ensureInitialState() {
  let knownChats = await refreshChats();
  if (knownChats.length === 0) {
    await apiCreateChat();
    knownChats = await refreshChats();
  }

  if (knownChats.length === 0) {
    throw new Error("No chats available.");
  }

  const preferred = readActiveChatId();
  const defaultId =
    preferred && knownChats.some((chat) => chat.session_id === preferred)
      ? preferred
      : knownChats[0].session_id;
  await setActiveChat(defaultId);
}

newChatEl.addEventListener("click", async () => {
  try {
    await startFreshChat();
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  }
});

drawerToggleEl.addEventListener("click", () => {
  toggleDrawer();
});

memorySearchToggleEl?.addEventListener("click", () => {
  if (!memorySearchAvailable) {
    return;
  }
  setMemorySearchOpen(!memorySearchOpen);
});

drawerBackdropEl.addEventListener("click", () => {
  closeDrawer();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    if (memorySearchOpen) {
      setMemorySearchOpen(false);
      return;
    }
    closeDrawer();
  }
});

async function runMemorySearch() {
  if (!memorySearchAvailable) {
    return;
  }
  const query = memorySearchQueryEl.value.trim();
  if (!query) {
    return;
  }
  const sourceTypes = normalizeSearchSourceTypes();
  const useSessionScope = memorySearchSessionScopeEl.checked;
  const scopedSessionId = useSessionScope ? activeChatId : null;

  memorySearchRunEl.disabled = true;
  setMemorySearchStatus("Searching index...");
  memorySearchResultsEl.innerHTML = "";
  try {
    const payload = await apiFileSearch({
      query,
      sessionId: scopedSessionId,
      sourceTypes,
      limit: 6,
    });
    const matches = Array.isArray(payload.matches) ? payload.matches : [];
    renderMemorySearchResults(matches);
    if (matches.length === 0) {
      setMemorySearchStatus("No matches found. Try broader terms or another source.");
      return;
    }
    setMemorySearchStatus(`Found ${matches.length} match${matches.length === 1 ? "" : "es"}.`);
  } catch (error) {
    setMemorySearchStatus(String(error), { isError: true });
  } finally {
    memorySearchRunEl.disabled = false;
  }
}

if (memorySearchAvailable) {
  memorySearchRunEl.addEventListener("click", async () => {
    await runMemorySearch();
  });
  memorySearchQueryEl.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    await runMemorySearch();
  });
}

memoryScopeSelectEl.addEventListener("change", async () => {
  if (!activeChatId) {
    return;
  }
  const previousScope = activeMemoryScope;
  const nextScope = normalizeMemoryScope(memoryScopeSelectEl.value);
  if (nextScope === previousScope) {
    return;
  }

  memoryScopeSelectEl.disabled = true;
  try {
    const payload = await apiSetPersonalization(activeChatId, nextScope);
    activeMemoryScope = normalizeMemoryScope(payload.memory_scope);
    memoryScopeSelectEl.value = activeMemoryScope;
  } catch (error) {
    memoryScopeSelectEl.value = previousScope;
    appendMessage("error", String(error), { persist: false });
  } finally {
    memoryScopeSelectEl.disabled = false;
  }
});

composerEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const messageText = messageEl.value.trim();
  const queuedAttachments = [...pendingAttachments];
  if ((!messageText && queuedAttachments.length === 0) || !activeChatId) {
    return;
  }

  const noteText = parsePreferenceNote(messageText);
  if (noteText && queuedAttachments.length === 0) {
    try {
      await apiAddNote(activeChatId, noteText);
      messageEl.value = "";
      autoSizeComposer();
      await refreshChats();
    } catch (error) {
      appendMessage("error", String(error), { persist: false });
    }
    return;
  }

  for (const attachment of queuedAttachments) {
    appendImagePrompt(attachment.data_base64, attachment.source_name, { scroll: false });
  }
  if (messageText) {
    appendMessage("user", messageText);
  }
  messageEl.value = "";
  clearPendingAttachments();
  autoSizeComposer();
  const thinkingNode = appendThinkingIndicator();

  try {
    const outboundMessage = messageText || DEFAULT_ATTACHMENT_PROMPT;
    const result = await sendMessage(outboundMessage, activeChatId, {
      attachments: queuedAttachments.map((attachment) => ({
        data_base64: attachment.data_base64,
        source_name: attachment.source_name,
        mime_type: attachment.mime_type,
        memory_scope: attachment.memory_scope,
      })),
    });
    await sleep(RESPONSE_RENDER_DELAY_MS);
    thinkingNode.remove();
    await appendAssistantTypedMessage(result.output, {
      messageId: result.assistant_message_id || null,
      sessionId: activeChatId,
      feedback: result.assistant_message_id
        ? messageFeedbackById.get(result.assistant_message_id) || null
        : null,
    });
    await refreshChats();
  } catch (error) {
    thinkingNode.remove();
    appendMessage("error", String(error), { persist: false });
  }
});

messageEl.addEventListener("input", autoSizeComposer);
messageEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    composerEl.requestSubmit();
  }
});

resetEl.addEventListener("click", async () => {
  if (!activeChatId) {
    return;
  }
  try {
    await startFreshChat({ deprecateCurrent: true });
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  }
});

evalSubmitEl?.addEventListener("click", async () => {
  if (!activeChatId || evalSubmitEl.disabled) {
    return;
  }
  evalSubmitEl.disabled = true;
  try {
    await submitEvalCheckpoint();
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  } finally {
    evalSubmitEl.disabled = false;
  }
});

exportMarkdownEl.addEventListener("click", async () => {
  if (!activeChatId) {
    return;
  }
  await withExportLock(async () => {
    try {
      const payload = await apiExportChat(activeChatId, { includeMarkdown: true });
      const markdown = String(payload.markdown || "").trim();
      if (!markdown) {
        throw new Error("No markdown transcript available for this chat.");
      }
      triggerDownload(
        `${exportBaseName(payload)}.md`,
        `${payload.markdown}\n`,
        "text/markdown;charset=utf-8",
      );
    } catch (error) {
      appendMessage("error", String(error), { persist: false });
    }
  });
});

exportJsonEl.addEventListener("click", async () => {
  if (!activeChatId) {
    return;
  }
  await withExportLock(async () => {
    try {
      const payload = await apiExportChat(activeChatId);
      downloadJson(`${exportBaseName(payload)}.json`, payload);
    } catch (error) {
      appendMessage("error", String(error), { persist: false });
    }
  });
});

exportOcrEl.addEventListener("click", async () => {
  if (!activeChatId) {
    return;
  }
  await withExportLock(async () => {
    try {
      const payload = await apiExportChat(activeChatId);
      downloadJson(`${exportBaseName(payload)}.ocr-runs.json`, {
        session_id: payload.session_id,
        title: payload.title,
        memory_scope: normalizeMemoryScope(payload.memory_scope),
        context_scope: payload.context_scope === "local" ? "local" : "global",
        exported_at: payload.exported_at,
        ocr_run_count: Array.isArray(payload.ocr_runs) ? payload.ocr_runs.length : 0,
        ocr_runs: payload.ocr_runs || [],
      });
    } catch (error) {
      appendMessage("error", String(error), { persist: false });
    }
  });
});

ocrUploadEl?.addEventListener("click", () => {
  if (!activeChatId || ocrUploadEl.disabled) {
    return;
  }
  ocrFileInputEl.click();
});

ocrFileInputEl?.addEventListener("change", async () => {
  const files = [...(ocrFileInputEl.files || [])];
  if (files.length === 0) {
    return;
  }
  ocrUploadEl.disabled = true;
  try {
    await queueAttachmentFiles(files);
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  } finally {
    ocrUploadEl.disabled = false;
    ocrFileInputEl.value = "";
  }
});

composerEl.addEventListener("dragenter", (event) => {
  const types = event.dataTransfer?.types;
  if (!types || !Array.from(types).includes("Files")) {
    return;
  }
  event.preventDefault();
  attachmentDragDepth += 1;
  setComposerDropActive(true);
});

composerEl.addEventListener("dragover", (event) => {
  const types = event.dataTransfer?.types;
  if (!types || !Array.from(types).includes("Files")) {
    return;
  }
  event.preventDefault();
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = "copy";
  }
});

composerEl.addEventListener("dragleave", (event) => {
  const types = event.dataTransfer?.types;
  if (!types || !Array.from(types).includes("Files")) {
    return;
  }
  event.preventDefault();
  attachmentDragDepth = Math.max(0, attachmentDragDepth - 1);
  if (attachmentDragDepth === 0) {
    setComposerDropActive(false);
  }
});

composerEl.addEventListener("drop", async (event) => {
  event.preventDefault();
  attachmentDragDepth = 0;
  setComposerDropActive(false);
  const files = [...(event.dataTransfer?.files || [])];
  if (files.length === 0) {
    return;
  }
  ocrUploadEl.disabled = true;
  try {
    await queueAttachmentFiles(files);
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  } finally {
    ocrUploadEl.disabled = false;
  }
});

(async () => {
  try {
    initTheme();
    syncExportControls();
    if (memorySearchAvailable) {
      setMemorySearchOpen(false);
      setMemorySearchStatus("");
    } else {
      if (memorySearchPanelEl) {
        memorySearchPanelEl.hidden = true;
      }
    }
    await ensureInitialState();
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  } finally {
    if (window.matchMedia("(min-width: 901px)").matches) {
      openDrawer();
    } else {
      closeDrawer();
    }
    autoSizeComposer();
    syncEmptyState();
  }
})();
