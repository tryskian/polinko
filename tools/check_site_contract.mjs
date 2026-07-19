import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const siteDir = path.join(root, "site");
const contentRouteFiles = [
  "index.html",
  "research/index.html",
  "method/index.html",
  "evidence/index.html",
  "diagrams/index.html",
];
const redirectRouteFiles = [
  "about/index.html",
];
const routeFiles = [...contentRouteFiles, ...redirectRouteFiles];
const requiredFiles = [
  ...routeFiles,
  "README.md",
  "styles.css",
  "script.js",
  "favicon.svg",
  "_redirects",
];
const issues = [];

for (const file of requiredFiles) {
  if (!existsSync(path.join(siteDir, file))) {
    issues.push(`site/${file} is missing`);
  }
}

if (issues.length === 0) {
  const contentPages = new Map(
    contentRouteFiles.map((file) => [
      file,
      readFileSync(path.join(siteDir, file), "utf8"),
    ]),
  );
  const redirectPages = new Map(
    redirectRouteFiles.map((file) => [
      file,
      readFileSync(path.join(siteDir, file), "utf8"),
    ]),
  );
  const css = readFileSync(path.join(siteDir, "styles.css"), "utf8");
  const js = readFileSync(path.join(siteDir, "script.js"), "utf8");
  const redirects = readFileSync(path.join(siteDir, "_redirects"), "utf8");
  const combined = [
    ...contentPages.values(),
    ...redirectPages.values(),
    css,
    js,
    redirects,
  ].join("\n");

  for (const [file, html] of contentPages) {
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
      'href="https://github.com/tryskian/polinko/blob/main/site/README.md"',
    ]) {
      if (!html.includes(token)) {
        issues.push(`site/${file} is missing ${token}`);
      }
    }

    if (html.includes('href="/about/"')) {
      issues.push(`site/${file} links to duplicate about route`);
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

  for (const [file, html] of redirectPages) {
    for (const token of [
      '<html lang="en"',
      'name="robots" content="noindex, follow"',
      'http-equiv="refresh" content="0; url=/"',
      '<link rel="canonical" href="https://www.krystian.io/"',
      'href="/"',
    ]) {
      if (!html.includes(token)) {
        issues.push(`site/${file} is missing redirect token ${token}`);
      }
    }
  }

  const home = contentPages.get("index.html");

  for (const token of [
    "About me",
    "I'm Krystian Fernando, an applied AI research engineer",
    "Polinko makes AI reliability observable",
    "I lead Polinko's research, engineering direction, and final claims",
    "AI systems are collaborators, instruments, and part of what Polinko evaluates",
    "Read the research",
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

  if (!redirects.includes("/about/ / 301!")) {
    issues.push("site/_redirects must force /about/ to /");
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

console.log(
  `Site contract check passed for ${contentRouteFiles.length} content route(s) and ${redirectRouteFiles.length} redirect route(s).`,
);
