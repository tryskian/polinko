<!-- @format -->

# Portfolio App

This directory contains the source app for Polinko's public `/portfolio`
surface.

The website is the doorway. The repository and docs remain the canonical
research surface.

## Start Here

If you landed in this folder first, these are the better entrypoints:

- [Root README](../../README.md)
- [Public Reading Path](../../docs/public/README.md)
- [Research Surface](../../docs/research/README.md)

## What Lives Here

- `src/main.js`: the staged portfolio experience, gesture flow, and Sankey data
  wiring
- `src/styles.css`: layout, typography, and motion
- `src/*.svg`: fixed visual assets used by the portfolio surface
- `index.html`, `vite.config.js`, `package.json`: the Vite app shell and build
  contract

## Build Contract

- source lives in `apps/portfolio/`
- tracked static output lives in `public/portfolio/`
- `npm run build` writes to `public/portfolio/` by default
- `tools/build_portfolio_static.py` rebuilds the app and copies the tracked
  output into `output/netlify/` for publish

## Local Commands

From the repo root:

```bash
npm --prefix apps/portfolio ci
npm --prefix apps/portfolio run dev
npm --prefix apps/portfolio run build
python tools/build_portfolio_static.py
```
