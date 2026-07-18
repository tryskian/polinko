# krystian.io website source

This directory contains the static website published at
[krystian.io](https://www.krystian.io/).

The site presents Polinko as Krystian Fernando's human-led AI evaluation
research system. The broader repository remains the research surface; this
directory is the public website layer.

## Route contract

The public reader path is:

```text
/ -> /research/ -> /evidence/ -> /method/
```

Supporting routes:

- `/` owns Krystian, authorship, collaboration, and why Polinko exists.
- `/diagrams/` owns visual support tied back to the public pages.
- `/about/` redirects to `/` for compatibility with older links.

The homepage should introduce Krystian first, then Polinko. Detailed research
lanes belong on `/research/`, result counts and source notes belong on
`/evidence/`, and method mechanics belong on `/method/`.

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
