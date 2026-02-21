import "./style.css";

const chatEl = document.getElementById("chat");
const composerEl = document.getElementById("composer");
const messageEl = document.getElementById("message");
const sessionIdEl = document.getElementById("session-id");
const resetEl = document.getElementById("reset");

const SESSION_STORAGE_KEY = "polinko_ui_session_id";
const API_KEY_STORAGE_KEY = "polinko_server_api_key_session";

function ensureSessionApiKey() {
  const existing = sessionStorage.getItem(API_KEY_STORAGE_KEY);
  if (existing !== null) {
    return existing;
  }
  const entered = window.prompt(
    "Enter x-api-key for this browser session (leave blank if API auth is disabled):",
  );
  const value = (entered ?? "").trim();
  sessionStorage.setItem(API_KEY_STORAGE_KEY, value);
  return value;
}

function appendMessage(kind, text) {
  const node = document.createElement("article");
  node.className = `msg ${kind}`;
  node.textContent = text;
  chatEl.appendChild(node);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function headers() {
  const hdrs = {
    "Content-Type": "application/json",
  };
  const apiKey = ensureSessionApiKey();
  if (apiKey) {
    hdrs["x-api-key"] = apiKey;
  }
  return hdrs;
}

function currentSessionId() {
  const value = sessionIdEl.value.trim();
  return value || null;
}

async function sendMessage(messageText) {
  const resp = await fetch("/chat", {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      message: messageText,
      session_id: currentSessionId(),
    }),
  });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    const retryAfter = resp.headers.get("Retry-After");
    const detail = body.detail || `HTTP ${resp.status}`;
    throw new Error(retryAfter ? `${detail} (retry in ~${retryAfter}s)` : detail);
  }

  return resp.json();
}

async function resetSession() {
  const resp = await fetch("/session/reset", {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      session_id: currentSessionId(),
    }),
  });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${resp.status}`);
  }

  return resp.json();
}

composerEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const messageText = messageEl.value.trim();
  if (!messageText) {
    return;
  }

  appendMessage("user", messageText);
  messageEl.value = "";

  try {
    const result = await sendMessage(messageText);
    appendMessage("assistant", result.output);
  } catch (error) {
    appendMessage("error", String(error));
  }
});

resetEl.addEventListener("click", async () => {
  try {
    const result = await resetSession();
    appendMessage("meta", `Session reset: ${result.session_id}`);
  } catch (error) {
    appendMessage("error", String(error));
  }
});

sessionIdEl.addEventListener("change", () => {
  const value = sessionIdEl.value.trim();
  if (!value) {
    localStorage.removeItem(SESSION_STORAGE_KEY);
    return;
  }
  localStorage.setItem(SESSION_STORAGE_KEY, value);
});

const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
if (savedSessionId) {
  sessionIdEl.value = savedSessionId;
}
ensureSessionApiKey();

appendMessage("meta", "Connected. Start chatting.");
