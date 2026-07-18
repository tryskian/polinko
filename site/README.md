# krystian.io website source

This directory contains the static website published at
[krystian.io](https://www.krystian.io/).

The site presents Polinko as Krystian Fernando's human-led AI evaluation
research system. The broader repository remains the research surface; this
directory is the public website layer.

## Build

Netlify builds the site with:

```bash
npm run build
```

The build copies `site/` into `dist/`.

## Check

Run the site contract check before publishing website changes:

```bash
npm run site:check
```
