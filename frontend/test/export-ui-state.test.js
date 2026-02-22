import test from "node:test";
import assert from "node:assert/strict";
import { createExportUiState } from "../src/export-ui-state.js";

test("sync disables controls when no active chat", () => {
  let activeChatId = "";
  const calls = [];
  const state = createExportUiState({
    getActiveChatId: () => activeChatId,
    setButtonsDisabled: (disabled) => calls.push(disabled),
  });

  state.sync();
  assert.equal(calls.at(-1), true);

  activeChatId = "chat-1";
  state.sync();
  assert.equal(calls.at(-1), false);
});

test("runLocked enforces in-flight lock and re-enables after completion", async () => {
  const calls = [];
  let resolveTask;
  const taskPromise = new Promise((resolve) => {
    resolveTask = resolve;
  });

  const state = createExportUiState({
    getActiveChatId: () => "chat-1",
    setButtonsDisabled: (disabled) => calls.push(disabled),
  });

  const firstRun = state.runLocked(() => taskPromise);
  assert.equal(state.isInFlight(), true);
  assert.equal(calls.at(-1), true);

  const secondRunResult = await state.runLocked(() => Promise.resolve());
  assert.equal(secondRunResult, false);
  assert.equal(state.isInFlight(), true);

  resolveTask();
  const firstRunResult = await firstRun;
  assert.equal(firstRunResult, true);
  assert.equal(state.isInFlight(), false);
  assert.equal(calls.at(-1), false);
});

test("runLocked is skipped when no active chat", async () => {
  const calls = [];
  const state = createExportUiState({
    getActiveChatId: () => "",
    setButtonsDisabled: (disabled) => calls.push(disabled),
  });

  const ran = await state.runLocked(() => Promise.resolve());
  assert.equal(ran, false);
  assert.equal(state.isInFlight(), false);
  assert.equal(calls.at(-1), true);
});
