import { expect, test } from "@playwright/test";

const ONE_BY_ONE_PNG_BASE64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+qW6QAAAAASUVORK5CYII=";

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
      [sessionId]: [
        {
          session_id: sessionId,
          message_id: "seed-feedback-msg",
          outcome: "pass",
          positive_tags: ["accurate"],
          negative_tags: [],
          tags: ["accurate"],
          note: null,
          recommended_action: null,
          action_taken: null,
          status: "closed",
          created_at: createdAt,
          updated_at: createdAt,
        },
      ],
    },
    checkpointsBySession: {
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
      state.checkpointsBySession[sessionId] = [];
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

    const checkpointsMatch = path.match(/^\/chats\/([^/]+)\/feedback\/checkpoints$/);
    if (checkpointsMatch && method === "GET") {
      const sessionId = decodeURIComponent(checkpointsMatch[1]);
      await json(200, {
        session_id: sessionId,
        checkpoints: state.checkpointsBySession[sessionId] || [],
      });
      return;
    }

    if (checkpointsMatch && method === "POST") {
      const sessionId = decodeURIComponent(checkpointsMatch[1]);
      const feedback = state.feedbackBySession[sessionId] || [];
      if (feedback.length === 0) {
        await json(400, { detail: "No saved evals in this chat yet." });
        return;
      }
      const passCount = feedback.filter((entry) => String(entry.outcome || "").toLowerCase() === "pass").length;
      const failCount = feedback.filter((entry) => String(entry.outcome || "").toLowerCase() === "fail").length;
      const totalCount = feedback.length;
      const otherCount = Math.max(0, totalCount - passCount - failCount);
      const checkpoint = {
        checkpoint_id: `eval_e2e_${nowMs()}_${(state.checkpointsBySession[sessionId] || []).length + 1}`,
        session_id: sessionId,
        total_count: totalCount,
        pass_count: passCount,
        fail_count: failCount,
        other_count: otherCount,
        created_at: nowMs(),
      };
      const existing = state.checkpointsBySession[sessionId] || [];
      state.checkpointsBySession[sessionId] = [...existing, checkpoint];
      await json(200, checkpoint);
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
      const sourceUserMessageId = String(payload.source_user_message_id || "").trim();
      const attachmentCount = Array.isArray(payload.attachments) ? payload.attachments.length : 0;
      const createdAt = nowMs();
      const assistantMessageId = nextMessageId(state);
      state.messagesBySession[sessionId] = state.messagesBySession[sessionId] || [];
      let responseText = "E2E mock response";

      if (sourceUserMessageId) {
        // Retry variant path: create only a new assistant message under the
        // original user message lineage (no duplicated user row).
        const sourceExists = state.messagesBySession[sessionId].some(
          (entry) => entry.role === "user" && entry.message_id === sourceUserMessageId,
        );
        if (!sourceExists) {
          await json(404, { detail: "Source user message not found for retry." });
          return;
        }
        responseText = "E2E retry variant response";
        state.messagesBySession[sessionId].push({
          role: "assistant",
          content: responseText,
          created_at: createdAt + 1,
          message_id: assistantMessageId,
          parent_message_id: sourceUserMessageId,
        });
      } else {
        if (userText.trim().toLowerCase() === "try again") {
          if (attachmentCount > 0) {
            responseText = "E2E OCR retry reused prior image";
          } else {
            responseText = "No new image evidence in this turn.";
          }
        }
        const userMessageId = nextMessageId(state);
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
            content: responseText,
            created_at: createdAt + 1,
            message_id: assistantMessageId,
            parent_message_id: userMessageId,
          },
        );
      }

      const target = state.chats.find((chat) => chat.session_id === sessionId);
      if (target) {
        target.message_count += sourceUserMessageId ? 1 : 2;
        target.updated_at = createdAt;
        if (target.title === "New chat" && userText.trim()) {
          target.title = userText.trim().slice(0, 42);
        }
      }
      await json(200, {
        output: responseText,
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
  await expect(page.getByLabel("Chat threads").getByRole("button", { name: "New chat" })).toBeVisible();
});

test("retries assistant response as a variant without duplicating the user message", async ({ page }) => {
  await page.goto("/");

  await page.getByPlaceholder("message bigbrain").fill("variant lineage prompt");
  await page.keyboard.press("Enter");
  await expect(page.getByText("E2E mock response")).toBeVisible();

  // Reload to ensure the retry lineage can resolve persisted user message IDs.
  await page.reload();
  await expect(page.getByText("E2E mock response")).toBeVisible();

  await page.getByRole("button", { name: "Retry this response with the same prompt" }).first().click();
  await expect(page.getByText("E2E retry variant response")).toBeVisible();

  await expect(page.getByText("Variant 2 of 2")).toBeVisible();
  await expect(page.locator(".msg.user")).toHaveCount(1);

  await page.getByRole("button", { name: "Prev" }).click();
  await expect(page.getByText("Variant 1 of 2")).toBeVisible();
  await expect(page.getByText("E2E mock response")).toBeVisible();

  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByText("Variant 2 of 2")).toBeVisible();
  await expect(page.getByText("E2E retry variant response")).toBeVisible();
});

test("jump-to-latest retry selection works after browsing older variants", async ({ page }) => {
  await page.goto("/");

  await page.getByPlaceholder("message bigbrain").fill("multi retry lineage prompt");
  await page.keyboard.press("Enter");
  await expect(page.getByText("E2E mock response")).toBeVisible();

  // Ensure persisted lineage IDs are loaded before retrying variants.
  await page.reload();
  await expect(page.getByText("E2E mock response")).toBeVisible();

  await page.getByRole("button", { name: "Retry this response with the same prompt" }).first().click();
  await expect(page.getByText("Variant 2 of 2")).toBeVisible();

  await page.getByRole("button", { name: "Prev" }).click();
  await expect(page.getByText("Variant 1 of 2")).toBeVisible();

  await page.getByRole("button", { name: "Retry this response with the same prompt" }).first().click();
  await expect(page.getByText("Variant 3 of 3")).toBeVisible();
});

test("eval checkpoint confirmations persist across reload and chat switches", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Submit eval checkpoint" }).click();
  await expect(page.getByText(/Eval checkpoint 1/i)).toBeVisible();

  await page.getByRole("button", { name: "Submit eval checkpoint" }).click();
  await expect(page.getByText(/Eval checkpoint 2/i)).toBeVisible();

  await page.getByRole("button", { name: "New chat" }).click();
  await expect(page.getByLabel("Chat threads").getByRole("button", { name: "New chat" })).toBeVisible();

  await page.getByRole("button", { name: "E2E Seed Chat" }).click();
  await expect(page.getByText(/Eval checkpoint 1/i)).toBeVisible();
  await expect(page.getByText(/Eval checkpoint 2/i)).toBeVisible();

  await page.reload();
  await expect(page.getByText(/Eval checkpoint 1/i)).toBeVisible();
  await expect(page.getByText(/Eval checkpoint 2/i)).toBeVisible();
});

test("keeps uploaded images visible after switching chats and back", async ({ page }) => {
  await page.goto("/");

  await page.locator("#ocr-file-input").setInputFiles({
    name: "phi.png",
    mimeType: "image/png",
    buffer: Buffer.from(ONE_BY_ONE_PNG_BASE64, "base64"),
  });
  await page.getByPlaceholder("message bigbrain").fill("phi persists");
  await page.keyboard.press("Enter");
  await page.keyboard.press("Enter");

  await expect(page.locator(".msg.user.user-image img.user-image-preview")).toHaveCount(1);
  await expect(page.getByText("phi.png")).toBeVisible();

  await page.getByRole("button", { name: "New chat" }).click();
  await expect(page.getByLabel("Chat threads").getByRole("button", { name: "New chat" })).toBeVisible();

  await page.getByRole("button", { name: "E2E Seed Chat" }).click();
  await expect(page.locator(".msg.user.user-image img.user-image-preview")).toHaveCount(1);
  await expect(page.getByText("phi.png")).toBeVisible();

  await page.reload();
  await expect(page.locator(".msg.user.user-image img.user-image-preview")).toHaveCount(1);
  await expect(page.getByText("phi.png")).toBeVisible();
});

test("supports pasting an image directly into the prompt field", async ({ page }) => {
  await page.goto("/");

  await page.evaluate((base64) => {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let idx = 0; idx < binary.length; idx += 1) {
      bytes[idx] = binary.charCodeAt(idx);
    }
    const file = new File([bytes], "pasted-image.png", { type: "image/png" });
    const transfer = new DataTransfer();
    transfer.items.add(file);
    const textarea = document.querySelector("#message");
    const pasteEvent = new Event("paste", { bubbles: true, cancelable: true });
    Object.defineProperty(pasteEvent, "clipboardData", {
      value: transfer,
    });
    textarea.dispatchEvent(pasteEvent);
  }, ONE_BY_ONE_PNG_BASE64);

  await expect(page.getByText("pasted-image.png")).toBeVisible();
  await page.getByPlaceholder("message bigbrain").fill("from paste");
  await page.keyboard.press("Enter");
  await page.keyboard.press("Enter");
  await expect(page.locator(".msg.user.user-image img.user-image-preview")).toHaveCount(1);
});

test("reuses the latest image batch on OCR follow-up turns without re-upload", async ({ page }) => {
  await page.goto("/");

  await page.locator("#ocr-file-input").setInputFiles({
    name: "phi.png",
    mimeType: "image/png",
    buffer: Buffer.from(ONE_BY_ONE_PNG_BASE64, "base64"),
  });
  await page.getByPlaceholder("message bigbrain").fill("what letters are these?");
  await page.keyboard.press("Enter");
  await expect(page.getByText("E2E mock response")).toBeVisible();

  await page.getByPlaceholder("message bigbrain").fill("try again");
  await page.keyboard.press("Enter");
  await expect(page.getByText("E2E OCR retry reused prior image")).toBeVisible();
});
