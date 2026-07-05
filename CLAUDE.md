# CLAUDE.md

Operating notes for AI agents working in this repo. This is the QuaRCS-lab Network website:
a **Hugo** static site on a vendored **`timer-hugo`** theme, deployed by **Netlify** from
`master`. For full detail (structure, content schemas, design tokens) see **`README.md`** —
this file is just the rules and pointers, not a duplicate. Before adding a person, publication,
resource, event, or research area, consult **`README.md` → The coupling map** (change X → also
update Y) and run `python3 scripts/check-content.py` before committing.

## Build / preview / deploy

- **Deploy = push to `master`.** Netlify runs `hugo --gc --minify` and publishes `public/`.
  There are no preview branches; a push to `master` is a production deploy.
- **Local build/preview:** Hugo is **not on `PATH`** — use blogdown's pinned binary:
  `"$HOME/Library/Application Support/Hugo/0.89.4/hugo" server -D` (or `... --gc --minify` to
  build). Must stay **0.89.4** to match Netlify. Verify changes with a build before committing.
- To screenshot/verify visually: build/serve, then drive headless Chrome
  (`/Applications/Google Chrome.app/...`); `puppeteer-core` can be installed in the scratchpad.
- **Validate before committing:** `python3 scripts/check-content.py` (pure stdlib, no npm) — exit 1
  on any coupling error. Scaffold new content with `hugo new research/<slug>.md` (archetypes).

## Golden rules

1. **Never edit `themes/timer-hugo/**` to customize.** Shadow the file from the project root
   instead — see **`README.md` → Architecture** for the complete override table. The full set:
   `layouts/{404,index}.html`; `layouts/partials/{head,footer,banner,mission,research-areas,feature,
   portfolio,team,team-card,cta,authors-linkify,author-keys}.html`; `layouts/people/list.html`;
   `layouts/research/list.html`; `layouts/post/single.html`;
   `layouts/portfolio/{explainer,projects,publications,resources,single}.html`; `assets/css/custom.css`;
   `assets/js/custom.js`. Files with **no theme copy** (new): `mission`, `research-areas`,
   `team-card`, `authors-linkify`, `author-keys`, and the `explainer`/`projects`/`publications`/`resources`
   `portfolio/*` layouts (`cta.html` and `portfolio/single.html` are new *overrides* of theme files). `feature.html`/`research-areas.html` render the shared,
   count-agnostic `.info-grid`/`.info-card` system; `mission.html` is the `#mission` band.
2. **Load order is load-bearing:** `custom.css` loads after theme `style.css` (in `head.html`)
   and `custom.js` after `script.js` (in `footer.html`). Keep it that way or overrides lose.
3. **Do not remove `wow.min.js`** from `footer.html` — theme `script.js` calls
   `new WOW().init()`; without it, animated content stays hidden (and `new WOW` throws if the
   lib is gone, breaking slick/fancybox/smooth-scroll too).
4. **Design changes go in `assets/css/custom.css`.** The palette lives in `:root` custom props
   (`--ink`, `--navy`, `--cyan`, `--cyan-ink`, `--amber`, …); fonts are Space Grotesk + Inter.
   Bright `--cyan`/`--amber` are for dark backgrounds; use `--cyan-ink`/`--muted` on white (AA).
5. **Publication type is decided ONLY by `pubtype`** (`article` by default). Set
   `pubtype: book|working` on a non-article or it is mislabeled "Article". `tags[0]` only refines
   the label (`Book chapter`) and supplies the journal name / cover key — there is **no** tag-based
   type heuristic in the code (older docs claiming one were wrong).
6. **`public/` and `resources/` are gitignored** build artifacts — never commit them.
7. **Keep the Themefisher footer credit** (theme-license requirement).
8. **Concurrent editors:** this repo is edited from multiple sessions/people. `git fetch`
   first, keep commits tightly scoped to your files, and fetch-then-push (rebase if behind).
   Don't clobber unrelated in-flight changes.
9. **Keep coupled content in sync** — see `README.md → The coupling map`; run
   `scripts/check-content.py` before committing. Notably: a new team member needs `key`+`aliases`
   (else their publications won't link); a book needs `pubtype`; an article's `tags[0]` needs a
   `journal_covers.yml` entry + image; hero keywords come from `research-projects.yml`; the
   Discord/GitHub/Luma URLs live once in `[params.links]`.

## Where things live (quick map)

| To change… | Edit… |
|---|---|
| Nav menu, About/CTA text, shared links (`[params.links]`), logo | `config.toml` |
| Hero rotating keywords **and** Research Areas | `data/research-projects.yml` (single source for both) |
| Publications | `content/research/*.md` (`hugo new research/<slug>.md`) + cover in `static/images/journals/` |
| People roster + publication↔author links | `data/team.yml` (`key`+`aliases`; photo in `assets/images/team/`, Hugo-processed) |
| Journal cover thumbnails | `data/journal_covers.yml` + `static/images/journals/` |
| Resources hub | `data/resources.yml` (type/topic must match the vocab lists) |
| "Research methods and data" section | `data/feature.yml` |
| Events / Community / GitHub pages | `data/{events,community,github}.yml` (page = `layout: explainer` + `dataKey`) |
| Homepage "Activities" cards | `content/portfolio/*.md` (`hugo new portfolio/<slug>.md`) |
| Styles / palette / motion | `assets/css/custom.css`, `assets/js/custom.js` |
| Logo / favicons | `static/images/` (SVG set) + `layouts/partials/head.html` |
| Validate before committing | `python3 scripts/check-content.py` |

## Pointers

- **Coupling map (change X → also update Y):** `README.md` → *The coupling map* — consult before
  adding a person, publication, resource, event, or research area; then run `scripts/check-content.py`.
- **Content recipes** (add a publication / team member / resource / webinar / research area, change
  hero): see `README.md` → *Editing content*.
- **Architecture & override table:** `README.md` → *Architecture*.
- **Palette tokens & motion:** `README.md` → *Design system*.
- **Latent/placeholder areas to ignore:** `content/{contact,gallery,service}/` and
  `data/{contact,gallery,service}.yml`, and the blank `data/about.yml` (see `README.md` →
  *Conventions & gotchas*).

## Commit conventions

Short, imperative, type-prefixed subjects matching the existing history — e.g.
`feat: …`, `fix: …`, `style: …`, `content: …`, `docs: …`.
