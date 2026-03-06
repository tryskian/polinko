import { expect, test } from "@playwright/test";

function nowMs() {
  return Date.now();
}

function makeChat({ sessionId, title, createdAt, updatedAt, messageCount = 0, status = "active" }) {
  return {
    session_id: sessionId,
    title,
    created_at: createdAt,
    updated_at: updatedAt,
    message_count: messageCount,
    memory_scope: "global",
    context_scope: "global",
    status,
    deprecated_at: status === "deprecated" ? updatedAt : null,
  };
}

function createMockState() {
  const createdAt = nowMs();
  const sessionId = "e2e-seed-chat";
  return {
    seq: 0,
    chats: [
      makeChat({
        sessionId,
        title: "E2E Seed Chat",
        createdAt,
        updatedAt: createdAt,
      }),
    ],
    messagesBySession: {
      [sessionId]: [],
    },
    feedbackBySession: {
      [sessionId]: [],
    },
    memoryScopeBySession: {
      [sessionId]: "global",
    },
  };
}

function nextMessageId(state) {
  state.seq += 1;
  return `msg_e2e_${state.seq}`;
}

test.beforeEach(async ({ page }) => {
  const state = createMockState();

  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const method = request.method();
    const path = url.pathname;

    const isApiPath =
      path === "/chat" ||
      path === "/health" ||
      path === "/session/reset" ||
      path.startsWith("/chats") ||
      path.startsWith("/skills");

    if (!isApiPath) {
      await route.continue();
      return;
    }

    const json = (status, body) =>
      route.fulfill({
        status,
        contentType: "application/json",
        body: JSON.stringify(body),
      });

    const parseBody = () => {
      try {
        return request.postDataJSON() || {};
      } catch {
        return {};
      }
    };

    if (method === "GET" && path === "/health") {
      await json(200, { status: "ok" });
      return;
    }

    if (path === "/chats" && method === "GET") {
      await json(200, {
        chats: state.chats.filter((chat) => chat.status !== "deprecated"),
      });
      return;
    }

    if (path === "/chats" && method === "POST") {
      const payload = parseBody();
      const createdAt = nowMs();
      const sessionId =
        typeof payload.session_id === "string" && payload.session_id.trim()
          ? payload.session_id.trim()
          : `e2e-chat-${createdAt}`;
      const chat = makeChat({
        sessionId,
        title: "New chat",
        createdAt,
        updatedAt: createdAt,
      });
      state.chats.unshift(chat);
      state.messagesBySession[sessionId] = [];
      state.feedbackBySession[sessionId] = [];
      state.memoryScopeBySession[sessionId] = "global";
      await json(200, chat);
      return;
    }

    const messagesMatch = path.match(/^\/chats\/([^/]+)\/messages$/);
    if (messagesMatch && method === "GET") {
      const sessionId = decodeURIComponent(messagesMatch[1]);
      await json(200, {
        session_id: sessionId,
        messages: state.messagesBySession[sessionId] || [],
      });
      return;
    }

    const feedbackMatch = path.match(/^\/chats\/([^/]+)\/feedback$/);
    if (feedbackMatch && method === "GET") {
      const sessionId = decodeURIComponent(feedbackMatch[1]);
      await json(200, {
        session_id: sessionId,
        feedback: state.feedbackBySession[sessionId] || [],
      });
      return;
    }

    const personalizationMatch = path.match(/^\/chats\/([^/]+)\/personalization$/);
    if (personalizationMatch && method === "GET") {
      const sessionId = decodeURIComponent(personalizationMatch[1]);
      await json(200, {
        session_id: sessionId,
        memory_scope: state.memoryScopeBySession[sessionId] || "global",
      });
      return;
    }

    if (personalizationMatch && method === "POST") {
      const sessionId = decodeURIComponent(personalizationMatch[1]);
      const payload = parseBody();
      const memoryScope = payload.memory_scope === "session" ? "session" : "global";
      state.memoryScopeBySession[sessionId] = memoryScope;
      await json(200, {
        session_id: sessionId,
        memory_scope: memoryScope,
      });
      return;
    }

    const notesMatch = path.match(/^\/chats\/([^/]+)\/notes$/);
    if (notesMatch && method === "POST") {
      const sessionId = decodeURIComponent(notesMatch[1]);
      const payload = parseBody();
      const note = String(payload.note || "").trim();
      if (note) {
        state.messagesBySession[sessionId] = state.messagesBySession[sessionId] || [];
        state.messagesBySession[sessionId].push({
          role: "note",
          content: note,
          created_at: nowMs(),
          message_id: nextMessageId(state),
          parent_message_id: null,
        });
      }
      await json(200, { status: "ok", session_id: sessionId });
      return;
    }

    if (path === "/chat" && method === "POST") {
      const payload = parseBody();
      const sessionId = String(payload.session_id || "");
      const userText = String(payload.message || "");
      const createdAt = nowMs();
      const userMessageId = nextMessageId(state);
      const assistantMessageId = nextMessageId(state);
      state.messagesBySession[sessionId] = state.messagesBySession[sessionId] || [];
      state.messagesBySession[sessionId].push(
        {
          role: "user",
          content: userText,
          created_at: createdAt,
          message_id: userMessageId,
          parent_message_id: null,
        },
        {
          role: "assistant",
          content: "E2E mock response",
          created_at: createdAt + 1,
          message_id: assistantMessageId,
          parent_message_id: userMessageId,
        },
      );
      const target = state.chats.find((chat) => chat.session_id === sessionId);
      if (target) {
        target.message_count += 2;
        target.updated_at = createdAt;
        if (target.title === "New chat" && userText.trim()) {
          target.title = userText.trim().slice(0, 42);
        }
      }
      await json(200, {
        output: "E2E mock response",
        assistant_message_id: assistantMessageId,
      });
      return;
    }

    if (path === "/session/reset" && method === "POST") {
      await json(200, { status: "ok" });
      return;
    }

    await json(404, { detail: `Unhandled mocked route: ${method} ${path}` });
  });
});

test("loads the shell and sends a message", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("button", { name: "New chat" })).toBeVisible();
  await expect(page.getByRole("button", { name: "E2E Seed Chat" })).toBeVisible();

  await page.getByPlaceholder("message bigbrain").fill("hello from playwright");
  await page.keyboard.press("Enter");

  await expect(page.getByText("hello from playwright")).toBeVisible();
  await expect(page.getByText("E2E mock response")).toBeVisible();
});

test("creates a fresh chat from sidebar", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "New chat" }).click();

  await expect(page.getByRole("button", { name: "E2E Seed Chat" })).toBeVisible();
  await expect(page.getByRole("button", { name: "New chat" })).toBeVisible();
});
