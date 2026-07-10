# AGENTS.md

Durable instructions for Codex and other coding agents working in this repository. Keep this file practical and repo-specific: commands, paths, rules, verification, and review expectations. For full context, read `README.md`; this file is the operating checklist.

## Project

This is the QuaRCS-lab Network public website, a Hugo static site using the vendored `timer-hugo` theme. Netlify deploys from `master`; a push to `master` is a production deploy.

Core stack:

- Hugo `0.89.4`, pinned to match Netlify.
- Vendored Themefisher `timer-hugo` theme under `themes/timer-hugo/`.
- Project-root Hugo overrides under `layouts/`, `assets/css/custom.css`, and `assets/js/custom.js`.
- Content in `content/` and structured data in `data/`.
- No Node/npm build step. The checker is Python stdlib only.

## Commands

- Content validation: `python3 scripts/check-content.py`
- Strict validation: `python3 scripts/check-content.py --strict`
- Local Hugo binary: `"$HOME/Library/Application Support/Hugo/0.89.4/hugo"`
- Local preview: `"$HOME/Library/Application Support/Hugo/0.89.4/hugo" server -D`
- Production-style build: `"$HOME/Library/Application Support/Hugo/0.89.4/hugo" --gc --minify`

Run `python3 scripts/check-content.py` after content, data, config, image-path, or template changes. Run a Hugo build for layout/CSS/JS/image changes or any change with visual risk.

## Golden Rules

- Do not edit `themes/timer-hugo/**` for customization. Shadow theme files from the project root instead.
- Keep CSS changes in `assets/css/custom.css`; it loads after the theme stylesheet and is the design-system home.
- Keep JS overrides in `assets/js/custom.js`; it loads after the theme JS.
- Do not remove `wow.min.js` from `layouts/partials/footer.html`; theme JS depends on `new WOW().init()`.
- Do not commit `public/` or `resources/`; they are generated artifacts and gitignored.
- Keep the Themefisher footer credit.
- Be careful with concurrent edits. Check `git status`, keep changes scoped, and never overwrite unrelated user work.

## Routing Map

Use this first, then consult the README coupling map before changing coupled content.

| Change | Edit |
| --- | --- |
| Menus, homepage copy, shared links, logo path | `config.toml` |
| Hero keywords and research areas | `data/research-projects.yml` |
| Publications | `content/research/*.md` plus journal/image data |
| People | `data/team.yml` plus `assets/images/team/` |
| Journal covers | `data/journal_covers.yml` plus `static/images/journals/` |
| Resources hub | `data/resources.yml` |
| Events, community, GitHub pages | `data/{events,community,github}.yml` |
| Homepage activity cards | `content/portfolio/*.md` |
| Styles, palette, motion | `assets/css/custom.css`, `assets/js/custom.js` |
| Logo, favicons, static content images | `static/images/` |

## Coupled Content

Before adding or changing people, publications, resources, events, research areas, links, or image paths, read `README.md` -> "The coupling map".

Common failure points:

- Publications link to people through `data/team.yml` `key` and `aliases`.
- Books and working papers need explicit `pubtype: book` or `pubtype: working`; `tags[0]` does not decide type.
- Article `tags[0]` is the journal name and usually needs a matching `data/journal_covers.yml` entry and image under `static/images/journals/`.
- Resource `type` and `topic` values must match vocab lists in `data/resources.yml`.
- `data/research-projects.yml` drives the homepage research areas, research-projects page, all-publications program list, and hero rotating keywords.
- Shared Discord/GitHub/Luma links live in `[params.links]` in `config.toml`.

## Design System

Respect the existing visual language:

- Deep navy/space base, cyan accents, amber city-light accents.
- Fonts are Space Grotesk for display and Inter for body.
- Use CSS custom properties from `:root` in `assets/css/custom.css`.
- Bright `--cyan`, `--amber`, `--violet`, and `--emerald` are for dark backgrounds. Use `--cyan-ink`, `--amber-ink`, `--violet-ink`, `--emerald-ink`, and `--muted` on white/light surfaces.
- Preserve responsive behavior, contrast, focus states, `prefers-reduced-motion`, and existing section/card patterns.
- Avoid generic stock-photo aesthetics, decorative blobs, unreadable chart art, and text baked into images when HTML text would work better.

## Image And Visual Asset Workflow

Codex will often be asked to create images to make the site more beautiful. Treat image work as part design system, part build pipeline.

Before creating or replacing an image:

- Inspect the target template, CSS, and current image dimensions/use.
- Decide whether the image should be Hugo-processed from `assets/images/` or copied verbatim from `static/images/`.
- Keep meaningful text in HTML, not inside raster images, unless the image is itself a document cover or screenshot.
- Write descriptive `alt` text in the template/front matter/data that references the image.
- Prefer WebP/JPG for photos and rich generated visuals, PNG for transparency, and SVG for logos/icons/diagrams that should remain vector.

Where to put images:

- Hero background: `assets/images/slider7-hires.jpg` is read via `resources.Get` in `layouts/partials/banner.html` and resized by Hugo. If replacing it, update `config.toml` only if the path changes.
- Team portraits: `assets/images/team/`; `layouts/partials/team-card.html` crops them to square WebP avatars.
- About image: `static/images/about/`, referenced by `[params.about].image` in `config.toml`.
- Portfolio/activity images: `static/images/portfolio/`, referenced from `content/portfolio/*.md`.
- Publication images and book covers: `static/images/blog/`, referenced by `content/research/*.md`.
- Journal covers: `static/images/journals/`, mapped in `data/journal_covers.yml`.
- Logos and favicons: `static/images/`; keep the existing SVG/PNG/ICO set coherent.

Image-generation guidance:

- Fit the QuaRCS subject matter: spatial data science, regional inequality, sustainable development, satellite/night-lights, maps, networks, research collaboration, econometrics, and machine learning.
- Make visuals specific and inspectable, not merely atmospheric.
- Keep the palette compatible with the existing navy/cyan/amber system.
- Generate at or above the displayed size, then let Hugo/CSS scale down.
- Check mobile and desktop crops, especially hero and card thumbnails.
- If an image path changes, update all coupled references and run `python3 scripts/check-content.py`.

## Verification

Minimum checks:

- Run `python3 scripts/check-content.py`.
- For visual/template/CSS/image changes, run a Hugo build with the pinned binary.
- For major visual changes, serve locally and inspect desktop and mobile viewports. Watch for broken images, poor crops, low contrast, layout shift, hidden WOW-animated content, and text overlap.

If a check cannot be run, state that clearly in the final response with the reason.

## Review Guidelines

When reviewing this repository, prioritize:

- Broken Hugo paths or theme overrides.
- Coupling-map regressions.
- Image references that point to the wrong pipeline (`assets/` vs `static/`).
- Accessibility regressions: missing alt text, low contrast, text baked into decorative images, keyboard/focus issues.
- Mobile crop/layout problems.
- Accidental edits to `themes/timer-hugo/**`, generated artifacts, or unrelated files.

## Codex Guidance Maintenance

This file should stay under the practical instruction limit. Add rules only when they prevent repeated mistakes or capture stable workflow knowledge. Put deep explanations in `README.md` and point here to the relevant section.
