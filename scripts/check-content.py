#!/usr/bin/env python3
"""
check-content.py — QuaRCS-lab content consistency checker.

Guards the ~14 "coupling points" where editing one thing silently requires editing
another (see README.md -> "The coupling map"). Run it before every commit:

    python3 scripts/check-content.py            # report; exit 1 if any ERROR
    python3 scripts/check-content.py --strict    # treat WARNINGs as errors too
    python3 scripts/check-content.py --quiet      # errors only

No third-party dependencies. `tomllib` (Python >= 3.11 stdlib) parses config.toml;
`json` parses the inline `[...]`/`{...}` values in front matter; the small readers
below parse this repo's flat YAML. PyYAML is used only if it happens to be importable.
Never touches the Hugo build — it is a local, pre-commit correctness gate.

Exit codes: 0 = clean (warnings allowed), 1 = at least one ERROR, 2 = the checker
itself failed to run (unreadable/unparseable input).
"""

import sys
import os
import re
import json
import glob

try:
    import tomllib  # py3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

try:
    import yaml as _pyyaml  # optional fidelity upgrade; not required
except Exception:
    _pyyaml = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Journals that intentionally have no cover (see data/journal_covers.yml). Articles in
# these show the styled text-fallback card by design -> reported as info, not warning.
EXPECTED_FALLBACK_JOURNALS = {
    "Economies", "Empirical Economics Letters", "Economía",
    "Economics Bulletin", "Coyuntural Economics",
    "Forum of International Development Studies",
}

# Aliases kept deliberately for future-proofing even though they match 0 publications
# today (the person appears under a shorter/other form). Suppresses the zero-match warn.
DEFENSIVE_ALIASES = {"Erick Gonzales Rocha", "Lykke Andersen"}


# --------------------------------------------------------------------------- reporting
class Reporter:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def error(self, msg, where=""):
        self.errors.append((msg, where))

    def warn(self, msg, where=""):
        self.warnings.append((msg, where))

    def info(self, msg, where=""):
        self.infos.append((msg, where))

    def dump(self, quiet=False):
        def block(title, items):
            if not items:
                return
            print(f"\n{title}")
            for msg, where in items:
                loc = f"  ({where})" if where else ""
                print(f"  {msg}{loc}")
        block("ERRORS", self.errors)
        if not quiet:
            block("WARNINGS", self.warnings)
            block("NOTES", self.infos)


# ------------------------------------------------------------------------ tiny parsers
def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def _strip_inline_comment(v):
    """Drop a ` # ...` trailing comment when the # is not inside quotes.
    Safe for this repo (no value legitimately contains ' #')."""
    in_q = None
    for i, ch in enumerate(v):
        if ch in "\"'":
            in_q = None if in_q == ch else (in_q or ch)
        elif ch == "#" and in_q is None and i > 0 and v[i - 1] in " \t":
            return v[:i].rstrip()
    return v


def _scalar(v):
    """Parse a front-matter/YAML scalar value: JSON flow collections as JSON, else a
    de-quoted string (with any inline comment stripped)."""
    v = _strip_inline_comment(v).strip()
    if v and v[0] in "[{":
        try:
            return json.loads(v)
        except Exception:
            return v  # leave as raw string; specific checks tolerate this
    return _unquote(v)


def read_frontmatter(path):
    """Return the front-matter of a Hugo markdown file as a dict. Only the flat, single
    line `key: value` fields this checker needs are parsed (which is all these files use)."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end]
    out = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t":  # nested line (e.g. multi-line _build) — ignore safely
            continue
        m = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            out[m.group(1)] = _scalar(m.group(2))
    return out


def load_team(path):
    """data/team.yml -> list of active member dicts. Members are flat, so a line-based
    reader is exact. Commented-out (#) members are skipped, matching the live site."""
    if _pyyaml:
        with open(path, encoding="utf-8") as fh:
            data = _pyyaml.safe_load(fh) or {}
        return [m for m in (data.get("members") or []) if isinstance(m, dict)]
    members, cur = [], None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            m = re.match(r"-\s*name\s*:\s*(.*)$", s)
            if m:
                if cur:
                    members.append(cur)
                cur = {"name": _scalar(m.group(1))}
                continue
            if cur is None:
                continue
            fm = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", s)
            if fm:
                cur[fm.group(1)] = _scalar(fm.group(2))
    if cur:
        members.append(cur)
    return members


def load_covers(path):
    """data/journal_covers.yml -> {journal name: relative image path}."""
    if _pyyaml:
        with open(path, encoding="utf-8") as fh:
            data = _pyyaml.safe_load(fh) or {}
        return data.get("covers") or {}
    covers = {}
    with open(path, encoding="utf-8") as fh:
        in_covers = False
        for raw in fh:
            s = raw.rstrip("\n")
            st = s.strip()
            if not st or st.startswith("#"):
                continue
            if re.match(r"covers\s*:\s*$", st):
                in_covers = True
                continue
            if in_covers and s[:1] not in " \t":  # dedent -> left the covers map
                in_covers = False
            if in_covers:
                m = re.match(r'"?([^":]+?)"?\s*:\s*(\S+)\s*$', st)
                if m:
                    covers[m.group(1)] = m.group(2)
    return covers


def _load_yaml_lists(path, keys):
    """Extract the named top-level block-sequence keys from a simple data file.
    Returns {key: [items]} where an item is a scalar string, or a dict for `- k: v`
    blocks. Handles this repo's data files (resources.yml, research-projects.yml)."""
    if _pyyaml:
        with open(path, encoding="utf-8") as fh:
            return _pyyaml.safe_load(fh) or {}
    result = {k: [] for k in keys}
    scalars = {}
    cur_key = None
    cur_item = None
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    for raw in lines:
        s = raw.rstrip("\n")
        st = s.strip()
        if not st or st.startswith("#"):
            continue
        indent = len(s) - len(s.lstrip(" "))
        # top-level key?
        m = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", st)
        if indent == 0 and m:
            key, val = m.group(1), _strip_inline_comment(m.group(2)).strip()
            cur_item = None
            if key in keys:
                cur_key = key
            else:
                cur_key = None
                if val != "":
                    scalars[key] = _scalar(val)
            continue
        if cur_key is None:
            continue
        # sequence item under the current key
        seq = re.match(r"-\s*(.*)$", st)
        if seq:
            rest = seq.group(1)
            kv = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", rest)
            if kv:  # "- key: value" -> start a dict item
                cur_item = {kv.group(1): _scalar(kv.group(2))}
                result[cur_key].append(cur_item)
            else:  # "- scalar"
                result[cur_key].append(_scalar(rest))
                cur_item = None
            continue
        # continuation field of the current dict item
        if isinstance(cur_item, dict):
            kv = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", st)
            if kv:
                cur_item[kv.group(1)] = _scalar(kv.group(2))
    result.update({k: v for k, v in scalars.items() if k in ("enable", "title")})
    return result


def load_config():
    path = os.path.join(ROOT, "config.toml")
    if tomllib:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    raise RuntimeError("tomllib unavailable (need Python >= 3.11)")


# ------------------------------------------------------------------------ path helpers
def static_exists(rel):
    if not rel:
        return False
    rel = str(rel).strip().strip("\"'").lstrip("/")
    return os.path.isfile(os.path.join(ROOT, "static", rel))


def asset_exists(rel):
    # Files under assets/ are processed by Hugo's pipeline (e.g. team avatars).
    if not rel:
        return False
    rel = str(rel).strip().strip("\"'").lstrip("/")
    return os.path.isfile(os.path.join(ROOT, "assets", rel))


def journal_cover_exists(rel):
    # journal_covers.yml values are relative to static/images/, not static/
    if not rel:
        return False
    return os.path.isfile(os.path.join(ROOT, "static", "images", str(rel).strip()))


# ------------------------------------------------------------------------------- loader
class Ctx:
    pass


def load_all():
    c = Ctx()
    c.cfg = load_config()
    c.team = load_team(os.path.join(ROOT, "data", "team.yml"))
    c.covers = load_covers(os.path.join(ROOT, "data", "journal_covers.yml"))
    c.resources = _load_yaml_lists(
        os.path.join(ROOT, "data", "resources.yml"), ["types", "topics", "items"]
    )
    c.rprojects = _load_yaml_lists(
        os.path.join(ROOT, "data", "research-projects.yml"), ["items"]
    )
    c.research = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content", "research", "*.md"))):
        if os.path.basename(p) == "_index.md":
            continue
        fm = read_frontmatter(p)
        fm["_file"] = os.path.relpath(p, ROOT)
        fm["_base"] = os.path.basename(p)
        c.research.append(fm)
    c.portfolio = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content", "portfolio", "*.md"))):
        if os.path.basename(p) == "_index.md":
            continue
        fm = read_frontmatter(p)
        fm["_file"] = os.path.relpath(p, ROOT)
        c.portfolio.append(fm)
    return c


def tags0(fm):
    t = fm.get("tags")
    return t[0] if isinstance(t, list) and t else None


def pub_type(fm):
    return fm.get("pubtype") or "article"


# ------------------------------------------------------------------------------- checks
def check_journal_covers(c, rep):
    """Coupling #1: every article's tags[0] should map to a cover key + on-disk file."""
    for fm in c.research:
        if pub_type(fm) != "article":
            continue
        if fm.get("cover"):  # explicit self-cover overrides the journal cover
            if not static_exists(fm["cover"]):
                rep.error(f'cover image missing: {fm["cover"]}', fm["_file"])
            continue
        journal = tags0(fm)
        if not journal:
            rep.warn("article has no tags[0] (journal name)", fm["_file"])
            continue
        rel = c.covers.get(journal)
        if rel is None:
            if journal in EXPECTED_FALLBACK_JOURNALS:
                rep.info(f'text-fallback (by design): "{journal}"', fm["_base"])
            else:
                rep.warn(
                    f'journal "{journal}" has no cover key -> text-fallback card; add it '
                    f"to data/journal_covers.yml or list it as an intended fallback",
                    fm["_base"],
                )
        elif not journal_cover_exists(rel):
            rep.error(f'cover file missing on disk: static/images/{rel} (journal "{journal}")',
                      fm["_base"])


def check_orphan_covers(c, rep):
    used = {tags0(fm) for fm in c.research if pub_type(fm) == "article"}
    for journal, rel in c.covers.items():
        if journal not in used:
            rep.warn(f'cover key "{journal}" is used by no article (orphan)', "journal_covers.yml")
        if not journal_cover_exists(rel):
            rep.error(f'cover file missing on disk: static/images/{rel}', "journal_covers.yml")


def check_topic_vocab(c, rep):
    """Coupling #2: topics have no central vocab — flag singletons as likely typos."""
    counts = {}
    for fm in c.research:
        for t in (fm.get("topics") or []):
            counts[t] = counts.get(t, 0) + 1
    for t, n in sorted(counts.items()):
        if n == 1:
            rep.warn(f'topic "{t}" is used by only one publication — typo of an existing topic?',
                     "content/research")


def check_pubtype(c, rep):
    """Coupling #3: a book/working paper must set pubtype, else it is mislabeled Article."""
    booky = re.compile(r"\b(book|chapter|press|publisher|springer|routledge)\b", re.I)
    for fm in c.research:
        if fm.get("pubtype"):
            continue
        j = tags0(fm) or ""
        if booky.search(j):
            rep.warn(f'looks book-like (tags[0]="{j}") but has no pubtype -> shown as "Article"',
                     fm["_base"])


def check_resources_vocab(c, rep):
    """Coupling #5: item type/topic must be in the vocab lists, else it renders nowhere."""
    types = set(c.resources.get("types") or [])
    topics = set(c.resources.get("topics") or [])
    for i, it in enumerate(c.resources.get("items") or []):
        if not isinstance(it, dict):
            continue
        title = it.get("title", f"item #{i+1}")
        if it.get("type") not in types:
            rep.error(f'resource type "{it.get("type")}" not in types: vocab ({title})',
                      "data/resources.yml")
        if it.get("topic") not in topics:
            rep.error(f'resource topic "{it.get("topic")}" not in topics: vocab ({title})',
                      "data/resources.yml")


def check_portfolio(c, rep):
    """Coupling #6: layout -> template must exist; dataKey -> data file must exist."""
    for fm in c.portfolio:
        layout = fm.get("layout")
        if layout:
            tmpl = os.path.join(ROOT, "layouts", "portfolio", f"{layout}.html")
            if not os.path.isfile(tmpl):
                rep.error(f'layout "{layout}" has no layouts/portfolio/{layout}.html', fm["_file"])
        dk = fm.get("dataKey")
        if dk:
            if not os.path.isfile(os.path.join(ROOT, "data", f"{dk}.yml")):
                rep.error(f'dataKey "{dk}" has no data/{dk}.yml (page renders blank)', fm["_file"])
        if layout == "explainer" and not dk:
            rep.error("layout: explainer requires a dataKey:", fm["_file"])


def check_images(c, rep):
    """Coupling #12/#14: every referenced image must exist on disk."""
    for m in c.team:
        # Team avatars run through Hugo's image pipeline, so they live in
        # assets/images/team/ (not static/). Accept either location.
        if m.get("image") and not (asset_exists(m["image"]) or static_exists(m["image"])):
            rep.error(f'team image missing: {m["image"]} ({m.get("name")})', "data/team.yml")
    for fm in c.research:
        for field in ("image", "cover"):
            if fm.get(field) and not static_exists(fm[field]):
                rep.error(f'{field} image missing: {fm[field]}', fm["_base"])
    for fm in c.portfolio:
        if fm.get("image") and not static_exists(fm["image"]):
            rep.error(f'portfolio image missing: {fm["image"]}', fm["_file"])
    params = c.cfg.get("params", {})
    for label, rel in (("logo", params.get("logo")),
                       ("banner.bgImage", params.get("banner", {}).get("bgImage")),
                       ("about.image", params.get("about", {}).get("image"))):
        if rel and not static_exists(rel):
            rep.error(f'config {label} image missing: {rel}', "config.toml")


def check_menu(c, rep):
    """Coupling #8: each non-external menu URL must resolve to content."""
    for entry in c.cfg.get("menu", {}).get("main", []):
        url = (entry.get("url") or "").strip("/")
        if not url or url.startswith("http"):
            continue
        cands = [
            os.path.join(ROOT, "content", url),
            os.path.join(ROOT, "content", url + ".md"),
            os.path.join(ROOT, "content", url, "_index.md"),
            os.path.join(ROOT, "content", url, "index.md"),
        ]
        if not any(os.path.exists(x) for x in cands):
            rep.error(f'menu "{entry.get("name")}" -> /{url}/ has no matching content', "config.toml")


def check_links_single_source(c, rep):
    """Coupling #10: [params.links] is the single source; the one URL TOML can't dedupe
    (socialIcon vs cta) must equal params.links.discord."""
    params = c.cfg.get("params", {})
    links = params.get("links", {})
    if not links.get("discord"):
        rep.error("params.links.discord is not set (cta.html / community CTA depend on it)",
                  "config.toml")
        return
    for icon in params.get("socialIcon", []):
        u = icon.get("url", "")
        if "discord" in u and u != links["discord"]:
            rep.error(f'socialIcon discord url "{u}" != params.links.discord "{links["discord"]}"',
                      "config.toml")


def check_flip_source(c, rep):
    """Coupling #9: the hero derives its keywords from research-projects.yml titles."""
    items = c.rprojects.get("items") or []
    titles = [it.get("title") for it in items if isinstance(it, dict) and it.get("title")]
    if not titles:
        rep.error("data/research-projects.yml has no item titles -> the hero keywords are empty",
                  "data/research-projects.yml")


def check_team(c, rep):
    """Couplings #4/#11: keys unique + present; designation parseable; alias health."""
    seen = {}
    caps = re.compile(r"[A-Z][A-Z]+(?:\s[A-Z]+)*\.?$")
    for m in c.team:
        name = m.get("name", "?")
        key = m.get("key")
        if not key:
            rep.error(f'team member "{name}" has no key:', "data/team.yml")
        elif key in seen:
            rep.error(f'duplicate team key "{key}" ({name} & {seen[key]})', "data/team.yml")
        else:
            seen[key] = name
        if not m.get("aliases"):
            rep.error(f'team member "{name}" has no aliases: (its publications will not link)',
                      "data/team.yml")
        desig = m.get("designation", "")
        if not caps.search(desig):
            rep.warn(f'"{name}" designation has no trailing ALL-CAPS country -> no country pill',
                     "data/team.yml")


def check_author_aliases(c, rep):
    """Coupling #4: alias health vs the real publication author strings."""
    authors = [str(fm.get("author") or "") for fm in c.research]
    all_alias = []
    for m in c.team:
        for a in (m.get("aliases") or []):
            all_alias.append((a, m.get("name")))
    # aliases that match no publication
    for alias, who in all_alias:
        if alias in DEFENSIVE_ALIASES:
            continue
        if not any(alias in au for au in authors):
            rep.warn(f'alias "{alias}" ({who}) matches no publication author', "data/team.yml")
    # a member whose full alias set matches nothing (affordance hidden)
    for m in c.team:
        al = m.get("aliases") or []
        if al and not any(any(a in au for a in al) for au in authors):
            rep.info(f'member "{m.get("name")}" has 0 linked publications (button hidden)',
                     "data/team.yml")
    # a co-author whose surname AND first initial match a team member, but no alias
    # matched -> probably a missing alias (catches "Tifani H. Siregar"). Requiring the
    # first initial filters out different people who merely share a surname
    # (e.g. "Sabar I. Siregar" vs team member Tifani Siregar).
    team_surnames = {}
    for m in c.team:
        parts = (m.get("name") or "").split()
        if parts:
            team_surnames.setdefault(parts[-1], (m.get("name"), parts[0][:1].upper()))
    alias_set = [a for a, _ in all_alias]
    for fm in c.research:
        au = str(fm.get("author") or "")
        for token in re.split(r",| and | & ", au):
            token = token.strip().rstrip(".").strip()
            tp = token.split()
            if not tp:
                continue
            hit = team_surnames.get(tp[-1])
            if hit and tp[0][:1].upper() == hit[1] and not any(a in token for a in alias_set):
                rep.warn(f'"{token}" looks like {hit[0]} but no alias matched — add an alias?',
                         fm["_base"])


CHECKS = [
    check_journal_covers, check_orphan_covers, check_topic_vocab, check_pubtype,
    check_resources_vocab, check_portfolio, check_images, check_menu,
    check_links_single_source, check_flip_source, check_team, check_author_aliases,
]


def main(argv):
    strict = "--strict" in argv
    quiet = "--quiet" in argv
    try:
        c = load_all()
    except Exception as e:  # pragma: no cover
        print(f"check-content: failed to load content: {e}", file=sys.stderr)
        return 2
    rep = Reporter()
    for chk in CHECKS:
        try:
            chk(c, rep)
        except Exception as e:  # a broken check must not mask the others
            rep.error(f"{chk.__name__} crashed: {e}", "check-content.py")
    print(f"QuaRCS content check — {len(c.research)} publications, "
          f"{len(c.portfolio)} portfolio pages, {len(c.team)} team members")
    rep.dump(quiet=quiet)
    ne, nw, ni = len(rep.errors), len(rep.warnings), len(rep.infos)
    print(f"\nSummary: {ne} errors, {nw} warnings, {ni} notes.")
    if ne or (strict and nw):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
