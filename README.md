# QuaRCS-lab Network — website

Source for the **QuaRCS-lab Network** website: **<https://quarcs.netlify.app>**

QuaRCS (Quantitative Regional and Computational Science) is an international, interdisciplinary
research network that promotes science and innovation for economic, social, and environmental
sustainability, integrating development economics, spatial data science, machine learning, and
satellite remote sensing to understand and inform sustainable development across subnational
regions and countries. The network is part of the UN Sustainable Development Solutions Network
(SDSN). This repository holds the site's content, configuration, and a customized
[Hugo](https://gohugo.io/) theme.

> **Maintaining the site?** Jump to [Editing content](#editing-content) — most updates are just
> adding a publication, a team member, or a resource, then pushing to `master`.

---

## Table of contents

- [Tech stack](#tech-stack)
- [How it builds & deploys](#how-it-builds--deploys)
- [Repository structure](#repository-structure)
- [Architecture](#architecture)
- [Editing content](#editing-content) — publications, people, activities, tutorials, hero
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

No Node/npm build step — the theme's JS/CSS are pre-vendored, and Hugo Pipes handles the
project's CSS/JS.

## How it builds & deploys

**The normal workflow is edit → commit → push.** Netlify does the rest.

```
edit content/config  →  git commit  →  git push origin master  →  Netlify builds & deploys
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
so double-check changes locally if a build is risky.

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
├── config.toml            # Site config: baseURL, theme, menus, homepage params (edit this a lot)
├── netlify.toml           # Netlify build command + pinned Hugo version
├── index.Rmd              # blogdown site descriptor (local authoring only)
├── tryWEB3.Rproj          # RStudio project (local authoring only)
│
├── content/               # Markdown content, one folder per section
│   ├── research/          #   ~80 publication .md files + _index.md  → Research page
│   ├── portfolio/         #   6 "Activities" cards + the Tutorials hub page
│   ├── people/_index.md   #   People page at /people/ (aliases /about/); roster from data/team.yml
│   ├── contact|gallery|service/_index.md   # latent (not linked in the menu)
│
├── data/                  # YAML that feeds templates (see "Editing content")
│   ├── team.yml           #   People roster           (active)
│   ├── resources.yml      #   Tutorials/datasets hub   (active)
│   ├── feature.yml        #   Homepage "Research methods" (active)
│   └── about|service|gallery|contact|client.yml  # blank / latent / disabled
│
├── layouts/               # PROJECT-ROOT template overrides (win over the theme)
│   ├── partials/{head,footer,banner,team,team-card}.html
│   ├── people/list.html            # People page: grouped, animated team grid
│   ├── research/list.html          # filterable publication list
│   └── portfolio/resources.html    # filterable tutorials/datasets/projects hub
│
├── assets/                # Processed by Hugo Pipes (loaded AFTER the theme's)
│   ├── css/custom.css     #   the design system
│   └── js/custom.js        #   hero parallax
│
├── static/                # Copied verbatim to the site root
│   └── images/            #   logos, favicons, hero, team/ photos, blog/ pub images, portfolio/
│
├── themes/timer-hugo/     # Vendored theme — DO NOT edit for customization (override instead)
│
├── public/                # Hugo build output  — GITIGNORED (Netlify regenerates)
└── resources/             # Hugo Pipes cache   — GITIGNORED
```

## Architecture

### The theme-override pattern (read this first)

The theme is vendored in `themes/timer-hugo/` and is **never edited for customization**.
Instead, a file placed at the **project root** with the same path *shadows* the theme's copy
(Hugo's template/asset lookup prefers the project root). Only a small, surgical set is
overridden:

| Project-root override | Replaces / adds | Purpose |
|---|---|---|
| `layouts/partials/head.html` | theme `head.html` | Modern favicons; preloads Google Fonts (Space Grotesk + Inter); loads theme `style.css` **then `custom.css` last** so custom rules win. |
| `layouts/partials/footer.html` | theme `footer.html` | Footer + Themefisher credit; loads theme JS (incl. **wow-js**) then `script.js` then **`custom.js` last**. |
| `layouts/partials/banner.html` | theme `banner.html` | Cinematic hero: layered media (parallax + Ken-Burns zoom), gradient overlay, rotating keywords, scroll cue. |
| `layouts/research/list.html` | theme `_default/list.html` (research section) | Publications grouped by year with JS search + year + type filters. |
| `layouts/portfolio/resources.html` | *(new; `layout: resources`)* | Datasets/tutorials/projects hub, rendered from `data/resources.yml`. |
| `layouts/people/list.html` | *(new; `people` section)* | People page: intro header + team grid + CTA (drops the theme's empty blurb/feature/clients sections). |
| `layouts/partials/team.html` | theme `team.html` | Splits `data/team.yml` into **Directors/Associates** groups (by role) with an intro lead. |
| `layouts/partials/team-card.html` | *(new)* | One member card: circular ringed avatar, country pill, clamped role/bio, icon social links, fast row-reset reveal. |
| `assets/css/custom.css` | overrides theme `style.css` | The design system (see [Design system](#design-system)). |
| `assets/js/custom.js` | *(new)* | Hero scroll parallax. |

Everything else (the navbar `header.html`, the homepage `index.html`, the
`about/portfolio/feature/cta` partials, `single.html`, `404.html`, and all
`static/plugins/*`) comes straight from the theme. **The load order matters:** `custom.css`
must load after `style.css`, and `custom.js` after `script.js`, or the overrides lose.

### Homepage composition

`themes/timer-hugo/layouts/index.html` stacks five partials, each driven by config or data:

1. **banner** (overridden) ← `[params.banner]` + `[[params.banner.flipText]]`
2. **about** ← `[params.about]` (title, HTML `content`, `image`)
3. **portfolio** ("Activities") ← cards from `content/portfolio/*.md`
4. **feature** ("Research methods") ← `data/feature.yml`
5. **cta** ← `[params.cta]`

---

## Editing content

Most maintenance is here. After any edit: **commit and push to `master`.**

### Add a publication

1. Create `content/research/<slug>.md`:

   ```yaml
   ---
   title: "Okun's law and spatial regimes in Indonesia: A machine learning approach"
   author: Tifani Husna Siregar, Harry Aginta and Carlos Mendez
   date: "2026-05-28"          # quoted YYYY-MM-DD — drives the year grouping
   type: post                  # required
   tags: ["Economic Modelling"]  # usually the journal name
   image: "images/blog/<slug>.webp"
   ---
   One-paragraph abstract (this first paragraph becomes the list summary).

   [- Link to the published paper](https://doi.org/10.xxxx/xxxxx)
   ```

2. Put the thumbnail at `static/images/blog/<slug>.webp` (or `.jpg/.png`).
3. It appears automatically on **/research**, grouped under its year, and is searchable.

**Publication type filter (Journal articles / Books & chapters / Working papers):** the type is
decided in this order — (1) an explicit `pubtype: "book"` / `"working"` / `"article"` in
front-matter wins; (2) otherwise a tag containing `Book` → book or `Working paper` → working;
(3) otherwise it's an `article`. If a non-article's tags don't say so (e.g. a book tagged only
with a publisher), **set `pubtype` explicitly** (see `content/research/mendez2020-book-convergence-clubs.md`).

### Add or deactivate a team member

Edit `data/team.yml` under `members:` (note the `key : value` spacing style). Live example:

```yaml
  - name  : Carlos Mendez
    image : images/team/carlos-mendez.jpg
    designation : Founding research director. Associate professor, Nagoya University, JAPAN.
    description : "Research interests: Development Macroeconomics, Regional Economics, Spatial econometrics"
    net         : https://www.researchgate.net/profile/Carlos_Mendez54   # globe icon
    linkedIn    : https://www.linkedin.com/in/mendezguerra                # LinkedIn icon
    web         : https://carlos-mendez.org                               # "Website" text link
```

- **Add:** append a block like the above; drop the photo in `static/images/team/` (square/round
  crop recommended — the theme renders it as a circle).
- **Deactivate:** comment the member's block out with leading `#` (don't delete — keeps history
  and makes it easy to re-add). Members render in file order.

### Add an Activity card, or a tutorial / dataset / project

- **Homepage "Activities" card:** create `content/portfolio/<slug>.md` with `type: portfolio`,
  `title`, `image: images/portfolio/<file>.jpg`, and `caption: Find out more`; put the image in
  `static/images/portfolio/`. Cards sort by `date` (newest first).
- **Tutorials/datasets/projects hub** (the "Tutorials" menu → `/portfolio/data-tutorials`):
  append one entry to `items:` in `data/resources.yml` — no new file needed:

  ```yaml
    - title  : "Provincial income & convergence clubs in Indonesia 2001–2017"
      type   : Dataset            # must be one of `types:` at the top of the file
      topic  : Regional convergence   # must be one of `topics:`
      url    : "https://rpubs.com/quarcs-lab/..."
      author : "Gunawan & Mendez (2020)"   # optional
      lang   : R                            # optional badge
      desc   : "Short description."          # optional
  ```

  To add a new filter option, extend the `types:` or `topics:` lists at the top of the file.

### Change the hero rotating keywords

Edit the `[[params.banner.flipText]]` list in `config.toml`. The **first** entry shows first.
The static heading ("We conduct research about") and subheading are `params.banner.heading` /
`params.banner.description`.

### Edit the About text, CTA, or nav menu

All in `config.toml`: `[params.about].content` (HTML allowed), `[params.cta]`, and the
`[[menu.main]]` entries (each has `name`, `url`, `weight` — lower weight = further left).

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
- **Logo/favicons:** hand-built **vector** set in `static/images/` — `logo-white.svg` (nav, via
  `params.logo`) and `favicon.svg` / `favicon.ico` / `apple-touch-icon.png` (wired in
  `head.html`); these are resolution-independent. The About-section image (`params.about.image`)
  is the raster `about/about.png`; `logo-stacked.svg` remains as an unused vector alternate.

## Conventions & gotchas

- **Never edit `themes/timer-hugo/**` to customize** — add/adjust a project-root override
  instead (see [Architecture](#architecture)). The theme copies of `head.html`/`banner.html`
  still exist but are shadowed; edit the **root** `layouts/` versions.
- **Don't remove `wow.min.js`** from `footer.html` — the theme's `script.js` calls
  `new WOW().init()`, which reveals every animated element. Remove it and content stays hidden.
- **`public/` and `resources/` are gitignored** build artifacts — never commit them.
- **Concurrent editors:** this repo is often edited from more than one place. `git fetch`
  before committing, keep commits scoped, and fetch-then-push (rebase if the remote moved).
- **Latent sections:** `content/{contact,gallery,service}/` and
  `data/{contact,gallery,service}.yml` still contain theme placeholder text and aren't linked in
  the menu — ignore them (don't mistake `data/contact.yml`'s "Kings Street" text for real data).
- **`data/about.yml` is intentionally blank** — the People page (`layouts/people/list.html`) no
  longer renders that section anyway; the roster comes entirely from `team.yml`.

## Credits & license

- **Theme:** [`timer-hugo`](https://themefisher.com/) by **Themefisher** — see
  `themes/timer-hugo/LICENSE`. The "Design and Developed by Themefisher" credit in the footer is
  required by that license; please keep it.
- **Content** (text, research, logos, photos) © the QuaRCS-lab Network.
- This repository currently has **no top-level `LICENSE` file**. If you intend others to reuse
  the code/content, consider adding one (the theme's own license continues to apply to the theme).

Questions / contact: <https://carlos-mendez.rbind.io/#contact> ·
GitHub: <https://github.com/quarcs-lab>
