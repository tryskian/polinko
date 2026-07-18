import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const siteDir = path.join(root, "site");
const routeFiles = [
  "index.html",
  "research/index.html",
  "method/index.html",
  "evidence/index.html",
  "diagrams/index.html",
  "about/index.html",
];
const requiredFiles = [...routeFiles, "styles.css", "script.js", "favicon.svg"];
const issues = [];

for (const file of requiredFiles) {
  if (!existsSync(path.join(siteDir, file))) {
    issues.push(`site/${file} is missing`);
  }
}

if (issues.length === 0) {
  const pages = new Map(
    routeFiles.map((file) => [
      file,
      readFileSync(path.join(siteDir, file), "utf8"),
    ]),
  );
  const css = readFileSync(path.join(siteDir, "styles.css"), "utf8");
  const js = readFileSync(path.join(siteDir, "script.js"), "utf8");
  const combined = [...pages.values(), css, js].join("\n");

  for (const [file, html] of pages) {
    for (const token of [
      '<html lang="en"',
      "<main",
      "<title>",
      'name="description"',
      'name="viewport"',
      'aria-label="Site navigation"',
      'aria-label="Primary navigation"',
      'aria-label="Switch to dark theme"',
      'href="/research/"',
      'href="/method/"',
      'href="/evidence/"',
      'href="/diagrams/"',
      'href="/about/"',
    ]) {
      if (!html.includes(token)) {
        issues.push(`site/${file} is missing ${token}`);
      }
    }

    const themeBootstrap = 'localStorage.getItem("krystian-io-theme")';
    const themeIndex = html.indexOf(themeBootstrap);
    const stylesheetIndex = html.indexOf('<link rel="stylesheet" href="/styles.css" />');

    if (themeIndex === -1) {
      issues.push(`site/${file} is missing early theme bootstrap`);
    }

    if (stylesheetIndex === -1 || themeIndex > stylesheetIndex) {
      issues.push(`site/${file} must set saved theme before stylesheet loads`);
    }

    const h1Count = (html.match(/<h1\b/g) ?? []).length;

    if (h1Count !== 1) {
      issues.push(`site/${file} must have exactly one h1, found ${h1Count}`);
    }

    const labelledSections = [
      ...html.matchAll(/<(?:section|article)\b[^>]*aria-labelledby="([^"]+)"/g),
    ];

    if (labelledSections.length < 2) {
      issues.push(`site/${file} needs at least two labelled content regions`);
    }

    for (const [, id] of labelledSections) {
      if (!html.includes(`id="${id}"`)) {
        issues.push(`site/${file} references missing label id ${id}`);
      }
    }

    for (const image of html.matchAll(/<img\b[^>]*>/g)) {
      if (!/\salt=/.test(image[0])) {
        issues.push(`site/${file} has an image without alt text`);
      }
    }

    for (const buttonTag of html.matchAll(/<button\b[^>]*>/g)) {
      const source = buttonTag[0];

      if (!/\saria-label=/.test(source) && !/\stitle=/.test(source)) {
        issues.push(`site/${file} has a button without an accessible label`);
      }
    }
  }

  const home = pages.get("index.html");

  for (const token of [
    "Polinko evaluates AI behaviour through binary gates, evidence, and retained failures",
    "I created Polinko and lead its research",
    "Krystian Fernando",
    "coherent output",
    "being mistaken for reliable behaviour",
  ]) {
    if (!home.includes(token)) {
      issues.push(`site/index.html is missing grounded homepage copy: ${token}`);
    }
  }

  if (!css.includes("https://use.typekit.net/rhw6amk.css")) {
    issues.push("site/styles.css is missing the Typekit import");
  }

  if (!css.includes("prefers-reduced-motion")) {
    issues.push("site/styles.css is missing reduced-motion handling");
  }

  if (!js.includes("localStorage")) {
    issues.push("site/script.js is missing persisted theme handling");
  }

  for (const retiredClaim of [
    "15-minute PASS/FAIL",
    "15-minute pulses",
    "unnecessary computational work",
    "Review the grant path",
  ]) {
    if (combined.includes(retiredClaim)) {
      issues.push(`site files include retired claim: ${retiredClaim}`);
    }
  }

  if (combined.includes("—")) {
    issues.push("site files include an em dash");
  }
}

if (issues.length > 0) {
  console.error(
    `Site contract check failed:\n${issues.map((issue) => `- ${issue}`).join("\n")}`,
  );
  process.exit(1);
}

console.log(`Site contract check passed for ${routeFiles.length} route(s).`);
