import "./style.css";
import { createExportUiState } from "./export-ui-state.js";

const STORAGE_ACTIVE_CHAT_KEY = "polinko.active_chat_id.v2";

const chatEl = document.getElementById("chat");
const composerEl = document.getElementById("composer");
const messageEl = document.getElementById("message");
const ocrFileInputEl = document.getElementById("ocr-file-input");
const ocrUploadEl = document.getElementById("ocr-upload");
const shellEl = document.querySelector(".shell");
const resetEl = document.getElementById("reset");
const exportMarkdownEl = document.getElementById("export-markdown");
const exportJsonEl = document.getElementById("export-json");
const exportOcrEl = document.getElementById("export-ocr");
const emptyStateEl = document.getElementById("empty-state");
const newChatEl = document.getElementById("new-chat");
const drawerToggleEl = document.getElementById("drawer-toggle");
const drawerEl = document.getElementById("chat-drawer");
const drawerBackdropEl = document.getElementById("drawer-backdrop");
const chatListEl = document.getElementById("chat-list");
const RESPONSE_RENDER_DELAY_MS = 220;

let chats = [];
let activeChatId = "";
let currentMessages = [];

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

function appendMessage(kind, text, { persist = true, scroll = true } = {}) {
  const node = document.createElement("article");
  node.className = `msg ${kind}`;
  if (kind === "assistant" || kind === "user") {
    node.innerHTML = renderMarkdown(text);
  } else {
    node.textContent = text;
  }
  chatEl.appendChild(node);
  if (persist) {
    currentMessages.push({ kind, text });
  }
  syncEmptyState();
  if (scroll) {
    chatEl.scrollTop = chatEl.scrollHeight;
  }
}

function renderCurrentMessages() {
  chatEl.querySelectorAll(".msg").forEach((node) => node.remove());
  currentMessages.forEach((entry) => {
    appendMessage(entry.kind, entry.text, { persist: false, scroll: false });
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

async function sendMessage(messageText, sessionId) {
  return requestJson("/chat", {
    method: "POST",
    body: JSON.stringify({ message: messageText, session_id: sessionId }),
  });
}

async function runOcr(payload) {
  return requestJson("/skills/ocr", {
    method: "POST",
    body: JSON.stringify(payload),
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

function parsePreferenceNote(value) {
  const match = value.match(/^\/note(?:\s+|:\s*)([\s\S]+)$/i);
  if (!match) {
    return "";
  }
  return match[1].trim();
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
  closeDrawer();
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

async function handleOcrUpload(file) {
  if (!file || !activeChatId) {
    return;
  }

  ocrUploadEl.disabled = true;
  const thinkingNode = appendThinkingIndicator();
  try {
    const dataBase64 = await readFileAsDataUrl(file);
    await runOcr({
      session_id: activeChatId,
      source_name: file.name,
      mime_type: file.type || null,
      data_base64: dataBase64,
      attach_to_chat: true,
    });
    await sleep(RESPONSE_RENDER_DELAY_MS);
    thinkingNode.remove();
    await loadActiveMessages();
    await refreshChats();
  } catch (error) {
    thinkingNode.remove();
    appendMessage("error", String(error), { persist: false });
  } finally {
    ocrUploadEl.disabled = false;
    ocrFileInputEl.value = "";
  }
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
          closeDrawer();
          return;
        }
        try {
          await setActiveChat(chat.session_id);
          closeDrawer();
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
    renderCurrentMessages();
    return;
  }

  const payload = await apiListMessages(activeChatId);
  currentMessages = (payload.messages ?? []).map((entry) => ({
    kind: entry.role === "assistant" ? "assistant" : "user",
    text: entry.content,
  }));
  renderCurrentMessages();
}

async function setActiveChat(sessionId) {
  activeChatId = sessionId;
  writeActiveChatId(activeChatId);
  renderChatList();
  syncExportControls();
  await loadActiveMessages();
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

drawerBackdropEl.addEventListener("click", () => {
  closeDrawer();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeDrawer();
  }
});

composerEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const messageText = messageEl.value.trim();
  if (!messageText || !activeChatId) {
    return;
  }

  const noteText = parsePreferenceNote(messageText);
  if (noteText) {
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

  appendMessage("user", messageText);
  messageEl.value = "";
  autoSizeComposer();
  const thinkingNode = appendThinkingIndicator();

  try {
    const result = await sendMessage(messageText, activeChatId);
    await sleep(RESPONSE_RENDER_DELAY_MS);
    thinkingNode.remove();
    appendMessage("assistant", result.output);
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
        exported_at: payload.exported_at,
        ocr_run_count: Array.isArray(payload.ocr_runs) ? payload.ocr_runs.length : 0,
        ocr_runs: payload.ocr_runs || [],
      });
    } catch (error) {
      appendMessage("error", String(error), { persist: false });
    }
  });
});

ocrUploadEl.addEventListener("click", () => {
  if (!activeChatId || ocrUploadEl.disabled) {
    return;
  }
  ocrFileInputEl.click();
});

ocrFileInputEl.addEventListener("change", async () => {
  const [file] = ocrFileInputEl.files || [];
  await handleOcrUpload(file);
});

(async () => {
  try {
    syncExportControls();
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
