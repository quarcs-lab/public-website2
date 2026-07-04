# QuaRCS-lab Network — website

Source for the **QuaRCS-lab Network** website: **<https://quarcs.netlify.app>**

QuaRCS (Quantitative Regional and Computational Science) is an international, interdisciplinary
research network that promotes science and innovation for economic, social, and environmental
sustainability, integrating development economics, spatial data science, machine learning, and
satellite remote sensing to understand and inform sustainable development across subnational
regions and countries. The network is part of the UN Sustainable Development Solutions Network
(SDSN). This repository holds the site's content, configuration, and a customized
[Hugo](https://gohugo.io/) theme.

> **Maintaining the site?** Jump to [Editing content](#editing-content). Most updates are just
> adding a publication, a team member, or a resource — but first skim
> [The coupling map](#the-coupling-map): it lists the few places where changing one thing means
> you must change another. Then run `python3 scripts/check-content.py` and push to `master`.

---

## Table of contents

- [Tech stack](#tech-stack)
- [How it builds & deploys](#how-it-builds--deploys)
- [Repository structure](#repository-structure)
- [Architecture](#architecture)
- [The coupling map](#the-coupling-map) — **start here when editing** (change X → also update Y)
- [Editing content](#editing-content) — publications, people, events, community, resources, research areas, hero
- [Content validation](#content-validation) — `scripts/check-content.py`
- [Design system](#design-system)
- [Conventions & gotchas](#conventions--gotchas)
- [Credits & license](#credits--license)

---

## Tech stack

| Piece | What it is |
|---|---|
| **Hugo** | Static-site generator that builds the site. Pinned to **0.89.4**. |
| **`timer-hugo` theme** | A [Themefisher](https://themefisher.com/) theme, vendored under `themes/timer-hugo/` and customized via project-root overrides (see [Architecture](#architecture)). |
| **R `blogdown`** *(optional)* | Convenience layer for authoring/previewing from RStudio (`index.Rmd`, `tryWEB3.Rproj`). Not used by the deploy. |
| **Netlify** | Hosting + CI. Builds from `master` and serves `quarcs.netlify.app`. |
| **`scripts/check-content.py`** | A pure-Python (stdlib only) pre-commit checker for the coupling points. **No Node/npm.** |
| **`archetypes/`** | `hugo new research/<slug>.md` / `hugo new portfolio/<slug>.md` scaffold full front matter. |

No Node/npm build step — the theme's JS/CSS are pre-vendored, Hugo Pipes handles the project's
CSS/JS, and the checker uses only the Python standard library.

## How it builds & deploys

**The normal workflow is edit → check → commit → push.** Netlify does the rest.

```
edit content/config  →  python3 scripts/check-content.py  →  git commit  →  git push origin master  →  Netlify builds & deploys
```

Netlify config (`netlify.toml`):

```toml
[build]
command = "hugo --gc --minify"
publish = "public"
[build.environment]
HUGO_VERSION = "0.89.4"
```

Pushing to **`master`** triggers a production deploy. There are no preview branches configured,
so run the checker and (for risky changes) a local build before pushing.

### Optional local preview

You don't need this to make content changes, but to preview locally:

- **Hugo CLI:** `hugo server -D` from the repo root, then open the printed `localhost` URL.
- **RStudio + blogdown:** open `tryWEB3.Rproj` and run `blogdown::serve_site()`.

> ⚠️ `blogdown` installs its **own** Hugo binary that is **not on your `PATH`** — it lives at
> `~/Library/Application Support/Hugo/0.89.4/hugo`. A bare `hugo` command may be missing or a
> different version. Use `blogdown::serve_site()`, or invoke that absolute path, and keep it at
> **0.89.4** to match Netlify. A one-off production-style build: `hugo --gc --minify`.

## Repository structure

```
.
├── config.toml            # Site config: baseURL, menus, homepage params, [params.links] (edit a lot)
├── netlify.toml           # Netlify build command + pinned Hugo version
├── index.Rmd / tryWEB3.Rproj   # blogdown / RStudio (local authoring only)
│
├── archetypes/            # `hugo new` scaffolds
│   ├── research.md        #   → content/research/<slug>.md front matter
│   └── portfolio.md       #   → content/portfolio/<slug>.md front matter
│
├── scripts/
│   ├── check-content.py   # Pre-commit content-consistency checker (no npm)
│   └── git-hooks/pre-commit   # Optional hook (git config core.hooksPath scripts/git-hooks)
│
├── content/               # Markdown content, one folder per section
│   ├── research/          #   80 publication .md files + _index.md  → /research/
│   ├── portfolio/         #   7 pages: all-publications, research-projects, data-tutorials,
│   │                      #     webinars, learning-community, github, book-mendez2020 (hidden)
│   ├── people/_index.md   #   People page at /people/; roster from data/team.yml
│   └── contact|gallery|service/_index.md   # latent (not in the menu — ignore)
│
├── data/                  # YAML that feeds templates (see "Editing content")
│   ├── team.yml           #   People roster (name, key, aliases, …)        (active)
│   ├── resources.yml      #   Resources hub (types/topics vocab + items)   (active)
│   ├── feature.yml        #   Homepage "Research methods" cards            (active)
│   ├── research-projects.yml #  Research Areas + /research-projects/ + hero keywords (active)
│   ├── events.yml         #   Events page  (via layout: explainer + dataKey: events)     (active)
│   ├── community.yml      #   Community page (dataKey: community)          (active)
│   ├── github.yml         #   GitHub page    (dataKey: github)             (active)
│   ├── journal_covers.yml #   journal name (tags[0]) → cover image         (active)
│   └── about|service|gallery|contact|client.yml   # blank / latent / ignore
│
├── layouts/               # PROJECT-ROOT template overrides (win over the theme) — see table below
├── assets/                # Processed by Hugo Pipes (loaded AFTER the theme's)
│   ├── css/custom.css     #   the design system
│   └── js/custom.js        #   hero parallax
│
├── static/                # Copied verbatim to the site root
│   └── images/            #   logos, favicons, hero, team/, blog/ (pub covers), portfolio/, journals/
│
├── themes/timer-hugo/     # Vendored theme — DO NOT edit for customization (override instead)
├── public/                # Hugo build output  — GITIGNORED (Netlify regenerates)
└── resources/             # Hugo Pipes cache   — GITIGNORED
```

## Architecture

### The theme-override pattern (read this first)

The theme is vendored in `themes/timer-hugo/` and is **never edited for customization**.
Instead, a file placed at the **project root** with the same path *shadows* the theme's copy
(Hugo's template/asset lookup prefers the project root). The complete set of overrides:

| Project-root override | New / replaces | Purpose | Data source |
|---|---|---|---|
| `layouts/404.html` | replaces empty theme 404 | Branded 404 page | — |
| `layouts/index.html` | replaces theme `index.html` | Homepage partial order | its partials |
| `layouts/partials/head.html` | theme `head.html` | Favicons, Google Fonts, **SEO/Open Graph/Twitter/canonical + JSON-LD**; loads `style.css` **then `custom.css` last** | `params` |
| `layouts/partials/footer.html` | theme `footer.html` | Footer + Themefisher credit; JS order (wow → `script.js` → **`custom.js` last**) | `params.links` |
| `layouts/partials/banner.html` | theme `banner.html` | Cinematic hero; rotating keywords **derived from `research-projects.yml`** | `params.banner` + `research-projects.yml` |
| `layouts/partials/mission.html` | **new** | Homepage mission band (`#mission`) | hardcoded copy |
| `layouts/partials/research-areas.html` | **new** | Homepage "Research Areas" info-grid | `research-projects.yml` |
| `layouts/partials/feature.html` | theme `feature.html` | Homepage "Research methods" info-grid | `feature.yml` |
| `layouts/partials/portfolio.html` | theme `portfolio.html` | Homepage "Activities" cards | `content/portfolio/*` |
| `layouts/partials/team.html` | theme `team.html` | Splits roster into Directors/Associates | `team.yml` |
| `layouts/partials/team-card.html` | **new** | Member card: country pill + **"Publications (N)"** link | a `team.yml` member |
| `layouts/partials/cta.html` | theme `cta.html` | Homepage CTA; button URL from `params.links.discord` | `params.cta` + `params.links` |
| `layouts/partials/authors-linkify.html` | **new** | Wraps team-member author names in links to `/people/#<key>` | `team.yml` |
| `layouts/partials/author-keys.html` | **new** | Emits `data-authors` keys for the `/research` author filter | `team.yml` |
| `layouts/people/list.html` | **new** (`people` section) | People page: header + team grid + CTA | `team.yml` |
| `layouts/research/list.html` | theme `_default/list.html` | Publications list: filters, year chart, journal covers, author links | `content/research/*` + `journal_covers.yml` |
| `layouts/post/single.html` | theme `post/single.html` | Single publication page (type beats section in lookup) | research post front matter |
| `layouts/portfolio/explainer.html` | **new** (`layout: explainer`) | Data-driven Events/Community/GitHub pages via `dataKey` | `data/<dataKey>.yml` |
| `layouts/portfolio/projects.html` | **new** (`layout: projects`) | `/portfolio/research-projects/` | `research-projects.yml` |
| `layouts/portfolio/publications.html` | **new** (`layout: publications`) | `/portfolio/all-publications/` | `content/research/*` + `research-projects.yml` |
| `layouts/portfolio/resources.html` | **new** (`layout: resources`) | Resources hub with filters | `resources.yml` |
| `layouts/portfolio/single.html` | theme `portfolio/single.html` | Portfolio single (only `book-mendez2020`); `<h1>` title, descriptive alt | portfolio front matter |
| `assets/css/custom.css` | overrides theme `style.css` | The design system (see [Design system](#design-system)) | — |
| `assets/js/custom.js` | **new** | Hero scroll parallax | — |

Everything else comes straight from the theme — the navbar `header.html`, the `about.html` and
`page-title.html` partials, `baseof.html`, and all `static/plugins/*`. **The load order matters:**
`custom.css` must load after `style.css`, and `custom.js` after `script.js`, or the overrides lose.

### Homepage composition

`layouts/index.html` stacks **seven** partials, each driven by config or data:

1. **banner** ← `[params.banner]` (+ rotating keywords derived from `data/research-projects.yml`)
2. **mission** ← hardcoded copy in `mission.html` (`#mission`)
3. **about** ← `[params.about]` (title, HTML `content`, `image`) — *theme partial*
4. **research-areas** ← `data/research-projects.yml`
5. **feature** ("Research methods") ← `data/feature.yml`
6. **portfolio** ("Activities") ← `content/portfolio/*.md` (`type: portfolio`, minus any `_build: {list: never}`)
7. **cta** ← `[params.cta]` + `params.links.discord`

---

## The coupling map

The site has a handful of **coupling points** — places where changing one thing means you must
also change another. Most are enforced by [`scripts/check-content.py`](#content-validation); run
it before every commit. **When you change / add X, also update Y:**

| # | When you change / add… | …also update | Why / failure mode | Checked? |
|---|---|---|---|---|
| 1 | A research article's **`tags[0]`** (journal name) | a matching key in `data/journal_covers.yml` **and** the image at `static/images/journals/<file>` | No match → text-fallback card, and a new/misspelled name adds a stray option to the `/research` journal filter | ✅ |
| 2 | A research **`topics:`** value | reuse an existing spelling (there is no central vocab) | A typo makes an orphan one-item option in the topic filter | ✅ (singleton warn) |
| 3 | Add a **book / working paper / chapter** | set **`pubtype: book`** or **`working`** in front matter | Type is read **only** from `pubtype` (default `article`); without it a book is mislabeled "Article". (`tags[0] == "Book chapter"` only refines the *label*.) | ✅ |
| 4 | A publication **`author`**, or **add a team member** | the member's **`key` + `aliases`** in `data/team.yml` | Build-time alias matching links author names → `/people/#<key>` and powers the card's "Publications (N)". A new member with no aliases gets **zero** linked publications | ✅ |
| 5 | A `data/resources.yml` item's **`type` / `topic`** | the `types:` / `topics:` vocab lists at the top of the file | A value not in the vocab makes the item render in **no** section (invisible) | ✅ |
| 6 | A `content/portfolio/*.md` **`layout:`** or **`dataKey:`** | the `layouts/portfolio/<layout>.html` template / the `data/<key>.yml` file must exist | Missing layout → wrong render; missing data file → **blank page** | ✅ |
| 7 | Any **`type: portfolio`** page | decide if it should be a homepage Activity card; if not, add **`_build: {list: never}`** | Every portfolio page auto-appears as an Activities card (see `book-mendez2020.md`) | — |
| 8 | A **`[[menu.main]]`** `url` in `config.toml` | the target content slug/section must exist | Broken nav link (404) | ✅ |
| 9 | The **hero rotating keywords** | edit the item titles in **`data/research-projects.yml`** (single source) — **not** `config.toml` | The banner *derives* its keywords from that data file; editing config has no effect | — |
| 10 | A **Discord / GitHub / Luma** URL | the **`[params.links]`** block in `config.toml` (single source) | Templates (`cta.html`, `explainer.html`) and `footer.html` read from there; the checker asserts `links.discord` is set | ✅ |
| 11 | A team member's **`designation`** | keep the format `"Sentence one. Role, Institution, COUNTRY."` | The **first sentence** must contain "director" for the Directors group; the **trailing ALL-CAPS token** becomes the country pill | ✅ |
| 12 | A **book cover image** | update **both** copies if the book has one in `static/images/blog/` *and* `static/images/portfolio/` | Cover looks updated on one surface, stale on the other | ✅ (existence) |
| 13 | A `data/research-projects.yml` item | know it drives **four** surfaces: homepage Research Areas, `/portfolio/research-projects/`, the programs list on `/portfolio/all-publications/`, and the hero keywords | One edit ripples to four places. The card grid is count-agnostic, so add/remove freely | — |
| 14 | Any **image path** in front matter / data / config | the file must exist under `static/…` (team, blog, portfolio, journals, logo, hero, about) | Broken image | ✅ |

---

## Editing content

Most maintenance is here. After any edit: **run `python3 scripts/check-content.py`, then commit
and push to `master`.**

### Add a publication

1. Scaffold: `hugo new research/<slug>.md` (uses `archetypes/research.md`, which pre-fills every
   field with inline notes). Then fill it in:

   ```yaml
   ---
   title: "Okun's law and spatial regimes in Indonesia: A machine learning approach"
   author: Tifani Husna Siregar, Harry Aginta and Carlos Mendez   # names matching a team alias auto-link
   date: "2026-05-28"           # quoted YYYY-MM-DD — drives the year grouping
   type: post                   # required
   tags: ["Economic Modelling"] # articles: tags[0] = EXACT journal name (see step 3)
   topics: ["Spatial econometrics", "Machine learning & data science"]   # reuse existing spellings
   links: [{"label":"Read paper","url":"https://doi.org/10.xxxx/xxxxx"}]
   image: "images/blog/<slug>.webp"   # optional; used for non-articles / when no journal cover
   # pubtype: "book"            # ONLY for a book / working paper / chapter (omit for an article)
   ---
   One-paragraph abstract (this first paragraph becomes the list summary).
   ```

2. Drop the thumbnail at `static/images/blog/<slug>.webp` (or `.jpg/.png`) if you set `image`.
3. **Journal cover (articles):** `tags[0]` must **exactly** match a key in
   `data/journal_covers.yml`, whose file must exist under `static/images/journals/`. A new journal
   → add both the key and the image, or the card falls back to styled text **and** the journal name
   shows up as a stray option in the `/research` journal filter. (Some venues have no cover by
   design — see the list in `journal_covers.yml`.)
4. **Books / working papers / chapters:** set `pubtype: book` (or `working`). The label refines to
   "Chapter" when `tags[0] == "Book chapter"`. See `content/research/mendez2020-book-convergence-clubs.md`.
5. Run `python3 scripts/check-content.py`, fix anything it flags, then push. The publication
   appears on **/research** automatically, grouped by year and searchable.

### Add or deactivate a team member

Edit `data/team.yml` under `members:` (note the `key : value` spacing style):

```yaml
  - name  : Carlos Mendez
    key         : carlos-mendez                 # stable slug — the /people anchor + publication-link id
    aliases     : ["Carlos Mendez"]             # names as they appear in publication `author:` fields
    image       : images/team/carlos-mendez.jpg
    designation : Founding research director. Associate professor, Nagoya University, JAPAN.
    description : "Research interests: Development Macroeconomics, Regional Economics, Spatial econometrics"
    net         : https://www.researchgate.net/profile/Carlos_Mendez54   # kept for reference (NOT shown)
    linkedIn    : https://www.linkedin.com/in/mendezguerra                # kept for reference (NOT shown)
    web         : https://carlos-mendez.org                               # the ONLY link that renders
```

- **`key` + `aliases` are what link a person to their publications.** At build time each
  publication's `author` string is matched against every member's `aliases`; matches turn the name
  into a link to that member's `/people/#<key>` anchor and add a **"Publications (N)"** button to
  the card. List aliases **longest-first** and include every spelling a paper uses (e.g. Felipe:
  `["Felipe Santos-Marquez", "Felipe Santos"]`). **A new member with no aliases gets zero linked
  publications**, so always fill this in.
- **`designation` is load-bearing** (coupling #11): the first sentence must contain "director" to
  land in the **Directors** group (else **Associates**); the trailing ALL-CAPS token (e.g. `JAPAN`)
  becomes the country pill. Keep the `Sentence one. Role, Institution, COUNTRY.` shape.
- Only **`web`** renders (a "Website" button); `net`/`linkedIn` are kept for reference but not shown.
- **Add:** append a block; drop the photo in `assets/images/team/` (any size/format — Hugo crops it
  to a normalized 150/300 WebP circle via the pipeline in `team-card.html`; `image:` stays
  `images/team/<file>`). **Deactivate:** comment the block out with leading `#` (don't delete).
  Members render in file order. Run the checker afterwards.

### Add an Activity card, or a resource

- **Homepage "Activities" card:** `hugo new portfolio/<slug>.md`, then set `type: portfolio`,
  `image: images/portfolio/<file>.jpg`, and a `caption`. Any `type: portfolio` page **auto-appears**
  as an Activities card (sorted by `date`, newest first) unless you add `_build: {list: never}`.
- **Resource** (the **Resources** menu → `/portfolio/data-tutorials`, driven by `data/resources.yml`):
  append one entry to `items:` — no new file needed:

  ```yaml
    - title  : "Provincial income & convergence clubs in Indonesia 2001–2017"
      type   : Dataset                  # MUST be one of `types:` at the top of the file
      topic  : Regional convergence     # MUST be one of `topics:`
      url    : "https://rpubs.com/quarcs-lab/..."
      author : "Gunawan & Mendez (2020)"   # optional
      lang   : R                            # optional badge
      desc   : "Short description."          # optional
  ```

  A `type`/`topic` outside the vocab lists makes the item **invisible** (coupling #5). To add a new
  category, extend `types:` or `topics:` at the top of the file.

### Add a webinar / event

The **Events** page (`/portfolio/webinars/`) is data-driven: `content/portfolio/webinars.md` sets
`layout: explainer` + `dataKey: events`, so all copy lives in **`data/events.yml`**. Edit that file:

- `sections:` → `items:` — the "What to expect" cards (`icon` = an Ionicons class, `title`,
  `description`).
- `steps:` — the numbered "How to join" list.
- `cta:` — the call-to-action. Use **`linkKey: luma`** (resolved to `params.links.luma`) rather than
  a hard-coded URL.

No new file or menu change is needed — the menu already routes here.

### Edit the Community page

`/portfolio/learning-community/` works exactly like Events: `layout: explainer` + `dataKey:
community` → all copy in **`data/community.yml`** (`sections` / `steps` / `cta`, with
`cta.linkKey: discord`). The **GitHub** page is the same pattern (`data/github.yml`,
`cta.linkKey: discussions` + `secondary.linkKey: github`).

### Add a research area / research line

Edit `data/research-projects.yml` → `items:` (`icon` = Ionicons class, `title`, `description`).
This single file is the source for **four** surfaces (coupling #13): the homepage **Research
Areas** section, the **`/portfolio/research-projects/`** page, the "Main research programs" list on
**`/portfolio/all-publications/`**, and the **hero rotating keywords**. The card grid is
count-agnostic, so you can add or remove areas freely. `enable: false` hides the homepage section.

### Add a data-driven explainer page (general pattern)

To add a page like Events/Community/GitHub: (1) `hugo new portfolio/<slug>.md` and set
`layout: explainer` + `dataKey: <key>`; (2) create `data/<key>.yml` with
`eyebrow / title / subtitle / lede / sections / steps / cta` (copy `data/events.yml` as a model);
(3) add a `[[menu.main]]` entry pointing at `portfolio/<slug>`; (4) add `_build: {list: never}` if
it should **not** also be a homepage Activities card.

### Change the hero rotating keywords

Edit the item **titles** in **`data/research-projects.yml`** — the banner derives its rotating
words from them (coupling #9). Do **not** edit `config.toml` for this; the `flipText` block there
is only a disabled fallback. The static heading ("We conduct research about") is
`params.banner.heading`.

### Edit the About text, CTA, nav menu, or shared links

All in `config.toml`: `[params.about].content` (HTML allowed), `[params.cta]`, the `[[menu.main]]`
entries (each has `name`, `url`, `weight` — lower weight = further left), and **`[params.links]`**
(the single source for the Discord / GitHub / Luma URLs — coupling #10). The live menu is
People / Research / Events / Community / Resources / Github / Contact.

---

## Content validation

`scripts/check-content.py` is a **pure-Python (stdlib only, no npm)** checker for the coupling
points. Run it before every commit:

```
python3 scripts/check-content.py            # report; exit 1 if any ERROR
python3 scripts/check-content.py --strict    # treat WARNINGs as errors too
python3 scripts/check-content.py --quiet      # errors only
```

It reports **errors** (things that break the site — a missing image, a resource outside the vocab,
a `dataKey` with no data file, a broken menu URL, a missing `key`/`aliases`, a Discord URL that
drifted out of sync) and **warnings/notes** (a journal with no cover, a one-off topic that looks
like a typo, an author name that resembles a team member but matched no alias). Each check maps to
a row of [the coupling map](#the-coupling-map).

**Optional git hook** (blocks a commit on any error, no npm):

```
git config core.hooksPath scripts/git-hooks      # enable once per clone
git commit --no-verify                            # bypass for a single commit
```

---

## Design system

Defined in **`assets/css/custom.css`** (loaded after the theme's `style.css`, so it wins). It's
a "space-inspired" palette — deep-navy base, cyan sun-flare, amber city-lights — exposed as CSS
custom properties on `:root`:

| Token | Value | Use |
|---|---|---|
| `--ink` | `#0a1024` | deepest background (footer, hero base) |
| `--navy` / `--navy-2` | `#0f1836` / `#131f47` | dark surfaces, nav, gradients |
| `--cyan` | `#2ed6ee` | bright accent — **dark backgrounds only** |
| `--cyan-600` | `#06b6d4` | buttons / accents |
| `--cyan-ink` | `#0e7490` | cyan for text/links on **white** (AA-contrast) |
| `--amber` / `--amber-ink` | `#ffb84d` / `#b06d00` | warm accent (bright / on-white) |

Plus `--text*`, `--muted`, `--surface*`, `--radius*`, `--ease`, `--shadow-*`, and the font
tokens `--font-display` (**Space Grotesk**) / `--font-sans` (**Inter**), both loaded in
`head.html`. **To restyle the site, edit `custom.css`** — change a token once and it propagates.

Key pieces:

- **Nav:** dark frosted glass (transparent over the hero, opaque on scroll) paired with the
  white logo.
- **Hero:** the Earth-at-night photo (`static/images/slider7-hires.jpg`) with a slow Ken-Burns
  zoom (CSS) + scroll parallax (`assets/js/custom.js`); all motion respects
  `prefers-reduced-motion`.
- **Cards:** the homepage **Research Areas** and **Research methods** sections share the
  `.info-grid` / `.info-card` system, which is **count-agnostic** (flex-wrap centers any partial
  last row) — add a 6th research area or a 7th method with no CSS change.
- **Logo/favicons:** hand-built **vector** set in `static/images/` — `logo-white.svg` (nav, via
  `params.logo`) and `favicon.svg` / `favicon.ico` / `apple-touch-icon.png` (wired in
  `head.html`). The About-section image (`params.about.image`) is the raster `about/about.png`.

## Conventions & gotchas

- **Never edit `themes/timer-hugo/**` to customize** — add/adjust a project-root override
  instead (see [Architecture](#architecture)). The theme copies still exist but are shadowed;
  edit the **root** `layouts/` versions.
- **Don't remove `wow.min.js`** from `footer.html` — the theme's `script.js` calls
  `new WOW().init()`, which reveals every animated element. Remove it and content stays hidden.
- **`public/` and `resources/` are gitignored** build artifacts — never commit them.
- **Concurrent editors:** this repo is often edited from more than one place. `git fetch`
  before committing, keep commits scoped, and fetch-then-push (rebase if the remote moved).
- **Book covers can live in two places:** a book may have a cover in `static/images/blog/`
  (research `image:`) *and* `static/images/portfolio/` (its Activity card) — update both
  (coupling #12).
- **Latent sections:** `content/{contact,gallery,service}/` and
  `data/{contact,gallery,service}.yml` still contain theme placeholder text and aren't linked in
  the menu — ignore them. `data/about.yml` is intentionally blank (the People page renders the
  roster entirely from `team.yml`). The top-of-file comments in `data/team.yml` about editing
  `themes/timer-hugo/.../team.html` are historical — customization is via the root `team-card.html`.

## Credits & license

- **Theme:** [`timer-hugo`](https://themefisher.com/) by **Themefisher** — see
  `themes/timer-hugo/LICENSE`. The "Design and Developed by Themefisher" credit in the footer is
  required by that license; please keep it.
- **Content** (text, research, logos, photos) © the QuaRCS-lab Network.
- This repository currently has **no top-level `LICENSE` file**. If you intend others to reuse
  the code/content, consider adding one (the theme's own license continues to apply to the theme).

Questions / contact: <https://carlos-mendez.rbind.io/#contact> ·
GitHub: <https://github.com/quarcs-lab>
