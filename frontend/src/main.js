import "./style.css";

const STORAGE_ACTIVE_CHAT_KEY = "polinko.active_chat_id.v2";

const chatEl = document.getElementById("chat");
const composerEl = document.getElementById("composer");
const messageEl = document.getElementById("message");
const resetEl = document.getElementById("reset");
const emptyStateEl = document.getElementById("empty-state");
const chatSelectEl = document.getElementById("chat-select");
const newChatEl = document.getElementById("new-chat");
const RESPONSE_RENDER_DELAY_MS = 220;

let chats = [];
let activeChatId = "";
let currentMessages = [];

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

async function sendMessage(messageText, sessionId) {
  return requestJson("/chat", {
    method: "POST",
    body: JSON.stringify({ message: messageText, session_id: sessionId }),
  });
}

async function resetSession(sessionId) {
  return requestJson("/session/reset", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
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

function sortChatsByRecent(nextChats) {
  return [...nextChats].sort((a, b) => b.updated_at - a.updated_at || b.created_at - a.created_at);
}

function applyChats(nextChats) {
  chats = sortChatsByRecent(nextChats);
  refreshChatSelector();
}

function refreshChatSelector() {
  chatSelectEl.innerHTML = "";
  chats.forEach((chat) => {
    const option = document.createElement("option");
    option.value = chat.session_id;
    option.textContent = chat.title;
    chatSelectEl.appendChild(option);
  });
  if (activeChatId) {
    chatSelectEl.value = activeChatId;
  }
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
  chatSelectEl.value = activeChatId;
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

chatSelectEl.addEventListener("change", async (event) => {
  const nextId = String(event.target.value || "");
  if (!nextId || nextId === activeChatId) {
    return;
  }
  try {
    await setActiveChat(nextId);
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  }
});

newChatEl.addEventListener("click", async () => {
  try {
    const created = await apiCreateChat();
    await refreshChats();
    await setActiveChat(created.session_id);
    messageEl.focus();
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  }
});

composerEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const messageText = messageEl.value.trim();
  if (!messageText || !activeChatId) {
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
    chatSelectEl.value = activeChatId;
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
    await resetSession(activeChatId);
    currentMessages = [];
    renderCurrentMessages();
    await refreshChats();
    chatSelectEl.value = activeChatId;
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  }
});

(async () => {
  try {
    await ensureInitialState();
  } catch (error) {
    appendMessage("error", String(error), { persist: false });
  } finally {
    autoSizeComposer();
    syncEmptyState();
  }
})();
