---
# One publication = one file in content/research/. Rendered by layouts/research/list.html
# (cards) and layouts/post/single.html (detail page). Scaffold with the pinned Hugo:
#   "$HOME/Library/Application Support/Hugo/0.89.4/hugo" new research/<slug>.md
# then fill the fields below and run: python3 scripts/check-content.py
title: "{{ replace .Name "-" " " | title }}"
author: ""                        # e.g. "Harry Aginta, Carlos Mendez". Names that match a team
                                  # member's alias (data/team.yml) auto-link to /people.
date: "{{ dateFormat "2006-01-02" .Date }}"   # quoted YYYY-MM-DD — drives the year grouping
type: post                        # REQUIRED — routes to the single-publication template
tags: [""]                        # articles: tags[0] = EXACT journal name; it must match a key
                                  # in data/journal_covers.yml to show a cover (else a text card)
topics: [""]                      # 1–3 topics; reuse the existing spellings (no central vocab)
links: [{"label": "Read paper", "url": ""}]   # inline JSON; the first 3 render as buttons
image: ""                         # optional; static/images/blog/<slug>.jpg (used for non-articles)
# pubtype: "book"                 # set for a book | working paper (omit it for a journal article)
# cover: ""                       # optional per-article cover override, relative to static/images/
---

Abstract goes here — the first ~220 characters become the card excerpt.
