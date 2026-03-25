import test from "node:test";
import assert from "node:assert/strict";
import {
  coerceFeedbackEntry,
  deriveOutcomeFromStreams,
  formatFeedbackStatusText,
  inferRubricSelectionsFromFeedback,
  normalizeFeedbackOutcome,
} from "../src/eval-rubric.js";

test("coerceFeedbackEntry maps legacy pass tags to positive stream", () => {
  const coerced = coerceFeedbackEntry({
    message_id: "msg-1",
    outcome: "pass",
    tags: ["style", "grounded"],
  });
  assert.deepEqual(coerced?.positive_tags, ["style", "grounded"]);
  assert.deepEqual(coerced?.negative_tags, []);
  assert.deepEqual(coerced?.tags, ["style", "grounded"]);
});

test("deriveOutcomeFromStreams keeps pass when only soft negative style penalty exists", () => {
  const outcome = deriveOutcomeFromStreams(["style"], ["default_style"]);
  assert.equal(outcome, "pass");
});

test("formatFeedbackStatusText is stream-first for dual signals", () => {
  const text = formatFeedbackStatusText({
    outcome: "fail",
    positive_tags: ["style"],
    negative_tags: ["hallucination_risk", "em_dash_style"],
  });
  assert.equal(text, "pass: style • fail: hallucination_risk, em_dash_style");
});

test("normalizeFeedbackOutcome infers fail from positive + hard-negative streams", () => {
  const outcome = normalizeFeedbackOutcome({
    positive_tags: ["style"],
    negative_tags: ["hallucination_risk"],
  });
  assert.equal(outcome, "fail");
});

test("inferRubricSelectionsFromFeedback handles compatibility tags", () => {
  const selection = inferRubricSelectionsFromFeedback({
    outcome: "pass",
    tags: ["style", "grounded"],
  });
  assert.equal(selection.style, "pass");
  assert.equal(selection.hallucination_risk, "pass");
});
