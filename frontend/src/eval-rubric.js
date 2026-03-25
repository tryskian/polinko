const FEEDBACK_POSITIVE_TAG_OPTIONS = [
  "accurate",
  "high_value",
  "medium_value",
  "low_value",
  "recovered",
  "ocr_accurate",
  "grounded",
  "style",
];

const FEEDBACK_NEGATIVE_TAG_OPTIONS = [
  "ocr_miss",
  "grounding_gap",
  "style_mismatch",
  "default_style",
  "em_dash_style",
  "hallucination_risk",
  "needs_retry",
];

export const FEEDBACK_PASS_SOFT_NEGATIVE_TAGS = ["default_style"];
export const FEEDBACK_PASS_SOFT_NEGATIVE_TAG_SET = new Set(FEEDBACK_PASS_SOFT_NEGATIVE_TAGS);

export const FEEDBACK_OPTIONAL_STYLE_NEGATIVE_TAGS = [
  { key: "default_style", label: "default/straight style" },
  { key: "em_dash_style", label: "em-dash style" },
];

export const FEEDBACK_RUBRIC_DIMENSIONS = [
  {
    key: "style",
    label: "Style",
    levels: [
      { key: "pass", label: "pass", positiveTags: ["style"], negativeTags: [] },
      { key: "fail", label: "fail", positiveTags: [], negativeTags: ["style_mismatch"] },
    ],
  },
  {
    key: "hallucination_risk",
    label: "Hallucination risk",
    levels: [
      { key: "pass", label: "pass", positiveTags: ["grounded"], negativeTags: [] },
      { key: "fail", label: "fail", positiveTags: [], negativeTags: ["hallucination_risk"] },
    ],
  },
];

function normalizeTagArray(value) {
  if (!Array.isArray(value)) {
    return [];
  }
  const cleaned = [];
  value.forEach((item) => {
    const tag = String(item || "").trim().toLowerCase();
    if (tag && !cleaned.includes(tag)) {
      cleaned.push(tag);
    }
  });
  return cleaned;
}

export function coerceFeedbackEntry(entry) {
  if (!entry || typeof entry !== "object") {
    return null;
  }

  const normalized = { ...entry };
  let positiveTags = normalizeTagArray(entry.positive_tags);
  let negativeTags = normalizeTagArray(entry.negative_tags);
  const legacyTags = normalizeTagArray(entry.tags);
  const rawOutcome = String(entry.outcome || "").trim().toLowerCase();

  if (positiveTags.length === 0 && negativeTags.length === 0 && legacyTags.length > 0) {
    for (const tag of legacyTags) {
      if (FEEDBACK_POSITIVE_TAG_OPTIONS.includes(tag)) {
        positiveTags.push(tag);
      } else if (FEEDBACK_NEGATIVE_TAG_OPTIONS.includes(tag)) {
        negativeTags.push(tag);
      }
    }
    if (positiveTags.length === 0 && negativeTags.length === 0) {
      if (rawOutcome === "pass") {
        positiveTags = [...legacyTags];
      } else if (rawOutcome === "fail") {
        negativeTags = [...legacyTags];
      }
    }
  }

  normalized.positive_tags = [...new Set(positiveTags)];
  normalized.negative_tags = [...new Set(negativeTags)];
  normalized.tags = [...new Set([...normalized.positive_tags, ...normalized.negative_tags])];
  normalized.outcome = rawOutcome || normalized.outcome;
  return normalized;
}

export function inferRubricSelectionsFromFeedback(entry) {
  const normalized = coerceFeedbackEntry(entry) || {};
  const positive = new Set(normalized.positive_tags || []);
  const negative = new Set(normalized.negative_tags || []);

  const selection = {
    style: null,
    hallucination_risk: null,
  };

  if (negative.has("style_mismatch")) {
    selection.style = "fail";
  } else if (
    positive.has("style") ||
    positive.has("high_value") ||
    positive.has("medium_value") ||
    positive.has("low_value")
  ) {
    selection.style = "pass";
  }

  if (
    negative.has("hallucination_risk") ||
    negative.has("grounding_gap") ||
    negative.has("needs_retry") ||
    negative.has("ocr_miss")
  ) {
    selection.hallucination_risk = "fail";
  } else if (positive.has("grounded")) {
    selection.hallucination_risk = "pass";
  }
  return selection;
}

export function deriveTagsFromRubricSelections(selection) {
  const positive = new Set();
  const negative = new Set();
  FEEDBACK_RUBRIC_DIMENSIONS.forEach((dimension) => {
    const levelKey = selection?.[dimension.key];
    if (!levelKey) {
      return;
    }
    const level = dimension.levels.find((entry) => entry.key === levelKey);
    if (!level) {
      return;
    }
    level.positiveTags.forEach((tag) => positive.add(tag));
    level.negativeTags.forEach((tag) => negative.add(tag));
  });
  return {
    positiveTags: [...positive],
    negativeTags: [...negative],
  };
}

export function inferOptionalStyleNegativeTagsFromFeedback(entry) {
  const normalized = coerceFeedbackEntry(entry) || {};
  const negative = new Set(normalized.negative_tags || []);
  const selected = FEEDBACK_OPTIONAL_STYLE_NEGATIVE_TAGS.filter((option) =>
    negative.has(option.key),
  ).map((option) => option.key);
  return new Set(selected);
}

export function deriveOutcomeFromStreams(positiveTags, negativeTags) {
  const normalizedPositive = normalizeTagArray(positiveTags);
  const normalizedNegative = normalizeTagArray(negativeTags);
  const hardNegativeTags = normalizedNegative.filter((tag) => !FEEDBACK_PASS_SOFT_NEGATIVE_TAG_SET.has(tag));
  if (hardNegativeTags.length > 0) {
    return "fail";
  }
  return "pass";
}

export function normalizeFeedbackOutcome(feedback) {
  const normalized = coerceFeedbackEntry(feedback) || {};
  const rawOutcome = String(normalized?.outcome || "").toLowerCase();
  const positiveTags = Array.isArray(normalized?.positive_tags) ? normalized.positive_tags : [];
  const negativeTags = Array.isArray(normalized?.negative_tags) ? normalized.negative_tags : [];
  if (rawOutcome === "pass" || rawOutcome === "fail") {
    return rawOutcome;
  }
  if (rawOutcome === "mixed") {
    return deriveOutcomeFromStreams(positiveTags, negativeTags);
  }
  if (rawOutcome === "partial") {
    if (negativeTags.length > 0) {
      return "fail";
    }
    if (positiveTags.length > 0) {
      return "pass";
    }
    return "fail";
  }
  return deriveOutcomeFromStreams(positiveTags, negativeTags);
}

export function formatFeedbackStatusText(feedback) {
  const normalized = coerceFeedbackEntry(feedback);
  if (!normalized) {
    return "";
  }
  const parts = [];
  const positiveTags = Array.isArray(normalized.positive_tags) ? normalized.positive_tags : [];
  const negativeTags = Array.isArray(normalized.negative_tags) ? normalized.negative_tags : [];
  const passSoftNegativeTags = negativeTags.filter((tag) =>
    FEEDBACK_PASS_SOFT_NEGATIVE_TAG_SET.has(tag),
  );
  if (positiveTags.length > 0) {
    parts.push(`pass: ${positiveTags.join(", ")}`);
  }
  if (negativeTags.length > 0) {
    if (passSoftNegativeTags.length > 0 && negativeTags.length === passSoftNegativeTags.length) {
      parts.push(`penalty: ${passSoftNegativeTags.join(", ")}`);
    } else {
      parts.push(`fail: ${negativeTags.join(", ")}`);
    }
  }
  if (parts.length === 0 && Array.isArray(normalized.tags) && normalized.tags.length > 0) {
    parts.push(normalized.tags.join(", "));
  }
  if (parts.length === 0) {
    const rawOutcome = String(normalized.outcome || "").toLowerCase();
    if (rawOutcome) {
      parts.push(rawOutcome.toUpperCase());
    }
  }
  return parts.filter(Boolean).join(" • ");
}
