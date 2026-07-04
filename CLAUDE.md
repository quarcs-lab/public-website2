# CLAUDE.md

Operating notes for AI agents working in this repo. This is the QuaRCS-lab Network website:
a **Hugo** static site on a vendored **`timer-hugo`** theme, deployed by **Netlify** from
`master`. For full detail (structure, content schemas, design tokens) see **`README.md`** —
this file is just the rules and pointers, not a duplicate.

## Build / preview / deploy

- **Deploy = push to `master`.** Netlify runs `hugo --gc --minify` and publishes `public/`.
  There are no preview branches; a push to `master` is a production deploy.
- **Local build/preview:** Hugo is **not on `PATH`** — use blogdown's pinned binary:
  `"$HOME/Library/Application Support/Hugo/0.89.4/hugo" server -D` (or `... --gc --minify` to
  build). Must stay **0.89.4** to match Netlify. Verify changes with a build before committing.
- To screenshot/verify visually: build/serve, then drive headless Chrome
  (`/Applications/Google Chrome.app/...`); `puppeteer-core` can be installed in the scratchpad.

## Golden rules

1. **Never edit `themes/timer-hugo/**` to customize.** Shadow the file from the project root
   instead. Current overrides: `layouts/index.html` (homepage section order),
   `layouts/partials/{head,footer,banner,team,team-card,portfolio,research-areas}.html`,
   `layouts/people/list.html`, `layouts/research/list.html`, `layouts/portfolio/resources.html`,
   `assets/css/custom.css`, `assets/js/custom.js`. (Theme copies still exist but are ignored —
   edit the root ones. `research-areas.html` is new — no theme copy exists.)
2. **Load order is load-bearing:** `custom.css` loads after theme `style.css` (in `head.html`)
   and `custom.js` after `script.js` (in `footer.html`). Keep it that way or overrides lose.
3. **Do not remove `wow.min.js`** from `footer.html` — theme `script.js` calls
   `new WOW().init()`; without it, animated content stays hidden (and `new WOW` throws if the
   lib is gone, breaking slick/fancybox/smooth-scroll too).
4. **Design changes go in `assets/css/custom.css`.** The palette lives in `:root` custom props
   (`--ink`, `--navy`, `--cyan`, `--cyan-ink`, `--amber`, …); fonts are Space Grotesk + Inter.
   Bright `--cyan`/`--amber` are for dark backgrounds; use `--cyan-ink`/`--muted` on white (AA).
5. **Publication type filter:** set `pubtype: book|working|article` in a research post's
   front-matter when the tag heuristic would misclassify it (heuristic: a tag containing "Book"
   or "Working paper"; else "article").
6. **`public/` and `resources/` are gitignored** build artifacts — never commit them.
7. **Keep the Themefisher footer credit** (theme-license requirement).
8. **Concurrent editors:** this repo is edited from multiple sessions/people. `git fetch`
   first, keep commits tightly scoped to your files, and fetch-then-push (rebase if behind).
   Don't clobber unrelated in-flight changes.

## Where things live (quick map)

| To change… | Edit… |
|---|---|
| Hero keywords / heading, nav menu, About/CTA text, logo path | `config.toml` |
| Publications | `content/research/*.md` (+ image in `static/images/blog/`) |
| People roster | `data/team.yml` (+ photo in `static/images/team/`) |
| Tutorials/datasets/projects hub | `data/resources.yml` |
| "Research methods" section | `data/feature.yml` |
| Homepage "Activities" cards | `content/portfolio/*.md` |
| Styles / palette / motion | `assets/css/custom.css`, `assets/js/custom.js` |
| Logo / favicons | `static/images/` (SVG set) + `layouts/partials/head.html` |

## Pointers

- **Content recipes** (add a publication / team member / resource, change hero): see
  `README.md` → *Editing content*.
- **Architecture & override table:** `README.md` → *Architecture*.
- **Palette tokens & motion:** `README.md` → *Design system*.
- **Latent/placeholder areas to ignore:** `content/{contact,gallery,service}/` and
  `data/{contact,gallery,service}.yml`, and the blank `data/about.yml` (see `README.md` →
  *Conventions & gotchas*).

## Commit conventions

Short, imperative, type-prefixed subjects matching the existing history — e.g.
`feat: …`, `fix: …`, `style: …`, `content: …`, `docs: …`.
